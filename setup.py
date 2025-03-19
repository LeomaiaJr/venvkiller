from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
with open(os.path.join("venvkiller", "__init__.py"), "r") as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    version = version_match.group(1) if version_match else "0.0.0"

# Read README.md for long description
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="venvkiller",
    version=version,
    description="Tool to find and delete Python virtual environments to free up disk space",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="venvkiller Contributors",
    author_email="me@leomaiajr.dev",
    url="https://github.com/LeomaiaJr/venvkiller",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "textual>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "venvkiller=venvkiller.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
    keywords="virtualenv venv cleanup disk-space utility development",
    project_urls={
        "Bug Reports": "https://github.com/LeomaiaJr/venvkiller/issues",
        "Source": "https://github.com/LeomaiaJr/venvkiller",
    },
)
