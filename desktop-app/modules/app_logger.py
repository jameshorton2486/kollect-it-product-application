"""
Kollect-It Product Manager - Enhanced Application Logger
Comprehensive logging with file and console output, decorators, and utilities.
"""

import logging
import sys
import os
import traceback
import time
from pathlib import Path
from datetime import datetime
from functools import wraps
from typing import Callable, Any, Optional
from contextlib import contextmanager

# ============================================
# CONFIGURATION
# ============================================

# Create logs directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file with timestamp
LOG_FILE = LOG_DIR / f"kollect_it_{datetime.now().strftime('%Y%m%d')}.log"
DEBUG_LOG_FILE = LOG_DIR / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Enable/disable verbose debugging
VERBOSE_DEBUG = os.getenv("KOLLECTIT_DEBUG", "0") == "1"


# ============================================
# COLOR FORMATTER FOR CONSOLE
# ============================================

class ColorFormatter(logging.Formatter):
    """Custom formatter with colors for console output (ASCII-safe for Windows)."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
        # Skip color codes on Windows to avoid encoding issues
        if sys.platform == 'win32':
            return super().format(record)
        
        color = self.COLORS.get(record.levelname, self.RESET)
        original_levelname = record.levelname
        record.levelname = f"{color}{record.levelname:8}{self.RESET}"
        result = super().format(record)
        record.levelname = original_levelname
        return result


# ============================================
# LOGGER SETUP
# ============================================

def setup_logger(name: str = "KollectIt", level: int = logging.DEBUG) -> logging.Logger:
    """Set up and return a configured logger with console and file handlers."""
    
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    logger.propagate = False
    
    # Console handler (ASCII-safe for Windows)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO if not VERBOSE_DEBUG else logging.DEBUG)
    console_format = ColorFormatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (detailed, UTF-8 for file)
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s.%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()


# ============================================
# DECORATORS
# ============================================

def log_function_call(func: Callable) -> Callable:
    """Decorator to log function entry, exit, duration, and exceptions."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        class_name = ""
        
        # Get class name if it's a method
        if args and hasattr(args[0], '__class__'):
            class_name = args[0].__class__.__name__ + "."
        
        full_name = f"{class_name}{func_name}"
        start_time = time.time()
        
        # Log entry with arguments (sanitized)
        arg_summary = _summarize_args(args[1:] if class_name else args, kwargs)
        logger.debug(f"→ {full_name}({arg_summary})")
        
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000  # ms
            logger.debug(f"← {full_name}() completed in {duration:.1f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"✗ {full_name}() FAILED after {duration:.1f}ms: {type(e).__name__}: {e}")
            logger.debug(f"Traceback:\n{traceback.format_exc()}")
            raise
    
    return wrapper


def log_exceptions(context: str = ""):
    """Decorator to catch and log exceptions without stopping execution."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ctx = context or func.__name__
                logger.error(f"Exception in {ctx}: {type(e).__name__}: {e}")
                logger.debug(traceback.format_exc())
                return None
        return wrapper
    return decorator


def timed(func: Callable) -> Callable:
    """Decorator to measure and log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = (time.time() - start) * 1000
        logger.info(f"⏱ {func.__name__}() took {duration:.1f}ms")
        return result
    return wrapper


# ============================================
# CONTEXT MANAGERS
# ============================================

@contextmanager
def log_operation(operation_name: str, details: str = ""):
    """Context manager to log the start and end of an operation."""
    start_time = time.time()
    msg = f">> Starting: {operation_name}"
    if details:
        msg += f" - {details}"
    logger.info(msg)
    print(f"[START] {operation_name}")
    
    try:
        yield
        duration = (time.time() - start_time) * 1000
        logger.info(f"[OK] Completed: {operation_name} ({duration:.1f}ms)")
        print(f"[DONE] {operation_name} ({duration:.1f}ms)")
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(f"[FAIL] Failed: {operation_name} ({duration:.1f}ms) - {e}")
        print(f"[ERROR] {operation_name}: {e}")
        raise


# ============================================
# UTILITY FUNCTIONS
# ============================================

def _summarize_args(args, kwargs, max_len: int = 50) -> str:
    """Create a summary of function arguments for logging."""
    parts = []
    
    for arg in args:
        if isinstance(arg, str):
            val = arg if len(arg) <= max_len else f"{arg[:max_len]}..."
            parts.append(f'"{val}"')
        elif isinstance(arg, (int, float, bool)):
            parts.append(str(arg))
        elif isinstance(arg, (list, tuple)):
            parts.append(f"[{len(arg)} items]")
        elif isinstance(arg, dict):
            parts.append(f"{{{len(arg)} keys}}")
        elif arg is None:
            parts.append("None")
        else:
            parts.append(f"<{type(arg).__name__}>")
    
    for key, val in kwargs.items():
        if isinstance(val, str):
            val_str = val if len(val) <= 20 else f"{val[:20]}..."
            parts.append(f'{key}="{val_str}"')
        else:
            parts.append(f'{key}=...')
    
    return ", ".join(parts) if parts else ""


def log_exception(e: Exception, context: str = "", include_traceback: bool = True):
    """Log an exception with optional context and traceback."""
    prefix = f"[{context}] " if context else ""
    logger.error(f"{prefix}{type(e).__name__}: {e}")
    if include_traceback:
        logger.debug(f"Full traceback:\n{traceback.format_exc()}")
    print(f"[ERROR] {prefix}{type(e).__name__}: {e}")


def log_startup_info(version: str = "1.0.0"):
    """Log application startup information."""
    logger.info("=" * 60)
    logger.info("KOLLECT-IT PRODUCT MANAGER - STARTING")
    logger.info("=" * 60)
    logger.info(f"Version: {version}")
    logger.info(f"Log file: {LOG_FILE}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Working directory: {os.getcwd()}")
    print(f"\n{'='*60}")
    print(f"  KOLLECT-IT PRODUCT MANAGER v{version}")
    print(f"  Log: {LOG_FILE}")
    print(f"{'='*60}\n")


def log_config_status(config: dict):
    """Log configuration status with detailed checks."""
    logger.info("-" * 40)
    logger.info("CONFIGURATION STATUS:")
    print("\n[CONFIG] Checking configuration...")
    
    # Check API keys (without revealing them)
    api_key = config.get("api", {}).get("SERVICE_API_KEY", "")
    status = '[OK]' if api_key and api_key != 'YOUR_SERVICE_API_KEY_HERE' else '[X]'
    logger.info(f"  SERVICE_API_KEY: {status}")
    print(f"  - SERVICE_API_KEY: {status}")
    
    ik_public = config.get("imagekit", {}).get("public_key", "")
    ik_private = config.get("imagekit", {}).get("private_key", "")
    logger.info(f"  ImageKit Public Key: {'[OK]' if ik_public else '[X]'}")
    logger.info(f"  ImageKit Private Key: {'[OK]' if ik_private else '[X]'}")
    print(f"  - ImageKit: {'[OK] Configured' if ik_public and ik_private else '[X] Not configured'}")
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    status = '[OK]' if anthropic_key else '[X]'
    logger.info(f"  ANTHROPIC_API_KEY: {status}")
    print(f"  - ANTHROPIC_API_KEY: {status}")
    
    # Check paths
    products_root = config.get("paths", {}).get("products_root", "")
    exists = Path(products_root).exists() if products_root else False
    logger.info(f"  Products root: {products_root}")
    logger.info(f"  Products root exists: {exists}")
    print(f"  - Products root: {products_root} {'[OK]' if exists else '[X]'}")
    
    # Categories
    categories = config.get("categories", {})
    logger.info(f"  Categories: {len(categories)}")
    print(f"  - Categories: {len(categories)}")
    
    logger.info("-" * 40)
    print()


def log_module_import(module_name: str, success: bool, error: str = ""):
    """Log module import status."""
    if success:
        logger.debug(f"  ✓ Imported: {module_name}")
    else:
        logger.error(f"  ✗ Failed to import: {module_name} - {error}")
        print(f"[ERROR] Failed to import {module_name}: {error}")


def log_ui_action(action: str, details: str = ""):
    """Log user interface actions."""
    msg = f"UI: {action}"
    if details:
        msg += f" - {details}"
    logger.info(msg)
    print(f"[UI] {action}" + (f" - {details}" if details else ""))


def log_processing(step: str, item: str = "", status: str = "progress"):
    """Log processing steps with status indicators (ASCII-safe)."""
    status_icons = {
        "start": ">>",
        "progress": "*",
        "success": "[OK]",
        "warning": "[!]",
        "error": "[X]",
        "complete": "[OK]"
    }
    icon = status_icons.get(status, "-")
    msg = f"{icon} {step}"
    if item:
        msg += f": {item}"
    logger.info(msg)
    print(f"[PROCESS] {msg}")


def log_api_call(service: str, endpoint: str, method: str = "POST", status_code: int = None):
    """Log API calls with details."""
    msg = f"API: {method} {service}/{endpoint}"
    if status_code:
        status_icon = "[OK]" if 200 <= status_code < 300 else "[X]"
        msg += f" -> {status_code} {status_icon}"
    logger.info(msg)
    print(f"[API] {msg}")


def log_image_operation(operation: str, image_path: str, result: str = ""):
    """Log image processing operations."""
    filename = Path(image_path).name if image_path else "unknown"
    msg = f"IMAGE: {operation} - {filename}"
    if result:
        msg += f" → {result}"
    logger.info(msg)


def log_validation(field: str, valid: bool, message: str = ""):
    """Log validation results."""
    status = "✓ Valid" if valid else "✗ Invalid"
    msg = f"VALIDATE: {field} - {status}"
    if message:
        msg += f" ({message})"
    if valid:
        logger.debug(msg)
    else:
        logger.warning(msg)
        print(f"[VALIDATION] {msg}")


# ============================================
# PRINT HELPERS (for debugging)
# ============================================

def debug_print(message: str, category: str = "DEBUG"):
    """Print debug message to console and log."""
    print(f"[{category}] {message}")
    logger.debug(f"[{category}] {message}")


def info_print(message: str):
    """Print info message to console and log."""
    print(f"[INFO] {message}")
    logger.info(message)


def error_print(message: str, exception: Exception = None):
    """Print error message to console and log."""
    print(f"[ERROR] {message}")
    logger.error(message)
    if exception:
        logger.debug(traceback.format_exc())


def success_print(message: str):
    """Print success message to console and log."""
    print(f"[SUCCESS] {message}")
    logger.info(f"[OK] {message}")


def warning_print(message: str):
    """Print warning message to console and log."""
    print(f"[WARNING] {message}")
    logger.warning(message)


# ============================================
# ERROR HANDLING HELPERS
# ============================================

class AppError(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, context: str = "", original: Exception = None):
        self.message = message
        self.context = context
        self.original = original
        super().__init__(message)
        
        # Auto-log when created
        log_exception(self, context)


class ConfigError(AppError):
    """Configuration-related errors."""
    pass


class APIError(AppError):
    """API-related errors."""
    pass


class ImageProcessingError(AppError):
    """Image processing errors."""
    pass


class ValidationError(AppError):
    """Validation errors."""
    pass


def safe_execute(func: Callable, *args, default=None, context: str = "", **kwargs):
    """Safely execute a function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_exception(e, context or func.__name__)
        return default


# ============================================
# SESSION LOG
# ============================================

def log_session_summary(stats: dict):
    """Log end-of-session summary."""
    logger.info("=" * 60)
    logger.info("SESSION SUMMARY")
    logger.info("=" * 60)
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    logger.info("=" * 60)
    
    print("\n" + "=" * 40)
    print("SESSION SUMMARY")
    print("=" * 40)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("=" * 40 + "\n")
