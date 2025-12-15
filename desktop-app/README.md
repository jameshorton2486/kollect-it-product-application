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
pip install PyQt5 Pillow numpy requests python-docx anthropic
```

### Step 1.5: Install rembg (Optional but Recommended)

**rembg** is used for AI-powered background removal. It's optional - the app will work without it but with lower-quality fallback methods.

#### Standard Installation (CPU)
Works on all computers:
```bash
pip install rembg
```

#### GPU Installation (Faster - NVIDIA GPU Required)
For faster processing, especially with batch operations:
```bash
pip install rembg[gpu]
```

**Note:** GPU version requires:
- NVIDIA GPU with CUDA support
- CUDA Toolkit installed
- cuDNN library

**First Run:** The first time you use rembg, it will download a pre-trained AI model (~170MB). This is automatic but may take a few moments.

**Troubleshooting:**
- If you get ONNX runtime conflicts when switching between CPU/GPU versions:
  ```bash
  pip uninstall onnxruntime onnxruntime-gpu
  pip install rembg[gpu]  # or rembg for CPU
  ```
- Python version: rembg works best with Python 3.8-3.11. If you're on 3.12+, consider using a virtual environment with Python 3.11.

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

### Batch Background Removal (Standalone Script)

Process all images in a folder to remove backgrounds:

```bash
# Basic usage - processes images in folder, saves to ./processed
python batch_remove_backgrounds.py ./photos

# Specify output folder
python batch_remove_backgrounds.py ./photos ./output

# Custom settings
python batch_remove_backgrounds.py ./photos --strength 0.9 --bg-color "#FFFFFF"

# Check rembg installation
python batch_remove_backgrounds.py --check-install
```

**Options:**
- `--strength`: Removal strength 0.0-1.0 (default: 0.8)
- `--bg-color`: Background color hex code or "transparent" (default: #FFFFFF)
- `--gpu`: Use GPU acceleration (requires rembg[gpu])
- `--check-install`: Check rembg installation status

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

**Check installation:**
```bash
python batch_remove_backgrounds.py --check-install
```

**Install rembg:**
```bash
# CPU version (works everywhere)
pip install rembg

# GPU version (NVIDIA GPU required, faster)
pip install rembg[gpu]
```

**First run:** rembg will download the AI model (~170MB) on first use. This is normal and automatic.

**If you get ONNX runtime errors:**
```bash
pip uninstall onnxruntime onnxruntime-gpu
pip install rembg  # or rembg[gpu] for GPU
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
