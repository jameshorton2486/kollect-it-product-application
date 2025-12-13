# Cursor AI Prompt: Fix All Issues in Kollect-It Product Application

## Project Context

You are working on the **Kollect-It Product Application**, a PyQt5 desktop application for processing and publishing antiques/collectibles listings. The application includes:

- **Desktop App**: PyQt5 GUI with dark theme for manual product processing
- **Background Worker**: Automated folder monitoring and processing
- **Next.js API**: Backend endpoint for product creation
- **Modules**: Image processing, AI generation, ImageKit CDN upload, SKU generation

**Tech Stack:**
- Python 3.x with PyQt5
- Pillow for image processing
- Anthropic Claude API for AI descriptions
- ImageKit for CDN storage
- Next.js with Prisma for backend

---

## CRITICAL FIXES (Do These First)

### Issue #1: Missing `defaults` Configuration Section

**File:** `desktop-app/config/config.example.json`

**Problem:** The code in `main.py` line 678 references `self.config.get("defaults", {}).get("condition_grades", [])` but the config file has no `defaults` section. This causes the Condition dropdown to be empty.

**Fix:** Add the `defaults` section to the config file. Insert this after the `"categories"` section:

```json
"defaults": {
  "condition_grades": [
    "Mint",
    "Excellent",
    "Very Good",
    "Good",
    "Fair",
    "Poor",
    "As-Is"
  ],
  "default_category": "collectibles",
  "default_status": "draft"
},
```

---

### Issue #2: Browse Folder Default Path Not Set

**File:** `desktop-app/main.py`
**Lines:** 408-414

**Problem:** The `browse_folder` method uses an empty string as the default path, forcing users to navigate from system root every time.

**Current Code:**
```python
def browse_folder(self):
    folder = QFileDialog.getExistingDirectory(
        self, "Select Product Folder",
        "", QFileDialog.ShowDirsOnly
    )
    if folder:
        self.folder_dropped.emit(folder)
```

**Fix:** Replace with:
```python
def browse_folder(self):
    # Get default path from config, fallback to user's home directory
    default_path = ""
    if hasattr(self, 'config'):
        default_path = self.config.get("paths", {}).get("default_browse", "")
    if not default_path:
        default_path = str(Path.home())
    
    folder = QFileDialog.getExistingDirectory(
        self, "Select Product Folder",
        default_path, QFileDialog.ShowDirsOnly
    )
    if folder:
        self.folder_dropped.emit(folder)
```

**Also add to `config.example.json`** in the `paths` section:
```json
"paths": {
  "default_browse": "G:\\My Drive\\Kollect-It\\Products",
  "watch_folder": "G:\\My Drive\\Kollect-It\\New Products",
  "processed": "./processed",
  "completed": "G:\\My Drive\\Kollect-It\\Completed",
  "failed": "G:\\My Drive\\Kollect-It\\Failed",
  "temp": "./temp",
  "logs": "./logs"
},
```

---

### Issue #3: Product Publisher URL Construction Error

**File:** `desktop-app/modules/product_publisher.py`
**Lines:** 20-33

**Problem:** The code checks `use_production` but the config uses `use_local`. The variable name mismatch causes the config option to be ignored.

**Current Code:**
```python
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
```

**Fix:** Replace with:
```python
def __init__(self, config: dict):
    self.config = config
    api_config = config.get("api", {})
    
    self.api_key = api_config.get("SERVICE_API_KEY", "")
    self.use_local = api_config.get("use_local", False)
    
    # Build base URL from config
    if self.use_local:
        base = api_config.get("local_url", "http://localhost:3000")
    else:
        base = api_config.get("production_url", "https://kollect-it.com")
    
    # Ensure no trailing slash and append endpoint
    self.base_url = f"{base.rstrip('/')}/api/admin/products/service-create"
    
    self.timeout = api_config.get("timeout", 30)
    self.max_retries = api_config.get("max_retries", 3)
```

**Also update line 122** to use `self.max_retries` instead of `self.retry_attempts`:
```python
for attempt in range(self.max_retries):
```

---

## HIGH PRIORITY FIXES

### Issue #4: Uninitialized `uploaded_image_urls` Attribute

**File:** `desktop-app/main.py`
**Lines:** 529-534 (in `__init__` method of `KollectItApp` class)

**Problem:** The `uploaded_image_urls` attribute is not initialized, causing potential issues when publishing.

**Current Code:**
```python
def __init__(self):
    super().__init__()
    self.config = self.load_config()
    self.current_folder = None
    self.current_images = []
    self.processing_thread = None
```

**Fix:** Add the missing attribute:
```python
def __init__(self):
    super().__init__()
    self.config = self.load_config()
    self.current_folder = None
    self.current_images = []
    self.uploaded_image_urls = []  # Store URLs after ImageKit upload
    self.processing_thread = None
```

---

### Issue #5: Missing Error Handling for Config File

**File:** `desktop-app/main.py`
**Lines:** 541-547

**Problem:** If `config.json` doesn't exist or is malformed, the app returns an empty dict and may crash later with confusing errors.

**Current Code:**
```python
def load_config(self) -> dict:
    """Load configuration from config.json."""
    config_path = Path(__file__).parent / "config" / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}
```

**Fix:** Replace with comprehensive error handling:
```python
def load_config(self) -> dict:
    """Load configuration from config.json with validation."""
    config_path = Path(__file__).parent / "config" / "config.json"
    example_path = Path(__file__).parent / "config" / "config.example.json"
    
    # Check if config exists
    if not config_path.exists():
        error_msg = (
            "Configuration file not found!\n\n"
            f"Expected: {config_path}\n\n"
            "Please copy config.example.json to config.json and configure your API keys:\n"
            "1. Copy config/config.example.json to config/config.json\n"
            "2. Add your SERVICE_API_KEY\n"
            "3. Add your ImageKit credentials\n"
            "4. Add your Anthropic API key"
        )
        QMessageBox.critical(None, "Configuration Error", error_msg)
        sys.exit(1)
    
    # Try to parse config
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        QMessageBox.critical(
            None, "Configuration Error",
            f"Invalid JSON in config.json:\n\n{e}\n\nPlease fix the syntax error."
        )
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(
            None, "Configuration Error",
            f"Error reading config.json:\n\n{e}"
        )
        sys.exit(1)
    
    # Validate required sections
    required_sections = ["api", "imagekit", "categories", "image_processing"]
    missing = [s for s in required_sections if s not in config]
    
    if missing:
        QMessageBox.warning(
            None, "Configuration Warning",
            f"Missing configuration sections: {', '.join(missing)}\n\n"
            "Some features may not work correctly."
        )
    
    # Validate API keys are not placeholder values
    api_key = config.get("api", {}).get("SERVICE_API_KEY", "")
    if not api_key or api_key == "YOUR_SERVICE_API_KEY_HERE":
        QMessageBox.warning(
            None, "Configuration Warning",
            "SERVICE_API_KEY is not configured.\n\n"
            "Publishing to the website will not work until you add your API key."
        )
    
    return config
```

---

### Issue #6: ImageKit Upload Returns Dict but Code Expects URL String

**File:** `desktop-app/main.py`
**Lines:** 1239-1276 (the `upload_to_imagekit` method)

**Problem:** The ImageKit uploader returns a dict `{"success": True, "url": "..."}` but the code appends the entire dict to `uploaded_urls` instead of extracting the URL string.

**Current Code (around line 1258-1261):**
```python
for i, img_path in enumerate(self.current_images):
    result = uploader.upload(img_path, folder)
    if result:
        uploaded_urls.append(result)
```

**Fix:** Replace with:
```python
for i, img_path in enumerate(self.current_images):
    result = uploader.upload(img_path, folder)
    if result and result.get("success"):
        url = result.get("url")
        if url:
            uploaded_urls.append(url)
            self.log(f"Uploaded: {Path(img_path).name} → {url}", "info")
        else:
            self.log(f"Upload returned no URL for {Path(img_path).name}", "warning")
    else:
        error_msg = result.get("error", "Unknown error") if result else "No response"
        self.log(f"Failed to upload {Path(img_path).name}: {error_msg}", "error")
    
    progress = int(((i + 1) / total) * 100)
    self.progress_bar.setValue(progress)
    self.status_label.setText(f"Uploading {i + 1}/{total}...")
    QApplication.processEvents()  # Keep UI responsive
```

**Also add at the top of main.py** (if not already present):
```python
from PyQt5.QtWidgets import QApplication
```

---

### Issue #7: Undefined Variable in Product Publisher Retry Loop

**File:** `desktop-app/modules/product_publisher.py`
**Lines:** 119-179 (the `publish` method)

**Problem:** The code references `response.status_code` after the try/except block, but `response` may not exist if an exception occurred before assignment.

**Find this section (around line 170-173):**
```python
except requests.exceptions.RequestException as e:
    last_error = str(e)

# Don't retry on authentication or validation errors
if response.status_code in (401, 400, 409):
    break
```

**Fix:** Replace the entire retry loop with proper response handling:
```python
# Attempt publish with retries
last_error = None
response = None

for attempt in range(self.max_retries):
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
    if response is not None and response.status_code in (401, 400, 409):
        break
    
    # Wait before retry (exponential backoff)
    if attempt < self.max_retries - 1:
        import time
        time.sleep(2 ** attempt)

return {
    "success": False,
    "error": "Publishing failed",
    "message": last_error or "Unknown error after all retries"
}
```

---

## MEDIUM PRIORITY FIXES

### Issue #8: Category Combo Data Not Properly Set

**File:** `desktop-app/main.py`

**Problem:** When populating the category combo box, the data (category ID) may not be properly set, causing `currentData()` to return None.

**Find where categories are added to the combo box** (search for `category_combo.addItem`) and ensure it follows this pattern:

```python
# Clear existing items
self.category_combo.clear()

# Add categories from config with proper data
for cat_id, cat_info in self.config.get("categories", {}).items():
    display_name = cat_info.get("name", cat_id.title())
    # addItem(display_text, user_data) - the second param is returned by currentData()
    self.category_combo.addItem(display_name, cat_id)

# Set default selection
default_cat = self.config.get("defaults", {}).get("default_category", "collectibles")
index = self.category_combo.findData(default_cat)
if index >= 0:
    self.category_combo.setCurrentIndex(index)
```

**Also update the config.example.json categories** to include display names:
```json
"categories": {
  "militaria": {
    "name": "Militaria",
    "prefix": "MILI",
    "keywords": ["military", "war", "army", "navy", "air force", "marines", "wwii", "ww2", "ww1", "wwi", "civil war", "vietnam", "korea", "uniform", "medal", "badge", "insignia", "helmet", "weapon"],
    "subcategories": ["Uniforms & Clothing", "Medals & Decorations", "Headgear", "Equipment & Gear", "Edged Weapons", "Documents & Photos", "Flags & Banners", "Aviation", "Naval"]
  },
  "collectibles": {
    "name": "Collectibles",
    "prefix": "COLL",
    "keywords": ["vintage", "antique", "collectible", "retro", "classic", "rare", "advertising", "sign", "toy", "game"],
    "subcategories": ["Advertising", "Toys & Games", "Ephemera", "Memorabilia", "Kitchenware", "Tobacciana", "Breweriana", "Petroliana", "Sports"]
  },
  "books": {
    "name": "Books & Manuscripts",
    "prefix": "BOOK",
    "keywords": ["book", "books", "manuscript", "first edition", "signed", "rare book", "antique book", "leather bound", "map", "atlas", "print"],
    "subcategories": ["First Editions", "Signed Copies", "Manuscripts", "Maps & Atlases", "Antique Books", "Children's Books", "Art Books", "History", "Literature"]
  },
  "fineart": {
    "name": "Fine Art",
    "prefix": "ART",
    "keywords": ["art", "painting", "sculpture", "print", "lithograph", "etching", "watercolor", "oil painting", "drawing", "sketch", "portrait", "landscape"],
    "subcategories": ["Oil Paintings", "Watercolors", "Prints & Lithographs", "Drawings", "Sculpture", "Photography", "Mixed Media", "Folk Art", "Decorative Arts"]
  }
},
```

---

### Issue #9: SKU State File Should Be Gitignored

**File:** `desktop-app/.gitignore`

**Problem:** The `sku_state.json` file stores incrementing counters and should not be committed to version control.

**Add these lines to `.gitignore`:**
```gitignore
# Configuration files with secrets
config/config.json

# SKU state (auto-generated, machine-specific)
config/sku_state.json

# Processed files
processed/
temp/
logs/

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp
```

---

### Issue #10: Inconsistent Path Separators in Config

**File:** `desktop-app/config/config.example.json`

**Problem:** Uses Unix-style paths (`~/Google Drive/`) which don't work on Windows.

**Fix:** Update the paths section to use Windows-compatible paths (forward slashes work in Python on all platforms):

```json
"paths": {
  "default_browse": "G:/My Drive/Kollect-It/Products",
  "watch_folder": "G:/My Drive/Kollect-It/New Products",
  "processed": "./processed",
  "completed": "G:/My Drive/Kollect-It/Completed",
  "failed": "G:/My Drive/Kollect-It/Failed",
  "temp": "./temp",
  "logs": "./logs"
},
```

**Note:** Forward slashes (`/`) work on both Windows and Unix in Python. Alternatively, document that users should update paths for their system.

---

### Issue #11: AI Engine JSON Parsing Edge Cases

**File:** `desktop-app/modules/ai_engine.py`
**Lines:** 231-246, 294-305, 339-350, 386-400

**Problem:** The JSON cleanup logic may fail on edge cases when Claude returns malformed responses.

**Find all instances of this pattern:**
```python
cleaned = response.strip()
if cleaned.startswith("```"):
    cleaned = cleaned.split("```")[1]
    if cleaned.startswith("json"):
        cleaned = cleaned[4:]
cleaned = cleaned.strip()
```

**Replace each instance with this more robust version:**
```python
import re

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
```

**Then update each call site to use:**
```python
cleaned = self._clean_json_response(response)
try:
    return json.loads(cleaned)
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    print(f"Raw response: {response[:500]}...")
    return {"description": response, "error": "JSON parsing failed", "raw": cleaned}
```

---

## LOW PRIORITY FIXES

### Issue #12: Add Proper Logging Framework

**File:** Create new file `desktop-app/modules/logger.py`

```python
#!/usr/bin/env python3
"""
Logging configuration for Kollect-It application.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "kollectit", log_dir: str = "./logs") -> logging.Logger:
    """
    Set up application logger with file and console handlers.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        
    Returns:
        Configured logger instance
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler - detailed logs
    log_file = log_path / f"kollectit_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s.%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Console handler - info and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(levelname)-8s | %(message)s'
    )
    console_handler.setFormatter(console_format)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
logger = setup_logger()
```

**Then in each module**, replace `print()` statements with logger calls:

```python
# At top of file
from modules.logger import logger

# Replace print statements:
# print(f"Error: {e}")  →  logger.error(f"Error: {e}")
# print(f"Uploaded {file}")  →  logger.info(f"Uploaded {file}")
# print(f"Debug info: {data}")  →  logger.debug(f"Debug info: {data}")
```

---

### Issue #13: Add Type Hints Throughout

**Example improvements for `modules/image_processor.py`:**

```python
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from PIL import Image

def process_image(
    self,
    input_path: str | Path,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a single image with optimization.
    
    Args:
        input_path: Path to the source image
        options: Optional processing options to override config
            - max_dimension: int - Maximum width/height
            - quality: int - WebP quality (0-100)
            - strip_exif: bool - Remove EXIF metadata
            - output_format: str - Output format (default: webp)
            
    Returns:
        Dictionary containing:
            - input_path: str
            - output_path: str
            - original_size: Tuple[int, int]
            - new_size: Tuple[int, int]
            - savings_percent: float
    """
```

---

## COMPLETE CONFIG.EXAMPLE.JSON TEMPLATE

After all fixes, the complete `config/config.example.json` should look like:

```json
{
  "api": {
    "SERVICE_API_KEY": "YOUR_SERVICE_API_KEY_HERE",
    "production_url": "https://kollect-it.com",
    "local_url": "http://localhost:3000",
    "use_local": false,
    "timeout": 30,
    "max_retries": 3
  },
  "imagekit": {
    "public_key": "YOUR_IMAGEKIT_PUBLIC_KEY",
    "private_key": "YOUR_IMAGEKIT_PRIVATE_KEY",
    "url_endpoint": "https://ik.imagekit.io/kollectit",
    "upload_folder": "products"
  },
  "ai": {
    "api_key": "YOUR_ANTHROPIC_API_KEY",
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 4000,
    "temperature": 0.7
  },
  "categories": {
    "militaria": {
      "name": "Militaria",
      "prefix": "MILI",
      "keywords": ["military", "war", "army", "navy", "air force", "marines", "wwii", "ww2", "ww1", "wwi", "civil war", "vietnam", "korea", "uniform", "medal", "badge", "insignia", "helmet", "weapon"],
      "subcategories": ["Uniforms & Clothing", "Medals & Decorations", "Headgear", "Equipment & Gear", "Edged Weapons", "Documents & Photos", "Flags & Banners", "Aviation", "Naval"]
    },
    "collectibles": {
      "name": "Collectibles",
      "prefix": "COLL",
      "keywords": ["vintage", "antique", "collectible", "retro", "classic", "rare", "advertising", "sign", "toy", "game"],
      "subcategories": ["Advertising", "Toys & Games", "Ephemera", "Memorabilia", "Kitchenware", "Tobacciana", "Breweriana", "Petroliana", "Sports"]
    },
    "books": {
      "name": "Books & Manuscripts",
      "prefix": "BOOK",
      "keywords": ["book", "books", "manuscript", "first edition", "signed", "rare book", "antique book", "leather bound", "map", "atlas", "print"],
      "subcategories": ["First Editions", "Signed Copies", "Manuscripts", "Maps & Atlases", "Antique Books", "Children's Books", "Art Books", "History", "Literature"]
    },
    "fineart": {
      "name": "Fine Art",
      "prefix": "ART",
      "keywords": ["art", "painting", "sculpture", "print", "lithograph", "etching", "watercolor", "oil painting", "drawing", "sketch", "portrait", "landscape"],
      "subcategories": ["Oil Paintings", "Watercolors", "Prints & Lithographs", "Drawings", "Sculpture", "Photography", "Mixed Media", "Folk Art", "Decorative Arts"]
    }
  },
  "defaults": {
    "condition_grades": [
      "Mint",
      "Excellent",
      "Very Good",
      "Good",
      "Fair",
      "Poor",
      "As-Is"
    ],
    "default_category": "collectibles",
    "default_status": "draft"
  },
  "image_processing": {
    "max_dimension": 2400,
    "webp_quality": 88,
    "thumbnail_size": 400,
    "strip_exif": true,
    "auto_orient": true,
    "background_removal": {
      "enabled": true,
      "default_strength": 0.9,
      "default_bg_color": "#FFFFFF",
      "preserve_shadows": true,
      "feather_amount": 2
    }
  },
  "paths": {
    "default_browse": "G:/My Drive/Kollect-It/Products",
    "watch_folder": "G:/My Drive/Kollect-It/New Products",
    "processed": "./processed",
    "completed": "G:/My Drive/Kollect-It/Completed",
    "failed": "G:/My Drive/Kollect-It/Failed",
    "temp": "./temp",
    "logs": "./logs"
  },
  "automation": {
    "watch_interval": 60,
    "auto_publish": false,
    "auto_background_removal": false,
    "archive_after_publish": true,
    "max_images_per_product": 20,
    "min_images_per_product": 1
  },
  "ui": {
    "theme": "dark",
    "window_width": 1400,
    "window_height": 900,
    "thumbnail_size": 120,
    "show_grid_lines": true
  }
}
```

---

## TESTING CHECKLIST

After making all fixes, verify:

1. **Config Loading:**
   - [ ] App shows error if config.json missing
   - [ ] App shows warning for placeholder API keys
   - [ ] Condition dropdown is populated

2. **Browse Functionality:**
   - [ ] Browse button opens to configured default path
   - [ ] Falls back to home directory if path invalid

3. **Image Upload:**
   - [ ] Images upload to ImageKit successfully
   - [ ] URLs are extracted correctly (strings, not dicts)
   - [ ] Upload progress shows correctly

4. **Publishing:**
   - [ ] use_local=true routes to localhost
   - [ ] use_local=false routes to production
   - [ ] Retry logic works without errors
   - [ ] Authentication errors handled gracefully

5. **Category Selection:**
   - [ ] All 4 categories appear in dropdown
   - [ ] currentData() returns correct category ID
   - [ ] SKU generates with correct prefix

---

## EXECUTION ORDER

Apply fixes in this order to minimize conflicts:

1. `config/config.example.json` - Add all missing sections
2. `desktop-app/.gitignore` - Add ignores
3. `modules/product_publisher.py` - Fix URL construction and retry loop
4. `main.py` - Fix config loading, browse_folder, upload handling, init
5. `modules/ai_engine.py` - Fix JSON parsing
6. Create `modules/logger.py` - Add logging (optional but recommended)

---

*Prompt created: December 12, 2025*
*For: Kollect-It Product Application v1.0*
