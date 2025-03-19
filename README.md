# venvkiller

[![PyPI version](https://img.shields.io/pypi/v/venvkiller.svg)](https://pypi.org/project/venvkiller/)
[![Python versions](https://img.shields.io/pypi/pyversions/venvkiller.svg)](https://pypi.org/project/venvkiller/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/LeomaiaJr/venvkiller.svg)](https://github.com/LeomaiaJr/venvkiller/stargazers)

A Python tool to find and delete Python virtual environments to free up disk space.

> **Inspiration**: This project was inspired by [npkill](https://www.npmjs.com/package/npkill), which provides similar functionality for cleaning up node_modules folders in JavaScript/Node.js projects.

## Why venvkiller?

Python developers often create many virtual environments during development, which can end up occupying gigabytes of disk space. venvkiller helps you:

- Quickly identify all virtual environments on your system
- See which ones are old or unused
- Safely delete them to reclaim disk space
- Avoid accidentally deleting environments that belong to active projects

## Features

- **Comprehensive Scanning**: Find all Python virtual environments on your system
- **Detailed Information**: Display size, last modified date, and full path
- **Modern TUI Interface**: Built with the Textual library for an elegant terminal UI
- **Easy Navigation**: Cursor-based navigation for effortless selection
- **Sorting Capabilities**: Sort environments by size, age, or other criteria
- **Visual Progress**: Real-time progress indicators during scanning and deletion
- **Smart Age Detection**: Color-coding by age (green=recent, yellow=old, red=very old)
- **Safe Deletion**: Verify requirements.txt/poetry/pipenv files exist before deletion
- **Folder Access**: Keyboard shortcut to open containing folder in file explorer
- **Detailed Info**: Comprehensive information panel for selected environment
- **Space Management**: Total disk space usage and potential savings statistics

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

### Command Line Options

| Option              | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| `--start-dir`, `-d` | Directory to start searching from (default: home directory)  |
| `--recent`, `-r`    | Days threshold for considering an environment recent (green) |
| `--old`, `-o`       | Days threshold for considering an environment old (red)      |
| `--version`         | Show version and exit                                        |
| `--help`            | Show help message and exit                                   |

## Keyboard Shortcuts

| Key        | Action                     |
| ---------- | -------------------------- |
| Arrow keys | Navigate the list          |
| Space      | Mark/unmark for deletion   |
| 'd'        | Delete marked environments |
| 'o'        | Open containing folder     |
| 'q'        | Quit                       |

## Screenshots

![venvkiller Main Screen](https://raw.githubusercontent.com/LeomaiaJr/venvkiller/main/screenshots/main.png)

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/LeomaiaJr/venvkiller.git
cd venvkiller

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run the development version
python -m venvkiller.cli

# Run tests
pytest tests/
# Or for more verbose output with coverage
pytest tests/ -v --cov=venvkiller
```

## How It Works

venvkiller works by recursively scanning directories for Python virtual environments, which it identifies by looking for common markers like `pyvenv.cfg`, `bin/activate`, or `Scripts/activate.bat`. It analyzes each environment to determine:

1. Size on disk
2. Last modified date
3. Python version
4. Installed packages
5. Whether the parent directory contains requirements files

This information helps you make informed decisions about which environments to keep and which to delete.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

- [Leo Maia](https://github.com/LeomaiaJr) - me@leomaiajr.dev
