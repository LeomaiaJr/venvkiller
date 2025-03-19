"""Tests for the analyzer module."""

import time
import tempfile
import shutil
from pathlib import Path
import unittest

from venvkiller.analyzer import (
    get_size,
    format_size,
    format_time_ago,
    classify_venv_age,
)


class TestAnalyzer(unittest.TestCase):
    """Test cases for the analyzer module."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = Path(tempfile.mkdtemp()).resolve()

    def tearDown(self):
        """Clean up temporary directory after tests."""
        shutil.rmtree(self.temp_dir)

    def test_get_size(self):
        """Test calculating directory size."""
        # Create a test directory with some files
        test_dir = self.temp_dir / "test_size_dir"
        test_dir.mkdir()

        # Create a few files with known sizes
        file1 = test_dir / "file1.txt"
        file2 = test_dir / "file2.txt"

        with open(file1, "w") as f:
            f.write("A" * 1000)  # 1000 bytes

        with open(file2, "w") as f:
            f.write("B" * 2000)  # 2000 bytes

        # Create a subdirectory with a file
        subdir = test_dir / "subdir"
        subdir.mkdir()
        subfile = subdir / "subfile.txt"

        with open(subfile, "w") as f:
            f.write("C" * 3000)  # 3000 bytes

        # Test size calculation (should be 6000 bytes total)
        size = get_size(test_dir)
        self.assertEqual(size, 6000)

    def test_format_size(self):
        """Test formatting bytes to human-readable format."""
        self.assertEqual(format_size(0), "0 B")
        self.assertEqual(format_size(500), "500.0 B")
        self.assertEqual(format_size(1024), "1.0 KB")
        self.assertEqual(format_size(1536), "1.5 KB")
        self.assertEqual(format_size(1048576), "1.0 MB")
        self.assertEqual(format_size(1073741824), "1.0 GB")

    def test_format_time_ago(self):
        """Test formatting time ago strings."""
        now = time.time()

        # Test various time differences
        self.assertEqual(format_time_ago(now), "just now")
        self.assertEqual(format_time_ago(now - 30), "just now")
        self.assertEqual(format_time_ago(now - 60), "1 minute ago")
        self.assertEqual(format_time_ago(now - 120), "2 minutes ago")
        self.assertEqual(format_time_ago(now - 3600), "1 hour ago")
        self.assertEqual(format_time_ago(now - 7200), "2 hours ago")
        self.assertEqual(format_time_ago(now - 86400), "1 day ago")
        self.assertEqual(format_time_ago(now - 172800), "2 days ago")
        self.assertEqual(format_time_ago(now - 604800), "1 week ago")
        self.assertEqual(format_time_ago(now - 1209600), "2 weeks ago")
        self.assertEqual(format_time_ago(now - 2592000), "1 month ago")
        self.assertEqual(format_time_ago(now - 5184000), "2 months ago")
        self.assertEqual(format_time_ago(now - 31536000), "1 year ago")
        self.assertEqual(format_time_ago(now - 63072000), "2 years ago")

    def test_classify_venv_age(self):
        """Test classification of virtual environment ages."""
        # Test with default thresholds (recent: 30 days, old: 180 days)
        self.assertEqual(classify_venv_age(10), "recent")
        self.assertEqual(classify_venv_age(29), "recent")
        self.assertEqual(classify_venv_age(30), "old")
        self.assertEqual(classify_venv_age(100), "old")
        self.assertEqual(classify_venv_age(179), "old")
        self.assertEqual(classify_venv_age(180), "very_old")
        self.assertEqual(classify_venv_age(365), "very_old")

        # Test with custom thresholds
        threshold_args = dict(recent_threshold=15, old_threshold=60)
        self.assertEqual(classify_venv_age(10, **threshold_args), "recent")
        self.assertEqual(classify_venv_age(20, **threshold_args), "old")
        self.assertEqual(classify_venv_age(70, **threshold_args), "very_old")


if __name__ == "__main__":
    unittest.main()
