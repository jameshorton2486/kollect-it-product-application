#!/usr/bin/env python3
"""
PATCH: safe_settings_dialog.py
Fixes potential None access when saving settings.

INSTALLATION:
Replace save_settings_from_dialog() in main.py with this version.
"""


def save_settings_from_dialog(self, dialog):
    """Save settings from the settings dialog - WITH SAFETY CHECKS."""
    
    # FIX: Guard against None widgets
    # This can happen if dialog setup failed partway through
    
    # Ensure config sections exist
    if "api" not in self.config:
        self.config["api"] = {}
    if "imagekit" not in self.config:
        self.config["imagekit"] = {}
    if "ai" not in self.config:
        self.config["ai"] = {}
    if "image_processing" not in self.config:
        self.config["image_processing"] = {}

    # API settings - WITH SAFETY CHECKS
    if self.api_key_edit is not None:
        self.config["api"]["SERVICE_API_KEY"] = self.api_key_edit.text()
    
    if self.prod_url_edit is not None:
        self.config["api"]["production_url"] = self.prod_url_edit.text()
    
    if self.use_prod_check is not None:
        self.config["api"]["use_production"] = self.use_prod_check.isChecked()

    # ImageKit settings - WITH SAFETY CHECKS
    if self.ik_public_edit is not None:
        self.config["imagekit"]["public_key"] = self.ik_public_edit.text()
    
    if self.ik_private_edit is not None:
        self.config["imagekit"]["private_key"] = self.ik_private_edit.text()
    
    if self.ik_url_edit is not None:
        self.config["imagekit"]["url_endpoint"] = self.ik_url_edit.text()

    # AI settings - WITH SAFETY CHECKS
    # Note: API key is read from ANTHROPIC_API_KEY env var only, not saved to config
    if self.ai_model_edit is not None:
        self.config["ai"]["model"] = self.ai_model_edit.text()

    # Image processing settings - WITH SAFETY CHECKS
    if self.max_dim_spin is not None:
        self.config["image_processing"]["max_dimension"] = self.max_dim_spin.value()
    
    if self.quality_spin is not None:
        self.config["image_processing"]["webp_quality"] = self.quality_spin.value()
    
    if self.strip_exif_check is not None:
        self.config["image_processing"]["strip_exif"] = self.strip_exif_check.isChecked()

    # Save to file
    try:
        self.save_config()
        QMessageBox.information(dialog, "Settings Saved", "Settings have been saved successfully.")
        dialog.accept()
    except Exception as e:
        QMessageBox.warning(dialog, "Save Error", f"Failed to save settings:\n{e}")


# =============================================================================
# MANUAL PATCH INSTRUCTIONS:
# =============================================================================
#
# In save_settings_from_dialog(), add None checks before accessing each widget:
#
# BEFORE:
#     self.config["api"]["SERVICE_API_KEY"] = self.api_key_edit.text()
#
# AFTER:
#     if self.api_key_edit is not None:
#         self.config["api"]["SERVICE_API_KEY"] = self.api_key_edit.text()
#
# Apply this pattern to ALL widget accesses in the method.
#
# Also add try/except around save_config() for error handling.
#
# =============================================================================
