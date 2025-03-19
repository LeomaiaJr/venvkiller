# Installing VenvKiller

VenvKiller is a Python utility to find and delete Python virtual environments to free up disk space.

## Requirements

- Python 3.7 or higher
- pip or pipx for installation

## Dependencies

VenvKiller relies on the following major dependencies:
- click: Command-line interface parsing
- rich: Terminal formatting and progress bars
- textual: Advanced TUI interface with widgets
- pathlib: Path manipulation

All dependencies will be automatically installed when you install VenvKiller.

## Installation Methods

### From PyPI (Recommended)

```bash
# Install with pip
pip install venvkiller

# Or use pipx for isolated installation (recommended)
pipx install venvkiller
```

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/contributor/venvkiller.git
   cd venvkiller
   ```

2. Install the package:
   ```bash
   pip install .
   ```

3. For development purposes, install in editable mode:
   ```bash
   pip install -e .
   ```

## Verifying Installation

After installation, you should be able to run:

```bash
venvkiller --version
```

## Usage

Run the interactive tool:

```bash
# Start from your home directory (default)
venvkiller

# Start from a specific directory
venvkiller --start-dir ~/projects

# Customize age thresholds
venvkiller --recent 14 --old 90
```

For more options, run:

```bash
venvkiller --help
```

## User Interface

VenvKiller uses the Textual library to provide a modern, cursor-based terminal user interface:

- Table of virtual environments with size, age, and other details
- Detail panel showing comprehensive information about the selected environment
- Statistics panel showing total space, saved space, and scan metrics
- Mark/unmark environments for batch deletion
- Confirmation dialogs to prevent accidental deletions

## Troubleshooting

### Common Issues

- **Permission errors**: If you encounter permission issues when scanning system directories, try running with elevated privileges or exclude those directories.
- **Environment not found**: If VenvKiller isn't finding specific environments, check if they follow standard directory structures (.venv, venv, env, etc.)
- **Display issues**: If you experience display rendering problems, ensure your terminal supports Unicode characters and True Color.

### Terminal Compatibility

VenvKiller's TUI should work in most modern terminals including:
- Terminal.app (macOS)
- iTerm2 (macOS)
- Windows Terminal (Windows)
- GNOME Terminal (Linux)
- Konsole (Linux) 