#!/usr/bin/env python3
"""
Kollect-It Automation Worker
============================
Background service that monitors a watch folder for new product folders,
automatically processes images, generates descriptions, and publishes products.

Usage:
    python automation_worker.py              # Run once
    python automation_worker.py --daemon     # Run continuously
    python automation_worker.py --test       # Test mode (no publishing)
"""

import os
import sys
import json
import time
import shutil
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.image_processor import ImageProcessor
from modules.imagekit_uploader import ImageKitUploader
from modules.sku_generator import SKUGenerator
from modules.ai_engine import AIEngine
from modules.product_publisher import ProductPublisher
from modules.background_remover import BackgroundRemover


class AutomationWorker:
    """
    Automated product processing worker.
    
    Monitors a watch folder for new product folders and processes them through:
    1. Image optimization (resize, WebP conversion)
    2. Optional background removal
    3. ImageKit upload
    4. AI description generation
    5. Product publishing to website
    6. Archive completed folders
    """
    
    def __init__(self, config_path: str = None):
        """Initialize the automation worker."""
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), 'config', 'config.json'
        )
        self.config = self._load_config()
        self.setup_logging()
        self.initialize_modules()
        
    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
            
    def setup_logging(self):
        """Configure logging for the worker."""
        log_dir = self.config.get('paths', {}).get('logs', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(
            log_dir, 
            f"worker_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AutomationWorker')
        
    def initialize_modules(self):
        """Initialize all processing modules."""
        self.logger.info("Initializing modules...")
        
        # Image processor - pass full config
        self.image_processor = ImageProcessor(self.config)
        
        # ImageKit uploader - pass full config
        self.imagekit = ImageKitUploader(self.config)
        
        # SKU generator
        sku_state_path = os.path.join(
            os.path.dirname(self.config_path), 'sku_state.json'
        )
        self.sku_generator = SKUGenerator(sku_state_path)
        
        # AI engine - pass full config
        self.ai_engine = AIEngine(self.config)
        
        # Product publisher - pass full config
        self.publisher = ProductPublisher(self.config)
        
        # Background remover - pass full config
        self.bg_remover = BackgroundRemover(self.config)
        
        self.logger.info("All modules initialized successfully")
        
    def get_watch_folder(self) -> str:
        """Get the watch folder path from config."""
        return self.config.get('paths', {}).get(
            'watch_folder', 
            os.path.expanduser('~/Google Drive/Kollect-It/New Products')
        )
        
    def get_completed_folder(self) -> str:
        """Get the completed folder path from config."""
        return self.config.get('paths', {}).get(
            'completed',
            os.path.expanduser('~/Google Drive/Kollect-It/Completed')
        )
        
    def get_failed_folder(self) -> str:
        """Get the failed folder path from config."""
        return self.config.get('paths', {}).get(
            'failed',
            os.path.expanduser('~/Google Drive/Kollect-It/Failed')
        )
        
    def detect_category(self, folder_name: str) -> tuple:
        """
        Detect category from folder name.
        
        Returns:
            tuple: (category_key, prefix) e.g., ('militaria', 'MILI')
        """
        folder_lower = folder_name.lower()
        categories = self.config.get('categories', {})
        
        # Check each category for keyword matches
        for cat_key, cat_data in categories.items():
            keywords = cat_data.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in folder_lower:
                    return (cat_key, cat_data.get('prefix', 'COLL'))
                    
        # Check subcategories
        for cat_key, cat_data in categories.items():
            for subcat in cat_data.get('subcategories', []):
                if subcat.lower() in folder_lower:
                    return (cat_key, cat_data.get('prefix', 'COLL'))
                    
        # Default to collectibles
        return ('collectibles', 'COLL')
        
    def find_product_folders(self) -> List[str]:
        """
        Find all product folders in the watch directory.
        
        A valid product folder contains at least one image file.
        """
        watch_folder = self.get_watch_folder()
        
        if not os.path.exists(watch_folder):
            self.logger.warning(f"Watch folder does not exist: {watch_folder}")
            return []
            
        product_folders = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp', '.gif'}
        
        for item in os.listdir(watch_folder):
            item_path = os.path.join(watch_folder, item)
            
            # Skip files, only process folders
            if not os.path.isdir(item_path):
                continue
                
            # Skip hidden folders and system folders
            if item.startswith('.') or item.startswith('_'):
                continue
                
            # Check if folder contains images
            has_images = False
            for file in os.listdir(item_path):
                if Path(file).suffix.lower() in image_extensions:
                    has_images = True
                    break
                    
            if has_images:
                product_folders.append(item_path)
                
        return product_folders
        
    def process_folder(self, folder_path: str, test_mode: bool = False) -> Dict:
        """
        Process a single product folder.
        
        Args:
            folder_path: Path to the product folder
            test_mode: If True, skip publishing
            
        Returns:
            dict: Processing result with status and details
        """
        folder_name = os.path.basename(folder_path)
        self.logger.info(f"Processing folder: {folder_name}")
        
        result = {
            'folder': folder_name,
            'status': 'pending',
            'sku': None,
            'product_id': None,
            'product_url': None,
            'errors': []
        }
        
        try:
            # Step 1: Detect category
            category, prefix = self.detect_category(folder_name)
            self.logger.info(f"  Category detected: {category} ({prefix})")
            
            # Step 2: Generate SKU
            year = datetime.now().year
            sku = self.sku_generator.generate(prefix, year)
            result['sku'] = sku
            self.logger.info(f"  SKU generated: {sku}")
            
            # Step 3: Find and process images
            processed_dir = os.path.join(folder_path, 'processed')
            os.makedirs(processed_dir, exist_ok=True)
            
            image_files = self._find_images(folder_path)
            if not image_files:
                raise ValueError("No images found in folder")
                
            self.logger.info(f"  Found {len(image_files)} images")
            
            # Step 4: Process images (resize, convert to WebP)
            processed_images = []
            options = {
                "max_dimension": self.config.get("image_processing", {}).get("max_dimension", 2400),
                "quality": self.config.get("image_processing", {}).get("webp_quality", 88),
                "strip_exif": self.config.get("image_processing", {}).get("strip_exif", True),
                "output_format": "webp"
            }
            
            for i, img_path in enumerate(image_files, 1):
                try:
                    processed = self.image_processor.process_image(str(img_path), options)
                    processed_images.append(processed['output_path'])
                    self.logger.info(f"    Processed: {os.path.basename(img_path)}")
                except Exception as e:
                    self.logger.warning(f"    Failed to process {img_path}: {e}")
                    
            if not processed_images:
                raise ValueError("No images were successfully processed")
                
            # Step 5: Optional background removal (based on config)
            auto_bg_removal = self.config.get('automation', {}).get('auto_background_removal', False)
            if auto_bg_removal:
                self.logger.info("  Applying background removal...")
                for img_path in processed_images:
                    try:
                        self.bg_remover.remove_background(
                            img_path,
                            output_path=img_path  # Overwrite
                        )
                    except Exception as e:
                        self.logger.warning(f"    BG removal failed for {img_path}: {e}")
                        
            # Step 6: Upload to ImageKit
            self.logger.info("  Uploading to ImageKit...")
            uploaded_images = []
            folder = f"products/{category}/{sku}"
            for img_path in processed_images:
                try:
                    upload_result = self.imagekit.upload(
                        img_path,
                        folder=folder
                    )
                    if upload_result and upload_result.get('success'):
                        uploaded_images.append({
                            'url': upload_result['url'],
                            'thumbnailUrl': upload_result.get('thumbnailUrl', ''),
                            'fileId': upload_result.get('fileId', '')
                        })
                        self.logger.info(f"    Uploaded: {os.path.basename(img_path)}")
                    else:
                        raise Exception("Upload returned no result")
                except Exception as e:
                    self.logger.warning(f"    Upload failed for {img_path}: {e}")
                    
            if not uploaded_images:
                raise ValueError("No images were successfully uploaded")
                
            # Step 7: Generate AI description
            self.logger.info("  Generating AI description...")
            product_data = {
                "title": folder_name,
                "category": category,
                "images": processed_images[:5]  # Max 5 images for AI
            }
            ai_result = self.ai_engine.generate_description(product_data)
            
            # Step 8: Build product payload
            if not ai_result:
                ai_result = {}
            
            product_payload = {
                'title': ai_result.get('suggested_title') or ai_result.get('title') or folder_name,
                'sku': sku,
                'category': category,
                'description': ai_result.get('description', ''),
                'descriptionHtml': ai_result.get('description_html', f"<p>{ai_result.get('description', '')}</p>"),
                'price': ai_result.get('recommended', 0) or ai_result.get('recommended_price', 0),
                'condition': ai_result.get('condition', 'Good'),
                'conditionDetails': ai_result.get('condition_notes', ''),
                'era': ai_result.get('era', ''),
                'origin': ai_result.get('origin', ''),
                'materials': ai_result.get('materials', []),
                'dimensions': ai_result.get('dimensions_estimate', ''),
                'images': [
                    {
                        'url': img['url'],
                        'alt': f"{ai_result.get('suggested_title', folder_name)} - Image {i+1}",
                        'order': i
                    }
                    for i, img in enumerate(uploaded_images)
                ],
                'seoTitle': ai_result.get('seo_title', ''),
                'seoDescription': ai_result.get('seo_description', ''),
                'seoKeywords': ai_result.get('keywords', [])
            }
            
            # Step 9: Publish to website (unless test mode)
            if test_mode:
                self.logger.info("  TEST MODE - Skipping publish")
                result['status'] = 'test_complete'
            else:
                self.logger.info("  Publishing to website...")
                publish_result = self.publisher.publish(product_payload)
                
                if publish_result.get('success'):
                    result['product_id'] = publish_result.get('product', {}).get('id')
                    result['product_url'] = publish_result.get('product', {}).get('url')
                    result['status'] = 'published'
                    self.logger.info(f"  Published! ID: {result['product_id']}")
                else:
                    error_msg = publish_result.get('error') or publish_result.get('message', 'Unknown error')
                    raise ValueError(f"Publish failed: {error_msg}")
                    
            # Step 10: Save product JSON for records
            json_path = os.path.join(folder_path, f"{sku}_product.json")
            with open(json_path, 'w') as f:
                json.dump({
                    'sku': sku,
                    'category': category,
                    'product_data': product_payload,
                    'ai_result': ai_result,
                    'uploaded_images': uploaded_images,
                    'processed_at': datetime.now().isoformat(),
                    'status': result['status']
                }, f, indent=2)
                
            # Step 11: Move to completed folder
            if result['status'] in ('published', 'test_complete'):
                self._move_to_completed(folder_path)
                
        except Exception as e:
            result['status'] = 'failed'
            result['errors'].append(str(e))
            self.logger.error(f"  FAILED: {e}")
            self._move_to_failed(folder_path, str(e))
            
        return result
        
    def _find_images(self, folder_path: str) -> List[str]:
        """Find all image files in a folder (non-recursive)."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp', '.gif'}
        images = []
        
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                if Path(file).suffix.lower() in image_extensions:
                    # Skip already processed images
                    if 'processed' not in file_path:
                        images.append(file_path)
                        
        # Sort by filename
        return sorted(images)
        
    def _move_to_completed(self, folder_path: str):
        """Move processed folder to completed directory."""
        completed_dir = self.get_completed_folder()
        os.makedirs(completed_dir, exist_ok=True)
        
        folder_name = os.path.basename(folder_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{timestamp}_{folder_name}"
        
        dest_path = os.path.join(completed_dir, new_name)
        
        try:
            shutil.move(folder_path, dest_path)
            self.logger.info(f"  Moved to completed: {new_name}")
        except Exception as e:
            self.logger.warning(f"  Failed to move folder: {e}")
            
    def _move_to_failed(self, folder_path: str, error: str):
        """Move failed folder to failed directory."""
        failed_dir = self.get_failed_folder()
        os.makedirs(failed_dir, exist_ok=True)
        
        folder_name = os.path.basename(folder_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{timestamp}_{folder_name}"
        
        dest_path = os.path.join(failed_dir, new_name)
        
        try:
            shutil.move(folder_path, dest_path)
            
            # Write error log
            error_log = os.path.join(dest_path, '_ERROR.txt')
            with open(error_log, 'w') as f:
                f.write(f"Failed at: {datetime.now().isoformat()}\n")
                f.write(f"Error: {error}\n")
                
            self.logger.info(f"  Moved to failed: {new_name}")
        except Exception as e:
            self.logger.warning(f"  Failed to move folder: {e}")
            
    def run_once(self, test_mode: bool = False) -> List[Dict]:
        """
        Run a single processing cycle.
        
        Args:
            test_mode: If True, skip publishing
            
        Returns:
            list: Results for each processed folder
        """
        self.logger.info("=" * 50)
        self.logger.info("Starting processing cycle")
        self.logger.info("=" * 50)
        
        # Find product folders
        folders = self.find_product_folders()
        
        if not folders:
            self.logger.info("No product folders found")
            return []
            
        self.logger.info(f"Found {len(folders)} product folder(s)")
        
        # Process each folder
        results = []
        for folder in folders:
            result = self.process_folder(folder, test_mode=test_mode)
            results.append(result)
            
        # Summary
        self.logger.info("=" * 50)
        self.logger.info("Processing cycle complete")
        successful = sum(1 for r in results if r['status'] in ('published', 'test_complete'))
        failed = sum(1 for r in results if r['status'] == 'failed')
        self.logger.info(f"  Successful: {successful}")
        self.logger.info(f"  Failed: {failed}")
        self.logger.info("=" * 50)
        
        return results
        
    def run_daemon(self, test_mode: bool = False):
        """
        Run continuously, checking for new folders at intervals.
        
        Args:
            test_mode: If True, skip publishing
        """
        interval = self.config.get('automation', {}).get('watch_interval', 60)
        self.logger.info(f"Starting daemon mode (interval: {interval}s)")
        self.logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_once(test_mode=test_mode)
                self.logger.info(f"Sleeping for {interval} seconds...")
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("Daemon stopped by user")
            
    def check_status(self) -> Dict:
        """
        Check system status and configuration.
        
        Returns:
            dict: Status information
        """
        status = {
            'config_loaded': True,
            'watch_folder_exists': os.path.exists(self.get_watch_folder()),
            'completed_folder_exists': os.path.exists(self.get_completed_folder()),
            'api_configured': bool(self.config.get('api', {}).get('SERVICE_API_KEY')),
            'imagekit_configured': bool(self.config.get('imagekit', {}).get('private_key')),
            'ai_configured': bool(self.config.get('ai', {}).get('api_key')),
            'pending_folders': len(self.find_product_folders())
        }
        
        # Check API connectivity
        try:
            api_status = self.publisher.check_service_status()
            status['api_online'] = api_status.get('success', False)
        except Exception:
            status['api_online'] = False
            
        return status


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Kollect-It Automation Worker'
    )
    parser.add_argument(
        '--daemon', '-d',
        action='store_true',
        help='Run continuously in daemon mode'
    )
    parser.add_argument(
        '--test', '-t',
        action='store_true',
        help='Test mode - process but do not publish'
    )
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to config file'
    )
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Check system status'
    )
    
    args = parser.parse_args()
    
    # Initialize worker
    worker = AutomationWorker(config_path=args.config)
    
    if args.status:
        # Print status
        status = worker.check_status()
        print("\n=== Kollect-It Automation Status ===")
        for key, value in status.items():
            indicator = "✓" if value else "✗"
            if isinstance(value, bool):
                print(f"  {indicator} {key.replace('_', ' ').title()}")
            else:
                print(f"  • {key.replace('_', ' ').title()}: {value}")
        print()
        
    elif args.daemon:
        # Run daemon
        worker.run_daemon(test_mode=args.test)
        
    else:
        # Run once
        results = worker.run_once(test_mode=args.test)
        
        # Print results
        if results:
            print("\n=== Processing Results ===")
            for r in results:
                status_icon = "✓" if r['status'] in ('published', 'test_complete') else "✗"
                print(f"  {status_icon} {r['folder']}")
                print(f"      SKU: {r['sku']}")
                print(f"      Status: {r['status']}")
                if r['product_url']:
                    print(f"      URL: {r['product_url']}")
                if r['errors']:
                    print(f"      Errors: {', '.join(r['errors'])}")
            print()


if __name__ == '__main__':
    main()
