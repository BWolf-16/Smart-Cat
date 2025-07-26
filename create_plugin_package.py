#!/usr/bin/env python3
"""
Create a minimal plugin package for KiCad Plugin Manager
This script creates a lightweight ZIP file containing only essential plugin files
"""

import os
import shutil
import zipfile
from pathlib import Path
import tempfile
import hashlib

def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def create_plugin_package():
    """Create a minimal plugin package"""
    
    # Essential plugin files only
    essential_files = [
        "__init__.py",
        "main.py", 
        "ui.py",
        "AI_API.py",
        "config.py",
        "enhanced_parser.py",
        "kicad_operations.py",
        "circuit_generator.py",
        "permissions.py",
        "parser.py"
    ]
    
    # Essential directories
    essential_dirs = [
        "resources"
    ]
    
    # Get current directory
    source_dir = Path(__file__).parent
    
    # Create temporary directory for package
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        package_dir = temp_path / "smart_cat"
        package_dir.mkdir()
        
        print("Creating minimal plugin package...")
        
        # Copy essential files
        total_size = 0
        for file_name in essential_files:
            source_file = source_dir / file_name
            if source_file.exists():
                dest_file = package_dir / file_name
                shutil.copy2(source_file, dest_file)
                size = dest_file.stat().st_size
                total_size += size
                print(f"  ✓ Added {file_name} ({size} bytes)")
            else:
                print(f"  ⚠ Missing {file_name}")
        
        # Copy essential directories
        for dir_name in essential_dirs:
            source_dir_path = source_dir / dir_name
            if source_dir_path.exists():
                dest_dir_path = package_dir / dir_name
                shutil.copytree(source_dir_path, dest_dir_path)
                # Calculate directory size
                dir_size = sum(f.stat().st_size for f in dest_dir_path.rglob('*') if f.is_file())
                total_size += dir_size
                print(f"  ✓ Added {dir_name}/ ({dir_size} bytes)")
        
        # Create ZIP package
        zip_path = source_dir / "smart_cat_plugin.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    # Calculate relative path from package_dir
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)
        
        # Calculate final package info
        package_size = zip_path.stat().st_size
        package_sha256 = calculate_sha256(zip_path)
        
        print(f"\n✓ Package created: {zip_path}")
        print(f"  Uncompressed size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        print(f"  Package size: {package_size:,} bytes ({package_size/1024:.1f} KB)")
        print(f"  Compression ratio: {((total_size - package_size) / total_size * 100):.1f}%")
        print(f"  SHA256: {package_sha256}")
        
        return {
            "download_size": package_size,
            "install_size": total_size,
            "download_sha256": package_sha256,
            "download_url": f"https://github.com/BWolf-16/Smart-Cat/releases/download/v1.0.0/smart_cat_plugin.zip"
        }

if __name__ == "__main__":
    result = create_plugin_package()
    
    print("\n" + "="*50)
    print("Update metadata.json with these values:")
    print("="*50)
    print(f'"download_size": {result["download_size"]},')
    print(f'"install_size": {result["install_size"]},')
    print(f'"download_sha256": "{result["download_sha256"]}",')
    print(f'"download_url": "{result["download_url"]}"')
