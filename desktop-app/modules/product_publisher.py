#!/usr/bin/env python3
"""
Product Publisher Module
Handles publishing products to the Kollect-It website via the service API.
"""

import json
from typing import Dict, Any, Optional
import requests


class ProductPublisher:
    """
    Publish products to the Kollect-It website.
    
    Uses the SERVICE_API_KEY authentication method for secure,
    automated product creation without user login.
    """
    
    def __init__(self, config: dict):
        self.config = config
        api_config = config.get("api", {})
        
        self.api_key = api_config.get("SERVICE_API_KEY", "")
        self.use_production = api_config.get("use_production", True)
        
        if self.use_production:
            self.base_url = api_config.get("production_url", "https://kollect-it.com/api/admin/products/service-create")
        else:
            self.base_url = api_config.get("local_url", "http://localhost:3000/api/admin/products/service-create")
        
        self.timeout = api_config.get("timeout_seconds", 30)
        self.retry_attempts = api_config.get("retry_attempts", 3)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key."""
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "User-Agent": "KollectIt-Desktop/1.0"
        }
    
    def validate_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate product data before publishing.
        
        Args:
            product_data: Product data dictionary
            
        Returns:
            Dictionary with 'valid' boolean and 'errors' list
        """
        errors = []
        
        required_fields = ["title", "sku", "category", "description", "price", "condition"]
        
        for field in required_fields:
            if not product_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate price
        price = product_data.get("price", 0)
        if not isinstance(price, (int, float)) or price <= 0:
            errors.append("Price must be a positive number")
        
        # Validate images
        images = product_data.get("images", [])
        if not images:
            errors.append("At least one image is required")
        else:
            for i, img in enumerate(images):
                if not img.get("url"):
                    errors.append(f"Image {i+1} missing URL")
        
        # Validate SKU format
        sku = product_data.get("sku", "")
        if sku and not self._validate_sku_format(sku):
            errors.append("Invalid SKU format (expected: PREFIX-YYYY-NNNN)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _validate_sku_format(self, sku: str) -> bool:
        """Validate SKU format."""
        import re
        pattern = r'^[A-Z]{3,4}-\d{4}-\d{4}$'
        return bool(re.match(pattern, sku.upper()))
    
    def publish(
        self,
        product_data: Dict[str, Any],
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Publish a product to the website.
        
        Args:
            product_data: Complete product data dictionary
            validate: Whether to validate before publishing
            
        Returns:
            API response dictionary
        """
        # Validate if requested
        if validate:
            validation = self.validate_product(product_data)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "Validation failed",
                    "messages": validation["errors"]
                }
        
        # Prepare the request
        headers = self._get_headers()
        
        # Attempt publish with retries
        last_error = None
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=product_data,
                    timeout=self.timeout
                )
                
                # Parse response
                try:
                    result = response.json()
                except json.JSONDecodeError:
                    result = {"raw_response": response.text}
                
                if response.status_code == 201:
                    return {
                        "success": True,
                        "product": result.get("product", {}),
                        "message": "Product published successfully"
                    }
                elif response.status_code == 401:
                    return {
                        "success": False,
                        "error": "Authentication failed",
                        "message": "Invalid or missing API key"
                    }
                elif response.status_code == 400:
                    return {
                        "success": False,
                        "error": "Validation error",
                        "messages": result.get("messages", [result.get("error", "Unknown error")])
                    }
                elif response.status_code == 409:
                    return {
                        "success": False,
                        "error": "Duplicate",
                        "message": result.get("message", "Product with this SKU already exists")
                    }
                else:
                    last_error = f"HTTP {response.status_code}: {result.get('error', response.text)}"
                    
            except requests.exceptions.Timeout:
                last_error = "Request timed out"
            except requests.exceptions.ConnectionError:
                last_error = "Connection error - check your internet connection"
            except requests.exceptions.RequestException as e:
                last_error = str(e)
            
            # Don't retry on authentication or validation errors
            if response.status_code in (401, 400, 409):
                break
        
        return {
            "success": False,
            "error": "Publishing failed",
            "message": last_error
        }
    
    def check_service_status(self) -> Dict[str, Any]:
        """
        Check if the publishing service is operational.
        
        Returns:
            Service status dictionary
        """
        try:
            response = requests.get(
                self.base_url,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"status": "error", "message": "Invalid API key"}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a product by ID (if supported by the API).
        
        Args:
            product_id: Product ID to retrieve
            
        Returns:
            Product data or None
        """
        # This would need a corresponding GET endpoint
        # Placeholder for future implementation
        return None
    
    def update_product(
        self,
        product_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing product (if supported by the API).
        
        Args:
            product_id: Product ID to update
            updates: Fields to update
            
        Returns:
            Update result
        """
        # This would need a corresponding PUT/PATCH endpoint
        # Placeholder for future implementation
        return {
            "success": False,
            "error": "Update not implemented",
            "message": "Product updates require additional API endpoint"
        }
    
    def build_product_payload(
        self,
        title: str,
        sku: str,
        category: str,
        description: str,
        price: float,
        condition: str,
        images: list,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build a properly structured product payload.
        
        Args:
            title: Product title
            sku: Product SKU
            category: Category ID
            description: Product description
            price: Price in USD
            condition: Condition grade
            images: List of image dictionaries with url and alt
            **kwargs: Additional optional fields
            
        Returns:
            Properly structured product dictionary
        """
        payload = {
            "title": title.strip(),
            "sku": sku.upper().strip(),
            "category": category,
            "description": description.strip(),
            "descriptionHtml": kwargs.get("descriptionHtml") or f"<p>{description}</p>",
            "price": float(price),
            "condition": condition,
            "images": [
                {
                    "url": img.get("url", img) if isinstance(img, dict) else img,
                    "alt": img.get("alt", f"{title} - Image {i+1}") if isinstance(img, dict) else f"{title} - Image {i+1}",
                    "order": img.get("order", i) if isinstance(img, dict) else i
                }
                for i, img in enumerate(images)
            ],
            "status": kwargs.get("status", "draft")
        }
        
        # Add optional fields
        optional_fields = [
            "subcategory", "originalPrice", "conditionDetails",
            "era", "origin", "materials", "dimensions", "provenance",
            "seoTitle", "seoDescription", "seoKeywords",
            "featured", "authentication"
        ]
        
        for field in optional_fields:
            if field in kwargs and kwargs[field] is not None:
                payload[field] = kwargs[field]
        
        return payload
