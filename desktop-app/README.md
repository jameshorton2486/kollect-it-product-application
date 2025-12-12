# Kollect-It Automation System

A professional desktop application and automation system for managing the Kollect-It antiques marketplace. This system streamlines product listing through automated image processing, AI-powered descriptions, and direct website publishing.

## Features

### Desktop Application (PyQt5)
- **Drag & Drop Interface** - Drop product folders directly into the app
- **Image Processing Pipeline** - Automatic resize, WebP conversion, optimization
- **AI Background Removal** - Clean product photos with one click
- **Interactive Crop Tool** - Rule-of-thirds grid, aspect ratio presets, rotation
- **AI Description Generation** - Category-aware product descriptions via Claude
- **AI Valuation** - Price recommendations based on market analysis
- **Direct Publishing** - One-click publish to kollect-it.com
- **SKU Management** - Automatic SKU generation (PREFIX-YEAR-NNNN format)

### Background Automation Worker
- **Folder Monitoring** - Watches Google Drive for new products
- **Hands-Free Processing** - Fully automated pipeline
- **Archive Management** - Moves completed/failed folders automatically

## System Requirements

- Python 3.9 or higher
- Windows 10/11, macOS, or Linux
- 4GB RAM minimum
- Internet connection for API features

---

## Installation

### Step 1: Install Python Dependencies

```bash
cd desktop-app
pip install -r requirements.txt
```

Or install individually:
```bash
pip install PyQt5 Pillow numpy requests rembg python-docx anthropic
```

### Step 2: Configure API Keys

Edit `config/config.json` with your credentials:

```json
{
  "api": {
    "SERVICE_API_KEY": "your_service_api_key_here",
    "production_url": "https://kollect-it.com",
    "local_url": "http://localhost:3000",
    "use_local": false
  },
  "imagekit": {
    "public_key": "your_imagekit_public_key",
    "private_key": "your_imagekit_private_key",
    "url_endpoint": "https://ik.imagekit.io/kollectit"
  },
  "ai": {
    "api_key": "your_anthropic_api_key",
    "model": "claude-sonnet-4-20250514"
  }
}
```

### Step 3: Add Backend API Endpoint (Next.js)

Copy `nextjs-api/route.ts` to your Kollect-It website:

```
src/app/api/admin/products/service-create/route.ts
```

Add to your `.env.local`:
```
SERVICE_API_KEY=your_secure_service_key_here
```

---

## Usage

### Running the Desktop Application

```bash
cd desktop-app
python main.py
```

### Desktop App Workflow

1. **Drop a product folder** into the app (or use File → Open Folder)
2. **Review detected images** in the thumbnail grid
3. **Edit product details** - title, category, price, condition
4. **Optional: Crop/Remove backgrounds** via right-click menu
5. **Click "Optimize All"** to process images
6. **Click "Generate Description"** for AI content
7. **Click "Upload to ImageKit"** to upload images
8. **Click "Publish Product"** to create listing

### Running the Automation Worker

**Single run (process all pending folders):**
```bash
python automation_worker.py
```

**Daemon mode (continuous monitoring):**
```bash
python automation_worker.py --daemon
```

**Test mode (process without publishing):**
```bash
python automation_worker.py --test
```

**Check system status:**
```bash
python automation_worker.py --status
```

---

## Configuration Reference

### config.json Structure

```json
{
  "api": {
    "SERVICE_API_KEY": "",
    "production_url": "https://kollect-it.com",
    "local_url": "http://localhost:3000",
    "use_local": false,
    "timeout": 30,
    "max_retries": 3
  },
  "imagekit": {
    "public_key": "",
    "private_key": "",
    "url_endpoint": "https://ik.imagekit.io/kollectit"
  },
  "categories": {
    "militaria": {
      "prefix": "MILI",
      "keywords": ["military", "war", "army", "navy", "wwii", "ww2"],
      "subcategories": ["Uniforms", "Medals", "Equipment", "Documents"]
    },
    "collectibles": {
      "prefix": "COLL",
      "keywords": ["vintage", "antique", "collectible"],
      "subcategories": ["Advertising", "Toys", "Ephemera", "Memorabilia"]
    },
    "books": {
      "prefix": "BOOK",
      "keywords": ["book", "manuscript", "first edition", "signed"],
      "subcategories": ["First Editions", "Signed", "Manuscripts", "Maps"]
    },
    "fineart": {
      "prefix": "ART",
      "keywords": ["art", "painting", "sculpture", "print"],
      "subcategories": ["Paintings", "Prints", "Sculpture", "Photography"]
    }
  },
  "image_processing": {
    "max_dimension": 2400,
    "webp_quality": 88,
    "strip_exif": true,
    "background_removal": {
      "default_strength": 0.9,
      "default_bg_color": "#FFFFFF"
    }
  },
  "ai": {
    "api_key": "",
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 4000
  },
  "paths": {
    "watch_folder": "~/Google Drive/Kollect-It/New Products",
    "processed": "./processed",
    "completed": "~/Google Drive/Kollect-It/Completed",
    "failed": "~/Google Drive/Kollect-It/Failed",
    "temp": "./temp",
    "logs": "./logs"
  },
  "automation": {
    "watch_interval": 60,
    "auto_publish": true,
    "auto_background_removal": false,
    "archive_after_publish": true
  }
}
```

---

## SKU Format

SKUs follow the pattern: `PREFIX-YEAR-NNNN`

| Category | Prefix | Example |
|----------|--------|---------|
| Militaria | MILI | MILI-2025-0001 |
| Collectibles | COLL | COLL-2025-0042 |
| Books | BOOK | BOOK-2025-0007 |
| Fine Art | ART | ART-2025-0015 |

SKU counters are stored in `config/sku_state.json` and persist across sessions.

---

## Image Processing Pipeline

1. **Input**: RAW images (JPG, PNG, TIFF, etc.)
2. **Rename**: Sequential numbering (01-, 02-, etc.)
3. **Crop** (optional): Interactive tool with grid overlays
4. **Background Removal** (optional): AI-powered with U2-Net
5. **Resize**: Max 2400px on longest side
6. **Convert**: WebP format at 88% quality
7. **Upload**: ImageKit CDN
8. **Output**: Production-ready URLs

---

## File Structure

```
kollect-it-automation/
├── desktop-app/
│   ├── main.py                 # PyQt5 desktop application
│   ├── automation_worker.py    # Background processing daemon
│   ├── requirements.txt        # Python dependencies
│   ├── config/
│   │   ├── config.json         # Main configuration
│   │   └── sku_state.json      # SKU counter state
│   ├── modules/
│   │   ├── ai_engine.py        # AI description generation
│   │   ├── background_remover.py
│   │   ├── crop_tool.py        # Interactive crop dialog
│   │   ├── image_processor.py  # WebP conversion pipeline
│   │   ├── imagekit_uploader.py
│   │   ├── product_publisher.py
│   │   └── sku_generator.py
│   └── templates/
│       ├── militaria_template.json
│       ├── collectibles_template.json
│       ├── books_template.json
│       └── fineart_template.json
└── nextjs-api/
    └── route.ts                # Service API endpoint
```

---

## API Endpoint Reference

### POST /api/admin/products/service-create

**Headers:**
```
x-api-key: YOUR_SERVICE_API_KEY
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "WWII US Army M1 Helmet",
  "sku": "MILI-2025-0001",
  "category": "militaria",
  "description": "Original WWII US Army M1 helmet...",
  "price": 450.00,
  "condition": "Good",
  "images": [
    "https://ik.imagekit.io/kollectit/products/militaria/MILI-2025-0001/01.webp"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "productId": "clx123abc",
  "slug": "wwii-us-army-m1-helmet",
  "productUrl": "https://kollect-it.com/products/wwii-us-army-m1-helmet",
  "adminUrl": "https://kollect-it.com/admin/products/clx123abc"
}
```

---

## Troubleshooting

### "Module not found" errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### ImageKit upload fails
- Verify your private key in config.json
- Check that the URL endpoint matches your ImageKit account

### AI description generation fails
- Verify your Anthropic API key
- Check that you have API credits available

### Publishing returns 401 Unauthorized
- Verify SERVICE_API_KEY matches in both config.json and .env.local
- Ensure the Next.js server is running (for local testing)

### Background remover not working
Install rembg separately:
```bash
pip install rembg[gpu]  # For GPU acceleration
# or
pip install rembg       # CPU only
```

---

## Security Notes

- **Never commit config.json with real API keys**
- **Rotate SERVICE_API_KEY periodically**
- **Use environment variables in production**
- **The SERVICE_API_KEY grants product creation access only**

---

## Support

For issues with this automation system, check:
1. Log files in `desktop-app/logs/`
2. Error messages in the desktop app's activity log
3. Network connectivity to kollect-it.com and api.anthropic.com

---

## Version

v1.0.0 - December 2025
