#!/usr/bin/env python3
"""
Website Publisher Module
Publishes products to kollect-it.com via API.

Products are always created as DRAFT for admin review.
"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class WebsitePublisher:
    """
    Publish products to Kollect-It website.
    
    Features:
    - Secure API authentication
    - Validates before sending
    - Creates products as draft
    - Returns admin review URL
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the publisher.
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # API configuration
        api_config = config.get("api", {})
        self.base_url = api_config.get("production_url", "https://kollect-it.com")
        self.api_key = os.getenv("PRODUCT_INGEST_API_KEY") or api_config.get("ingest_api_key", "")
        
        # Endpoint
        self.ingest_endpoint = f"{self.base_url.rstrip('/')}/api/admin/products/ingest"
        
        # Request settings
        self.timeout = 60  # seconds
        self.max_retries = 2
    
    def is_configured(self) -> bool:
        """Check if publisher is properly configured."""
        return bool(self.api_key and self.api_key.strip())
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get detailed configuration status."""
        return {
            "api_key_set": bool(self.api_key),
            "api_key_length": len(self.api_key) if self.api_key else 0,
            "base_url": self.base_url,
            "endpoint": self.ingest_endpoint,
            "ready": self.is_configured()
        }
    
    def validate_product_data(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate product data before publishing.
        
        Args:
            product_data: Product dictionary from desktop app
            
        Returns:
            Dict with 'valid' boolean and 'errors' list
        """
        errors = []
        
        # Required fields
        if not product_data.get("sku"):
            errors.append("Missing SKU")
        if not product_data.get("title"):
            errors.append("Missing title")
        if not product_data.get("description"):
            errors.append("Missing description")
        if not product_data.get("price") and product_data.get("price") != 0:
            errors.append("Missing price")
        if not product_data.get("category"):
            errors.append("Missing category")
        
        # Images check
        images = product_data.get("images", [])
        if not images:
            errors.append("No images - upload to ImageKit first")
        else:
            # Check that images have URLs
            for i, img in enumerate(images):
                if not img.get("url"):
                    errors.append(f"Image {i+1} missing URL")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def build_payload(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build API payload from desktop app product data.
        
        Args:
            product_data: Product dictionary from desktop app
            
        Returns:
            Formatted payload for API
        """
        # Map desktop app fields to API fields
        payload = {
            "sku": product_data.get("sku", ""),
            "title": product_data.get("title", ""),
            "description": product_data.get("description", ""),
            "price": float(product_data.get("price", 0)),
            "condition": product_data.get("condition"),
            "category": product_data.get("category", ""),
            "subcategory": product_data.get("subcategory"),
            
            # Images
            "images": [
                {
                    "url": img.get("url", ""),
                    "alt": img.get("alt", f"{product_data.get('title', 'Product')} - Image {i+1}"),
                    "order": img.get("order", i)
                }
                for i, img in enumerate(product_data.get("images", []))
            ],
            
            # SEO
            "seoTitle": product_data.get("seoTitle") or product_data.get("title"),
            "seoDescription": product_data.get("seoDescription") or (product_data.get("description", "")[:160] if product_data.get("description") else ""),
            "seoKeywords": product_data.get("seoKeywords", []),
            
            # Additional fields
            "era": product_data.get("era"),
            "origin": product_data.get("origin"),
            "year": product_data.get("era"),  # Map era to year
            "artist": product_data.get("artist"),
            "medium": product_data.get("medium"),
            "period": product_data.get("era"),  # Map era to period
            "rarity": product_data.get("rarity"),
            "productNotes": product_data.get("productNotes"),
            
            # AI data
            "aiAnalysis": product_data.get("aiAnalysis"),
            "priceConfidence": product_data.get("priceConfidence"),
            "pricingReasoning": product_data.get("pricingReasoning"),
            "last_valuation": product_data.get("last_valuation"),
            
            # Metadata
            "source": "desktop-app",
            "created_at": datetime.now().isoformat()
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return payload
    
    def publish(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish product to website.
        
        Args:
            product_data: Product dictionary from desktop app
            
        Returns:
            Result dictionary with success status and details
        """
        # Check configuration
        if not self.is_configured():
            return {
                "success": False,
                "error": "Publisher not configured",
                "message": (
                    "PRODUCT_INGEST_API_KEY not set.\n\n"
                    "Add to your .env file:\n"
                    "PRODUCT_INGEST_API_KEY=your-api-key-here\n\n"
                    "Get this key from your website admin."
                )
            }
        
        # Validate data
        validation = self.validate_product_data(product_data)
        if not validation["valid"]:
            return {
                "success": False,
                "error": "Validation failed",
                "errors": validation["errors"]
            }
        
        # Build payload
        payload = self.build_payload(product_data)
        
        print(f"[PUBLISH] Publishing {payload['sku']} to {self.base_url}...")
        
        # Make request with retry
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    self.ingest_endpoint,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "X-Source": "kollect-it-desktop-app"
                    },
                    timeout=self.timeout
                )
                
                # Parse response
                try:
                    result = response.json()
                except:
                    result = {"raw": response.text}
                
                # Handle response codes
                if response.status_code == 201:
                    # Success!
                    print(f"[PUBLISH] ✓ Product created as draft")
                    return {
                        "success": True,
                        "message": "Product published as draft",
                        "product_id": result.get("product", {}).get("id"),
                        "sku": result.get("product", {}).get("sku"),
                        "admin_url": result.get("urls", {}).get("adminFull"),
                        "public_url": result.get("urls", {}).get("publicFull"),
                        "next_step": result.get("nextStep", "Review in admin panel"),
                        "response": result
                    }
                
                elif response.status_code == 409:
                    # Duplicate SKU
                    print(f"[PUBLISH] ✗ Duplicate SKU")
                    return {
                        "success": False,
                        "error": "Duplicate SKU",
                        "message": f"Product with SKU {payload['sku']} already exists",
                        "existing_product_id": result.get("existingProductId"),
                        "admin_url": f"{self.base_url}{result.get('adminUrl', '')}"
                    }
                
                elif response.status_code == 400:
                    # Validation error
                    print(f"[PUBLISH] ✗ Validation error: {result}")
                    return {
                        "success": False,
                        "error": "Validation error",
                        "message": result.get("error", "Invalid data"),
                        "details": result.get("details") or result.get("availableCategories")
                    }
                
                elif response.status_code == 401:
                    # Auth error
                    print(f"[PUBLISH] ✗ Unauthorized")
                    return {
                        "success": False,
                        "error": "Unauthorized",
                        "message": "Invalid API key. Check PRODUCT_INGEST_API_KEY in .env"
                    }
                
                else:
                    # Other error
                    last_error = f"HTTP {response.status_code}: {result}"
                    print(f"[PUBLISH] ✗ Error: {last_error}")
                    
            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                print(f"[PUBLISH] ✗ Timeout (attempt {attempt + 1})")
                
            except requests.exceptions.ConnectionError:
                last_error = "Could not connect to server"
                print(f"[PUBLISH] ✗ Connection error (attempt {attempt + 1})")
                
            except Exception as e:
                last_error = str(e)
                print(f"[PUBLISH] ✗ Error: {e}")
        
        return {
            "success": False,
            "error": "Request failed",
            "message": last_error
        }
    
    def check_status(self) -> Dict[str, Any]:
        """
        Check API status and get available categories.
        
        Returns:
            Status dictionary
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Not configured"
            }
        
        try:
            response = requests.get(
                self.ingest_endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def publish_product(config: Dict[str, Any], product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to publish a product.
    
    Args:
        config: Application configuration
        product_data: Product dictionary
        
    Returns:
        Publish result
    """
    publisher = WebsitePublisher(config)
    return publisher.publish(product_data)
