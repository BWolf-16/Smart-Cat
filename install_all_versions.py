"""
Multi-Version KiCad Plugin Installer
Installs Smart Cat AI Assistant in all detected KiCad versions
"""

import os
import shutil
from pathlib import Path

def get_kicad_versions():
    """Detect all installed KiCad versions"""
    kicad_base = Path.home() / "AppData" / "Roaming" / "kicad"
    versions = []
    
    if kicad_base.exists():
        for item in kicad_base.iterdir():
            if item.is_dir() and item.name.replace(".", "").isdigit():
                versions.append(item.name)
    
    return sorted(versions)

def install_to_version(version):
    """Install plugin to specific KiCad version"""
    plugins_dir = Path.home() / "AppData" / "Roaming" / "kicad" / version / "scripting" / "plugins"
    
    # Create plugins directory if it doesn't exist
    plugins_dir.mkdir(parents=True, exist_ok=True)
    
    dest_dir = plugins_dir / "smart_cat"
    source_dir = Path(__file__).parent
    
    print(f"Installing to KiCad {version}...")
    print(f"  Target: {dest_dir}")
    
    # Remove existing installation
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    
    # Create destination
    dest_dir.mkdir()
    
    # Essential files
    essential_files = [
        "__init__.py", "main.py", "ui.py", "AI_API.py", "config.py",
        "enhanced_parser.py", "kicad_operations.py", "circuit_generator.py", 
        "permissions.py", "parser.py"
    ]
    
    # Copy files
    for file_name in essential_files:
        source_file = source_dir / file_name
        if source_file.exists():
            shutil.copy2(source_file, dest_dir / file_name)
            print(f"    ✓ {file_name}")
    
    # Copy resources
    resources_src = source_dir / "resources"
    if resources_src.exists():
        shutil.copytree(resources_src, dest_dir / "resources")
        print(f"    ✓ resources/")
    
    return True

def main():
    print("Smart Cat AI Assistant - Multi-Version Installer")
    print("=" * 50)
    
    versions = get_kicad_versions()
    print(f"Detected KiCad versions: {', '.join(versions)}")
    print()
    
    if not versions:
        print("No KiCad installations found!")
        return
    
    success_count = 0
    for version in versions:
        try:
            install_to_version(version)
            success_count += 1
            print(f"  ✓ KiCad {version} installation successful")
        except Exception as e:
            print(f"  ✗ KiCad {version} installation failed: {e}")
        print()
    
    print("=" * 50)
    print(f"Installation Summary:")
    print(f"  Successful: {success_count}/{len(versions)} versions")
    print(f"  Plugin installed in: {', '.join(versions[:success_count])}")
    print()
    print("Next steps:")
    print("1. Restart ALL KiCad applications")
    print("2. Open KiCad PCB Editor (not Schematic Editor)")
    print("3. Look for 'Smart Cat AI Assistant' in toolbar/Tools menu")
    print("4. Try different KiCad versions if not visible in one")

if __name__ == "__main__":
    main()
