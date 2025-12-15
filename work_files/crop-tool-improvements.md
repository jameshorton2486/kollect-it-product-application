# Crop Tool Improvements

## Issues Identified in Original Implementation

### 1. Image Clipping on Load
**Problem:** When opening an image for cropping, portions of the image were being cut off before any user action.

**Root Cause:** 
- `fit_to_window()` called automatically via `QTimer.singleShot(0, self.fit_to_window)` (line 604)
- Zoom calculations in `fit_to_window()` could result in over-aggressive scaling
- The `QScrollArea` with `setWidgetResizable(False)` combined with immediate fit-to-window caused clipping

**Solution:** 
- Image now displays at 100% zoom initially
- ScrollArea allows viewing full image by scrolling
- User can manually choose "Fit to Window" if desired

### 2. No Visible Crop Frame Initially
**Problem:** Users had to click and drag to create a crop selection - there was no visual indication of crop boundaries from the start.

**Root Cause:**
- Used `QRubberBand` which only appears during drag operations
- No initial crop rectangle was set on image load

**Solution:**
- New `CropOverlay` widget with crop frame visible immediately
- Initial crop frame set to full image dimensions
- Visible handles on all 4 edges and 4 corners from the start

### 3. Limited Edge Manipulation
**Problem:** Users couldn't independently move each side of the crop rectangle.

**Root Cause:**
- `QRubberBand` only supports drag-to-create selection
- Edge/corner handle detection existed but visual feedback was minimal

**Solution:**
- 4 independent edge handles (top, bottom, left, right)
- 4 corner handles for diagonal resizing
- Visual indicators (white lines and squares) show handle positions
- Cursor changes to indicate available resize direction

### 4. No Restore Original Functionality
**Problem:** Once an image was cropped, there was no way to restore it to the original.

**Solution:**
- Automatic backup created in `.originals/` subfolder before first crop
- "🔄 Restore Original" button in dialog
- Only creates backup once (preserves true original)
- Confirmation dialog before restore

---

## New Features

### Visual Improvements
| Feature | Description |
|---------|-------------|
| Semi-transparent overlay | Areas outside crop are darkened for clarity |
| Visible edge handles | White line indicators on each edge center |
| Corner handles | White squares at each corner |
| Grid overlay | Rule of thirds or 5x5 grid (toggleable) |
| Dark theme | Modern dark UI matching application style |

### User Controls
| Control | Function |
|---------|----------|
| Reset Crop | Returns crop frame to full image size |
| 100% Button | Shows image at actual size |
| Fit to Window | Scales to fit (user-initiated only) |
| Restore Original | Recovers backed-up original image |

### Keyboard & Mouse Interactions
- **Click + Drag on edge**: Resize from that edge
- **Click + Drag on corner**: Resize diagonally
- **Click + Drag inside crop**: Move entire crop frame
- **Cursor feedback**: Changes to indicate available action

---

## File Changes

### Files Modified
- `modules/crop_tool.py` - Replaced with improved version

### Files Created
- `modules/crop_tool_original.py` - Backup of original implementation
- `modules/crop_tool_improved.py` - Source for new implementation

### Backup Location
Original images are backed up to:
```
{image_folder}/.originals/{filename}_original{extension}
```

---

## Code Architecture

### New Classes

#### `CropOverlay(QWidget)`
Transparent overlay widget that handles:
- Drawing crop frame with handles
- Mouse event handling for resize/move
- Grid overlay rendering
- Emits `crop_changed` signal when selection changes

#### `ImageLabel(QLabel)`  
Simple image display widget:
- Manages scale factor
- Stores original pixmap reference

#### `CropDialog(QDialog)` (Rewritten)
Main dialog with:
- Improved layout and controls
- Integration of overlay system
- Backup/restore functionality
- Better zoom handling

---

## Usage

```python
from modules.crop_tool import CropDialog

# Open crop dialog
dialog = CropDialog("/path/to/image.jpg", parent=self)
if dialog.exec_() == QDialog.Accepted:
    cropped_path = dialog.get_cropped_path()
    print(f"Cropped image saved to: {cropped_path}")
```

---

## Anthropic SDK Status

✅ **Installed:** Version 0.75.0
✅ **Client initialization:** Working
✅ **AI Engine integration:** Updated to use SDK with fallback
✅ **Default model:** Updated to `claude-sonnet-4-20250514`

### To verify in your environment:
```python
import anthropic
print(anthropic.__version__)  # Should show 0.75.0
```

---

## Testing Checklist

- [ ] Open crop dialog - image should display at 100% (full size)
- [ ] Verify crop frame visible immediately with handles
- [ ] Test dragging each edge independently
- [ ] Test dragging corners
- [ ] Test moving entire crop frame by dragging inside
- [ ] Test Reset Crop button
- [ ] Test Fit to Window button
- [ ] Apply crop and verify backup created in `.originals/`
- [ ] Test Restore Original button after cropping
- [ ] Test rotation and flip operations
- [ ] Test grid overlay toggle
- [ ] Test aspect ratio constraints

---

## Version Information

- **Updated:** December 2025
- **Anthropic SDK:** 0.75.0
- **Default Model:** claude-sonnet-4-20250514
- **PyQt5 Required:** ≥5.15.0
- **Pillow Required:** ≥9.0.0
