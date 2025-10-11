"""
Virtual Environment Management for Time_Warp
Handles Python virtual environment creation and package management.
"""

import os
import sys
import subprocess
import json


class VirtualEnvironmentManager:
    """Manages virtual environment for Time_Warp IDE and package installation"""

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.venv_dir = os.path.join(self.base_dir, "james_venv")
        self.python_exe = None
        self.pip_exe = None
        self.is_initialized = False
        self.status_callback = None

    def set_status_callback(self, callback):
        """Set callback function for status updates"""
        self.status_callback = callback

    def log_status(self, message):
        """Log status message"""
        print(f"🐍 VirtualEnv: {message}")
        if self.status_callback:
            self.status_callback(f"🐍 {message}")

    def check_venv_exists(self):
        """Check if virtual environment already exists"""
        if os.path.exists(self.venv_dir):
            # Check if it has the basic structure
            python_path = os.path.join(self.venv_dir, "bin", "python")
            pip_path = os.path.join(self.venv_dir, "bin", "pip")

            if os.path.exists(python_path) and os.path.exists(pip_path):
                self.python_exe = python_path
                self.pip_exe = pip_path
                return True
        return False

    def create_virtual_environment(self):
        """Create a new virtual environment"""
        try:
            import venv

            self.log_status("Creating virtual environment...")

            # Remove existing venv if it exists but is broken
            if os.path.exists(self.venv_dir):
                import shutil

                shutil.rmtree(self.venv_dir)

            # Create new virtual environment
            venv.create(self.venv_dir, with_pip=True)

            # Set paths for executables
            self.python_exe = os.path.join(self.venv_dir, "bin", "python")
            self.pip_exe = os.path.join(self.venv_dir, "bin", "pip")

            self.log_status(f"Virtual environment created at: {self.venv_dir}")
            return True

        except Exception as e:
            self.log_status(f"Failed to create virtual environment: {e}")
            return False

    def initialize(self):
        """Initialize virtual environment for Time_Warp"""
        if self.check_venv_exists():
            self.log_status("Virtual environment found")
            self.is_initialized = True
            return True

        self.log_status("Virtual environment not found, creating...")
        if self.create_virtual_environment():
            self.is_initialized = True
            return True

        return False

    def install_package(self, package_name, version=None):
        """Install a package in the virtual environment"""
        if not self.is_initialized or not self.pip_exe:
            self.log_status("Virtual environment not initialized")
            return False

        try:
            # Construct package specification
            if version:
                package_spec = f"{package_name}=={version}"
            else:
                package_spec = package_name

            self.log_status(f"Installing {package_spec}...")

            # Run pip install
            result = subprocess.run(
                [str(self.pip_exe), "install", package_spec],
                capture_output=True,
                text=True,
                timeout=300,
            )  # 5 minute timeout

            if result.returncode == 0:
                self.log_status(f"Successfully installed {package_spec}")
                return True
            else:
                self.log_status(f"Failed to install {package_spec}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.log_status(f"Installation of {package_spec} timed out")
            return False
        except Exception as e:
            self.log_status(f"Error installing {package_spec}: {e}")
            return False

    def install_james_dependencies(self):
        """Install all dependencies needed for Time_Warp functionality"""
        dependencies = [
            ("pandas", "2.1.0"),  # For data analysis features
            ("scikit-learn", "1.3.0"),  # For machine learning features
            ("matplotlib", "3.7.0"),  # For plotting features
            ("numpy", "1.24.0"),  # For numerical operations
            ("pillow", "10.0.0"),  # For image processing
            ("requests", "2.31.0"),  # For web operations
        ]

        self.log_status("Installing Time_Warp dependencies...")
        success_count = 0

        for package, version in dependencies:
            if self.install_package(package, version):
                success_count += 1
            else:
                # Try without version specification
                if self.install_package(package):
                    success_count += 1

        self.log_status(f"Installed {success_count}/{len(dependencies)} dependencies")
        return success_count == len(dependencies)

    def list_installed_packages(self):
        """List all installed packages in the virtual environment"""
        if not self.is_initialized or not self.pip_exe:
            return []

        try:
            result = subprocess.run(
                [str(self.pip_exe), "list", "--format=json"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return packages
            else:
                return []

        except Exception as e:
            self.log_status(f"Error listing packages: {e}")
            return []

    def get_python_executable(self):
        """Get the path to the Python executable in the virtual environment"""
        return self.python_exe if self.is_initialized else None

    def activate_environment(self):
        """Activate the virtual environment (modify sys.path)"""
        if not self.is_initialized:
            return False

        try:
            import site

            # Add the virtual environment's site-packages to sys.path
            site_packages = os.path.join(
                self.venv_dir,
                "lib",
                f"python{sys.version_info.major}.{sys.version_info.minor}",
                "site-packages",
            )

            if os.path.exists(site_packages) and site_packages not in sys.path:
                sys.path.insert(0, site_packages)
                site.addsitedir(site_packages)
                self.log_status("Virtual environment activated")
                return True

        except Exception as e:
            self.log_status(f"Error activating environment: {e}")

        return False
