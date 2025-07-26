"""
Installation and Setup Script for Smart Cat AI Assistant
Supports local installation and installation from GitHub repository
"""

import os
import sys
import platform
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlretrieve


def get_kicad_plugin_directory():
    """Get the KiCad plugins directory for the current OS"""
    system = platform.system()
    
    if system == "Windows":
        # Windows: %APPDATA%\kicad\7.0\scripting\plugins\
        appdata = os.environ.get("APPDATA", "")
        return Path(appdata) / "kicad" / "7.0" / "scripting" / "plugins"
    
    elif system == "Darwin":  # macOS
        # macOS: ~/Library/Application Support/kicad/7.0/scripting/plugins/
        return Path.home() / "Library" / "Application Support" / "kicad" / "7.0" / "scripting" / "plugins"
    
    else:  # Linux and others
        # Linux: ~/.local/share/kicad/7.0/scripting/plugins/
        return Path.home() / ".local" / "share" / "kicad" / "7.0" / "scripting" / "plugins"


def download_from_github(repo_url="https://github.com/BWolf-16/Smart-Cat", branch="main"):
    """Download the plugin from GitHub repository"""
    print(f"Downloading Smart Cat AI Assistant from GitHub...")
    print(f"Repository: {repo_url}")
    print(f"Branch: {branch}")
    
    try:
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())
        zip_path = temp_dir / "smart-cat.zip"
        
        # Download the repository as ZIP
        download_url = f"{repo_url}/archive/{branch}.zip"
        print(f"Downloading from: {download_url}")
        
        urlretrieve(download_url, zip_path)
        print("✓ Download completed")
        
        # Extract the ZIP file
        extract_dir = temp_dir / "extracted"
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the extracted folder (usually Smart-Cat-main or similar)
        extracted_folders = list(extract_dir.iterdir())
        if not extracted_folders:
            raise Exception("No files found in downloaded archive")
        
        source_dir = extracted_folders[0]
        print(f"✓ Extracted to: {source_dir}")
        
        return source_dir
        
    except Exception as e:
        print(f"✗ Failed to download from GitHub: {e}")
        return None


def install_from_github(repo_url="https://github.com/BWolf-16/Smart-Cat", branch="main"):
    """Install the plugin directly from GitHub repository"""
    try:
        # Download from GitHub
        source_dir = download_from_github(repo_url, branch)
        if not source_dir:
            return False
        
        # Get destination path
        dest_dir = get_kicad_plugin_directory() / "smart_cat"
        
        print(f"Installing Smart Cat AI Assistant from GitHub...")
        print(f"Source: {source_dir}")
        print(f"Destination: {dest_dir}")
        
        # Create destination directory if it doesn't exist
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing installation if present
        if dest_dir.exists():
            print("Removing existing installation...")
            shutil.rmtree(dest_dir)
        
        # Copy plugin files (exclude non-essential files)
        print("Copying plugin files...")
        dest_dir.mkdir(exist_ok=True)
        
        # List of essential plugin files to copy
        essential_files = [
            "__init__.py", "main.py", "ui.py", "AI_API.py", "config.py",
            "enhanced_parser.py", "kicad_operations.py", "circuit_generator.py",
            "permissions.py", "parser.py"
        ]
        
        # Copy essential files
        for file_name in essential_files:
            source_file = source_dir / file_name
            if source_file.exists():
                shutil.copy2(source_file, dest_dir / file_name)
                print(f"  ✓ Copied {file_name}")
        
        # Copy resources folder if it exists
        resources_src = source_dir / "resources"
        if resources_src.exists():
            resources_dest = dest_dir / "resources"
            shutil.copytree(resources_src, resources_dest)
            print("  ✓ Copied resources/")
        
        # Clean up temporary files
        shutil.rmtree(source_dir.parent.parent)
        
        print("✓ Plugin installed successfully from GitHub!")
        print("\nNext steps:")
        print("1. Restart KiCad PCB Editor")
        print("2. Look for 'Smart Cat AI Assistant' in the toolbar or Tools menu")
        print("3. Click the plugin button to launch the assistant")
        print("4. Configure your API key in the settings (gear icon)")
        
        return True
        
    except Exception as e:
        print(f"✗ GitHub installation failed: {e}")
        return False


def install_plugin():
    """Install the plugin to KiCad's plugins directory"""
    try:
        # Get source and destination paths - updated for Smart Cat rebranding
        source_dir = Path(__file__).parent
        dest_dir = get_kicad_plugin_directory() / "smart_cat"
        
        print(f"Installing Smart Cat AI Assistant Plugin...")
        print(f"Source: {source_dir}")
        print(f"Destination: {dest_dir}")
        
        # Create destination directory if it doesn't exist
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing installation if present
        if dest_dir.exists():
            print("Removing existing installation...")
            shutil.rmtree(dest_dir)
        
        # Create fresh destination directory
        dest_dir.mkdir(exist_ok=True)
        
        # List of essential plugin files to copy
        essential_files = [
            "__init__.py", "main.py", "ui.py", "AI_API.py", "config.py",
            "enhanced_parser.py", "kicad_operations.py", "circuit_generator.py",
            "permissions.py", "parser.py"
        ]
        
        # Copy essential files
        print("Copying essential plugin files...")
        for file_name in essential_files:
            source_file = source_dir / file_name
            if source_file.exists():
                shutil.copy2(source_file, dest_dir / file_name)
                print(f"  ✓ Copied {file_name}")
            else:
                print(f"  ⚠ Missing {file_name}")
        
        # Copy resources folder if it exists
        resources_src = source_dir / "resources"
        if resources_src.exists():
            resources_dest = dest_dir / "resources"
            shutil.copytree(resources_src, resources_dest)
            print("  ✓ Copied resources/")
        
        print("✓ Plugin installed successfully!")
        print("\nNext steps:")
        print("1. Restart KiCad PCB Editor")
        print("2. Look for 'Smart Cat AI Assistant' in the toolbar or Tools menu")
        print("3. Click the plugin button to launch the assistant")
        print("4. Configure your API key in the settings (gear icon)")
        
        return True
        
    except Exception as e:
        print(f"✗ Installation failed: {e}")
        return False


def uninstall_plugin():
    """Uninstall the plugin from KiCad"""
    try:
        dest_dir = get_kicad_plugin_directory() / "smart_cat"
        
        if dest_dir.exists():
            print("Uninstalling Smart Cat AI Assistant Plugin...")
            shutil.rmtree(dest_dir)
            print("✓ Plugin uninstalled successfully!")
            print("Please restart KiCad to complete the removal.")
        else:
            print("Plugin not found - nothing to uninstall.")
        
        return True
        
    except Exception as e:
        print(f"✗ Uninstallation failed: {e}")
        return False


def check_requirements():
    """Check if the system meets plugin requirements"""
    print("Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 6):
        print(f"✓ Python {python_version.major}.{python_version.minor} (supported)")
    else:
        print(f"✗ Python {python_version.major}.{python_version.minor} (requires 3.6+)")
        return False
    
    # Check for PyQt
    try:
        import PyQt5
        print("✓ PyQt5 available")
    except ImportError:
        try:
            import PyQt6
            print("✓ PyQt6 available")
        except ImportError:
            print("✗ PyQt5 or PyQt6 not found (required for UI)")
            return False
    
    # Check KiCad plugin directory
    plugin_dir = get_kicad_plugin_directory()
    if plugin_dir.parent.exists():
        print(f"✓ KiCad plugin directory found: {plugin_dir}")
    else:
        print(f"⚠ KiCad plugin directory not found: {plugin_dir}")
        print("  This might be normal if KiCad hasn't been run yet.")
    
    print("System requirements check complete.")
    return True


def main():
    """Main setup function"""
    print("Smart Cat AI Assistant Plugin Setup")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python setup.py install       - Install the plugin from local files")
        print("  python setup.py install-repo  - Install the plugin from GitHub repository")
        print("  python setup.py uninstall     - Uninstall the plugin")
        print("  python setup.py check         - Check system requirements")
        print("\nGitHub Installation Options:")
        print("  python setup.py install-repo [repo_url] [branch]")
        print("  Example: python setup.py install-repo https://github.com/BWolf-16/Smart-Cat main")
        return
    
    command = sys.argv[1].lower()
    
    if command == "check":
        check_requirements()
    
    elif command == "install":
        if check_requirements():
            install_plugin()
    
    elif command == "install-repo":
        repo_url = "https://github.com/BWolf-16/Smart-Cat"
        branch = "main"
        
        # Allow custom repo URL and branch
        if len(sys.argv) > 2:
            repo_url = sys.argv[2]
        if len(sys.argv) > 3:
            branch = sys.argv[3]
            
        if check_requirements():
            install_from_github(repo_url, branch)
    
    elif command == "uninstall":
        uninstall_plugin()
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'install', 'install-repo', 'uninstall', or 'check'")


if __name__ == "__main__":
    main()
