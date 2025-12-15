#!/usr/bin/env python3
"""
Environment Variable Loader
Loads sensitive API keys from .env file and merges with config.json
"""

import os
from pathlib import Path
from typing import Dict, Any

# Try to load python-dotenv if available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def load_env_file(env_path: Path = None) -> Dict[str, str]:
    """
    Load environment variables from .env file.

    Args:
        env_path: Path to .env file (defaults to desktop-app/.env)

    Returns:
        Dictionary of environment variables
    """
    if env_path is None:
        env_path = Path(__file__).parent.parent / ".env"

    env_vars = {}

    if not env_path.exists():
        return env_vars

    # Use python-dotenv if available
    if DOTENV_AVAILABLE:
        load_dotenv(env_path, override=True)
        # Read all relevant env vars
        env_vars = {
            "SERVICE_API_KEY": os.getenv("SERVICE_API_KEY", ""),
            "IMAGEKIT_PUBLIC_KEY": os.getenv("IMAGEKIT_PUBLIC_KEY", ""),
            "IMAGEKIT_PRIVATE_KEY": os.getenv("IMAGEKIT_PRIVATE_KEY", ""),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
            "STRIPE_PUBLISHABLE_KEY": os.getenv("STRIPE_PUBLISHABLE_KEY", ""),
            "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY", ""),
            "USE_PRODUCTION": os.getenv("USE_PRODUCTION", ""),
            "AI_TEMPERATURE": os.getenv("AI_TEMPERATURE", ""),
        }
    else:
        # Fallback: manual parsing
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    env_vars[key] = value

    return env_vars


def merge_env_into_config(config: Dict[str, Any], env_vars: Dict[str, str]) -> Dict[str, Any]:
    """
    Merge environment variables into config dictionary.

    Environment variables override config.json values for sensitive keys.

    Args:
        config: Configuration dictionary from config.json
        env_vars: Environment variables from .env file

    Returns:
        Merged configuration dictionary
    """
    # Create a deep copy to avoid modifying original
    merged = config.copy()

    # Merge API keys
    if "api" not in merged:
        merged["api"] = {}

    if env_vars.get("SERVICE_API_KEY"):
        merged["api"]["SERVICE_API_KEY"] = env_vars["SERVICE_API_KEY"]

    if env_vars.get("USE_PRODUCTION"):
        use_prod = env_vars["USE_PRODUCTION"].lower() in ("true", "1", "yes")
        merged["api"]["use_production"] = use_prod
        merged["api"]["use_local"] = not use_prod

    # Merge ImageKit keys
    if "imagekit" not in merged:
        merged["imagekit"] = {}

    if env_vars.get("IMAGEKIT_PUBLIC_KEY"):
        merged["imagekit"]["public_key"] = env_vars["IMAGEKIT_PUBLIC_KEY"]

    if env_vars.get("IMAGEKIT_PRIVATE_KEY"):
        merged["imagekit"]["private_key"] = env_vars["IMAGEKIT_PRIVATE_KEY"]

    # Merge Stripe keys
    if "stripe" not in merged:
        merged["stripe"] = {}

    if env_vars.get("STRIPE_PUBLISHABLE_KEY"):
        merged["stripe"]["publishable_key"] = env_vars["STRIPE_PUBLISHABLE_KEY"]

    if env_vars.get("STRIPE_SECRET_KEY"):
        merged["stripe"]["secret_key"] = env_vars["STRIPE_SECRET_KEY"]

    # Merge AI keys
    if "ai" not in merged:
        merged["ai"] = {}

    # ANTHROPIC_API_KEY is read directly from environment, not stored in config
    # This ensures single source of truth for the API key

    if env_vars.get("AI_TEMPERATURE"):
        try:
            merged["ai"]["temperature"] = float(env_vars["AI_TEMPERATURE"])
        except ValueError:
            pass  # Keep existing value if invalid

    return merged


def load_config_with_env(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from config.json and merge with .env file.

    Args:
        config_path: Path to config.json file

    Returns:
        Merged configuration dictionary
    """
    import json

    # Load base config from JSON
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Load environment variables
    env_path = config_path.parent.parent / ".env"
    env_vars = load_env_file(env_path)

    # Merge env vars into config (env vars take precedence)
    if env_vars:
        config = merge_env_into_config(config, env_vars)

    return config
