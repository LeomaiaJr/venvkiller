"""Tests for the cleaner module."""

import tempfile
import shutil
from pathlib import Path
import unittest

from venvkiller.cleaner import safe_delete_venv, delete_multiple_venvs


class TestCleaner(unittest.TestCase):
    """Test cases for the cleaner module."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = Path(tempfile.mkdtemp()).resolve()

    def tearDown(self):
        """Clean up temporary directory after tests."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_fake_venv(self, path: Path, file_count=5, file_size=1000):
        """Create a fake virtual environment for testing."""
        path.mkdir(parents=True, exist_ok=True)

        # Create pyvenv.cfg file (standard venv identifier)
        with open(path / "pyvenv.cfg", "w") as f:
            f.write("home = /usr/bin\nversion = 3.9.0\n")

        # Create bin directory
        bin_dir = path / "bin"
        bin_dir.mkdir(exist_ok=True)

        # Create activate script
        with open(bin_dir / "activate", "w") as f:
            f.write("# Fake activate script")

        # Create some additional files
        for i in range(file_count):
            with open(path / f"file{i}.txt", "w") as f:
                f.write("X" * file_size)

    def test_safe_delete_venv(self):
        """Test safely deleting a virtual environment."""
        # Create a fake venv
        venv_path = self.temp_dir / "testvenv"
        self.create_fake_venv(venv_path)

        # Verify it exists
        self.assertTrue(venv_path.exists())

        # Delete it
        success, error = safe_delete_venv(venv_path)

        # Verify deletion was successful
        self.assertTrue(success)
        self.assertEqual(error, "")
        self.assertFalse(venv_path.exists())

    def test_safe_delete_nonexistent_venv(self):
        """Test trying to delete a non-existent directory."""
        nonexistent_path = self.temp_dir / "nonexistent"

        # Try to delete non-existent path
        success, error = safe_delete_venv(nonexistent_path)

        # Verify operation failed with appropriate error
        self.assertFalse(success)
        self.assertIn("Directory does not exist", error)

    def test_delete_multiple_venvs(self):
        """Test deleting multiple virtual environments."""
        # Create multiple fake venvs
        venv1 = self.temp_dir / "venv1"
        venv2 = self.temp_dir / "venv2"
        venv3 = self.temp_dir / "venv3"

        self.create_fake_venv(venv1, file_count=3, file_size=1000)
        self.create_fake_venv(venv2, file_count=5, file_size=2000)
        self.create_fake_venv(venv3, file_count=2, file_size=3000)

        # Verify they exist
        self.assertTrue(venv1.exists())
        self.assertTrue(venv2.exists())
        self.assertTrue(venv3.exists())

        # Delete them
        venv_paths = [venv1, venv2, venv3]
        result = delete_multiple_venvs(venv_paths)
        success_count, bytes_freed, failures = result

        # Verify deletion was successful
        self.assertEqual(success_count, 3)
        self.assertEqual(len(failures), 0)
        self.assertFalse(venv1.exists())
        self.assertFalse(venv2.exists())
        self.assertFalse(venv3.exists())

        # Bytes freed should be greater than zero
        # (not checking exact value since it depends on file system)
        self.assertGreater(bytes_freed, 0)

    def test_delete_with_progress_callback(self):
        """Test deletion with a progress callback."""
        # Create a fake venv
        venv_path = self.temp_dir / "test_progress_venv"
        self.create_fake_venv(venv_path)

        # Setup a callback to track progress
        progress_called = False

        def progress_callback(current, total):
            nonlocal progress_called
            progress_called = True
            self.assertGreaterEqual(current, 0)
            self.assertGreater(total, 0)
            self.assertLessEqual(current, total)

        # Delete with progress callback
        success, error = safe_delete_venv(venv_path, progress_callback)

        # Verify callback was called and deletion was successful
        self.assertTrue(progress_called)
        self.assertTrue(success)
        self.assertEqual(error, "")
        self.assertFalse(venv_path.exists())


if __name__ == "__main__":
    unittest.main()
