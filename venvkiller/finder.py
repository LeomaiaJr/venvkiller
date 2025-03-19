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
            if item.is_dir() and not item.is_symlink():
                if item.name.startswith('.') and item.name not in VENV_NAMES:
                    continue
                    
                yield from find_venvs_in_dir(
                    item, 
                    max_depth - 1, 
                    exclude_dirs
                )
    except (PermissionError, OSError):
        # Skip directories we can't access
        pass

def find_venvs(start_dir: Optional[str] = None, 
              max_depth: int = 5,
              exclude_dirs: Optional[List[str]] = None,
              parallel: bool = True) -> List[Path]:
    """Find all Python virtual environments starting from a directory.
    
    Args:
        start_dir: Directory to start searching from (defaults to home directory)
        max_depth: Maximum directory depth to search
        exclude_dirs: Directory names to exclude from search
        parallel: Whether to use parallel processing for search
        
    Returns:
        List of paths to virtual environments
    """
    if start_dir is None:
        start_dir = os.path.expanduser("~")
    
    start_path = Path(os.path.expanduser(start_dir)).resolve()
    
    if not start_path.exists() or not start_path.is_dir():
        return []
    
    exclude_set = set(exclude_dirs or [])
    exclude_set.update({'node_modules', 'site-packages', '__pycache__'})
    
    if parallel and max_depth > 1:
        # Get first level directories for parallel processing
        try:
            first_level = [d for d in start_path.iterdir() 
                       if d.is_dir() and not d.is_symlink() and d.name not in exclude_set]
        except (PermissionError, OSError):
            return []
        
        # First check if start path itself is a venv
        results = list(find_venvs_in_dir(start_path, 0, exclude_set))
        
        # Then process first level directories in parallel
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    list, 
                    find_venvs_in_dir(d, max_depth - 1, exclude_set)
                ) 
                for d in first_level
            ]
            
            for future in futures:
                try:
                    results.extend(future.result())
                except Exception:
                    pass
                    
        return results
    else:
        # Sequential search
        return list(find_venvs_in_dir(start_path, max_depth, exclude_set))

def has_requirement_files(parent_dir: Path) -> Tuple[bool, List[str]]:
    """Check if a directory has Python requirements files.
    
    Args:
        parent_dir: Directory to check for requirements files
        
    Returns:
        Tuple of (has_requirements, list_of_found_files)
    """
    requirement_files = [
        'requirements.txt',
        'requirements-dev.txt',
        'requirements_dev.txt',
        'requirements/dev.txt',
        'requirements/prod.txt',
        'Pipfile',
        'Pipfile.lock',
        'pyproject.toml',
        'poetry.lock'
    ]
    
    found_files = []
    
    for req_file in requirement_files:
        req_path = parent_dir / req_file
        if req_path.exists() and req_path.is_file():
            found_files.append(req_file)
    
    return bool(found_files), found_files
