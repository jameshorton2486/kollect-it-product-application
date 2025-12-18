#!/usr/bin/env python3
"""
Comprehensive Test Suite for Kollect-It Product Manager
Tests all modules and functionality
"""

import os
import sys
import json
import traceback
from pathlib import Path

# Add the desktop-app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Test results tracking
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_pass(name, details=""):
    results["passed"].append(name)
    print(f"  [PASS] {name}" + (f" - {details}" if details else ""))

def test_fail(name, error):
    results["failed"].append((name, str(error)))
    print(f"  [FAIL] {name} - {error}")

def test_warn(name, warning):
    results["warnings"].append((name, warning))
    print(f"  [WARN] {name} - {warning}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================
# TEST 1: Module Imports
# ============================================================
section("1. MODULE IMPORTS")

modules_to_test = [
    ("PyQt5.QtWidgets", "PyQt5 GUI Framework"),
    ("PyQt5.QtCore", "PyQt5 Core"),
    ("PyQt5.QtGui", "PyQt5 GUI"),
    ("PIL", "Pillow Image Processing"),
    ("requests", "HTTP Requests"),
    ("dotenv", "Environment Variables"),
    ("certifi", "SSL Certificates"),
]

for module, desc in modules_to_test:
    try:
        __import__(module)
        test_pass(desc)
    except ImportError as e:
        test_fail(desc, str(e))

# Test optional modules
optional_modules = [
    ("anthropic", "Anthropic SDK (optional)"),
    ("rembg", "Background Removal (optional)"),
    ("imagekitio", "ImageKit SDK (optional)"),
]

for module, desc in optional_modules:
    try:
        __import__(module)
        test_pass(desc)
    except ImportError:
        test_warn(desc, "Not installed - feature may be limited")


# ============================================================
# TEST 2: Application Modules
# ============================================================
section("2. APPLICATION MODULES")

app_modules = [
    ("modules.ai_engine", "AI Engine"),
    ("modules.image_processor", "Image Processor"),
    ("modules.background_remover", "Background Remover"),
    ("modules.crop_tool", "Crop Tool"),
    ("modules.imagekit_uploader", "ImageKit Uploader"),
    ("modules.config_validator", "Config Validator"),
    ("modules.env_loader", "Environment Loader"),
    ("modules.sku_scanner", "SKU Scanner"),
    ("modules.theme", "Theme Module"),
    ("modules.widgets", "Custom Widgets"),
    ("modules.workers", "Background Workers"),
    ("modules.app_logger", "App Logger"),
]

for module, desc in app_modules:
    try:
        __import__(module)
        test_pass(desc)
    except Exception as e:
        test_fail(desc, str(e))


# ============================================================
# TEST 3: Configuration Files
# ============================================================
section("3. CONFIGURATION FILES")

config_path = Path(__file__).parent / "config" / "config.json"
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
    test_pass("config.json loads")
    
    # Check required sections
    required_sections = ["app", "api", "imagekit", "categories", "image_processing", "paths", "ai"]
    for section_name in required_sections:
        if section_name in config:
            test_pass(f"Config section: {section_name}")
        else:
            test_fail(f"Config section: {section_name}", "Missing")
except Exception as e:
    test_fail("config.json", str(e))


# ============================================================
# TEST 4: Environment Variables
# ============================================================
section("4. ENVIRONMENT VARIABLES")

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    test_pass(".env file exists")
    
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    # Check for API keys
    env_vars = [
        ("ANTHROPIC_API_KEY", "Anthropic API Key"),
        ("IMAGEKIT_PRIVATE_KEY", "ImageKit Private Key"),
        ("IMAGEKIT_PUBLIC_KEY", "ImageKit Public Key"),
    ]
    
    for var, desc in env_vars:
        value = os.getenv(var)
        if value and len(value) > 10:
            # Mask the key for security
            masked = value[:8] + "..." + value[-4:]
            test_pass(f"{desc}: {masked}")
        elif value:
            test_warn(desc, "Set but seems too short")
        else:
            test_warn(desc, "Not set")
else:
    test_fail(".env file", "Does not exist - create from env.example.txt")


# ============================================================
# TEST 5: SSL/TLS Certificates
# ============================================================
section("5. SSL/TLS CERTIFICATES")

try:
    import certifi
    cert_path = certifi.where()
    if os.path.exists(cert_path):
        test_pass(f"Certifi path: {cert_path}")
    else:
        test_fail("Certifi", "Certificate file not found")
except Exception as e:
    test_fail("Certifi", str(e))

# Test HTTPS connectivity
try:
    import requests
    response = requests.get("https://api.anthropic.com", timeout=10)
    test_pass(f"HTTPS to api.anthropic.com (status: {response.status_code})")
except requests.exceptions.SSLError as e:
    test_fail("HTTPS SSL", str(e))
except Exception as e:
    test_warn("HTTPS connectivity", str(e))


# ============================================================
# TEST 6: AI Engine
# ============================================================
section("6. AI ENGINE")

try:
    from modules.ai_engine import AIEngine
    test_pass("AIEngine class imports")
    
    # Create instance with config
    ai = AIEngine(config)
    test_pass("AIEngine instance created")
    
    # Check API key
    if ai.api_key and len(ai.api_key) > 20:
        test_pass(f"API key loaded: {ai.api_key[:8]}...{ai.api_key[-4:]}")
    else:
        test_warn("API key", "Not loaded or too short")
    
    # Check model
    if hasattr(ai, 'model'):
        test_pass(f"Model configured: {ai.model}")
    
except Exception as e:
    test_fail("AI Engine", str(e))


# ============================================================
# TEST 7: Image Processor
# ============================================================
section("7. IMAGE PROCESSOR")

try:
    from modules.image_processor import ImageProcessor
    test_pass("ImageProcessor imports")
    
    processor = ImageProcessor(config)
    test_pass("ImageProcessor instance created")
    
    # Check methods exist
    methods = ['resize_image', 'optimize_image', 'convert_to_webp']
    for method in methods:
        if hasattr(processor, method):
            test_pass(f"Method: {method}()")
        else:
            test_warn(f"Method: {method}()", "Not found")
            
except Exception as e:
    test_fail("Image Processor", str(e))


# ============================================================
# TEST 8: Background Remover
# ============================================================
section("8. BACKGROUND REMOVER")

try:
    from modules.background_remover import BackgroundRemover
    test_pass("BackgroundRemover imports")
    
    remover = BackgroundRemover()
    test_pass("BackgroundRemover instance created")
    
    if hasattr(remover, 'remove_background'):
        test_pass("Method: remove_background()")
    
except ImportError as e:
    test_warn("Background Remover", f"rembg not installed: {e}")
except Exception as e:
    test_fail("Background Remover", str(e))


# ============================================================
# TEST 9: ImageKit Uploader
# ============================================================
section("9. IMAGEKIT UPLOADER")

try:
    from modules.imagekit_uploader import ImageKitUploader
    test_pass("ImageKitUploader imports")
    
    # Check if credentials are available
    private_key = os.getenv("IMAGEKIT_PRIVATE_KEY")
    public_key = os.getenv("IMAGEKIT_PUBLIC_KEY")
    
    if private_key and public_key:
        test_pass("ImageKit credentials available")
    else:
        test_warn("ImageKit credentials", "Not configured in .env")
        
except Exception as e:
    test_fail("ImageKit Uploader", str(e))


# ============================================================
# TEST 10: Crop Tool
# ============================================================
section("10. CROP TOOL")

try:
    from modules.crop_tool import CropDialog
    test_pass("CropDialog imports")
    
    # Can't instantiate without QApplication, but class exists
    if hasattr(CropDialog, '__init__'):
        test_pass("CropDialog class available")
        
except Exception as e:
    test_fail("Crop Tool", str(e))


# ============================================================
# TEST 11: Theme & Widgets
# ============================================================
section("11. THEME & WIDGETS")

try:
    from modules.theme import DarkPalette
    test_pass("DarkPalette class imports")
    
    stylesheet = DarkPalette.get_stylesheet()
    if len(stylesheet) > 100:
        test_pass(f"Theme stylesheet size: {len(stylesheet)} chars")
    else:
        test_warn("Theme", "Stylesheet seems too short")
        
except Exception as e:
    test_fail("Theme", str(e))

try:
    from modules.widgets import ImageThumbnail
    test_pass("ImageThumbnail widget imports")
except Exception as e:
    test_fail("Widgets", str(e))


# ============================================================
# TEST 12: Main Application
# ============================================================
section("12. MAIN APPLICATION")

try:
    # Import main module (but don't run the app)
    import importlib.util
    spec = importlib.util.spec_from_file_location("main", Path(__file__).parent / "main.py")
    main_module = importlib.util.module_from_spec(spec)
    
    # Check if we can at least parse the module
    import ast
    with open(Path(__file__).parent / "main.py", 'r', encoding='utf-8') as f:
        source = f.read()
    ast.parse(source)
    test_pass("main.py syntax valid")
    
    # Check for key classes
    if "class KollectItApp" in source:
        test_pass("KollectItApp class defined")
    if "class ImageThumbnail" in source:
        test_pass("ImageThumbnail class defined")
    if "def generate_description" in source:
        test_pass("generate_description() defined")
    if "def analyze_and_autofill" in source:
        test_pass("analyze_and_autofill() defined")
    if "ctrl_clicked" in source:
        test_pass("Multi-select (ctrl_clicked) implemented")
    if "delete_selected_images" in source:
        test_pass("delete_selected_images() implemented")
    if "select_all_images" in source:
        test_pass("select_all_images() (Ctrl+A) implemented")
        
except SyntaxError as e:
    test_fail("main.py syntax", str(e))
except Exception as e:
    test_fail("Main Application", str(e))


# ============================================================
# TEST 13: SKU Scanner
# ============================================================
section("13. SKU SCANNER")

try:
    from modules.sku_scanner import SKUScanner
    test_pass("SKUScanner imports")
    
    # Get products_root and categories from config
    products_root = config.get("paths", {}).get("products_root", "./products")
    categories = config.get("categories", {})
    
    scanner = SKUScanner(products_root, categories)
    test_pass("SKUScanner instance created")
    
    if hasattr(scanner, 'generate_sku'):
        test_pass("Method: generate_sku()")
        
except Exception as e:
    test_fail("SKU Scanner", str(e))


# ============================================================
# TEST 14: Templates
# ============================================================
section("14. CATEGORY TEMPLATES")

templates_dir = Path(__file__).parent / "templates"
if templates_dir.exists():
    templates = list(templates_dir.glob("*.json"))
    test_pass(f"Templates directory exists ({len(templates)} templates)")
    
    for template in templates:
        try:
            with open(template, 'r') as f:
                data = json.load(f)
            test_pass(f"Template: {template.name}")
        except Exception as e:
            test_fail(f"Template: {template.name}", str(e))
else:
    test_warn("Templates", "Directory not found")


# ============================================================
# SUMMARY
# ============================================================
section("TEST SUMMARY")

total = len(results["passed"]) + len(results["failed"]) + len(results["warnings"])
print(f"\n  Total Tests: {total}")
print(f"  Passed:      {len(results['passed'])} ({100*len(results['passed'])//total}%)")
print(f"  Failed:      {len(results['failed'])}")
print(f"  Warnings:    {len(results['warnings'])}")

if results["failed"]:
    print(f"\n  FAILED TESTS:")
    for name, error in results["failed"]:
        print(f"    - {name}: {error}")

if results["warnings"]:
    print(f"\n  WARNINGS:")
    for name, warning in results["warnings"]:
        print(f"    - {name}: {warning}")

print(f"\n{'='*60}")
if not results["failed"]:
    print("  ALL CRITICAL TESTS PASSED!")
else:
    print(f"  {len(results['failed'])} TESTS FAILED - Review above")
print(f"{'='*60}\n")

# Exit with appropriate code
sys.exit(0 if not results["failed"] else 1)

