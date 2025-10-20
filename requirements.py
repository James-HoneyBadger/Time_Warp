#!/usr/bin/env python3
"""
Time_Warp IDE Requirements Manager
Handles virtual environment setup, dependency installation, and environment validation
Runs automatically at startup to ensure all requirements are met
"""

import os
import sys
import subprocess
import importlib.util
import platform
import json
from pathlib import Path


class RequirementsManager:
    """Manages Python environment setup and dependency installation for Time_Warp IDE"""

    def __init__(self, project_root=None):
        # Find project root by looking for key files
        if project_root is None:
            current = Path(__file__).resolve().parent
            # Look for Time_Warp.py or pyproject.toml to find project root
            while current.parent != current:  # Stop at filesystem root
                if (current / "Time_Warp.py").exists() or (current / "pyproject.toml").exists():
                    project_root = current
                    break
                current = current.parent
            else:
                # Fallback to script directory's parent
                project_root = Path(__file__).resolve().parent.parent

        self.project_root = Path(project_root)
        self.venv_path = self.project_root / ".venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.pyproject_file = self.project_root / "pyproject.toml"
        self.config_dir = Path.home() / ".Time_Warp"
        self.config_file = self.config_dir / "requirements_config.json"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def check_python_version(self):
        """Check if Python version meets requirements"""
        print("🐍 Checking Python version...")
        version = sys.version_info
        min_version = (3, 8)

        if version < min_version:
            print(f"❌ Python {min_version[0]}.{min_version[1]}+ required, found {version.major}.{version.minor}")
            return False

        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True

    def check_venv(self):
        """Check if virtual environment exists and is valid"""
        print("📦 Checking virtual environment...")

        if not self.venv_path.exists():
            print("❌ Virtual environment not found")
            return False

        # Check if venv is functional
        python_exe = self.venv_path / "bin" / "python" if platform.system() != "Windows" else self.venv_path / "Scripts" / "python.exe"

        if not python_exe.exists():
            print("❌ Virtual environment Python executable not found")
            return False

        print(f"✅ Virtual environment found at {self.venv_path}")
        return True

    def create_venv(self):
        """Create virtual environment"""
        print(f"🏗️  Creating virtual environment at {self.venv_path}...")

        try:
            subprocess.check_call([sys.executable, "-m", "venv", str(self.venv_path)])
            print("✅ Virtual environment created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False

    def get_venv_python(self):
        """Get path to virtual environment Python executable"""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"

    def upgrade_pip(self):
        """Upgrade pip in virtual environment"""
        print("⬆️  Upgrading pip...")
        venv_python = self.get_venv_python()

        try:
            subprocess.check_call([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
            print("✅ Pip upgraded successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to upgrade pip: {e}")
            return False

    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("🔍 Checking dependencies...")

        # Read requirements
        required_packages = self._read_requirements()
        if not required_packages:
            print("⚠️  No requirements found")
            return False

        venv_python = self.get_venv_python()
        missing_packages = []

        for package in required_packages:
            if not self._check_package_installed(package, venv_python):
                missing_packages.append(package)

        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            return False

        print("✅ All dependencies are installed")
        return True

    def install_dependencies(self):
        """Install all required dependencies"""
        print("📚 Installing dependencies...")

        venv_python = self.get_venv_python()
        pip_exe = self.venv_path / "bin" / "pip" if platform.system() != "Windows" else self.venv_path / "Scripts" / "pip.exe"

        try:
            # Install from requirements.txt first
            if self.requirements_file.exists():
                print("Installing from requirements.txt...")
                subprocess.check_call([str(pip_exe), "install", "-r", str(self.requirements_file)])
                print("✅ requirements.txt installed")

            # Install from pyproject.toml if it exists
            if self.pyproject_file.exists():
                print("Installing from pyproject.toml...")
                subprocess.check_call([str(pip_exe), "install", "-e", str(self.project_root)])
                print("✅ pyproject.toml installed")

            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

    def _read_requirements(self):
        """Read requirements from files"""
        packages = set()

        # Read from requirements.txt
        if self.requirements_file.exists():
            try:
                with open(self.requirements_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (remove version specifiers)
                            package = line.split()[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0]
                            packages.add(package)
            except Exception as e:
                print(f"⚠️  Error reading requirements.txt: {e}")

        # Read from pyproject.toml
        if self.pyproject_file.exists():
            try:
                import tomllib
                with open(self.pyproject_file, 'rb') as f:
                    data = tomllib.load(f)
                    deps = data.get('project', {}).get('dependencies', [])
                    for dep in deps:
                        package = dep.split()[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0]
                        packages.add(package)
            except Exception as e:
                print(f"⚠️  Error reading pyproject.toml: {e}")

        return list(packages)

    def _check_package_installed(self, package, python_exe):
        """Check if a package is installed"""
        # Map package names to their import names
        import_map = {
            'Pillow': 'PIL',
            'PIL': 'PIL',
            'beautifulsoup4': 'bs4',
            'scikit-learn': 'sklearn',
            'python-dateutil': 'dateutil',
            'PyYAML': 'yaml',
            'pytest-cov': 'pytest_cov',
            'sphinx-rtd-theme': 'sphinx_rtd_theme',
        }

        import_name = import_map.get(package, package.lower().replace('-', '_'))

        try:
            result = subprocess.run(
                [str(python_exe), "-c", f"import {import_name}; print('OK')"],
                capture_output=True,
                text=True,
                timeout=15  # Increased timeout for slower systems
            )
            return result.returncode == 0 and 'OK' in result.stdout
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False

    def check_system_dependencies(self):
        """Check for system-level dependencies"""
        print("🔧 Checking system dependencies...")

        issues = []

        # Check for tkinter (usually included with Python)
        try:
            import tkinter
            print("✅ tkinter available")
        except ImportError:
            issues.append("tkinter not available - install python3-tk or similar")

        # Check for other common system dependencies
        system_checks = [
            ("PIL", "Pillow"),
            ("pygame", "pygame"),
        ]

        venv_python = self.get_venv_python()
        for module, package in system_checks:
            if not self._check_package_installed(module, venv_python):
                print(f"⚠️  {package} not available (optional)")
            else:
                print(f"✅ {package} available")

        if issues:
            print("❌ System dependency issues:")
            for issue in issues:
                print(f"   - {issue}")
            return False

        print("✅ System dependencies OK")
        return True

    def save_config(self):
        """Save current configuration"""
        config = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "venv_path": str(self.venv_path),
            "last_check": str(Path(__file__).stat().st_mtime),
            "platform": platform.system(),
        }

        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print("💾 Configuration saved")
        except Exception as e:
            print(f"⚠️  Failed to save config: {e}")

    def load_config(self):
        """Load saved configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def is_setup_complete(self):
        """Check if setup is complete and valid"""
        if not self.check_python_version():
            return False

        if not self.check_venv():
            return False

        if not self.check_dependencies():
            return False

        if not self.check_system_dependencies():
            return False

        return True

    def setup_environment(self):
        """Complete environment setup"""
        print("🚀 Setting up Time_Warp IDE environment...")
        print("=" * 50)

        # Check Python version
        if not self.check_python_version():
            return False

        # Setup virtual environment
        if not self.check_venv():
            if not self.create_venv():
                return False

        # Upgrade pip
        if not self.upgrade_pip():
            print("⚠️  Continuing with current pip version...")

        # Install dependencies
        if not self.check_dependencies():
            if not self.install_dependencies():
                return False

        # Final system check
        if not self.check_system_dependencies():
            print("⚠️  Some optional dependencies missing, but continuing...")

        # Save configuration
        self.save_config()

        print("=" * 50)
        print("✅ Environment setup complete!")
        print("🎉 Time_Warp IDE is ready to run!")
        return True

    def activate_venv(self):
        """Get command to activate virtual environment"""
        if platform.system() == "Windows":
            return f"{self.venv_path}\\Scripts\\activate.bat"
        else:
            return f"source {self.venv_path}/bin/activate"

    def get_venv_info(self):
        """Get information about the virtual environment"""
        info = {
            "path": str(self.venv_path),
            "python": str(self.get_venv_python()),
            "exists": self.venv_path.exists(),
            "valid": self.check_venv(),
        }
        return info


def main():
    """Main entry point"""
    manager = RequirementsManager()

    # Check if setup is needed
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("🔄 Forcing complete environment setup...")
        success = manager.setup_environment()
    elif len(sys.argv) > 1 and sys.argv[1] == "--check":
        print("🔍 Checking environment status...")
        success = manager.is_setup_complete()
        if success:
            print("✅ Environment is properly configured")
        else:
            print("❌ Environment needs setup")
            sys.exit(1)
    else:
        # Normal startup check
        if manager.is_setup_complete():
            print("✅ Environment is ready")
            success = True
        else:
            print("🔧 Environment needs setup...")
            success = manager.setup_environment()

    if not success:
        print("❌ Environment setup failed")
        print("Please check the error messages above and try again")
        sys.exit(1)

    # Print venv activation info for user
    if manager.check_venv():
        print(f"\n💡 To activate this environment later, run: {manager.activate_venv()}")


if __name__ == "__main__":
    main()