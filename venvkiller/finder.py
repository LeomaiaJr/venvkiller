"""Module for finding Python virtual environments."""

import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Iterator, Optional, Set, Tuple

# Common venv directory names and identifiers
VENV_NAMES = {'venv', 'env', '.venv', '.env', 'virtualenv', '.virtualenv', 'pyenv'}
VENV_IDENTIFIERS = {
    'pyvenv.cfg',  # Standard venv
    'bin/activate',  # Unix-like
    'Scripts/activate',  # Windows
    'bin/python',  # Unix-like
    'Scripts/python.exe',  # Windows
}

def is_virtual_env(path: Path) -> bool:
    """Check if a directory is a Python virtual environment."""
    if not path.is_dir():
        return False

    # Check for venv identifiers
    for identifier in VENV_IDENTIFIERS:
        if (path / identifier).exists():
            return True
    
    return False

def find_venvs_in_dir(directory: Path, max_depth: int = 5, 
                     exclude_dirs: Optional[Set[str]] = None) -> Iterator[Path]:
    """Find all virtual environments in a directory with depth limit."""
    if exclude_dirs is None:
        exclude_dirs = set()
    
    # Skip if excluded
    if directory.name in exclude_dirs:
        return
    
    # Check if this directory is a venv
    if is_virtual_env(directory):
        yield directory
        return  # Don't recurse into venvs
    
    # Depth limit reached
    if max_depth <= 0:
        return
    
    try:
        # Iterate through subdirectories
        for item in directory.iterdir():
            # Include hidden directories that start with "." (like .venv)
            if item.is_dir() and (
                # Include .venv, .env and other hidden folders that might be venvs
                (item.name.startswith('.') and item.name.lower() in {'.venv', '.env', '.virtualenv'}) or 
                # Also include regular non-hidden directories
                (not item.name.startswith('.'))
            ):
                yield from find_venvs_in_dir(item, max_depth - 1, exclude_dirs)
    except (PermissionError, OSError):
        # Skip directories we can't access
        pass

def find_venvs(start_dir: Optional[str] = None, 
              max_depth: int = 5,
              exclude_dirs: Optional[List[str]] = None,
              parallel: bool = True) -> List[Path]:
    """Find all virtual environments from a starting directory.
    
    Args:
        start_dir: Directory to start search from (default: current directory)
        max_depth: Maximum recursion depth
        exclude_dirs: List of directory names to exclude
        parallel: Use parallel processing for faster searching
        
    Returns:
        List of paths to found virtual environments
    """
    start_path = Path(start_dir or os.getcwd()).expanduser().resolve()
    exclude_set = set(exclude_dirs or [])
    
    # Add standard system directories to exclude
    if sys.platform == 'win32':
        exclude_set.update(['Windows', 'Program Files', 'Program Files (x86)'])
    else:
        exclude_set.update(['proc', 'sys', 'dev', 'run'])
    
    if not parallel:
        # Single-threaded search
        return list(find_venvs_in_dir(start_path, max_depth, exclude_set))
    
    # Parallel search starting from the top-level directories
    venvs = []
    try:
        top_dirs = [d for d in start_path.iterdir() if d.is_dir() and d.name not in exclude_set]
        
        with ThreadPoolExecutor() as executor:
            for result in executor.map(
                lambda d: list(find_venvs_in_dir(d, max_depth - 1, exclude_set)), 
                top_dirs
            ):
                venvs.extend(result)
    except (PermissionError, OSError):
        # Handle errors accessing the start directory
        pass
    
    return venvs

def has_requirement_files(parent_dir: Path) -> Tuple[bool, List[str]]:
    """Check if the project directory has requirement files."""
    req_files = []
    
    # Common requirement files
    req_patterns = [
        'requirements.txt',
        'pyproject.toml',
        'Pipfile',
        'setup.py',
        'poetry.lock',
        'Pipfile.lock',
    ]
    
    # Check parent directories up to 3 levels
    dir_to_check = parent_dir
    for _ in range(3):  # Check this dir and up to 2 levels up
        for pattern in req_patterns:
            if (dir_to_check / pattern).exists():
                req_files.append(str(dir_to_check / pattern))
        
        # Move up one directory
        parent = dir_to_check.parent
        if parent == dir_to_check:  # Reached root
            break
        dir_to_check = parent
    
    return bool(req_files), req_files
