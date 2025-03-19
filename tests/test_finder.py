"""Tests for the finder module."""

import tempfile
import shutil
from pathlib import Path
import unittest

from venvkiller.finder import is_virtual_env, find_venvs, has_requirement_files


class TestFinder(unittest.TestCase):
    """Test cases for the finder module."""

    def setUp(self):
        """Set up a temporary directory for tests."""
        self.temp_dir = Path(tempfile.mkdtemp()).resolve()

    def tearDown(self):
        """Clean up temporary directory after tests."""
        shutil.rmtree(self.temp_dir)

    def create_fake_venv(self, path: Path):
        """Create a fake virtual environment for testing."""
        path.mkdir(parents=True, exist_ok=True)
        # Create pyvenv.cfg file (standard venv identifier)
        with open(path / "pyvenv.cfg", "w") as f:
            f.write("home = /usr/bin\nversion = 3.9.0\n")

    def test_is_virtual_env(self):
        """Test that a directory with pyvenv.cfg is identified as a venv."""
        # Create a fake venv
        venv_path = self.temp_dir / "testvenv"
        self.create_fake_venv(venv_path)

        # Test if it's correctly identified
        self.assertTrue(is_virtual_env(venv_path))

        # Test that a regular directory is not identified as a venv
        regular_dir = self.temp_dir / "regular_dir"
        regular_dir.mkdir()
        self.assertFalse(is_virtual_env(regular_dir))

    def test_find_venvs(self):
        """Test finding virtual environments in a directory."""
        # Create a few fake venvs
        venv1 = self.temp_dir / "project1" / "venv"
        venv2 = self.temp_dir / "project2" / ".venv"
        venv3 = self.temp_dir / "project3" / "env"

        self.create_fake_venv(venv1)
        self.create_fake_venv(venv2)
        self.create_fake_venv(venv3)

        # Create a regular directory to ensure it's not included
        regular_dir = self.temp_dir / "regular_dir"
        regular_dir.mkdir()

        # Test finding venvs
        found_venvs = find_venvs(start_dir=str(self.temp_dir), max_depth=3)

        # Get resolved paths for comparison
        venv1_resolved = str(venv1.resolve())
        venv2_resolved = str(venv2.resolve())
        venv3_resolved = str(venv3.resolve())

        # Convert paths to strings for easier comparison
        found_venv_strs = [str(p.resolve()) for p in found_venvs]

        # Check if all fake venvs were found
        self.assertIn(venv1_resolved, found_venv_strs)
        self.assertIn(venv2_resolved, found_venv_strs)
        self.assertIn(venv3_resolved, found_venv_strs)
        self.assertEqual(len(found_venvs), 3)

    def test_has_requirement_files(self):
        """Test detecting requirements files in a directory."""
        project_dir = self.temp_dir / "project_with_reqs"
        project_dir.mkdir()

        # Create a requirements.txt file
        with open(project_dir / "requirements.txt", "w") as f:
            f.write("pytest==7.0.0\n")

        # Test detection
        has_reqs, found_files = has_requirement_files(project_dir)
        self.assertTrue(has_reqs)
        self.assertIn("requirements.txt", found_files)

        # Test with a directory that has no requirements files
        empty_dir = self.temp_dir / "empty_project"
        empty_dir.mkdir()
        has_reqs, found_files = has_requirement_files(empty_dir)
        self.assertFalse(has_reqs)
        self.assertEqual(len(found_files), 0)


if __name__ == "__main__":
    unittest.main()
