#!/usr/bin/env python3
"""
Kollect-It File Organizer
=========================
Organizes files from a flat directory into the correct structure.
Run this script from the desktop-app folder.

Usage:
    python organize_files.py
    python organize_files.py --check   (verify structure only)
"""

import os
import shutil
import sys
from pathlib import Path


def create_directories(base_path: Path):
    """Create required directory structure."""
    directories = [
        'config',
        'modules', 
        'templates',
        'logs',
        'processed',
        'temp'
    ]
    
    for dir_name in directories:
        dir_path = base_path / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"  [OK] Created: {dir_name}/")
    
    # Create nextjs-api at parent level
    nextjs_path = base_path.parent / 'nextjs-api'
    nextjs_path.mkdir(exist_ok=True)
    print(f"  [OK] Created: ../nextjs-api/")


def move_file(src: Path, dest_dir: Path, filename: str = None):
    """Move a file to destination directory."""
    if not src.exists():
        return False
    
    dest_filename = filename or src.name
    dest = dest_dir / dest_filename
    
    try:
        shutil.move(str(src), str(dest))
        print(f"  [OK] {src.name} -> {dest_dir.name}/")
        return True
    except Exception as e:
        print(f"  [ERROR] {src.name}: {e}")
        return False


def organize_files(base_path: Path):
    """Move files to their correct locations."""
    
    # Config files -> config/
    config_files = [
        'config.json',
        'config.example.json', 
        'sku_state.json'
    ]
    
    print("\nMoving config files...")
    config_dir = base_path / 'config'
    for f in config_files:
        move_file(base_path / f, config_dir)
    
    # Module files -> modules/
    module_files = [
        '__init__.py',
        'image_processor.py',
        'imagekit_uploader.py',
        'sku_generator.py',
        'ai_engine.py',
        'product_publisher.py',
        'background_remover.py',
        'crop_tool.py'
    ]
    
    print("\nMoving module files...")
    modules_dir = base_path / 'modules'
    for f in module_files:
        move_file(base_path / f, modules_dir)
    
    # Template files -> templates/
    template_files = [
        'militaria_template.json',
        'collectibles_template.json',
        'books_template.json',
        'fineart_template.json'
    ]
    
    print("\nMoving template files...")
    templates_dir = base_path / 'templates'
    for f in template_files:
        move_file(base_path / f, templates_dir)
    
    # Next.js API file -> ../nextjs-api/
    print("\nMoving Next.js API file...")
    nextjs_dir = base_path.parent / 'nextjs-api'
    move_file(base_path / 'route.ts', nextjs_dir)


def check_structure(base_path: Path) -> bool:
    """Verify the directory structure is correct."""
    print("\n" + "=" * 50)
    print("Checking directory structure...")
    print("=" * 50)
    
    all_ok = True
    
    # Check directories
    required_dirs = ['config', 'modules', 'templates', 'logs', 'processed', 'temp']
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"  [OK] {dir_name}/")
        else:
            print(f"  [MISSING] {dir_name}/")
            all_ok = False
    
    # Check root files
    print("\nRoot files:")
    root_files = ['main.py', 'automation_worker.py', 'requirements.txt']
    for f in root_files:
        if (base_path / f).exists():
            print(f"  [OK] {f}")
        else:
            print(f"  [MISSING] {f}")
            all_ok = False
    
    # Check config files
    print("\nConfig files:")
    config_files = ['config.json', 'config.example.json', 'sku_state.json']
    for f in config_files:
        if (base_path / 'config' / f).exists():
            print(f"  [OK] config/{f}")
        else:
            print(f"  [MISSING] config/{f}")
            all_ok = False
    
    # Check module files
    print("\nModule files:")
    module_files = [
        '__init__.py', 'image_processor.py', 'imagekit_uploader.py',
        'sku_generator.py', 'ai_engine.py', 'product_publisher.py',
        'background_remover.py', 'crop_tool.py'
    ]
    for f in module_files:
        if (base_path / 'modules' / f).exists():
            print(f"  [OK] modules/{f}")
        else:
            print(f"  [MISSING] modules/{f}")
            all_ok = False
    
    # Check template files
    print("\nTemplate files:")
    template_files = [
        'militaria_template.json', 'collectibles_template.json',
        'books_template.json', 'fineart_template.json'
    ]
    for f in template_files:
        if (base_path / 'templates' / f).exists():
            print(f"  [OK] templates/{f}")
        else:
            print(f"  [MISSING] templates/{f}")
            all_ok = False
    
    # Check nextjs-api
    print("\nNext.js API:")
    nextjs_path = base_path.parent / 'nextjs-api' / 'route.ts'
    if nextjs_path.exists():
        print(f"  [OK] ../nextjs-api/route.ts")
    else:
        print(f"  [MISSING] ../nextjs-api/route.ts")
        all_ok = False
    
    return all_ok


def main():
    print("=" * 50)
    print("  Kollect-It File Organizer")
    print("=" * 50)
    
    base_path = Path.cwd()
    print(f"\nWorking directory: {base_path}")
    
    # Check for --check flag
    if '--check' in sys.argv:
        check_structure(base_path)
        return
    
    # Confirm with user
    print("\nThis script will organize files into subdirectories.")
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    # Create directories
    print("\nCreating directories...")
    create_directories(base_path)
    
    # Move files
    organize_files(base_path)
    
    # Verify
    all_ok = check_structure(base_path)
    
    print("\n" + "=" * 50)
    if all_ok:
        print("  Organization complete!")
    else:
        print("  Some files may be missing.")
        print("  Check the ZIP file and re-extract if needed.")
    print("=" * 50)
    
    print("\nNext steps:")
    print("  1. Edit config/config.json with your API keys")
    print("  2. Run: pip install -r requirements.txt")
    print("  3. Run: python main.py")


if __name__ == '__main__':
    main()
