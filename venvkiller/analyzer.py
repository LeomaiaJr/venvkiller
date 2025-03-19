"""Module for analyzing Python virtual environment details."""

import os
import time
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def get_size(path: Path) -> int:
    """Get the size of a directory in bytes."""
    total_size = 0

    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    try:
                        total_size += entry.stat().st_size
                    except (OSError, FileNotFoundError):
                        pass
                elif entry.is_dir():
                    total_size += get_size(Path(entry.path))
    except (PermissionError, OSError, FileNotFoundError):
        return 0

    return total_size


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"

    suffixes = ["B", "KB", "MB", "GB", "TB"]
    factor = 1024

    size_value = size_bytes
    suffix_index = 0

    while size_value >= factor and suffix_index < len(suffixes) - 1:
        size_value /= factor
        suffix_index += 1

    return f"{size_value:.1f} {suffixes[suffix_index]}"


def format_time_ago(timestamp: float) -> str:
    """Format a timestamp as a human-readable 'time ago' string."""
    now = time.time()
    diff = now - timestamp

    if diff < 60:
        return "just now"
    elif diff < 3600:
        minutes = int(diff / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < 604800:
        days = int(diff / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif diff < 2592000:
        weeks = int(diff / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif diff < 31536000:
        months = int(diff / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(diff / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"


def get_venv_info(venv_path: Path) -> Dict[str, Any]:
    """Get detailed information about a virtual environment.

    Args:
        venv_path: Path to the virtual environment

    Returns:
        Dictionary with information about the virtual environment
    """
    try:
        venv_path = venv_path.resolve()

        # Get basic stats
        modified_time = os.path.getmtime(venv_path)
        size_bytes = get_size(venv_path)

        # Calculate age
        modified_date = datetime.fromtimestamp(modified_time)
        now = datetime.now()
        age_days = (now - modified_date).days

        # Get parent directory (likely project directory)
        parent_dir = venv_path.parent

        # Get Python version info
        py_version = detect_python_version(venv_path)

        # Count packages
        packages_count = count_installed_packages(venv_path)

        # Check for requirements files
        from venvkiller.finder import has_requirement_files

        has_req, req_files = has_requirement_files(parent_dir)

        # Format for display
        info = {
            "path": str(venv_path),
            "parent_dir": str(parent_dir),
            "size_bytes": size_bytes,
            "size_formatted": format_size(size_bytes),
            "modified_time": modified_time,
            "modified_date": modified_date.strftime("%Y-%m-%d %H:%M"),
            "modified_ago": format_time_ago(modified_time),
            "age_days": age_days,
            "py_version": py_version,
            "packages_count": packages_count,
            "has_requirements": has_req,
            "requirement_files": req_files,
        }

        return info
    except Exception as e:
        return {
            "path": str(venv_path),
            "error": str(e),
            "size_bytes": 0,
            "size_formatted": "0 B",
            "modified_time": 0,
            "modified_date": "",
            "modified_ago": "unknown",
            "age_days": 0,
        }


def detect_python_version(venv_path: Path) -> str:
    """Detect the Python version used by a virtual environment.

    Args:
        venv_path: Path to the virtual environment

    Returns:
        Python version string or "Unknown"
    """
    # Try to find Python binary
    if platform.system() == "Windows":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"

    if not python_path.exists():
        # Try alternative locations
        if (venv_path / "python").exists():
            python_path = venv_path / "python"
        elif (venv_path / "python.exe").exists():
            python_path = venv_path / "python.exe"
        else:
            return "Unknown"

    try:
        # Run python --version
        result = subprocess.run(
            [str(python_path), "--version"], capture_output=True, text=True, timeout=1
        )
        if result.returncode == 0:
            return result.stdout.strip() or result.stderr.strip()
    except (subprocess.SubprocessError, OSError):
        pass

    # Fallback: try to check pyvenv.cfg
    cfg_path = venv_path / "pyvenv.cfg"
    if cfg_path.exists():
        try:
            with open(cfg_path, "r") as f:
                for line in f:
                    if line.startswith("version"):
                        return line.split("=")[1].strip()
        except (OSError, IndexError):
            pass

    return "Unknown"


def count_installed_packages(venv_path: Path) -> int:
    """Count the number of installed packages in a virtual environment.

    Args:
        venv_path: Path to the virtual environment

    Returns:
        Number of installed packages
    """
    if platform.system() == "Windows":
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        pip_path = venv_path / "bin" / "pip"

    if not pip_path.exists():
        return 0

    try:
        result = subprocess.run(
            [str(pip_path), "list", "--format=freeze"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0:
            return len([line for line in result.stdout.splitlines() if line.strip()])
    except (subprocess.SubprocessError, OSError):
        pass

    return 0


def classify_venv_age(
    age_days: int, recent_threshold: int = 30, old_threshold: int = 180
) -> str:
    """Classify the age of a virtual environment.

    Args:
        age_days: Age in days
        recent_threshold: Days threshold for recent environments
        old_threshold: Days threshold for old environments

    Returns:
        Classification string: "recent", "old", or "very_old"
    """
    if age_days < recent_threshold:
        return "recent"
    elif age_days < old_threshold:
        return "old"
    else:
        return "very_old"


def open_containing_folder(path: Path) -> None:
    """Open the containing folder of a path in the file explorer.

    Args:
        path: Path to open
    """
    if not path.exists():
        return

    path = path.parent if path.is_file() else path

    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)
    except (OSError, subprocess.SubprocessError):
        pass
