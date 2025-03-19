# VenvKiller

A Python tool to find and delete Python virtual environments to free up disk space.

## Features

- Find all Python virtual environments on your system
- Display size, last modified date, and full path
- Advanced interactive TUI with Textual library
- Cursor-based navigation for easy selection
- Modern data table with sorting capabilities
- Progress indicators during scanning operations
- Loading indicator during environment scanning
- Color-coding by age (green=recent, yellow=old, red=very old)
- Verify requirements.txt/poetry/pipenv files exist before deletion
- Keyboard shortcut to open containing folder
- Detailed information panel for selected environment
- Total disk space usage and savings statistics

## Installation

```bash
pip install venvkiller
```

## Usage

```bash
# Run the interactive TUI
venvkiller

# Run with a specific start directory
venvkiller --start-dir ~/projects

# Run with custom age thresholds (in days)
venvkiller --recent 14 --old 90
```

## Keyboard Shortcuts

- Arrow keys: Navigate the list
- Space: Mark/unmark for deletion
- 'd': Delete marked environments
- 'o': Open containing folder
- 'q': Quit

## Screenshots

(Screenshots coming soon)

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/yourusername/venvkiller.git
cd venvkiller

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Run the development version
./run_dev.sh  # On Windows: run_dev.bat
```

## License

MIT
