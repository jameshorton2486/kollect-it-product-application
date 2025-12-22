#!/usr/bin/env python3
"""
PATCH: thread_cleanup.py
Fixes memory leak by properly cleaning up ProcessingThread after completion.

INSTALLATION:
Add these methods to your KollectItApp class, replacing the existing ones.
"""


# =============================================================================
# METHOD 1: on_processing_finished - ADD CLEANUP
# =============================================================================

def on_processing_finished(self, results: dict):
    """Handle processing completion - WITH CLEANUP."""
    # Re-enable buttons
    self.optimize_btn.setEnabled(True)
    self.upload_btn.setEnabled(True)

    success_count = len(results.get("images", []))
    error_count = len(results.get("errors", []))

    self.log(f"Optimization complete: {success_count} images processed", "success")

    if error_count > 0:
        self.log(f"Errors: {error_count} images failed", "warning")

    # Reload to show processed images
    processed_folder = Path(self.current_folder) / "processed"
    if processed_folder.exists():
        self.load_images_from_folder(str(processed_folder))

    # FIX: Clean up thread reference to prevent memory leak
    if self.processing_thread is not None:
        self.processing_thread.deleteLater()
        self.processing_thread = None


# =============================================================================
# METHOD 2: on_processing_error - ADD CLEANUP
# =============================================================================

def on_processing_error(self, error: str):
    """Handle processing errors - WITH CLEANUP."""
    self.optimize_btn.setEnabled(True)
    self.log(f"Processing error: {error}", "error")
    self.status_label.setText("Error during processing")

    # FIX: Clean up thread reference to prevent memory leak
    if self.processing_thread is not None:
        self.processing_thread.deleteLater()
        self.processing_thread = None


# =============================================================================
# METHOD 3: closeEvent - ENSURE THREAD STOPS
# =============================================================================

def closeEvent(self, event):
    """Handle application close event - cleanup temporary directories AND threads."""
    import shutil
    
    # FIX: Stop any running processing thread
    if self.processing_thread is not None:
        if self.processing_thread.isRunning():
            self.processing_thread.terminate()
            self.processing_thread.wait(2000)  # Wait up to 2 seconds
        self.processing_thread.deleteLater()
        self.processing_thread = None
    
    # Clean up temporary directories
    for temp_dir in getattr(self, '_temp_dirs', []):
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception:
            pass
    
    super().closeEvent(event)


# =============================================================================
# MANUAL PATCH INSTRUCTIONS:
# =============================================================================
#
# 1. Find on_processing_finished() in main.py
# 2. Add at the END of the method:
#
#    # Clean up thread reference
#    if self.processing_thread is not None:
#        self.processing_thread.deleteLater()
#        self.processing_thread = None
#
# 3. Find on_processing_error() in main.py
# 4. Add at the END of the method:
#
#    # Clean up thread reference  
#    if self.processing_thread is not None:
#        self.processing_thread.deleteLater()
#        self.processing_thread = None
#
# 5. Find closeEvent() in main.py
# 6. Add BEFORE the temp dir cleanup:
#
#    # Stop any running processing thread
#    if self.processing_thread is not None:
#        if self.processing_thread.isRunning():
#            self.processing_thread.terminate()
#            self.processing_thread.wait(2000)
#        self.processing_thread.deleteLater()
#        self.processing_thread = None
#
# =============================================================================
