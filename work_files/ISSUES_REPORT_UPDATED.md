# Kollect-It Product Application - Issues Report (Updated)

## Executive Summary

After a thorough code review and cross-referencing with the original design specification, I've identified **16 issues** across different severity levels. The application architecture closely follows the design document, but has several configuration gaps and implementation bugs that should be addressed before production use.

**Design Document Confirmed Features:**
- ✅ SERVICE_API_KEY authentication (Option B chosen)
- ✅ Dark theme UI
- ✅ WebP-only output (intentional design decision)
- ✅ Built-in cropping tool
- ✅ AI background removal (rembg/U2-Net)
- ✅ SKU format: PREFIX-YYYY-NNNN
- ✅ Four categories: MILI, COLL, BOOK, ART
- ✅ ImageKit CDN integration
- ✅ AI description generation via Claude API

---

## Critical Issues (Requires Immediate Fix)

### 1. Missing `defaults` Configuration Section
**File:** `main.py` (line 678) and `config/config.example.json`  
**Problem:** The code references `self.config.get("defaults", {}).get("condition_grades", [])` but the config file has no `defaults` section.

**Impact:** The Condition dropdown will be empty - users cannot select item condition.

**Fix:** Add to `config.example.json`:
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
    ]
}
```

---

### 2. Browse Folder Default Path Not Set
**File:** `main.py` (lines 408-412)  
**Problem:** The browse folder dialog uses an empty string as the default path.

**Design Reference:** The design doc mentions monitoring Google Drive folders and structured paths like `/products/<category>/<SKU>/`

**Fix:** Add `default_browse` to config paths section:
```json
"paths": {
    "default_browse": "G:\\My Drive\\Kollect-It\\Products",
    "watch_folder": "G:\\My Drive\\Kollect-It\\New Products",
    "completed": "G:\\My Drive\\Kollect-It\\Completed",
    "failed": "G:\\My Drive\\Kollect-It\\Failed"
}
```

---

### 3. Product Publisher URL Construction Error
**File:** `modules/product_publisher.py` (lines 27-30)  
**Problem:** Code checks `use_production` but config uses `use_local`.

**Design Reference:** The design doc specifies:
- Production: `https://kollect-it.com/api/admin/products/service-create`
- Local: `http://localhost:3000/api/admin/products/service-create`

**Fix:**
```python
self.use_local = api_config.get("use_local", False)
if self.use_local:
    base = api_config.get("local_url", "http://localhost:3000")
else:
    base = api_config.get("production_url", "https://kollect-it.com")
self.base_url = f"{base}/api/admin/products/service-create"
```

---

## High Priority Issues

### 4. Uninitialized `uploaded_image_urls` Attribute
**File:** `main.py` (line 1314)  
**Problem:** The attribute isn't initialized in `__init__`, relies on `getattr()` fallback.

**Fix:** Initialize in `__init__`:
```python
self.uploaded_image_urls = []
```

---

### 5. Missing Error Handling for Config File
**File:** `main.py` (lines 541-547)  
**Problem:** No validation or user-friendly error if config.json is missing or malformed.

**Design Reference:** Config is critical - stores SERVICE_API_KEY, ImageKit keys, and all operational settings.

**Fix:** Add validation with clear error messages directing users to copy config.example.json.

---

### 6. rembg Dependency Installation Issues
**File:** `modules/background_remover.py`  
**Problem:** rembg requires compiled dependencies that fail on Python 3.14.

**Design Reference:** The design doc specifically requested "AI Background Remover (In-App)" using "U2-Net background removal model" with rembg integration.

**Fix Options:**
1. Document Python 3.12 requirement
2. The fallback edge-detection method exists but produces poor results
3. Consider alternative: RemBG API service as fallback

---

### 7. ImageKit Upload Returns Dict but Code Expects URL String
**File:** `modules/imagekit_uploader.py` vs `main.py` (line 1259-1261)

**Problem:** Uploader returns `{"success": True, "url": "..."}` but main.py appends the entire dict to `uploaded_urls`.

**Design Reference:** ImageKit URLs should be in format: `https://ik.imagekit.io/kollectit/products/<category>/<SKU>/`

**Fix in main.py:**
```python
result = uploader.upload(img_path, folder)
if result and result.get("success"):
    uploaded_urls.append(result.get("url"))
```

---

## Medium Priority Issues

### 8. Category Combo Data Not Properly Set
**File:** `main.py`  
**Problem:** `currentData()` may return None.

**Design Reference:** Categories must match: militaria, collectibles, books, fineart with prefixes MILI, COLL, BOOK, ART.

---

### ~~9. Hardcoded WebP Output Format~~ (NOT AN ISSUE)
**Status:** By Design  
**Design Reference:** The design doc explicitly states "WebP-Only Pipeline" with specifications:
- Max 2400px
- Quality 88%
- Remove EXIF
- Standardize color profile

This is intentional, not a bug.

---

### 9. SKU State File Should Be Gitignored
**File:** `modules/sku_generator.py`  
**Problem:** `config/sku_state.json` stores incrementing counters but isn't gitignored.

**Design Reference:** SKU format MILI-2025-0001 auto-increments per category.

---

### 10. Undefined Variable in Product Publisher
**File:** `modules/product_publisher.py` (line 172)  
**Problem:** `response` may be undefined if exception occurs before assignment.

---

### 11. Inconsistent Path Separators in Config
**File:** `config/config.example.json`  
**Problem:** Uses Unix paths (`~/Google Drive/`) incompatible with Windows.

---

## Low Priority Issues

### 12. AI Engine JSON Parsing Edge Cases
**File:** `modules/ai_engine.py`  
**Problem:** Markdown fence cleanup may fail on malformed responses.

---

### 13. Missing Type Hints
**Impact:** Reduced IDE support.

---

### 14. No Logging Framework
**Problem:** Uses `print()` instead of proper logging.

**Design Reference:** Design doc mentions "Logs actions" for the automation worker.

---

### 15. Batch Processing Not Implemented
**File:** `main.py`  
**Design Reference:** The design doc mentions "Bulk imports" as future expansion.

---

### 16. Settings Dialog Not Implemented
**File:** `main.py`  
**Problem:** Shows message to edit config.json manually.

---

## Design Document Alignment Check

| Feature | Design Doc | Implementation | Status |
|---------|-----------|----------------|--------|
| SERVICE_API_KEY auth | ✅ | ✅ | Complete |
| Dark theme | ✅ | ✅ | Complete |
| Drag-and-drop | ✅ | ✅ | Complete |
| Auto-rename images | ✅ | ✅ | Complete |
| WebP conversion | ✅ | ✅ | Complete |
| Image cropping | ✅ | ✅ | Complete |
| AI background removal | ✅ | ⚠️ | Fallback only |
| ImageKit upload | ✅ | ⚠️ | Bug in URL handling |
| AI descriptions | ✅ | ✅ | Complete |
| SKU generation | ✅ | ✅ | Complete |
| Category templates | ✅ | ✅ | Complete |
| Publish to website | ✅ | ⚠️ | URL config bug |
| Background worker | ✅ | ✅ | Complete |
| Batch processing | ✅ | ❌ | Not implemented |
| DOCX/TXT/HTML export | ✅ | Partial | JSON only |

---

## Configuration Template (Complete)

Based on design doc and code analysis, here's the complete config structure needed:

```json
{
  "api": {
    "SERVICE_API_KEY": "your_secure_key_here",
    "production_url": "https://kollect-it.com",
    "local_url": "http://localhost:3000",
    "use_local": false,
    "timeout": 30,
    "max_retries": 3
  },
  "imagekit": {
    "public_key": "your_public_key",
    "private_key": "your_private_key",
    "url_endpoint": "https://ik.imagekit.io/kollectit"
  },
  "ai": {
    "api_key": "your_anthropic_api_key",
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 4000,
    "temperature": 0.7
  },
  "categories": {
    "militaria": {
      "prefix": "MILI",
      "name": "Militaria",
      "keywords": ["military", "war", "army", "navy", "wwii"],
      "subcategories": ["Uniforms", "Medals", "Headgear", "Equipment"]
    },
    "collectibles": {
      "prefix": "COLL",
      "name": "Collectibles",
      "keywords": ["vintage", "antique", "collectible"],
      "subcategories": ["Advertising", "Toys", "Ephemera"]
    },
    "books": {
      "prefix": "BOOK",
      "name": "Books & Manuscripts",
      "keywords": ["book", "manuscript", "first edition"],
      "subcategories": ["First Editions", "Signed", "Maps"]
    },
    "fineart": {
      "prefix": "ART",
      "name": "Fine Art",
      "keywords": ["art", "painting", "sculpture"],
      "subcategories": ["Oil Paintings", "Watercolors", "Prints"]
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
    ]
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
      "default_bg_color": "#FFFFFF"
    }
  },
  "paths": {
    "default_browse": "G:\\My Drive\\Kollect-It\\Products",
    "watch_folder": "G:\\My Drive\\Kollect-It\\New Products",
    "completed": "G:\\My Drive\\Kollect-It\\Completed",
    "failed": "G:\\My Drive\\Kollect-It\\Failed",
    "processed": "./processed",
    "temp": "./temp",
    "logs": "./logs"
  },
  "automation": {
    "watch_interval": 60,
    "auto_publish": true,
    "auto_background_removal": false,
    "archive_after_publish": true
  },
  "ui": {
    "theme": "dark",
    "window_width": 1400,
    "window_height": 900,
    "thumbnail_size": 120
  }
}
```

---

## Priority Fix Order

1. **Immediate (Before Running):**
   - Add `defaults.condition_grades` to config
   - Fix ImageKit URL extraction in main.py
   - Fix Product Publisher use_local check

2. **Before Production:**
   - Add config validation
   - Add default_browse path
   - Fix undefined response variable

3. **Quality Improvements:**
   - Implement logging
   - Resolve rembg installation for Python 3.14

---

*Report updated: December 12, 2025*
*Cross-referenced with original design specification*
