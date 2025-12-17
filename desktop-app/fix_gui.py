#!/usr/bin/env python3
"""
Kollect-It GUI Fix Script
Run from your desktop-app folder
Command: py -3.12 fix_gui.py
"""

import re

def main():
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # ===========================================
    # FIX 1: Browse buttons too narrow
    # ===========================================
    content = content.replace(
        'self.browse_btn.setMaximumWidth(150)',
        'self.browse_btn.setMinimumWidth(140)'
    )
    content = content.replace(
        'self.browse_files_btn.setMaximumWidth(150)',
        'self.browse_files_btn.setMinimumWidth(140)'
    )
    print("✓ Fix 1: Browse buttons width corrected")

    # ===========================================
    # FIX 2: Form label min-width too small
    # ===========================================
    content = content.replace(
        'min-width: 90px;',
        'min-width: 130px;'
    )
    print("✓ Fix 2: Form label min-width increased")

    # ===========================================
    # FIX 3: Product Details form layout alignment
    # ===========================================
    old_form = '''form = QFormLayout()
        form.setSpacing(12)'''
    
    new_form = '''form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)'''
    
    content = content.replace(old_form, new_form)
    print("✓ Fix 3: Product Details form layout fixed")

    # ===========================================
    # FIX 4: SEO tab form layout alignment
    # ===========================================
    old_seo = '''seo_layout = QFormLayout(seo_tab)
        seo_layout.setSpacing(12)'''
    
    new_seo = '''seo_layout = QFormLayout(seo_tab)
        seo_layout.setSpacing(12)
        seo_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        seo_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)'''
    
    content = content.replace(old_seo, new_seo)
    print("✓ Fix 4: SEO tab form layout fixed")

    # ===========================================
    # FIX 5: Settings tab form layout alignment
    # ===========================================
    old_settings = '''settings_layout = QFormLayout(settings_tab)
        settings_layout.setSpacing(12)'''
    
    new_settings = '''settings_layout = QFormLayout(settings_tab)
        settings_layout.setSpacing(12)
        settings_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        settings_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)'''
    
    content = content.replace(old_settings, new_settings)
    print("✓ Fix 5: Settings tab form layout fixed")

    # ===========================================
    # FIX 6: Regenerate SKU button too narrow
    # ===========================================
    content = content.replace(
        'self.regenerate_sku_btn.setMaximumWidth(40)',
        'self.regenerate_sku_btn.setFixedWidth(100)'
    )
    content = content.replace(
        'self.regenerate_sku_btn = QPushButton("Regenerate")',
        'self.regenerate_sku_btn = QPushButton("Regen")'
    )
    print("✓ Fix 6: Regenerate SKU button fixed")

    # Write the fixed content
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n" + "="*50)
    print("All GUI fixes applied successfully!")
    print("="*50)
    print("\nNow run: py -3.12 main.py")

if __name__ == "__main__":
    main()