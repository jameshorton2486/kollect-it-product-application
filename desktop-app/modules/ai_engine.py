#!/usr/bin/env python3
"""
AI Engine Module - Handles AI-powered description and valuation generation.
Uses Anthropic Claude API for content generation.

CRITICAL: This module includes robust SSL/TLS certificate handling for Windows.
"""

import os
import sys
import json
import base64
import re
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

# ============================================
# CRITICAL: SSL/TLS Certificate Setup
# Must be done BEFORE importing requests/httpx
# ============================================

def setup_ssl_certificates():
    """
    Configure SSL certificates for Windows compatibility.
    Tries multiple methods to ensure HTTPS requests work.
    
    Returns:
        str or None: Path to certificate bundle, or None if not found
    """
    cert_path = None
    
    # Method 1: Try certifi package (most reliable)
    try:
        import certifi
        cert_path = certifi.where()
        if cert_path and os.path.exists(cert_path):
            os.environ['SSL_CERT_FILE'] = cert_path
            os.environ['REQUESTS_CA_BUNDLE'] = cert_path
            os.environ['CURL_CA_BUNDLE'] = cert_path
            return cert_path
    except ImportError:
        pass
    except Exception:
        pass
    
    # Method 2: Try Windows certificate store locations
    windows_cert_paths = [
        r"C:\Program Files\Common Files\SSL\certs\ca-bundle.crt",
        r"C:\Windows\System32\curl-ca-bundle.crt",
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'certifi', 'cacert.pem'),
        os.path.join(sys.base_prefix, 'Lib', 'site-packages', 'certifi', 'cacert.pem'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python', 'Python312', 'Lib', 'site-packages', 'certifi', 'cacert.pem'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'Python', 'Python311', 'Lib', 'site-packages', 'certifi', 'cacert.pem'),
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'Python312', 'Lib', 'site-packages', 'certifi', 'cacert.pem'),
    ]
    
    for path in windows_cert_paths:
        if path and os.path.exists(path):
            os.environ['SSL_CERT_FILE'] = path
            os.environ['REQUESTS_CA_BUNDLE'] = path
            return path
    
    # Method 3: Try to download certificates if nothing found
    try:
        import urllib.request
        import ssl
        
        # Create certs directory in app folder
        cert_dir = Path(__file__).parent.parent / "certs"
        cert_dir.mkdir(exist_ok=True)
        cert_file = cert_dir / "cacert.pem"
        
        if not cert_file.exists():
            # Download Mozilla's certificate bundle (use unverified context for bootstrap)
            url = "https://curl.se/ca/cacert.pem"
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            try:
                with urllib.request.urlopen(url, context=context, timeout=30) as response:
                    cert_file.write_bytes(response.read())
            except Exception:
                pass  # Failed to download, continue without
        
        if cert_file.exists():
            cert_path = str(cert_file)
            os.environ['SSL_CERT_FILE'] = cert_path
            os.environ['REQUESTS_CA_BUNDLE'] = cert_path
            return cert_path
    except Exception:
        pass
    
    return None

# Run SSL setup immediately at module import
SSL_CERT_PATH = setup_ssl_certificates()

# Now import HTTP libraries
import requests

# Suppress InsecureRequestWarning for fallback mode
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass

# Try to load environment variables from .env
try:
    from .env_loader import load_env_file
    load_env_file()
except ImportError:
    pass

# Try to import Anthropic SDK
try:
    from anthropic import Anthropic
    ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    ANTHROPIC_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)

# Log SSL status at module load
if SSL_CERT_PATH:
    logger.info(f"SSL certificates configured: {SSL_CERT_PATH}")
else:
    logger.warning("SSL certificates not found - will try fallback methods")


class AIEngine:
    """
    AI-powered content generation for product listings.
    Uses Claude API for descriptions, valuations, and image analysis.
    
    Features:
    - Product description generation
    - Valuation estimation
    - SEO title and meta generation
    - Category-specific templates
    - Image analysis for auto-filling forms
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.ai_config = config.get("ai", {})
        
        # Get API key from environment (strip whitespace and quotes)
        raw_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.api_key = raw_key.strip().strip('"').strip("'")
        
        # Log key info for debugging (NOT the actual key!)
        if self.api_key:
            key_len = len(self.api_key)
            key_prefix = self.api_key[:12] if key_len > 12 else self.api_key[:5]
            logger.info(f"Anthropic API key loaded: {key_len} chars, prefix: {key_prefix}...")
            if not self.api_key.startswith("sk-ant-"):
                logger.warning("API key doesn't start with 'sk-ant-' - may be invalid")
        else:
            logger.error("ANTHROPIC_API_KEY not found in environment! Set it in desktop-app/.env")
        
        self.model = self.ai_config.get("model", "claude-sonnet-4-20250514")
        self.max_tokens = self.ai_config.get("max_tokens", 4000)
        
        # Temperature from env or config
        temp_str = os.getenv("AI_TEMPERATURE")
        if temp_str:
            try:
                self.temperature = float(temp_str)
            except ValueError:
                self.temperature = self.ai_config.get("temperature", 0.7)
        else:
            self.temperature = self.ai_config.get("temperature", 0.7)
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.templates_dir = Path(__file__).parent.parent / "templates"
        
        # Initialize SDK client if available
        self.client = None
        if ANTHROPIC_SDK_AVAILABLE and self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                logger.info("Anthropic SDK client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic SDK: {e}")
    
    def _make_api_request(
        self,
        messages: list,
        system: str = None
    ) -> Optional[Dict]:
        """
        Make API request with robust error handling and SSL fallbacks.
        Tries SDK first, falls back to direct HTTP, then to unverified SSL.
        
        Args:
            messages: List of message dicts for the API
            system: Optional system prompt
            
        Returns:
            Dict with success status and text, or None on failure
        """
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not configured.\n\n"
                "Please add ANTHROPIC_API_KEY to your .env file:\n"
                "  ANTHROPIC_API_KEY=sk-ant-api03-your-key-here"
            )
        
        # Build request payload
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages
        }
        if system:
            payload["system"] = system
        
        # ========================================
        # Method 1: Try Anthropic SDK
        # ========================================
        if self.client:
            try:
                logger.debug(f"Trying Anthropic SDK with model: {self.model}")
                if system:
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        system=system,
                        messages=messages
                    )
                else:
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        messages=messages
                    )
                
                if response.content:
                    text = response.content[0].text
                    logger.info("API call successful via SDK")
                    return {"success": True, "text": text}
                    
            except Exception as e:
                logger.warning(f"SDK request failed: {e}, trying direct HTTP...")
        
        # ========================================
        # Method 2: Direct HTTP with SSL verification
        # ========================================
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        try:
            # Use SSL cert path if available
            verify_setting = SSL_CERT_PATH if (SSL_CERT_PATH and os.path.exists(SSL_CERT_PATH)) else True
            
            logger.debug(f"Trying direct HTTP with verify={verify_setting}")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120,
                verify=verify_setting
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("content"):
                    text = data["content"][0].get("text", "")
                    logger.info("API call successful via requests (verified SSL)")
                    return {"success": True, "text": text}
            elif response.status_code == 401:
                logger.error(f"API authentication failed (401). Check ANTHROPIC_API_KEY in .env")
                return {"success": False, "error": "Invalid API key"}
            else:
                logger.warning(f"API returned {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.SSLError as e:
            logger.warning(f"SSL error with verification: {e}")
        except Exception as e:
            logger.warning(f"Request failed with verification: {e}")
        
        # ========================================
        # Method 3: Direct HTTP WITHOUT SSL verification (last resort)
        # ========================================
        try:
            logger.warning("Trying API call without SSL verification (fallback)")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120,
                verify=False  # Disable SSL verification as last resort
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("content"):
                    text = data["content"][0].get("text", "")
                    logger.warning("API call succeeded with SSL verification DISABLED")
                    return {"success": True, "text": text}
            elif response.status_code == 401:
                logger.error("API authentication failed (401)")
                return {"success": False, "error": "Invalid API key"}
            else:
                logger.error(f"API error {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            logger.error(f"All API methods failed: {e}")
        
        return None
    
    def _encode_image(self, image_path: str) -> Optional[Dict]:
        """Encode image to base64 for API."""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.warning(f"Image not found: {image_path}")
                return None
            
            # Determine media type
            suffix = path.suffix.lower()
            media_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            media_type = media_types.get(suffix, 'image/jpeg')
            
            # Read and encode
            with open(path, 'rb') as f:
                data = base64.b64encode(f.read()).decode('utf-8')
            
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": data
                }
            }
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None
    
    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """Parse JSON from AI response, handling markdown fences."""
        if not text:
            return None
        
        # Remove markdown code fences
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            start = cleaned.find('{')
            end = cleaned.rfind('}')
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(cleaned[start:end+1])
                except json.JSONDecodeError:
                    pass
        
        logger.warning(f"Failed to parse JSON from response: {text[:200]}...")
        return None
    
    def _load_template(self, category: str) -> dict:
        """Load category-specific template."""
        template_file = self.templates_dir / f"{category}_template.json"
        
        if template_file.exists():
            try:
                with open(template_file) as f:
                    return json.load(f)
            except Exception:
                pass
        
        return self._get_default_template()
    
    def _get_default_template(self) -> dict:
        """Get the default description template."""
        return {
            "description_structure": [
                "opening_hook",
                "physical_description",
                "historical_context",
                "condition_assessment",
                "collector_appeal"
            ],
            "seo_rules": {
                "title_max_length": 70,
                "description_max_length": 160,
                "min_keywords": 5
            }
        }
    
    # ============================================================
    # ANALYZE IMAGES - Auto-fill ALL form fields
    # This is the primary method for the "Analyze Images" button
    # ============================================================
    
    def suggest_fields(
        self,
        product_data: Dict[str, Any],
        categories: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze images and suggest ALL form fields for auto-fill.
        This is the main method called by the "Analyze Images" button.
        
        Args:
            product_data: Dict with 'images' key containing list of image paths
            categories: Dict of available categories from config
            
        Returns:
            Dict with all suggested form fields:
            - title, category_id, subcategory, condition, era, origin
            - description, seo_title, seo_description, keywords
            - valuation {low, high, recommended}
        """
        images = product_data.get("images", [])
        if not images:
            logger.warning("No images provided for analysis")
            return None
        
        # Build content with images
        content = []
        for img_path in images[:5]:  # Max 5 images
            img_data = self._encode_image(img_path)
            if img_data:
                content.append(img_data)
        
        if not content:
            logger.error("No valid images to analyze")
            return None
        
        # Build categories spec for the prompt
        cat_spec = {}
        for k, v in categories.items():
            cat_spec[k] = {
                "display": v.get("display_name", k.title()),
                "subcategories": v.get("subcategories", [])
            }
        
        # Add analysis prompt
        prompt = f"""Analyze these product images and provide detailed information for a collectibles listing.

AVAILABLE CATEGORIES (choose category_id from these keys):
{json.dumps(cat_spec, indent=2)}

Return a JSON object with ALL of these fields filled in:

{{
    "title": "Descriptive product title (50-80 chars)",
    "category_id": "one of: militaria, collectibles, books, fineart",
    "subcategory": "Specific subcategory from the list above",
    "condition": "One of: Mint, Near Mint, Excellent, Very Good, Good, Fair, Poor",
    "era": "Time period (e.g., 'WWII', '1800s', 'Victorian', '1960s')",
    "origin": "Country or region of origin (e.g., 'United States', 'Germany')",
    "description": "Detailed 2-3 paragraph description of the item",
    "materials": "What the item is made of",
    "dimensions": "Estimated size if visible",
    "seo_title": "SEO optimized title (max 70 chars)",
    "seo_description": "Meta description (max 160 chars)",
    "keywords": ["relevant", "search", "keywords", "at least 8"],
    "valuation": {{
        "low": estimated_low_price_usd,
        "high": estimated_high_price_usd,
        "recommended": recommended_listing_price,
        "confidence": "Low/Medium/High"
    }}
}}

Be specific and detailed. Base your analysis ONLY on what you can see in the images.
Choose the most appropriate category and subcategory from the provided list."""

        content.append({"type": "text", "text": prompt})
        
        messages = [{"role": "user", "content": content}]
        
        system = """You are an expert antiques and collectibles appraiser with decades of experience.
Analyze images carefully and provide accurate, detailed information for product listings.
Always respond with valid JSON only, no additional text or markdown formatting."""
        
        result = self._make_api_request(messages, system)
        
        if result and result.get("success"):
            parsed = self._parse_json_response(result.get("text", ""))
            if parsed:
                logger.info("Image analysis completed successfully")
                return parsed
            else:
                logger.warning("Failed to parse analysis response")
        else:
            logger.warning("Image analysis API call failed")
        
        return None
    
    def analyze_images(
        self,
        image_paths: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze product images for details.
        Simpler version that returns basic image analysis.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Dictionary with analysis results
        """
        if not image_paths:
            return None
        
        content = []
        for img_path in image_paths[:5]:
            img_data = self._encode_image(img_path)
            if img_data:
                content.append(img_data)
        
        if not content:
            return None
        
        prompt = """Analyze these product images and provide:

{
    "image_descriptions": ["description for each image"],
    "suggested_names": ["suggested-filename-1", "makers-mark", "detail-view"],
    "key_features": ["Notable features visible"],
    "condition_observations": ["Any condition issues visible"],
    "recommended_primary": 0,
    "photography_suggestions": ["Tips to improve photos"]
}

Respond with valid JSON only."""

        content.append({"type": "text", "text": prompt})
        messages = [{"role": "user", "content": content}]
        
        system = "You are an expert at analyzing antiques photographs. Respond with valid JSON only."
        
        result = self._make_api_request(messages, system)
        
        if result and result.get("success"):
            return self._parse_json_response(result.get("text", ""))
        
        return None
    
    def generate_description(
        self,
        product_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a comprehensive product description.
        
        Args:
            product_data: Dictionary with product info
            
        Returns:
            Dictionary with generated content including description, SEO fields, valuation
        """
        category = product_data.get("category", "collectibles")
        template = self._load_template(category)
        
        # Build content with images
        content = []
        images = product_data.get("images", [])
        for img_path in images[:5]:
            img_data = self._encode_image(img_path)
            if img_data:
                content.append(img_data)
        
        prompt = f"""Generate a professional product listing for this collectible item.

PRODUCT INFORMATION:
- Title: {product_data.get('title', 'Please suggest a title')}
- Category: {category}
- Subcategory: {product_data.get('subcategory', 'General')}
- Condition: {product_data.get('condition', 'Not specified')}
- Era/Period: {product_data.get('era', 'Unknown')}
- Origin: {product_data.get('origin', 'Unknown')}

TEMPLATE STRUCTURE:
{json.dumps(template.get('description_structure', []), indent=2)}

Return a JSON object with:
{{
    "suggested_title": "Compelling title if current one is vague (max 70 chars)",
    "description": "Professional 2-3 paragraph product description (200-400 words)",
    "description_html": "Same description with HTML paragraph tags",
    "condition_notes": "Detailed condition assessment",
    "materials": ["identified", "materials"],
    "seo_title": "SEO optimized title (max 70 chars)",
    "seo_description": "Meta description (max 160 chars)",
    "keywords": ["keyword1", "keyword2", "...8-12 relevant keywords"],
    "valuation": {{
        "low": conservative_estimate_usd,
        "high": optimistic_estimate_usd,
        "recommended": recommended_listing_price,
        "confidence": "Low/Medium/High",
        "notes": "Brief pricing rationale"
    }}
}}

Respond with valid JSON only."""

        content.append({"type": "text", "text": prompt})
        messages = [{"role": "user", "content": content}]
        
        system = f"""You are an expert antiques dealer with 30 years experience in {category}.
Write compelling, accurate descriptions that highlight key features and appeal to collectors.
Your descriptions are SEO-optimized and professional.
Always respond with valid JSON only."""
        
        result = self._make_api_request(messages, system)
        
        if result and result.get("success"):
            parsed = self._parse_json_response(result.get("text", ""))
            if parsed:
                logger.info("Description generated successfully")
                return parsed
        
        logger.warning("Description generation failed")
        return None
    
    def generate_valuation(
        self,
        product_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate price research and valuation.
        
        Args:
            product_data: Product information dictionary
            
        Returns:
            Dictionary with valuation range and notes
        """
        content = []
        
        # Add images
        images = product_data.get("images", [])
        for img_path in images[:3]:
            img_data = self._encode_image(img_path)
            if img_data:
                content.append(img_data)
        
        prompt = f"""Provide a market valuation for this collectible item.

Item Details:
- Title: {product_data.get('title', 'Unknown')}
- Category: {product_data.get('category', 'Unknown')}
- Condition: {product_data.get('condition', 'Unknown')}
- Era: {product_data.get('era', 'Unknown')}
- Description: {product_data.get('description', 'Not provided')[:500]}

Return JSON:
{{
    "low": minimum_reasonable_price_usd,
    "high": maximum_reasonable_price_usd,
    "recommended": suggested_listing_price,
    "confidence": "Low/Medium/High",
    "notes": "Brief market analysis",
    "comparable_sales": "Reference to similar items if known",
    "market_demand": "cold/moderate/hot",
    "factors": ["factors", "affecting", "value"]
}}

Respond with valid JSON only."""

        content.append({"type": "text", "text": prompt})
        messages = [{"role": "user", "content": content}]
        
        system = """You are an expert antiques appraiser providing market valuations.
Base estimates on current market conditions for similar items.
Be conservative but realistic. Always respond with valid JSON only."""
        
        result = self._make_api_request(messages, system)
        
        if result and result.get("success"):
            parsed = self._parse_json_response(result.get("text", ""))
            if parsed:
                logger.info("Valuation generated successfully")
                return parsed
        
        logger.warning("Valuation generation failed")
        return None
    
    def generate_seo_keywords(
        self,
        product_data: Dict[str, Any],
        count: int = 15
    ) -> List[str]:
        """
        Generate SEO keywords for the product.
        
        Args:
            product_data: Product information
            count: Number of keywords to generate
            
        Returns:
            List of keywords
        """
        prompt = f"""Generate {count} SEO keywords for this antique/collectible:

Title: {product_data.get('title', 'Unknown')}
Category: {product_data.get('category', 'collectibles')}
Era: {product_data.get('era', 'Unknown')}
Origin: {product_data.get('origin', 'Unknown')}

Include long-tail keywords, collector search terms, category-specific terms.

Return ONLY a JSON array of keywords: ["keyword1", "keyword2", ...]"""

        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        
        result = self._make_api_request(messages)
        
        if result and result.get("success"):
            parsed = self._parse_json_response(result.get("text", ""))
            if isinstance(parsed, list):
                return parsed[:count]
        
        return []
