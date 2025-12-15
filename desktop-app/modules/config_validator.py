#!/usr/bin/env python3
"""
Configuration Validator Module
Validates configuration files and provides helpful error messages.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional


class ConfigValidator:
    """Validate configuration files and provide helpful error messages."""
    
    REQUIRED_SECTIONS = ["api", "imagekit", "ai", "categories", "image_processing"]
    
    REQUIRED_API_FIELDS = ["SERVICE_API_KEY", "production_url"]
    REQUIRED_IMAGEKIT_FIELDS = ["public_key", "private_key", "url_endpoint"]
    REQUIRED_AI_FIELDS = ["model"]  # api_key is read from ANTHROPIC_API_KEY env var only
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate the entire configuration.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Check required sections
        self._check_required_sections()
        
        # Validate each section
        if "api" in self.config:
            self._validate_api()
        
        if "imagekit" in self.config:
            self._validate_imagekit()
        
        if "ai" in self.config:
            self._validate_ai()
        
        if "categories" in self.config:
            self._validate_categories()
        
        if "image_processing" in self.config:
            self._validate_image_processing()
        
        # Check for common issues
        self._check_common_issues()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _check_required_sections(self):
        """Check that all required sections exist."""
        for section in self.REQUIRED_SECTIONS:
            if section not in self.config:
                self.errors.append(f"Missing required section: '{section}'")
    
    def _validate_api(self):
        """Validate API configuration."""
        api = self.config.get("api", {})
        
        for field in self.REQUIRED_API_FIELDS:
            if not api.get(field):
                self.errors.append(f"API: Missing required field '{field}'")
        
        # Check URL format
        prod_url = api.get("production_url", "")
        if prod_url and not (prod_url.startswith("http://") or prod_url.startswith("https://")):
            self.warnings.append("API: production_url should start with http:// or https://")
    
    def _validate_imagekit(self):
        """Validate ImageKit configuration."""
        ik = self.config.get("imagekit", {})
        
        for field in self.REQUIRED_IMAGEKIT_FIELDS:
            if not ik.get(field):
                self.errors.append(f"ImageKit: Missing required field '{field}'")
        
        # Check URL format
        url_endpoint = ik.get("url_endpoint", "")
        if url_endpoint and not (url_endpoint.startswith("http://") or url_endpoint.startswith("https://")):
            self.warnings.append("ImageKit: url_endpoint should start with http:// or https://")
    
    def _validate_ai(self):
        """Validate AI configuration."""
        ai = self.config.get("ai", {})
        
        # Check for required fields (api_key is read from ANTHROPIC_API_KEY env var only)
        for field in self.REQUIRED_AI_FIELDS:
            if not ai.get(field):
                self.errors.append(f"AI: Missing required field '{field}'")
        
        # Check if ANTHROPIC_API_KEY is set in environment
        import os
        if not os.getenv("ANTHROPIC_API_KEY"):
            self.warnings.append("AI: ANTHROPIC_API_KEY environment variable is not set. Set it in .env file.")
        
        # Model validation removed - models update frequently and strict validation is too brittle
        # The AI engine will handle invalid models gracefully
    
    def _validate_categories(self):
        """Validate categories configuration."""
        categories = self.config.get("categories", {})
        
        if not categories:
            self.errors.append("Categories: No categories defined")
            return
        
        for cat_id, cat_data in categories.items():
            if not isinstance(cat_data, dict):
                self.errors.append(f"Categories: '{cat_id}' must be an object")
                continue
            
            # prefix is required
            if "prefix" not in cat_data:
                self.errors.append(f"Categories: '{cat_id}' missing required field 'prefix'")
            
            # Either 'name' or 'display_name' must be present
            if "name" not in cat_data and "display_name" not in cat_data:
                self.errors.append(f"Categories: '{cat_id}' missing required field 'name' or 'display_name'")
            
            # Validate prefix format
            prefix = cat_data.get("prefix", "")
            if prefix and not (3 <= len(prefix) <= 4 and prefix.isupper()):
                self.warnings.append(f"Categories: '{cat_id}' prefix should be 3-4 uppercase letters")
    
    def _validate_image_processing(self):
        """Validate image processing configuration."""
        img = self.config.get("image_processing", {})
        
        # Check numeric ranges
        max_dim = img.get("max_dimension", 2400)
        if not (800 <= max_dim <= 5000):
            self.warnings.append("Image Processing: max_dimension should be between 800 and 5000")
        
        quality = img.get("webp_quality", 88)
        if not (50 <= quality <= 100):
            self.warnings.append("Image Processing: webp_quality should be between 50 and 100")
    
    def _check_common_issues(self):
        """Check for common configuration issues."""
        # Check for placeholder values
        api_key = self.config.get("api", {}).get("SERVICE_API_KEY", "")
        if api_key and ("YOUR_" in api_key.upper() or "EXAMPLE" in api_key.upper()):
            self.warnings.append("API: SERVICE_API_KEY appears to be a placeholder value")
        
        ik_key = self.config.get("imagekit", {}).get("private_key", "")
        if ik_key and ("YOUR_" in ik_key.upper() or "EXAMPLE" in ik_key.upper()):
            self.warnings.append("ImageKit: private_key appears to be a placeholder value")
        
        # API key is read from ANTHROPIC_API_KEY environment variable only
        # Check environment variable instead
        import os
        ai_key = os.getenv("ANTHROPIC_API_KEY", "")
        if ai_key and ("YOUR_" in ai_key.upper() or "EXAMPLE" in ai_key.upper() or "your_" in ai_key.lower()):
            self.warnings.append("AI: ANTHROPIC_API_KEY appears to be a placeholder value")
    
    def get_validation_report(self) -> str:
        """Get a formatted validation report."""
        is_valid, errors, warnings = self.validate()
        
        report = []
        report.append("=" * 50)
        report.append("Configuration Validation Report")
        report.append("=" * 50)
        
        if is_valid:
            report.append("\n✓ Configuration is valid!")
        else:
            report.append("\n✗ Configuration has errors:")
            for error in errors:
                report.append(f"  • {error}")
        
        if warnings:
            report.append("\n⚠ Warnings:")
            for warning in warnings:
                report.append(f"  • {warning}")
        
        report.append("\n" + "=" * 50)
        
        return "\n".join(report)
    
    @staticmethod
    def validate_file(config_path: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a configuration file.
        
        Args:
            config_path: Path to the config file
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        try:
            with open(config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"], []
        except FileNotFoundError:
            return False, [f"Config file not found: {config_path}"], []
        
        validator = ConfigValidator(config)
        return validator.validate()

