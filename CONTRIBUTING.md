# Contributing to venvkiller

Thank you for your interest in contributing to venvkiller! This document provides guidelines and instructions for contributing to this project.

## Setting Up Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/venvkiller.git
   cd venvkiller
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install in development mode with development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

We use pytest for testing. To run the tests:

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ -v --cov=venvkiller

# Run specific test file
pytest tests/test_finder.py
```

Please ensure that all tests pass before submitting a pull request. If you're adding new functionality, please include tests for it.

## Code Style

We follow the Black code style. Before submitting a pull request, please format your code:

```bash
# Format code with Black
black venvkiller tests

# Check code with flake8
flake8 venvkiller tests
```

## Pull Request Process

1. Update the documentation if needed
2. Update or add tests as appropriate
3. Format your code according to our style guide
4. Make sure all tests pass
5. Update the README.md with details of changes if applicable
6. Create a pull request with a clear description of the changes

## Reporting Bugs

When reporting bugs, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- System information (OS, Python version, etc.)

## Feature Requests

Feature requests are welcome! Please provide:

- A clear and detailed description of the feature
- Why this feature would be useful to venvkiller users
- Any potential implementation ideas you have

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We appreciate your time and effort in helping make venvkiller better! 