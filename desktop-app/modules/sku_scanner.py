#!/usr/bin/env python3
"""
SKU Scanner Module
Scans existing product folders to determine the next available SKU.
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime


class SKUScanner:
    """
    Scan existing product folders to find the highest SKU number.
    Used to ensure new SKUs don't conflict with existing products.
    """
    
    def __init__(self, products_root: str, categories: Dict):
        """
        Initialize the SKU scanner.
        
        Args:
            products_root: Root directory containing category folders (e.g., "G:/My Drive/Kollect-It/Products")
            categories: Dictionary of category configurations with prefix mappings
        """
        self.products_root = Path(products_root)
        self.categories = categories
        self.sku_pattern = re.compile(r'^([A-Z]{3,4})-(\d{4})-(\d{4})$')
    
    def scan_category_folder(self, prefix: str, year: Optional[int] = None) -> int:
        """
        Scan a category folder to find the highest SKU number.
        
        Args:
            prefix: Category prefix (e.g., "MILI", "COLL")
            year: Year to scan (defaults to current year)
            
        Returns:
            Highest SKU number found, or 0 if none found
        """
        if not year:
            year = datetime.now().year
        
        # Get category folder path from config
        category_folder = None
        for cat_id, cat_data in self.categories.items():
            if cat_data.get("prefix") == prefix.upper():
                # Try to find the category folder
                cat_path = self.products_root / prefix.upper()
                if cat_path.exists():
                    category_folder = cat_path
                break
        
        if not category_folder:
            # Fallback: try direct prefix folder
            category_folder = self.products_root / prefix.upper()
        
        if not category_folder.exists():
            return 0
        
        max_number = 0
        
        # Scan all folders in the category directory
        try:
            for item in category_folder.iterdir():
                if item.is_dir():
                    folder_name = item.name
                    match = self.sku_pattern.match(folder_name.upper())
                    if match:
                        folder_prefix, folder_year, folder_num = match.groups()
                        if folder_prefix == prefix.upper() and int(folder_year) == year:
                            max_number = max(max_number, int(folder_num))
        except (PermissionError, OSError):
            # Can't read directory, return 0
            pass
        
        return max_number
    
    def get_next_sku(self, prefix: str, year: Optional[int] = None) -> str:
        """
        Get the next available SKU by scanning existing folders.
        
        Args:
            prefix: Category prefix
            year: Year (defaults to current year)
            
        Returns:
            Next SKU string (e.g., "MILI-2025-0001")
        """
        if not year:
            year = datetime.now().year
        
        max_found = self.scan_category_folder(prefix, year)
        next_number = max_found + 1
        
        return f"{prefix.upper()}-{year}-{next_number:04d}"
    
    def scan_all_categories(self, year: Optional[int] = None) -> Dict[str, int]:
        """
        Scan all category folders and return the highest SKU for each.
        
        Args:
            year: Year to scan (defaults to current year)
            
        Returns:
            Dictionary mapping prefix to highest SKU number found
        """
        if not year:
            year = datetime.now().year
        
        results = {}
        
        for cat_id, cat_data in self.categories.items():
            prefix = cat_data.get("prefix", "")
            if prefix:
                max_num = self.scan_category_folder(prefix, year)
                results[prefix] = max_num
        
        return results
    
    def ensure_category_folder(self, prefix: str) -> Path:
        """
        Ensure the category folder exists, creating it if necessary.
        
        Args:
            prefix: Category prefix (e.g., "MILI", "COLL")
            
        Returns:
            Path to the category folder
        """
        category_folder = self.products_root / prefix.upper()
        category_folder.mkdir(parents=True, exist_ok=True)
        return category_folder
