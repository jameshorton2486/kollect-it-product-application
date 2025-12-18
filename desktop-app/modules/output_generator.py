#!/usr/bin/env python3
"""
Output Generator Module
Generates export files for products (product-info.txt, product-payload.json, imagekit-urls.txt).
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class OutputGenerator:
    """
    Generate export files for products.
    
    Creates:
    - product-info.txt: Human-readable product information for copy/paste
    - product-payload.json: Structured JSON data
    - imagekit-urls.txt: List of ImageKit CDN URLs
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the output generator.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.products_root = Path(
            config.get("paths", {}).get("products_root", r"G:\My Drive\Kollect-It\Products")
        )
    
    def export_package(
        self, 
        product_data: Dict[str, Any], 
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export a complete product package to files.
        
        Args:
            product_data: Dictionary containing all product information:
                - title, sku, category, subcategory
                - description, price, condition
                - era, origin, materials, dimensions
                - images (list of dicts with url, alt, order)
                - seoTitle, seoDescription, seoKeywords
                - last_valuation (optional)
            output_path: Optional path to output folder. If not provided,
                        uses products_root/prefix/sku structure.
        
        Returns:
            Dictionary with:
                - success: bool
                - output_path: Path to the created folder
                - files: List of created file paths
        """
        try:
            # Extract key data
            sku = product_data.get("sku", "").upper()
            category = product_data.get("category", "")
            
            if not sku or not category:
                return {
                    "success": False,
                    "error": "SKU and category are required"
                }
            
            # Determine output folder
            if output_path:
                product_folder = Path(output_path)
            else:
                # Get category prefix from SKU
                prefix = sku.split("-")[0] if "-" in sku else ""
                
                # Determine output folder structure
                category_folder = self.products_root / prefix
                product_folder = category_folder / sku
            
            # Create folders
            product_folder.mkdir(parents=True, exist_ok=True)
            
            created_files = []
            
            # 1. Generate product-info.txt (human-readable)
            info_file = product_folder / "product-info.txt"
            self._generate_info_file(info_file, product_data)
            created_files.append(info_file)
            
            # 2. Generate product-payload.json (structured data)
            payload_file = product_folder / "product-payload.json"
            self._generate_payload_file(payload_file, product_data)
            created_files.append(payload_file)
            
            # 3. Generate imagekit-urls.txt (image links)
            urls_file = product_folder / "imagekit-urls.txt"
            self._generate_urls_file(urls_file, product_data.get("images", []))
            created_files.append(urls_file)
            
            return {
                "success": True,
                "output_path": product_folder,
                "files": created_files,
                "sku": sku,
                "category": category
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_info_file(self, file_path: Path, product_data: Dict[str, Any]):
        """Generate human-readable product information file."""
        lines = []
        lines.append("=" * 60)
        lines.append("PRODUCT INFORMATION")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"Title: {product_data.get('title', '')}")
        lines.append(f"SKU: {product_data.get('sku', '')}")
        lines.append(f"Category: {product_data.get('category', '')}")
        if product_data.get('subcategory'):
            lines.append(f"Subcategory: {product_data.get('subcategory')}")
        lines.append("")
        
        lines.append(f"Price: ${product_data.get('price', 0):,.2f}")
        if product_data.get('originalPrice'):
            lines.append(f"Original Price: ${product_data.get('originalPrice'):,.2f}")
        lines.append(f"Condition: {product_data.get('condition', '')}")
        lines.append("")
        
        if product_data.get('era'):
            lines.append(f"Era/Period: {product_data.get('era')}")
        if product_data.get('origin'):
            lines.append(f"Origin: {product_data.get('origin')}")
        if product_data.get('materials'):
            materials = product_data.get('materials', [])
            if isinstance(materials, list):
                lines.append(f"Materials: {', '.join(materials)}")
            else:
                lines.append(f"Materials: {materials}")
        lines.append("")
        
        lines.append("-" * 60)
        lines.append("DESCRIPTION")
        lines.append("-" * 60)
        lines.append(product_data.get('description', ''))
        lines.append("")
        
        # Add pricing research if available
        if product_data.get('last_valuation'):
            valuation = product_data.get('last_valuation')
            lines.append("-" * 60)
            lines.append("PRICING RESEARCH")
            lines.append("-" * 60)
            lines.append(f"Suggested Range: ${valuation.get('low', 0):,.2f} - ${valuation.get('high', 0):,.2f}")
            lines.append(f"Recommended: ${valuation.get('recommended', 0):,.2f}")
            lines.append(f"Confidence: {valuation.get('confidence', 'Medium')}")
            if valuation.get('notes'):
                lines.append(f"Notes: {valuation.get('notes')}")
            lines.append("")
        
        # Add SEO information
        if product_data.get('seoTitle') or product_data.get('seoDescription'):
            lines.append("-" * 60)
            lines.append("SEO INFORMATION")
            lines.append("-" * 60)
            if product_data.get('seoTitle'):
                lines.append(f"SEO Title: {product_data.get('seoTitle')}")
            if product_data.get('seoDescription'):
                lines.append(f"SEO Description: {product_data.get('seoDescription')}")
            if product_data.get('seoKeywords'):
                keywords = product_data.get('seoKeywords', [])
                if isinstance(keywords, list):
                    lines.append(f"SEO Keywords: {', '.join(keywords)}")
            lines.append("")
        
        # Add image information
        images = product_data.get('images', [])
        if images:
            lines.append("-" * 60)
            lines.append("IMAGES")
            lines.append("-" * 60)
            for i, img in enumerate(images, 1):
                url = img.get('url', '')
                alt = img.get('alt', f'Image {i}')
                lines.append(f"{i}. {alt}")
                lines.append(f"   {url}")
            lines.append("")
        
        # Add Google Drive location if available
        if product_data.get('google_drive_folder'):
            lines.append("-" * 60)
            lines.append("FILE LOCATIONS")
            lines.append("-" * 60)
            lines.append(f"Google Drive: {product_data.get('google_drive_folder')}")
            if product_data.get('imagekit_folder'):
                lines.append(f"ImageKit: {product_data.get('imagekit_folder')}")
            lines.append("")
        
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def _generate_payload_file(self, file_path: Path, product_data: Dict[str, Any]):
        """Generate structured JSON payload file."""
        # Create a clean payload with all relevant data
        payload = {
            "title": product_data.get("title", ""),
            "sku": product_data.get("sku", ""),
            "category": product_data.get("category", ""),
            "subcategory": product_data.get("subcategory"),
            "description": product_data.get("description", ""),
            "descriptionHtml": product_data.get("descriptionHtml", f"<p>{product_data.get('description', '')}</p>"),
            "price": product_data.get("price", 0),
            "originalPrice": product_data.get("originalPrice"),
            "condition": product_data.get("condition", ""),
            "era": product_data.get("era"),
            "origin": product_data.get("origin"),
            "materials": product_data.get("materials", []),
            "dimensions": product_data.get("dimensions", {}),
            "images": product_data.get("images", []),
            "imagekit_folder": product_data.get("imagekit_folder"),
            "google_drive_folder": product_data.get("google_drive_folder"),
            "seoTitle": product_data.get("seoTitle", product_data.get("title", "")),
            "seoDescription": product_data.get("seoDescription", product_data.get("description", "")[:160]),
            "seoKeywords": product_data.get("seoKeywords", []),
            "status": "draft",
            "last_valuation": product_data.get("last_valuation"),
            "exported_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    
    def _generate_urls_file(self, file_path: Path, images: List[Dict[str, Any]]):
        """Generate ImageKit URLs file."""
        lines = []
        lines.append("ImageKit CDN URLs")
        lines.append("=" * 60)
        lines.append("")
        
        if not images:
            lines.append("No images uploaded.")
        else:
            for i, img in enumerate(images, 1):
                url = img.get('url', '')
                alt = img.get('alt', f'Image {i}')
                lines.append(f"{i}. {alt}")
                lines.append(f"   {url}")
                lines.append("")
        
        lines.append("=" * 60)
        lines.append(f"Total images: {len(images)}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
