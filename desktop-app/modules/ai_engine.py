#!/usr/bin/env python3
"""
AI Engine Module
Handles AI-powered description generation, valuation, and SEO optimization.
"""

import os
import json
import base64
import re
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests

# Try to load environment variables
try:
    from .env_loader import load_env_file
    load_env_file()
except ImportError:
    pass

# Try to use Anthropic SDK if available, fallback to requests
try:
    from anthropic import Anthropic
    ANTHROPIC_SDK_AVAILABLE = True
except ImportError:
    ANTHROPIC_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIEngine:
    """
    AI-powered product content generation.

    Features:
    - Product description generation
    - Valuation estimation
    - SEO title and meta generation
    - Category-specific templates
    - Image analysis for details
    """

    def __init__(self, config: dict):
        self.config = config
        ai_config = config.get("ai", {})

        self.provider = ai_config.get("provider", "anthropic")
        self.model = ai_config.get("model", "claude-sonnet-4-20250514")
        # Check .env first, fallback to config.json
        self.api_key = os.getenv("ANTHROPIC_API_KEY") or ai_config.get("api_key", "")
        self.max_tokens = ai_config.get("max_tokens", 4000)
        # Check .env for temperature override, fallback to config.json
        temp_str = os.getenv("AI_TEMPERATURE")
        if temp_str:
            try:
                self.temperature = float(temp_str)
            except ValueError:
                self.temperature = ai_config.get("temperature", 0.3)
        else:
            self.temperature = ai_config.get("temperature", 0.3)

        self.templates_dir = Path(__file__).parent.parent / "templates"

        # Initialize Anthropic client if SDK is available
        if ANTHROPIC_SDK_AVAILABLE and self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic SDK: {e}")
                self.client = None
        else:
            self.client = None

    def _clean_json_response(self, response: str) -> str:
        """Clean markdown formatting from JSON response."""
        if not response:
            return ""

        cleaned = response.strip()

        # Remove markdown code fences (```json ... ``` or ``` ... ```)
        # Handle cases with or without language identifier
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned)

        # Also handle single backticks sometimes used
        cleaned = cleaned.strip('`').strip()

        return cleaned

    def _load_template(self, category: str) -> dict:
        """Load category-specific template."""
        template_file = self.templates_dir / f"{category}_template.json"

        if template_file.exists():
            with open(template_file) as f:
                return json.load(f)

        # Return default template
        return self._get_default_template()

    def _get_default_template(self) -> dict:
        """Get the default description template."""
        return {
            "description_structure": [
                "opening_hook",
                "physical_description",
                "historical_context",
                "condition_assessment",
                "provenance_notes",
                "collector_appeal"
            ],
            "required_fields": [
                "title",
                "description",
                "condition",
                "dimensions"
            ],
            "seo_rules": {
                "title_max_length": 70,
                "description_max_length": 160,
                "min_keywords": 5
            }
        }

    def _encode_image(self, image_path: str) -> Optional[str]:
        """Encode image to base64 for API."""
        try:
            with open(image_path, "rb") as f:
                return base64.standard_b64encode(f.read()).decode("utf-8")
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None

    def _get_image_media_type(self, path: str) -> str:
        """Get media type from file extension."""
        ext = Path(path).suffix.lower()
        types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }
        return types.get(ext, "image/jpeg")

    def _call_anthropic(
        self,
        prompt: str,
        images: Optional[List[str]] = None,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Make a request to the Anthropic API."""
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")

        # Build message content
        content = []

        # Add images if provided
        if images:
            for img_path in images[:5]:  # Max 5 images
                encoded = self._encode_image(img_path)
                if encoded:
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": self._get_image_media_type(img_path),
                            "data": encoded
                        }
                    })

        # Add text prompt
        content.append({
            "type": "text",
            "text": prompt
        })

        # Use SDK if available, otherwise fallback to requests
        if self.client and ANTHROPIC_SDK_AVAILABLE:
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt or "",
                    messages=[
                        {"role": "user", "content": content}
                    ]
                )
                return response.content[0].text
            except Exception as e:
                logger.error(f"Anthropic SDK error: {e}")
                # Fallback to requests
                pass

        # Fallback to direct API calls
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": content}
            ]
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("content", [{}])[0].get("text", "")
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None

    def generate_description(
        self,
        product_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a comprehensive product description.

        Args:
            product_data: Dictionary with product info
                - title: Product title (optional, will suggest if empty)
                - category: Product category
                - subcategory: Product subcategory
                - condition: Item condition
                - era: Time period/era
                - origin: Country/region of origin
                - images: List of image paths

        Returns:
            Dictionary with generated content
        """
        category = product_data.get("category", "collectibles")
        template = self._load_template(category)

        system_prompt = f"""You are an expert antiques and collectibles appraiser with 30 years of experience,
specializing in {category}. You write compelling, accurate product descriptions for high-end
marketplaces like 1stDibs and Chairish. Your descriptions are:
- Factually accurate and professionally written
- Evocative without being flowery
- SEO-optimized for search visibility
- Focused on collector appeal and investment value
- Honest about condition

Always respond in valid JSON format."""

        prompt = f"""Analyze this product and generate a comprehensive listing.

PRODUCT INFORMATION:
- Title: {product_data.get('title', 'Please suggest a title')}
- Category: {category}
- Subcategory: {product_data.get('subcategory', 'General')}
- Condition: {product_data.get('condition', 'Not specified')}
- Era/Period: {product_data.get('era', 'Unknown')}
- Origin: {product_data.get('origin', 'Unknown')}

TEMPLATE STRUCTURE:
{json.dumps(template.get('description_structure', []), indent=2)}

Please analyze the images (if provided) and generate:

1. **suggested_title**: A compelling, SEO-friendly title (max 70 chars)
2. **description**: A detailed product description (200-400 words) following the template structure
3. **description_html**: The same description formatted with HTML paragraphs
4. **condition_notes**: Detailed condition assessment
5. **dimensions_estimate**: Estimated dimensions if visible
6. **materials**: List of identified materials
7. **seo_title**: Optimized SEO title (max 70 chars)
8. **seo_description**: Meta description (max 160 chars)
9. **keywords**: Array of 8-12 relevant keywords
10. **collector_notes**: Why this would appeal to collectors
11. **authentication_notes**: Suggestions for authentication if applicable
12. **valuation**: {{
    "low": Conservative low estimate (USD),
    "high": Optimistic high estimate (USD),
    "recommended": Recommended listing price (USD),
    "reasoning": Brief explanation of value
}}

Respond ONLY with a valid JSON object, no markdown formatting."""

        images = product_data.get("images", [])
        response = self._call_anthropic(prompt, images, system_prompt)

        if response:
            try:
                cleaned = self._clean_json_response(response)
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                logger.debug(f"Raw response: {response[:500]}...")
                # Try to extract description from raw text if JSON parsing fails
                return {
                    "description": response[:1000] if len(response) > 1000 else response,
                    "error": "JSON parsing failed",
                    "raw": cleaned
                }

        logger.warning("AI description generation returned no response")
        return None

    def generate_valuation(
        self,
        product_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a valuation estimate for the product.

        Args:
            product_data: Product information dictionary

        Returns:
            Dictionary with valuation range and notes
        """
        category = product_data.get("category", "collectibles")

        system_prompt = """You are an expert antiques appraiser with extensive auction house experience.
You provide realistic market valuations based on current collector demand and recent comparable sales.
Always be conservative and honest. Include your reasoning.
Respond in valid JSON format only."""

        prompt = f"""Provide a market valuation for this item:

PRODUCT DETAILS:
- Title: {product_data.get('title', 'Unknown')}
- Category: {category}
- Condition: {product_data.get('condition', 'Unknown')}
- Era: {product_data.get('era', 'Unknown')}
- Description: {product_data.get('description', 'No description')[:500]}

Please provide:

1. **low**: Conservative low estimate (USD)
2. **high**: Optimistic high estimate (USD)
3. **recommended**: Your recommended listing price (USD)
4. **confidence**: Your confidence level (low/medium/high)
5. **notes**: Brief explanation of valuation factors
6. **comparable_sales**: 2-3 comparable recent sales if known
7. **market_demand**: Current market demand (cold/moderate/hot)
8. **investment_potential**: Long-term investment outlook

Respond ONLY with a valid JSON object."""

        images = product_data.get("images", [])[:3]
        response = self._call_anthropic(prompt, images, system_prompt)

        if response:
            try:
                cleaned = self._clean_json_response(response)
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                logger.debug(f"Raw response: {response[:500]}...")
                return {"notes": response, "error": "JSON parsing failed", "raw": cleaned}

        logger.warning("AI valuation generation returned no response")
        return None

    def analyze_images(
        self,
        image_paths: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze product images for details and suggested naming.

        Args:
            image_paths: List of image file paths

        Returns:
            Dictionary with analysis results
        """
        system_prompt = """You are an expert at analyzing antiques and collectibles photographs.
You identify key details, suggest descriptive filenames, and note important features.
Respond in valid JSON format only."""

        prompt = """Analyze these product images and provide:

1. **image_descriptions**: Array of descriptions for each image
2. **suggested_names**: Array of suggested descriptive filenames (e.g., "front-view", "makers-mark", "detail-engraving")
3. **key_features**: Notable features visible in the images
4. **condition_observations**: Any condition issues visible
5. **recommended_primary**: Index (0-based) of the best main product photo
6. **photography_suggestions**: Tips to improve the photos

Respond ONLY with a valid JSON object."""

        response = self._call_anthropic(prompt, image_paths, system_prompt)

        if response:
            try:
                cleaned = self._clean_json_response(response)
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                logger.debug(f"Raw response: {response[:500]}...")
                return {"raw_response": response, "error": "JSON parsing failed", "raw": cleaned}

        logger.warning("AI image analysis returned no response")
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

Include:
- Long-tail keywords
- Collector search terms
- Category-specific terms
- Era/period keywords
- Condition descriptors

Return ONLY a JSON array of keywords, no other text."""

        response = self._call_anthropic(prompt)

        if response:
            try:
                cleaned = self._clean_json_response(response)
                keywords = json.loads(cleaned)
                if isinstance(keywords, list):
                    return keywords[:count]
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {e}")
                logger.debug(f"Raw response: {response[:500]}...")
                pass

        return []
