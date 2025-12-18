"""
Kollect-It Product Manager - Application Logger
Comprehensive logging with file and console output.
"""

import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime
from functools import wraps
from typing import Callable, Any

# Create logs directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file with timestamp
LOG_FILE = LOG_DIR / f"kollect_it_{datetime.now().strftime('%Y%m%d')}.log"


class ColorFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(name: str = "KollectIt") -> logging.Logger:
    """Set up and return a configured logger."""
    
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_format = ColorFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (detailed)
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()


def log_function_call(func: Callable) -> Callable:
    """Decorator to log function entry, exit, and exceptions."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        class_name = ""
        
        # Get class name if it's a method
        if args and hasattr(args[0], '__class__'):
            class_name = args[0].__class__.__name__ + "."
        
        full_name = f"{class_name}{func_name}"
        
        # Log entry
        logger.debug(f"→ ENTER: {full_name}()")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"← EXIT: {full_name}() - Success")
            return result
        except Exception as e:
            logger.error(f"✗ ERROR in {full_name}(): {type(e).__name__}: {e}")
            logger.debug(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    return wrapper


def log_exception(e: Exception, context: str = ""):
    """Log an exception with full traceback."""
    prefix = f"[{context}] " if context else ""
    logger.error(f"{prefix}{type(e).__name__}: {e}")
    logger.debug(f"Full traceback:\n{traceback.format_exc()}")


def log_startup_info():
    """Log application startup information."""
    logger.info("=" * 60)
    logger.info("KOLLECT-IT PRODUCT MANAGER - STARTING")
    logger.info("=" * 60)
    logger.info(f"Log file: {LOG_FILE}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    

def log_config_status(config: dict):
    """Log configuration status."""
    logger.info("-" * 40)
    logger.info("CONFIGURATION STATUS:")
    
    # Check API keys (without revealing them)
    api_key = config.get("api", {}).get("SERVICE_API_KEY", "")
    logger.info(f"  SERVICE_API_KEY: {'✓ Set' if api_key and api_key != 'YOUR_SERVICE_API_KEY_HERE' else '✗ Not configured'}")
    
    ik_public = config.get("imagekit", {}).get("public_key", "")
    ik_private = config.get("imagekit", {}).get("private_key", "")
    logger.info(f"  ImageKit Public Key: {'✓ Set' if ik_public else '✗ Not configured'}")
    logger.info(f"  ImageKit Private Key: {'✓ Set' if ik_private else '✗ Not configured'}")
    
    import os
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    logger.info(f"  ANTHROPIC_API_KEY: {'✓ Set in environment' if anthropic_key else '✗ Not set'}")
    
    # Check paths
    products_root = config.get("paths", {}).get("products_root", "")
    logger.info(f"  Products root: {products_root}")
    logger.info(f"  Products root exists: {Path(products_root).exists() if products_root else False}")
    
    # Categories
    categories = config.get("categories", {})
    logger.info(f"  Categories configured: {len(categories)}")
    for cat_id, cat_info in categories.items():
        logger.debug(f"    - {cat_id}: prefix={cat_info.get('prefix', 'N/A')}")
    
    logger.info("-" * 40)


def log_module_import(module_name: str, success: bool, error: str = ""):
    """Log module import status."""
    if success:
        logger.debug(f"  ✓ Imported: {module_name}")
    else:
        logger.error(f"  ✗ Failed to import: {module_name} - {error}")


def log_ui_action(action: str, details: str = ""):
    """Log user interface actions."""
    msg = f"UI: {action}"
    if details:
        msg += f" - {details}"
    logger.info(msg)


def log_processing(step: str, item: str = "", status: str = ""):
    """Log processing steps."""
    msg = f"PROCESS: {step}"
    if item:
        msg += f" [{item}]"
    if status:
        msg += f" - {status}"
    logger.info(msg)


def log_api_call(service: str, endpoint: str, status: str = ""):
    """Log API calls."""
    msg = f"API: {service} → {endpoint}"
    if status:
        msg += f" - {status}"
    logger.info(msg)


# Print wrapper for easy debugging
def debug_print(message: str, category: str = "DEBUG"):
    """Print debug message to console and log."""
    print(f"[{category}] {message}")
    logger.debug(f"[{category}] {message}")
