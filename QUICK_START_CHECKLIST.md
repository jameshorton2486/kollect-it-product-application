# Quick Start Checklist

Use this checklist to get the project running quickly.

## Prerequisites

- [ ] Python 3.9+ installed
- [ ] Node.js/Next.js project for kollect-it.com
- [ ] Google Drive access (or update paths in config)
- [x] API keys: All configured in `.env` file

## Setup Steps

### 1. Install Python Dependencies
```bash
cd desktop-app
pip install -r requirements.txt
# rembg is already installed (v2.0.69)
```

### 2. Configuration
✅ **Already configured!** API keys are in `.env` file.
- Keys are automatically loaded from `desktop-app/.env`
- No need to edit `config.json` - it uses `.env` values

### 3. Deploy API Endpoint
- [ ] Copy `nextjs-api/route.ts` to your Next.js project:
  - `src/app/api/admin/products/service-create/route.ts`
- [ ] Add to `.env.local`:
  ```
  SERVICE_API_KEY=your_key_here
  ```
- [ ] Deploy to production

### 4. Create Folders
Create these folders (or update paths in config):
- [ ] `G:/My Drive/Kollect-It/New Products/`
- [ ] `G:/My Drive/Kollect-It/Completed/`
- [ ] `G:/My Drive/Kollect-It/Failed/`
- [ ] `G:/My Drive/Kollect-It/Products/`

### 5. Test Desktop App
```bash
cd desktop-app
python main.py
```
- [ ] App launches
- [ ] Can drop a folder
- [ ] Images load
- [ ] SKU generates

### 6. Test API
```bash
curl -X GET https://kollect-it.com/api/admin/products/service-create \
  -H "x-api-key: your_key"
```
- [ ] Returns success response

### 7. Test Full Workflow
- [ ] Drop folder in app
- [ ] Optimize images
- [ ] Generate AI description
- [ ] Upload to ImageKit
- [ ] Publish product
- [ ] Verify product appears on website

## Configuration Checklist

✅ **All API keys are configured in `.env` file:**
- [x] `SERVICE_API_KEY` - Set in `.env`
- [x] `IMAGEKIT_PUBLIC_KEY` - Set in `.env`
- [x] `IMAGEKIT_PRIVATE_KEY` - Set in `.env`
- [x] `ANTHROPIC_API_KEY` - Set in `.env`
- [ ] `paths.*` - Verify folder paths in `config.json` match your system

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Config not found | Copy `config.example.json` to `config.json` |
| Unauthorized | Check `SERVICE_API_KEY` matches |
| No rembg | `pip install rembg` (optional) |
| Images not uploading | Check ImageKit credentials |
| AI fails | Check Anthropic API key |

## Next Steps

1. Read `PROJECT_ANALYSIS.md` for full details
2. Test automation worker: `python automation_worker.py --test`
3. Set up daemon mode for continuous processing
4. Monitor logs in `desktop-app/logs/`
