#!/usr/bin/env python3
"""
Standalone Batch Background Removal Script
==========================================
Processes all images in a folder to remove backgrounds.

Usage:
    python batch_remove_backgrounds.py <input_folder> [output_folder]
    
Examples:
    # Process images in current folder, save to ./processed
    python batch_remove_backgrounds.py .
    
    # Process images and save to specific folder
    python batch_remove_backgrounds.py ./photos ./output
    
    # Process with GPU acceleration (if rembg[gpu] installed)
    python batch_remove_backgrounds.py ./photos --gpu
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.background_remover import BackgroundRemover, REMBG_AVAILABLE, check_rembg_installation


def main():
    parser = argparse.ArgumentParser(
        description="Batch remove backgrounds from images in a folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "input_folder",
        type=str,
        help="Folder containing images to process"
    )
    
    parser.add_argument(
        "output_folder",
        type=str,
        nargs="?",
        default=None,
        help="Output folder (default: <input_folder>/processed)"
    )
    
    parser.add_argument(
        "--strength",
        type=float,
        default=0.8,
        help="Removal strength 0.0-1.0 (default: 0.8)"
    )
    
    parser.add_argument(
        "--bg-color",
        type=str,
        default="#FFFFFF",
        help="Background color hex code or 'transparent' (default: #FFFFFF)"
    )
    
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU acceleration (requires rembg[gpu] and NVIDIA GPU)"
    )
    
    parser.add_argument(
        "--check-install",
        action="store_true",
        help="Check rembg installation status and exit"
    )
    
    args = parser.parse_args()
    
    # Check installation status if requested
    if args.check_install:
        status = check_rembg_installation()
        print("\n" + "=" * 60)
        print("rembg Installation Status")
        print("=" * 60)
        print(f"Installed: {'Yes ✓' if status['installed'] else 'No ✗'}")
        if status['error']:
            print(f"Error: {status['error']}")
        print(f"\n{status['recommendation']}")
        print("=" * 60)
        return 0 if status['installed'] else 1
    
    # Check if rembg is available
    if not REMBG_AVAILABLE:
        print("\n⚠ WARNING: rembg is not installed!")
        print("\nFor best results, install rembg:")
        print("  CPU version:    pip install rembg")
        print("  GPU version:    pip install rembg[gpu] (requires NVIDIA GPU)")
        print("\nContinuing with fallback method (lower quality)...")
        print()
        
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Aborted.")
            return 1
    
    # Validate input folder
    input_path = Path(args.input_folder)
    if not input_path.exists():
        print(f"❌ Error: Input folder does not exist: {input_path}")
        return 1
    
    if not input_path.is_dir():
        print(f"❌ Error: Input path is not a directory: {input_path}")
        return 1
    
    # Determine output folder
    if args.output_folder:
        output_path = Path(args.output_folder)
    else:
        output_path = input_path / "processed"
    
    # Create output folder
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("Batch Background Removal")
    print("=" * 60)
    print(f"Input folder:  {input_path}")
    print(f"Output folder: {output_path}")
    print(f"Strength:      {args.strength}")
    print(f"Background:    {args.bg_color}")
    print(f"rembg:         {'Available ✓' if REMBG_AVAILABLE else 'Not available (using fallback)'}")
    print("=" * 60)
    print()
    
    # Initialize remover
    remover = BackgroundRemover()
    
    # Progress callback
    def progress_callback(current, total, filename):
        percent = int((current / total) * 100)
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\r[{bar}] {percent}% ({current}/{total}) - {filename}", end="", flush=True)
    
    # Process images
    try:
        results = remover.batch_remove(
            str(input_path),
            output_folder=str(output_path),
            progress_callback=progress_callback,
            strength=args.strength,
            bg_color=args.bg_color
        )
        
        print("\n\n" + "=" * 60)
        print("Processing Complete!")
        print("=" * 60)
        print(f"Total images:    {results['total']}")
        print(f"Processed:       {results['processed']} ✓")
        print(f"Failed:          {results['failed']}")
        
        if results['failed'] > 0:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  • {error['file']}: {error['error']}")
        
        print(f"\nOutput folder: {output_path}")
        print("=" * 60)
        
        return 0 if results['failed'] == 0 else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠ Processing interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

