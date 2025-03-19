"""Module for cleaning up (deleting) Python virtual environments."""

import os
import shutil
from pathlib import Path
from typing import Callable, Optional, Tuple, List


def safe_delete_venv(
    venv_path: Path, progress_callback: Optional[Callable[[int, int], None]] = None
) -> Tuple[bool, str]:
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

                    if progress_callback:
                        progress_callback(bytes_removed, total_size)
                except (OSError, PermissionError) as e:
                    errors.append(f"Error deleting {file_path}: {str(e)}")

            # Then delete empty directories
            for dir_name in dirs:
                try:
                    dir_path = Path(root) / dir_name
                    dir_path.rmdir()
                except (OSError, PermissionError) as e:
                    errors.append(f"Error deleting {dir_path}: {str(e)}")

        # Finally, delete the top-level directory
        try:
            venv_path.rmdir()
        except (OSError, PermissionError) as e:
            errors.append(f"Error deleting {venv_path}: {str(e)}")
    except Exception as e:
        return False, f"Error during deletion: {str(e)}"

    # Check if the directory still exists
    if venv_path.exists():
        # Try one last attempt with shutil.rmtree
        try:
            shutil.rmtree(venv_path, ignore_errors=True)
        except Exception:
            pass

    if venv_path.exists():
        return False, f"Failed to delete {venv_path}. Errors: {', '.join(errors)}"

    return True, ""


def delete_multiple_venvs(
    venv_paths: List[Path],
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> Tuple[int, int, List[Tuple[Path, str]]]:
    """Delete multiple virtual environments with progress reporting.

    Args:
        venv_paths: List of paths to virtual environments to delete
        progress_callback: Optional callback for overall progress
            (venvs_processed, total_venvs, current_venv_path)

    Returns:
        Tuple of (success_count, total_bytes_freed, failed_deletions)
    """
    total_venvs = len(venv_paths)
    venvs_deleted = 0
    bytes_freed = 0
    failures = []

    for i, venv_path in enumerate(venv_paths):
        if progress_callback:
            progress_callback(i, total_venvs, str(venv_path))

        def venv_progress(bytes_done, total):
            if progress_callback:
                progress_callback(i, total_venvs, str(venv_path))

        # Get size before deletion
        try:
            size = 0
            for root, _, files in os.walk(venv_path):
                for file in files:
                    try:
                        file_path = Path(root) / file
                        size += file_path.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            size = 0

        # Attempt deletion
        success, error = safe_delete_venv(venv_path, venv_progress)

        if success:
            venvs_deleted += 1
            bytes_freed += size
        else:
            failures.append((venv_path, error))

    return venvs_deleted, bytes_freed, failures
