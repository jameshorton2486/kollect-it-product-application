# PHASE 1: CURSOR INSTRUCTIONS
## Code to Remove from main.py

**Tool:** 🟣 CURSOR  
**File:** `C:\Users\james\Kollect-It Product Application\desktop-app\main.py`

---

## How to Use This Document

1. Open `main.py` in Cursor
2. Use `Ctrl+G` to go to a specific line number
3. Select the code block shown below
4. Delete it
5. Move to the next item

**Tip:** After each deletion, line numbers will shift. Work from BOTTOM to TOP to avoid this issue.

---

## DELETION ORDER (Bottom to Top)

### ❌ DELETE #1: publish_product() Method
**Go to line:** ~1864  
**Search for:** `def publish_product(self):`

Delete the ENTIRE method (approximately 78 lines):

```python
# DELETE FROM HERE ↓↓↓
    def publish_product(self):
        """Publish the product to the website."""
        if not self.title_edit.text():
            QMessageBox.warning(self, "Missing Title", "Please enter a product title.")
            return
        
        # ... entire method body ...
        
        self.status_label.setText("Ready")
# DELETE TO HERE ↑↑↑
```

**How to find it:** Search for `def publish_product` — delete from `def` to the next method definition.

---

### ❌ DELETE #2: Publish Button Code
**Go to line:** ~1242  
**Search for:** `self.publish_btn = QPushButton`

Delete these lines:

```python
# DELETE FROM HERE ↓↓↓
        self.publish_btn = QPushButton("🚀 Publish Product")
        self.publish_btn.setEnabled(False)
        self.publish_btn.clicked.connect(self.publish_product)
        self.publish_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DarkPalette.SUCCESS};
                font-size: 15px;
                padding: 14px 28px;
            }}
            QPushButton:hover {{
                background-color: #38a169;
            }}
        """)
        actions_layout.addWidget(self.publish_btn)
# DELETE TO HERE ↑↑↑
```

---

### ❌ DELETE #3: Original Price Field
**Go to line:** ~1121  
**Search for:** `self.original_price_spin`

Delete these lines:

```python
# DELETE FROM HERE ↓↓↓
        self.original_price_spin = QDoubleSpinBox()
        self.original_price_spin.setRange(0, 999999.99)
        self.original_price_spin.setPrefix("$ ")
        self.original_price_spin.setDecimals(2)
        self.original_price_spin.setSpecialValueText("Optional")
        price_layout.addWidget(self.original_price_spin)
# DELETE TO HERE ↑↑↑
```

Also find and delete the label "Original:" if it exists on a separate line above.

---

### ❌ DELETE #4: Production API Checkbox
**Go to line:** ~1210  
**Search for:** `self.use_production_check`

Delete these lines:

```python
# DELETE FROM HERE ↓↓↓
        self.use_production_check = QCheckBox("Use Production API")
        self.use_production_check.setChecked(
            self.config.get("api", {}).get("use_production", True)
        )
        settings_layout.addRow(self.use_production_check)
# DELETE TO HERE ↑↑↑
```

---

### ❌ DELETE #5: Auto-Publish Checkbox
**Go to line:** ~1207  
**Search for:** `self.auto_publish_check`

Delete these lines:

```python
# DELETE FROM HERE ↓↓↓
        self.auto_publish_check = QCheckBox("Auto-publish after processing")
        settings_layout.addRow(self.auto_publish_check)
# DELETE TO HERE ↑↑↑
```

---

### ❌ DELETE #6: ProductPublisher Import
**Go to line:** ~60  
**Search for:** `from modules.product_publisher`

Delete this line:

```python
# DELETE THIS LINE ↓↓↓
from modules.product_publisher import ProductPublisher  # type: ignore
```

---

### ❌ DELETE #7: Attribute Initializations (if present)
**Search for:** `self.publish_btn = None`

In the `__init__` method, find and delete any of these lines if they exist:

```python
# DELETE THESE LINES IF FOUND ↓↓↓
        self.publish_btn = None
        self.use_production_check = None
        self.auto_publish_check = None
        self.original_price_spin = None
```

---

## VERIFICATION CHECKLIST

After all deletions, verify:

- [ ] No `publish_product` method exists
- [ ] No `publish_btn` references exist
- [ ] No `auto_publish_check` references exist
- [ ] No `use_production_check` references exist
- [ ] No `original_price_spin` references exist
- [ ] No `ProductPublisher` import exists

**Quick Check:** Use `Ctrl+Shift+F` (Find in Files) in Cursor to search for:
- `publish_product` → Should find 0 results
- `ProductPublisher` → Should find 0 results
- `auto_publish` → Should find 0 results

---

## CURSOR AI PROMPT (Alternative Method)

If you prefer, you can paste this prompt into Cursor's AI chat:

```
I need to remove all publishing-related code from main.py. Please help me delete:

1. The ProductPublisher import (line ~60)
2. The original_price_spin field and its setup (lines ~1121-1126)
3. The auto_publish_check checkbox (lines ~1207-1208)
4. The use_production_check checkbox (lines ~1210-1214)
5. The publish_btn button and its styling (lines ~1242-1255)
6. The entire publish_product() method (lines ~1864-1942)
7. Any attribute initializations for these removed elements in __init__

Show me each section to delete.
```

---

## AFTER DELETIONS: Git Commit

Once all code is removed, commit your changes:

```batch
cd "C:\Users\james\Kollect-It Product Application"
git add -A
git commit -m "Phase 1: Remove publishing components

- Deleted product_publisher.py module
- Deleted nextjs-api/ folder
- Removed publish_product() method
- Removed publish button and related UI elements
- Removed auto-publish and production API checkboxes
- Removed original price field
- Cleaned up redundant scripts

Architecture: Intake-only model - no direct publishing"

git push
```

---

## NEXT STEP

After completing Phase 1 deletions, return to Claude and say:

**"Phase 1 complete, ready for Phase 2"**

I'll then guide you through the modifications (renaming labels, etc.).
