# Quick Start Checklist

Use this checklist to get the project running quickly.

## Prerequisites

- [ ] Python 3.9+ installed
- [ ] Node.js/Next.js project for kollect-it.com
- [ ] Google Drive access (or update paths in config)
- [ ] API keys: Anthropic, ImageKit, SERVICE_API_KEY

## Setup Steps

### 1. Install Python Dependencies
```bash
cd desktop-app
pip install -r requirements.txt
pip install rembg  # Optional but recommended
```

### 2. Create Configuration
```bash
cd desktop-app/config
cp config.example.json config.json
# Edit config.json with your API keys
```

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

In `config.json`, verify:
- [ ] `api.SERVICE_API_KEY` - matches server env var
- [ ] `imagekit.public_key` - from ImageKit dashboard
- [ ] `imagekit.private_key` - from ImageKit dashboard
- [ ] `ai.api_key` - Anthropic API key
- [ ] `paths.*` - all paths exist or will be created

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
