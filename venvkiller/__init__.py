"""VenvKiller - Tool to find and delete Python virtual environments to free up disk space."""

__version__ = "1.0.0"
__author__ = "VenvKiller Contributors"

# Default age thresholds for color coding (in days)
DEFAULT_RECENT_THRESHOLD = 30  # Less than 30 days is considered recent (green)
DEFAULT_OLD_THRESHOLD = 180    # More than 180 days is considered very old (red)
