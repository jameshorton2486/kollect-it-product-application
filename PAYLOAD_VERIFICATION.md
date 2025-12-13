# Product Publishing Payload Verification

**Date:** December 2025  
**Source:** Desktop Application (`main.py` → `product_publisher.py`)  
**Purpose:** Document exact JSON payload sent to Kollect-It API

---

## API Endpoint

- **Full URL:** `https://kollect-it.com/api/admin/products/service-create` (production)  
  OR `http://localhost:3000/api/admin/products/service-create` (local)
- **HTTP Method:** `POST`
- **URL Construction:** 
  ```python
  base = config.get("api", {}).get("production_url", "https://kollect-it.com")
  base_url = f"{base.rstrip('/')}/api/admin/products/service-create"
  ```

---

## Headers

All requests include these headers:

```http
Content-Type: application/json
x-api-key: {SERVICE_API_KEY from config.json}
User-Agent: KollectIt-Desktop/1.0
```

**Authentication:** Uses `x-api-key` header with value from `config.api.SERVICE_API_KEY`

---

## Payload Schema

### Complete Example Payload

```json
{
  "title": "WWII US Army M1 Helmet",
  "sku": "MILI-2025-0001",
  "category": "militaria",
  "subcategory": "Headgear",
  "description": "Original WWII US Army M1 helmet in excellent condition...",
  "descriptionHtml": "<p>Original WWII US Army M1 helmet in excellent condition...</p>",
  "price": 450.00,
  "originalPrice": 550.00,
  "condition": "Excellent",
  "era": "WWII",
  "origin": "United States",
  "images": [
    {
      "url": "https://ik.imagekit.io/kollectit/products/militaria/MILI-2025-0001/01.webp",
      "alt": "WWII US Army M1 Helmet - Image 1",
      "order": 0
    },
    {
      "url": "https://ik.imagekit.io/kollectit/products/militaria/MILI-2025-0001/02.webp",
      "alt": "WWII US Army M1 Helmet - Image 2",
      "order": 1
    }
  ],
  "seoTitle": "WWII US Army M1 Helmet - Original Military Collectible",
  "seoDescription": "Original WWII US Army M1 helmet in excellent condition. Authentic military collectible from World War II era.",
  "seoKeywords": ["wwii", "military", "helmet", "army", "collectible", "militaria"],
  "status": "draft"
}
```

---

## Field Details

| Field Name | Type | Required | Source | Notes |
|------------|------|----------|--------|-------|
| `title` | string | ✅ REQUIRED | `title_edit.text()` | Product title from UI input |
| `sku` | string | ✅ REQUIRED | `sku_edit.text()` | Format: `PREFIX-YYYY-NNNN` (e.g., `MILI-2025-0001`) |
| `category` | string | ✅ REQUIRED | `category_combo.currentData()` | Category ID: `militaria`, `collectibles`, `books`, `fineart` |
| `subcategory` | string | ⚠️ OPTIONAL | `subcategory_combo.currentText()` | Can be empty string if not selected |
| `description` | string | ✅ REQUIRED | `description_edit.toPlainText()` | Plain text description |
| `descriptionHtml` | string | ⚠️ OPTIONAL | Auto-generated | Simple `<p>` wrapper around description |
| `price` | number (float) | ✅ REQUIRED | `price_spin.value()` | Must be > 0 |
| `originalPrice` | number (float) \| null | ⚠️ OPTIONAL | `original_price_spin.value()` | Set to `None` if 0 or empty |
| `condition` | string | ✅ REQUIRED | `condition_combo.currentText()` | From dropdown: "Mint", "Excellent", "Very Good", "Good", "Fair", "Poor", "As-Is" |
| `era` | string \| null | ⚠️ OPTIONAL | `era_edit.text()` | Set to `None` if empty (e.g., "WWII", "Victorian") |
| `origin` | string \| null | ⚠️ OPTIONAL | `origin_edit.text()` | Set to `None` if empty (e.g., "United States", "Germany") |
| `images` | array | ✅ REQUIRED | `uploaded_image_urls` | Array of image objects (see Image Handling below) |
| `seoTitle` | string | ⚠️ OPTIONAL | `seo_title_edit.text()` | Falls back to `title` if empty |
| `seoDescription` | string | ⚠️ OPTIONAL | `seo_desc_edit.toPlainText()` | Falls back to first 160 chars of `description` if empty |
| `seoKeywords` | array | ⚠️ OPTIONAL | `seo_keywords_edit.text()` | Comma-separated string split into array, empty strings filtered |
| `status` | string | ⚠️ OPTIONAL | Hardcoded | Always set to `"draft"` |

---

## Image Handling

### Image Object Structure

Each image in the `images` array has this structure:

```json
{
  "url": "https://ik.imagekit.io/kollectit/products/militaria/MILI-2025-0001/01.webp",
  "alt": "WWII US Army M1 Helmet - Image 1",
  "order": 0
}
```

### Image URL Source

- **Source:** ImageKit CDN URLs
- **Format:** Full HTTPS URLs from ImageKit
- **Path Structure:** `products/{category}/{sku}/{filename}.webp`
- **Example:** `https://ik.imagekit.io/kollectit/products/militaria/MILI-2025-0001/01.webp`

### Image Upload Flow

1. **Processing:** Images are processed (resized, converted to WebP) → stored in `processed/` folder
2. **Upload:** Each image is uploaded to ImageKit via `ImageKitUploader.upload()`
3. **URL Storage:** ImageKit returns full CDN URL → stored in `self.uploaded_image_urls[]`
4. **Payload Construction:** URLs are mapped to image objects with `alt` text and `order` index

**Important:** Images are **NOT** sent as base64 or file paths. Only ImageKit CDN URLs are sent.

---

## Category Handling

### Category Format

Categories are sent as **string IDs** (not display names):

- `"militaria"` - Militaria category
- `"collectibles"` - Collectibles category  
- `"books"` - Books & Manuscripts category
- `"fineart"` - Fine Art category

The **category ID** (key) is sent, not the display name.

### Subcategory Format

Subcategories are sent as **display strings** (not IDs):

- Examples: `"Headgear"`, `"Uniforms & Clothing"`, `"First Editions"`, `"Oil Paintings"`
- Can be empty string `""` if not selected

---

## Validation Rules

### Client-Side Validation (Python)

**Required Fields:**
- `title` - Must not be empty
- `sku` - Must match format: `^[A-Z]{3,4}-\d{4}-\d{4}$`
- `category` - Must not be empty
- `description` - Must not be empty
- `price` - Must be number > 0
- `condition` - Must not be empty
- `images` - Must have at least 1 image with valid URL

### Server-Side Validation (TypeScript)

**Required Fields:**
- `title` - Non-empty string
- `sku` - Non-empty string
- `category` - Non-empty string
- `description` - Non-empty string
- `price` - Number >= 0
- `condition` - Non-empty string
- `images` - Array with at least 1 element, each with `url` property

---

## Code Locations

### Desktop App Payload Construction

- **File:** `desktop-app/main.py`
- **Function:** `publish_product()` (lines 1743-1821)
- **Payload Building:** Lines 1776-1796

### Publisher Module

- **File:** `desktop-app/modules/product_publisher.py`
- **Class:** `ProductPublisher`
- **Method:** `publish()` (lines 95-189)
- **Validation:** `validate_product()` (lines 47-87)
- **Headers:** `_get_headers()` (lines 39-45)

### API Endpoint

- **File:** `nextjs-api/route.ts`
- **Handler:** `POST()` function (lines 101-240)
- **Validation:** `validatePayload()` (lines 64-99)
