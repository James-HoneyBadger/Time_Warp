#!/usr/bin/env python3
"""
Setup script for Time_Warp IDE - A multi-language educational programming environment
"""

from setuptools import setup, find_packages
import os
import re


# Read the README file
def read_readme():
    with open(
        os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8"
    ) as f:
        return f.read()


# Read requirements
def read_requirements():
    with open(
        os.path.join(os.path.dirname(__file__), "requirements.txt"), encoding="utf-8"
    ) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


# Get version from a version file or set manually
__version__ = "1.0.0"

setup(
    name="time_warp-ide",
    version=__version__,
    author="Time_Warp IDE Team",
    author_email="time_warp-ide@example.com",
    description="A multi-language educational programming IDE with time-traveling themes",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Time_WarpIDE/Time_Warp",
    project_urls={
        "Bug Reports": "https://github.com/Time_WarpIDE/Time_Warp/issues",
        "Source": "https://github.com/James-HoneyBadger/Time_Warp",
        "Documentation": "https://github.com/James-HoneyBadger/Time_Warp#readme",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education",
        "Topic :: Software Development :: Interpreters",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications",
        "Natural Language :: English",
    ],
    keywords="education programming ide pilot basic logo python javascript educational",
    packages=find_packages(exclude=["tests", "test_*", "docs", "examples"]),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "time_warp=timewarp_ide.main:main",
            "time_warp-ide=timewarp_ide.main:main",
        ],
    },
    data_files=(
        [
            ("share/applications", ["data/time_warp-ide.desktop"]),
            ("share/pixmaps", ["data/time_warp-ide.png"]),
        ]
        if os.path.exists("data")
        else []
    ),
    zip_safe=False,
)
