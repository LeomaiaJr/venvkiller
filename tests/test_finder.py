"""Tests for the finder module."""

import os
import tempfile
import shutil
from pathlib import Path

import pytest

from venvkiller.finder import is_virtual_env, find_venvs, has_requirement_files

class TestFinder:
    """Tests for venv finding functions."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_is_virtual_env(self):
        """Test detection of virtual environments."""
        # Create a fake venv structure
        venv_dir = Path(self.temp_dir) / "test_venv"
        venv_dir.mkdir()
        
        # At first it should not be detected as a venv
        assert not is_virtual_env(venv_dir)
        
        # Add a pyvenv.cfg file
        with open(venv_dir / "pyvenv.cfg", "w") as f:
            f.write("home = /usr/bin\nversion = 3.9.0\n")
        
        # Now it should be detected
        assert is_virtual_env(venv_dir)
    
    def test_has_requirement_files(self):
        """Test detection of requirement files."""
        # Create a project structure
        project_dir = Path(self.temp_dir) / "test_project"
        project_dir.mkdir()
        
        # No requirement files initially
        has_reqs, files = has_requirement_files(project_dir)
        assert not has_reqs
        assert len(files) == 0
        
        # Add a requirements.txt file
        with open(project_dir / "requirements.txt", "w") as f:
            f.write("click==8.0.0\nrich==10.0.0\n")
        
        # Now it should find the requirements file
        has_reqs, files = has_requirement_files(project_dir)
        assert has_reqs
        assert len(files) == 1
        assert "requirements.txt" in files[0]
    
    def test_find_venvs(self):
        """Test finding virtual environments."""
        # Create some directories with venvs
        base_dir = Path(self.temp_dir)
        
        # Create fake venv 1
        venv1 = base_dir / "project1" / "venv"
        venv1.mkdir(parents=True)
        with open(venv1 / "pyvenv.cfg", "w") as f:
            f.write("home = /usr/bin\nversion = 3.8.0\n")
        
        # Create fake venv 2
        venv2 = base_dir / "project2" / ".venv"
        venv2.mkdir(parents=True)
        bin_dir = venv2 / "bin"
        bin_dir.mkdir()
        with open(bin_dir / "activate", "w") as f:
            f.write("# Fake activate script\n")
        
        # Non-venv directory
        non_venv = base_dir / "not_a_venv"
        non_venv.mkdir()
        
        # Find venvs
        found_venvs = find_venvs(base_dir, parallel=False)
        
        # Should find 2 venvs
        assert len(found_venvs) == 2
        
        # Convert to strings for easier comparison
        found_paths = [str(p) for p in found_venvs]
        
        # Check if our venvs were found
        assert any(str(venv1) in p for p in found_paths)
        assert any(str(venv2) in p for p in found_paths) 