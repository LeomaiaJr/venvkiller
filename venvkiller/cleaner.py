"""Module for cleaning up (deleting) Python virtual environments."""

import os
import shutil
import time
from pathlib import Path
from typing import Callable, Optional, Tuple, List

def safe_delete_venv(venv_path: Path, 
                    progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[bool, str]:
    """Safely delete a virtual environment directory.
    
    Args:
        venv_path: Path to the virtual environment
        progress_callback: Optional callback for deletion progress (bytes_removed, total_bytes)
        
    Returns:
        Tuple of (success, error_message)
    """
    if not venv_path.exists() or not venv_path.is_dir():
        return False, f"Directory does not exist: {venv_path}"
    
    # Get initial size for progress reporting
    total_size = 0
    try:
        for root, dirs, files in os.walk(venv_path):
            for file in files:
                try:
                    file_path = Path(root) / file
                    total_size += file_path.stat().st_size
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass
    
    # Start deletion process
    bytes_removed = 0
    errors = []
    
    try:
        for root, dirs, files in os.walk(venv_path, topdown=False):
            # Delete files first
            for file in files:
                try:
                    file_path = Path(root) / file
                    size = file_path.stat().st_size
                    file_path.unlink()
                    bytes_removed += size
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(bytes_removed, total_size)
                    
                except (OSError, PermissionError) as e:
                    errors.append(f"Error deleting file {file_path}: {str(e)}")
            
            # Delete empty directories
            for dir in dirs:
                try:
                    dir_path = Path(root) / dir
                    dir_path.rmdir()  # This will only remove empty directories
                except (OSError, PermissionError) as e:
                    errors.append(f"Error deleting directory {dir_path}: {str(e)}")
        
        # Finally remove the root directory
        try:
            venv_path.rmdir()
        except (OSError, PermissionError) as e:
            # If the directory still has content, try using shutil
            try:
                shutil.rmtree(venv_path)
            except (OSError, PermissionError) as e2:
                errors.append(f"Error deleting root directory: {str(e2)}")
    
    except Exception as e:
        return False, f"Unexpected error during deletion: {str(e)}"
    
    if errors:
        # If we encountered errors but deleted some content, report partial success
        if bytes_removed > 0:
            return True, f"Partially deleted ({len(errors)} errors)"
        return False, "\n".join(errors[:3]) + (f" (and {len(errors) - 3} more errors)" if len(errors) > 3 else "")
    
    return True, ""

def delete_multiple_venvs(venv_paths: List[Path], 
                        progress_callback: Optional[Callable[[int, int, str], None]] = None) -> Tuple[int, int, List[Tuple[Path, str]]]:
    """Delete multiple virtual environments with progress reporting.
    
    Args:
        venv_paths: List of paths to delete
        progress_callback: Optional callback for overall progress (venvs_deleted, total_venvs, current_path)
        
    Returns:
        Tuple of (venvs_deleted, bytes_freed, list of failures with error messages)
    """
    total_venvs = len(venv_paths)
    venvs_deleted = 0
    bytes_freed = 0
    failures = []
    
    for i, venv_path in enumerate(venv_paths):
        if progress_callback:
            progress_callback(venvs_deleted, total_venvs, str(venv_path))
        
        # Get size before deletion
        venv_size = 0
        try:
            for root, dirs, files in os.walk(venv_path):
                for file in files:
                    try:
                        file_path = Path(root) / file
                        venv_size += file_path.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        
        # Individual venv deletion progress callback
        def venv_progress(bytes_done, total):
            if progress_callback:
                progress_callback(venvs_deleted, total_venvs, f"{str(venv_path)} ({bytes_done/total*100:.0f}%)")
        
        # Attempt deletion
        success, error = safe_delete_venv(venv_path, venv_progress)
        
        if success:
            venvs_deleted += 1
            bytes_freed += venv_size
        else:
            failures.append((venv_path, error))
    
    return venvs_deleted, bytes_freed, failures
