"""Command-line interface for the VenvKiller tool."""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Confirm
from rich.text import Text

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Button, Footer, Header, Static
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual import events

from venvkiller import __version__, DEFAULT_RECENT_THRESHOLD, DEFAULT_OLD_THRESHOLD
from venvkiller.finder import find_venvs, has_requirement_files
from venvkiller.analyzer import get_venv_info, classify_venv_age, open_containing_folder
from venvkiller.cleaner import delete_multiple_venvs, safe_delete_venv

# Initialize console for non-TUI output
console = Console()

def format_bytes(bytes_: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_ < 1024 or unit == 'TB':
            return f"{bytes_:.1f} {unit}"
        bytes_ /= 1024

class VenvDetailsPanel(Static):
    """Panel that shows details about the selected venv."""
    
    def __init__(self, venv=None):
        super().__init__()
        self.venv = venv
        
    def update_venv(self, venv):
        """Update the displayed venv details."""
        self.venv = venv
        self.update()
        
    def render(self):
        """Render the venv details."""
        if not self.venv:
            return "No virtual environment selected"
        
        details = []
        details.append(f"[bold]Path:[/bold] {self.venv['path']}")
        details.append(f"[bold]Size:[/bold] [cyan]{self.venv['size_formatted']}[/cyan]")
        details.append(f"[bold]Last Modified:[/bold] [magenta]{self.venv['modified_ago']}[/magenta]")
        details.append(f"[bold]Python Version:[/bold] [blue]{self.venv.get('py_version', 'Unknown')}[/blue]")
        
        # Requirements info
        req_status = "[green]✓[/green]" if self.venv.get('has_requirements', False) else "[red]✗[/red]"
        details.append(f"[bold]Requirements Files:[/bold] {req_status}")
        
        if self.venv.get('packages_count', 0) > 0:
            details.append(f"[bold]Packages:[/bold] [cyan]{self.venv['packages_count']}[/cyan]")
        
        return "\n".join(details)

class StatsPanel(Static):
    """Panel that shows overall stats."""
    
    def __init__(self, total_size=0, venv_count=0, saved_size=0, scan_time=0):
        super().__init__()
        self.total_size = total_size
        self.venv_count = venv_count
        self.saved_size = saved_size
        self.scan_time = scan_time
        
    def update_stats(self, total_size, venv_count, saved_size=None, scan_time=None):
        """Update the statistics."""
        self.total_size = total_size
        self.venv_count = venv_count
        if saved_size is not None:
            self.saved_size = saved_size
        if scan_time is not None:
            self.scan_time = scan_time
        self.update()
        
    def render(self):
        """Render the stats panel."""
        return (
            f"[bold]Found:[/bold] {format_bytes(self.total_size)} ({self.venv_count} venvs) | "
            f"[bold green]Saved:[/bold green] {format_bytes(self.saved_size)} | "
            f"[dim]Scan Time:[/dim] {self.scan_time:.1f}s"
        )

class VenvKillerApp(App):
    """Textual app for VenvKiller."""
    
    CSS = """
    VenvDetailsPanel {
        height: auto;
        margin: 1 0;
        padding: 1;
        border: solid green;
    }
    
    StatsPanel {
        margin: 1 0;
        padding: 1;
        text-align: center;
        background: $boost;
    }
    
    DataTable {
        height: 1fr;
    }
    
    .buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    Button {
        margin: 1 2;
    }
    """
    
    BINDINGS = [
        Binding("d", "delete", "Delete Selected"),
        Binding("o", "open", "Open Folder"),
        Binding("q", "quit", "Quit"),
        Binding("up", "cursor_up", "Up"),
        Binding("down", "cursor_down", "Down"),
        Binding("space", "toggle_marked", "Mark/Unmark"),
    ]
    
    def __init__(self, start_dir, recent_threshold, old_threshold):
        super().__init__()
        self.start_dir = Path(start_dir).expanduser().resolve()
        self.recent_threshold = recent_threshold
        self.old_threshold = old_threshold
        self.venvs = []
        self.total_size = 0
        self.saved_size = 0
        self.scan_time = 0
        self.marked_venvs = set()
        self.deleted_venvs = set()
        
    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header(show_clock=True)
        yield StatsPanel(self.total_size, len(self.venvs), self.saved_size, self.scan_time)
        
        # Main venv table
        self.table = DataTable()
        self.table.cursor_type = "row"
        yield self.table
        
        # Details panel
        self.details = VenvDetailsPanel()
        yield self.details
        
        # Action buttons
        with Horizontal(classes="buttons"):
            yield Button("Delete Selected", id="delete", variant="error")
            yield Button("Open Folder", id="open", variant="primary")
            yield Button("Quit", id="quit", variant="default")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Set up table columns
        self.table.add_column("Mark", width=4)
        self.table.add_column("Path")
        self.table.add_column("Size", width=10)
        self.table.add_column("Age", width=10)
        self.table.add_column("Python", width=7)
        self.table.add_column("Req", width=3)
        
        # Start scanning for venvs
        self.scan_venvs()
    
    def scan_venvs(self) -> None:
        """Scan for virtual environments and populate the table."""
        # Show scanning message
        self.query_one(StatsPanel).update_stats(0, 0, 0, 0)
        self.sub_title = "Scanning for virtual environments..."
        
        # Perform scan
        start_time = time.time()
        venv_paths = find_venvs(self.start_dir, parallel=True)
        
        # Analyze each venv
        for venv_path in venv_paths:
            info = get_venv_info(venv_path)
            self.venvs.append(info)
            self.total_size += info.get('size', 0)
        
        self.scan_time = time.time() - start_time
        
        # Sort by size (largest first)
        self.venvs.sort(key=lambda x: x.get('size', 0), reverse=True)
        
        # Update stats and title
        self.sub_title = f"VenvKiller v{__version__}"
        self.query_one(StatsPanel).update_stats(
            self.total_size, 
            len(self.venvs), 
            self.saved_size,
            self.scan_time
        )
        
        # Populate table
        self.populate_table()
        
        # Update details if we have venvs
        if self.venvs:
            self.query_one(VenvDetailsPanel).update_venv(self.venvs[0])
    
    def populate_table(self) -> None:
        """Populate the table with venvs."""
        # Clear existing rows
        self.table.clear()
        
        # Add venvs to table
        for i, venv in enumerate(self.venvs):
            # Skip deleted venvs
            if i in self.deleted_venvs:
                continue
                
            # Determine style based on age
            age_class = classify_venv_age(
                venv['age_days'], 
                self.recent_threshold, 
                self.old_threshold
            )
            
            # Set color based on age
            if age_class == 'recent':
                path_style = "green"
            elif age_class == 'old':
                path_style = "red"
            else:
                path_style = "yellow"
            
            # Mark status
            mark = "✓" if i in self.marked_venvs else ""
            
            # Create right-aligned text for size and age
            size_text = Text(venv['size_formatted'], justify="right")
            age_text = Text(venv['modified_ago'], justify="right")
            # Create centered text for Python version and requirements status
            py_version = Text(venv.get('py_version', 'Unknown'), justify="center")
            req_status = Text("✓" if venv.get('has_requirements', False) else "✗", justify="center")
            
            # Add row
            self.table.add_row(
                mark,
                Text(venv['path'], style=path_style),
                size_text,
                age_text,
                py_version,
                req_status,
                key=i  # Store the original index as key
            )
    
    def action_toggle_marked(self) -> None:
        """Toggle the marked status of the selected row."""
        if not self.table.row_count:
            return
            
        # Get current cursor row
        cursor_row = self.table.cursor_row
        if cursor_row is None:
            return
            
        # Get the original index (key) from the row
        row_data = self.table.get_row_at(cursor_row)
        if not row_data or len(row_data) < 7:
            return
            
        row_key = row_data[6]
        
        if row_key in self.marked_venvs:
            self.marked_venvs.remove(row_key)
        else:
            self.marked_venvs.add(row_key)
            
        # Update the mark column
        self.table.update_cell_at((cursor_row, 0), "✓" if row_key in self.marked_venvs else "")
    
    def on_data_table_cell_highlighted(self, event) -> None:
        """Called when the cursor position changes in the table."""
        if not self.venvs or not self.table.row_count:
            return
        
        try:
            # Determine which row is highlighted
            row = event.coordinate.row
            if row is None:
                return
                
            # Get the row data
            row_data = self.table.get_row_at(row)
            if row_data and len(row_data) >= 7:
                row_key = row_data[6]
                if 0 <= row_key < len(self.venvs):
                    self.query_one(VenvDetailsPanel).update_venv(self.venvs[row_key])
        except Exception as e:
            self.log.error(f"Error updating details: {e}")
    
    def on_data_table_row_highlighted(self, event) -> None:
        """Called when a row is highlighted in the table."""
        if not self.venvs:
            return
            
        try:
            row_key = event.row_key.value if hasattr(event, 'row_key') else None
            if row_key is not None and 0 <= row_key < len(self.venvs):
                self.query_one(VenvDetailsPanel).update_venv(self.venvs[row_key])
        except Exception as e:
            self.log.error(f"Error in row highlighted: {e}")
    
    def action_open(self) -> None:
        """Open the folder containing the selected venv."""
        if not self.table.row_count:
            return
            
        # Get current cursor row
        cursor_row = self.table.cursor_row
        if cursor_row is None:
            return
            
        # Get row data
        row_data = self.table.get_row_at(cursor_row)
        if not row_data or len(row_data) < 7:
            return
            
        row_key = row_data[6]
        if 0 <= row_key < len(self.venvs):
            venv_path = Path(self.venvs[row_key]['path'])
            open_containing_folder(venv_path)
    
    async def action_delete(self) -> None:
        """Delete marked venvs."""
        if not self.marked_venvs:
            return
            
        # Create a list of venv paths to delete
        paths_to_delete = []
        indices_to_delete = []
        
        for idx in self.marked_venvs:
            if idx not in self.deleted_venvs and idx < len(self.venvs):
                venv = self.venvs[idx]
                paths_to_delete.append(Path(venv['path']))
                indices_to_delete.append(idx)
        
        if not paths_to_delete:
            return
        
        # Ask for confirmation
        if not await self.confirm_dialog(
            f"Delete {len(paths_to_delete)} virtual environment(s)?", 
            "This cannot be undone."
        ):
            return
        
        # Show deletion progress dialog
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold red]Deleting..."),
            BarColumn(),
            TextColumn("[bold]{task.completed}/{task.total}"),
            console=console,
        ) as progress:
            task = progress.add_task("[red]Deleting...", total=len(paths_to_delete))
            
            def update_progress(done, total, current_path):
                progress.update(task, completed=done, description=f"[red]Deleting: {current_path}")
            
            venvs_deleted, bytes_freed, failures = delete_multiple_venvs(
                paths_to_delete, update_progress
            )
        
        # Update stats
        self.saved_size += bytes_freed
        
        # Mark as deleted
        for idx in indices_to_delete:
            self.deleted_venvs.add(idx)
        
        # Clear marked set
        self.marked_venvs.clear()
        
        # Update table
        self.populate_table()
        
        # Update stats panel
        self.query_one(StatsPanel).update_stats(
            self.total_size, 
            len(self.venvs) - len(self.deleted_venvs), 
            self.saved_size,
            self.scan_time
        )
        
        # Show results
        if failures:
            self.notify(f"Warning: {len(failures)} environments had errors during deletion.")
        
        self.notify(f"Successfully deleted {venvs_deleted} environments, freed {format_bytes(bytes_freed)}")
    
    def on_button_pressed(self, event) -> None:
        """Handle button press events."""
        button_id = event.button.id
        
        if button_id == "delete":
            self.action_delete()
        elif button_id == "open":
            self.action_open()
        elif button_id == "quit":
            self.action_quit()
    
    async def confirm_dialog(self, title, message):
        """Show a confirmation dialog."""
        from textual._default_css import DEFAULT_CSS
        from textual.app import App
        from textual.widgets import Button, Label, Static
        from textual.containers import Grid
        
        class ConfirmationDialog(App):
            CSS = DEFAULT_CSS + """
            Grid {
                grid-size: 2;
                grid-gutter: 1;
                margin: 1 2;
            }
            Label {
                width: 100%;
                content-align: center middle;
                text-style: bold;
            }
            #message {
                column-span: 2;
            }
            """
            result = False
            
            def compose(self) -> ComposeResult:
                yield Label(title, id="title")
                yield Static(message, id="message")
                with Grid():
                    yield Button("Cancel", variant="default", id="cancel")
                    yield Button("Confirm", variant="error", id="confirm")
            
            def on_button_pressed(self, event) -> None:
                if event.button.id == "confirm":
                    self.result = True
                self.exit()
        
        dialog = ConfirmationDialog()
        await dialog.run()
        return dialog.result
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
        
        # Final stats after exit
        console.clear()
        console.print("[green]VenvKiller session summary:[/green]")
        console.print(f"- Total environments found: {len(self.venvs)}")
        console.print(f"- Environments deleted: {len(self.deleted_venvs)}")
        console.print(f"- Total size found: {format_bytes(self.total_size)}")
        console.print(f"- Disk space saved: {format_bytes(self.saved_size)}")

@click.command()
@click.option(
    "--start-dir", "-d",
    default="~",
    help="Directory to start searching from (default: home directory)"
)
@click.option(
    "--recent", "-r",
    default=DEFAULT_RECENT_THRESHOLD,
    help=f"Days threshold for considering an environment recent (green) (default: {DEFAULT_RECENT_THRESHOLD})"
)
@click.option(
    "--old", "-o",
    default=DEFAULT_OLD_THRESHOLD,
    help=f"Days threshold for considering an environment old (red) (default: {DEFAULT_OLD_THRESHOLD})"
)
@click.version_option(version=__version__)
def main(start_dir, recent, old):
    """Find and delete Python virtual environments to free up disk space."""
    try:
        app = VenvKillerApp(start_dir, recent, old)
        app.run()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
