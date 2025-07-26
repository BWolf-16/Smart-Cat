"""
Installation and Setup Script for KiCat AI Assistant
"""

import os
import sys
import platform
import shutil
from pathlib import Path


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


def install_plugin():
    """Install the plugin to KiCad's plugins directory"""
    try:
        # Get source and destination paths
        source_dir = Path(__file__).parent / "kicat_ai"
        dest_dir = get_kicad_plugin_directory() / "kicat_ai"
        
        print(f"Installing KiCat AI Assistant Plugin...")
        print(f"Source: {source_dir}")
        print(f"Destination: {dest_dir}")
        
        # Create destination directory if it doesn't exist
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing installation if present
        if dest_dir.exists():
            print("Removing existing installation...")
            shutil.rmtree(dest_dir)
        
        # Copy plugin files
        print("Copying plugin files...")
        shutil.copytree(source_dir, dest_dir)
        
        print("✓ Plugin installed successfully!")
        print("\nNext steps:")
        print("1. Restart KiCad PCB Editor")
        print("2. Look for 'KiCat AI Assistant' in the toolbar or Tools menu")
        print("3. Click the plugin button to launch the assistant")
        print("4. Configure your API key in the settings (gear icon)")
        
        return True
        
    except Exception as e:
        print(f"✗ Installation failed: {e}")
        return False


def uninstall_plugin():
    """Uninstall the plugin from KiCad"""
    try:
        dest_dir = get_kicad_plugin_directory() / "kicat_ai"
        
        if dest_dir.exists():
            print("Uninstalling KiCat AI Assistant Plugin...")
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
    print("KiCat AI Assistant Plugin Setup")
    print("=" * 40)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python setup.py install    - Install the plugin")
        print("  python setup.py uninstall  - Uninstall the plugin")
        print("  python setup.py check      - Check system requirements")
        return
    
    command = sys.argv[1].lower()
    
    if command == "check":
        check_requirements()
    
    elif command == "install":
        if check_requirements():
            install_plugin()
    
    elif command == "uninstall":
        uninstall_plugin()
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'install', 'uninstall', or 'check'")


if __name__ == "__main__":
    main()
