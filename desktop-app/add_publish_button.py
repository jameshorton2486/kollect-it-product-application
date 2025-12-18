# add_publish_button.py
# Run with: python add_publish_button.py
# From: C:\Users\james\Kollect-It Product Application\desktop-app

print("Adding Publish to Website button to main.py...")

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes_made = 0

# ============================================================
# CHANGE 1: Add import for WebsitePublisher
# ============================================================
if 'website_publisher' not in content:
    old_import = "from modules.output_generator import OutputGenerator"
    new_import = """from modules.output_generator import OutputGenerator
from modules.website_publisher import WebsitePublisher"""
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("  + Added website_publisher import")
        changes_made += 1
    else:
        print("  ? Could not find import location")

# ============================================================
# CHANGE 2: Add publish_btn attribute in __init__
# ============================================================
if 'self.publish_btn = None' not in content:
    old_attr = 'self.export_btn = None'
    new_attr = '''self.export_btn = None
        self.publish_btn = None'''
    
    if old_attr in content:
        content = content.replace(old_attr, new_attr)
        print("  + Added publish_btn attribute")
        changes_made += 1

# ============================================================
# CHANGE 3: Initialize WebsitePublisher
# ============================================================
if 'self.website_publisher' not in content:
    old_init = 'self.output_generator = OutputGenerator(self.config)'
    new_init = '''self.output_generator = OutputGenerator(self.config)
        self.website_publisher = WebsitePublisher(self.config)'''
    
    if old_init in content:
        content = content.replace(old_init, new_init)
        print("  + Added WebsitePublisher initialization")
        changes_made += 1

# ============================================================
# CHANGE 4: Add Publish button after Export button
# ============================================================
if 'self.publish_btn = QPushButton' not in content:
    old_btn = '''self.export_btn = QPushButton("📦 Export Package")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.setProperty("variant", "primary")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_package)
        actions_layout.addWidget(self.export_btn)'''
    
    new_btn = '''self.export_btn = QPushButton("📦 Export Package")
        self.export_btn.setObjectName("exportBtn")
        self.export_btn.setProperty("variant", "primary")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_package)
        actions_layout.addWidget(self.export_btn)

        self.publish_btn = QPushButton("🌐 Publish to Website")
        self.publish_btn.setObjectName("publishBtn")
        self.publish_btn.setProperty("variant", "success")
        self.publish_btn.setEnabled(False)
        self.publish_btn.setToolTip("Publish product to kollect-it.com as draft")
        self.publish_btn.clicked.connect(self.publish_to_website)
        actions_layout.addWidget(self.publish_btn)'''
    
    if old_btn in content:
        content = content.replace(old_btn, new_btn)
        print("  + Added Publish to Website button")
        changes_made += 1
    else:
        print("  ? Could not find Export button section")

# ============================================================
# CHANGE 5: Update export button state to include publish
# ============================================================
if 'self.publish_btn.setEnabled' not in content and 'update_export_button_state' in content:
    old_state = '''can_export = (
                bool(self.sku_edit.text().strip()) and
                bool(self.title_edit.text().strip()) and
                bool(self.description_edit.toPlainText().strip()) and
                len(self.uploaded_image_urls) > 0
            )
            self.export_btn.setEnabled(can_export)'''
    
    new_state = '''can_export = (
                bool(self.sku_edit.text().strip()) and
                bool(self.title_edit.text().strip()) and
                bool(self.description_edit.toPlainText().strip()) and
                len(self.uploaded_image_urls) > 0
            )
            self.export_btn.setEnabled(can_export)
            if self.publish_btn:
                self.publish_btn.setEnabled(can_export)'''
    
    if old_state in content:
        content = content.replace(old_state, new_state)
        print("  + Added publish button enable logic")
        changes_made += 1

# ============================================================
# CHANGE 6: Add publish_to_website method
# ============================================================
publish_method = '''
    def publish_to_website(self):
        """Publish product to kollect-it.com as draft."""
        print("[PUBLISH] Starting website publish...")
        logger.info("Starting website publish")
        
        # Validate required fields
        validation_errors = []
        if not self.title_edit.text():
            validation_errors.append("Missing title")
        if not self.description_edit.toPlainText():
            validation_errors.append("Missing description")
        if not self.uploaded_image_urls:
            validation_errors.append("No uploaded images - upload to ImageKit first")
        if not self.category_combo.currentData():
            validation_errors.append("No category selected")
        if not self.sku_edit.text():
            validation_errors.append("No SKU generated")
        
        if validation_errors:
            QMessageBox.warning(
                self, "Cannot Publish",
                "Please fix the following:\\n\\n• " + "\\n• ".join(validation_errors)
            )
            return
        
        # Check publisher configuration
        if not self.website_publisher.is_configured():
            QMessageBox.warning(
                self, "Publisher Not Configured",
                "PRODUCT_INGEST_API_KEY not set.\\n\\n"
                "Add to your .env file:\\n"
                "PRODUCT_INGEST_API_KEY=your-api-key\\n\\n"
                "Get this key from your website admin."
            )
            return
        
        # Confirm publish
        reply = QMessageBox.question(
            self, "Publish to Website",
            f"Publish \\"{self.title_edit.text()}\\" to kollect-it.com?\\n\\n"
            f"SKU: {self.sku_edit.text()}\\n"
            f"Price: ${self.price_spin.value():,.2f}\\n"
            f"Images: {len(self.uploaded_image_urls)}\\n\\n"
            "Product will be created as DRAFT for admin review.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.log("Publishing to website...", "info")
        self.status_label.setText("Publishing to website...")
        QApplication.processEvents()
        
        # Build product data
        product_data = {
            "title": self.title_edit.text(),
            "sku": self.sku_edit.text(),
            "category": self.category_combo.currentData(),
            "subcategory": self.subcategory_combo.currentText() or None,
            "description": self.description_edit.toPlainText(),
            "price": self.price_spin.value(),
            "condition": self.condition_combo.currentText(),
            "era": self.era_edit.text() or None,
            "origin": self.origin_edit.text() or None,
            "images": [
                {"url": url, "alt": f"{self.title_edit.text()} - Image {i+1}", "order": i}
                for i, url in enumerate(self.uploaded_image_urls)
            ],
            "seoTitle": self.seo_title_edit.text() or self.title_edit.text(),
            "seoDescription": self.seo_desc_edit.toPlainText() or self.description_edit.toPlainText()[:160],
            "seoKeywords": [k.strip() for k in self.seo_keywords_edit.text().split(",") if k.strip()],
            "last_valuation": self.last_valuation
        }
        
        # Publish
        try:
            result = self.website_publisher.publish(product_data)
            
            if result.get("success"):
                admin_url = result.get("admin_url", "")
                
                self.log(f"✓ Published to website: {result.get('sku')}", "success")
                logger.info(f"Published to website: {result}")
                
                # Show success dialog
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Published Successfully")
                msg.setText(
                    f"Product published as DRAFT!\\n\\n"
                    f"SKU: {result.get('sku')}\\n"
                    f"Status: Draft (awaiting review)\\n\\n"
                    f"Next: Review and publish in admin panel"
                )
                
                if admin_url:
                    open_admin_btn = msg.addButton("Open Admin", QMessageBox.ActionRole)
                
                new_product_btn = msg.addButton("New Product", QMessageBox.ActionRole)
                msg.addButton("OK", QMessageBox.AcceptRole)
                
                msg.exec_()
                
                if admin_url and msg.clickedButton() == open_admin_btn:
                    import webbrowser
                    webbrowser.open(admin_url)
                elif msg.clickedButton() == new_product_btn:
                    self.reset_form()
            
            else:
                error_msg = result.get("message") or result.get("error", "Unknown error")
                self.log(f"✗ Publish failed: {error_msg}", "error")
                logger.error(f"Publish failed: {result}")
                
                QMessageBox.warning(
                    self, "Publish Failed",
                    f"Could not publish to website:\\n\\n{error_msg}"
                )
        
        except Exception as e:
            self.log(f"✗ Publish error: {e}", "error")
            logger.error(f"Publish exception: {e}")
            QMessageBox.critical(self, "Error", f"Publish error: {e}")
        
        self.status_label.setText("Ready")

'''

if 'def publish_to_website' not in content:
    # Insert before export_package method
    if 'def export_package(self):' in content:
        content = content.replace(
            '    def export_package(self):',
            publish_method + '    def export_package(self):'
        )
        print("  + Added publish_to_website method")
        changes_made += 1
    else:
        print("  ? Could not find export_package method")

# ============================================================
# Save the file
# ============================================================
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nDone! Made {changes_made} changes to main.py")

if changes_made > 0:
    print("\nNext steps:")
    print("1. Copy website_publisher.py to modules/")
    print("2. Add PRODUCT_INGEST_API_KEY to .env")
    print("3. Add route.ts to your website")
    print("4. Run: python main.py")
else:
    print("\nNo changes needed (already configured)")
