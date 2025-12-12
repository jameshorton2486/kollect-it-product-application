#!/usr/bin/env python3
"""
SKU Generator Module
Generates unique SKU codes for products based on category and sequential numbering.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import threading


class SKUGenerator:
    """
    Generate unique SKU codes.
    
    Format: PREFIX-YYYY-NNNN
    Examples:
        - MILI-2025-0001 (Militaria)
        - COLL-2025-0042 (Collectibles)
        - BOOK-2025-0007 (Books)
        - ART-2025-0015 (Fine Art)
    """
    
    def __init__(self, state_file: Optional[str] = None):
        """
        Initialize the SKU generator.
        
        Args:
            state_file: Path to the JSON file storing SKU counters
        """
        self.state_file = Path(state_file) if state_file else Path(__file__).parent.parent / "config" / "sku_state.json"
        self.lock = threading.Lock()
        self._ensure_state_file()
    
    def _ensure_state_file(self):
        """Ensure the state file exists with proper structure."""
        if not self.state_file.exists():
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_state({
                "last_updated": "",
                "counters": {}
            })
    
    def _load_state(self) -> dict:
        """Load the current state from file."""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"last_updated": "", "counters": {}}
    
    def _save_state(self, state: dict):
        """Save state to file."""
        state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def generate(self, prefix: str, year: Optional[int] = None) -> str:
        """
        Generate a new SKU for the given prefix.
        
        Args:
            prefix: Category prefix (e.g., "MILI", "COLL", "BOOK", "ART")
            year: Year for the SKU (defaults to current year)
            
        Returns:
            New SKU string (e.g., "MILI-2025-0001")
        """
        with self.lock:
            prefix = prefix.upper()
            year = year or datetime.now().year
            year_str = str(year)
            
            state = self._load_state()
            counters = state.get("counters", {})
            
            # Initialize prefix if not exists
            if prefix not in counters:
                counters[prefix] = {}
            
            # Initialize year if not exists
            if year_str not in counters[prefix]:
                counters[prefix][year_str] = 0
            
            # Increment counter
            counters[prefix][year_str] += 1
            counter = counters[prefix][year_str]
            
            # Save updated state
            state["counters"] = counters
            self._save_state(state)
            
            # Format SKU
            return f"{prefix}-{year}-{counter:04d}"
    
    def peek_next(self, prefix: str, year: Optional[int] = None) -> str:
        """
        Preview the next SKU without incrementing the counter.
        
        Args:
            prefix: Category prefix
            year: Year for the SKU
            
        Returns:
            Next SKU string (preview only)
        """
        prefix = prefix.upper()
        year = year or datetime.now().year
        year_str = str(year)
        
        state = self._load_state()
        counters = state.get("counters", {})
        
        current = counters.get(prefix, {}).get(year_str, 0)
        next_num = current + 1
        
        return f"{prefix}-{year}-{next_num:04d}"
    
    def get_current_count(self, prefix: str, year: Optional[int] = None) -> int:
        """
        Get the current count for a prefix/year combination.
        
        Args:
            prefix: Category prefix
            year: Year (defaults to current)
            
        Returns:
            Current counter value
        """
        prefix = prefix.upper()
        year = year or datetime.now().year
        year_str = str(year)
        
        state = self._load_state()
        counters = state.get("counters", {})
        
        return counters.get(prefix, {}).get(year_str, 0)
    
    def set_counter(self, prefix: str, count: int, year: Optional[int] = None):
        """
        Set the counter to a specific value (use with caution).
        
        Args:
            prefix: Category prefix
            count: New counter value
            year: Year (defaults to current)
        """
        with self.lock:
            prefix = prefix.upper()
            year = year or datetime.now().year
            year_str = str(year)
            
            state = self._load_state()
            counters = state.get("counters", {})
            
            if prefix not in counters:
                counters[prefix] = {}
            
            counters[prefix][year_str] = count
            state["counters"] = counters
            self._save_state(state)
    
    def validate_sku(self, sku: str) -> bool:
        """
        Validate a SKU format.
        
        Args:
            sku: SKU string to validate
            
        Returns:
            True if valid format
        """
        import re
        pattern = r'^[A-Z]{3,4}-\d{4}-\d{4}$'
        return bool(re.match(pattern, sku.upper()))
    
    def parse_sku(self, sku: str) -> Optional[dict]:
        """
        Parse a SKU into its components.
        
        Args:
            sku: SKU string to parse
            
        Returns:
            Dictionary with prefix, year, and number, or None if invalid
        """
        if not self.validate_sku(sku):
            return None
        
        parts = sku.upper().split("-")
        return {
            "prefix": parts[0],
            "year": int(parts[1]),
            "number": int(parts[2]),
            "full": sku.upper()
        }
    
    def get_all_stats(self) -> dict:
        """
        Get statistics for all SKU counters.
        
        Returns:
            Dictionary with stats per prefix/year
        """
        state = self._load_state()
        counters = state.get("counters", {})
        
        stats = {
            "last_updated": state.get("last_updated"),
            "prefixes": {}
        }
        
        total_all = 0
        
        for prefix, years in counters.items():
            prefix_total = sum(years.values())
            total_all += prefix_total
            
            stats["prefixes"][prefix] = {
                "total": prefix_total,
                "by_year": years
            }
        
        stats["grand_total"] = total_all
        
        return stats
    
    def reset_counter(self, prefix: str, year: Optional[int] = None):
        """
        Reset counter to zero (use with caution).
        
        Args:
            prefix: Category prefix to reset
            year: Specific year to reset (or all years if None)
        """
        with self.lock:
            prefix = prefix.upper()
            
            state = self._load_state()
            counters = state.get("counters", {})
            
            if prefix in counters:
                if year:
                    year_str = str(year)
                    if year_str in counters[prefix]:
                        counters[prefix][year_str] = 0
                else:
                    counters[prefix] = {}
            
            state["counters"] = counters
            self._save_state(state)


# Convenience functions
_default_generator = None

def get_generator(state_file: Optional[str] = None) -> SKUGenerator:
    """Get or create the default SKU generator."""
    global _default_generator
    if _default_generator is None:
        _default_generator = SKUGenerator(state_file)
    return _default_generator

def generate_sku(prefix: str, year: Optional[int] = None) -> str:
    """Generate a new SKU using the default generator."""
    return get_generator().generate(prefix, year)
