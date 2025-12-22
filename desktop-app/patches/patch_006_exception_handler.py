#!/usr/bin/env python3
"""
PATCH: global_exception_handler.py
Adds global exception handling to prevent silent crashes.

INSTALLATION:
Add this code at the TOP of main.py, after the imports but before any class definitions.
"""

import sys
import traceback
import logging
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import QMessageBox, QApplication


def setup_exception_handling():
    """
    Set up global exception handling for the application.
    Catches unhandled exceptions and shows user-friendly error dialog.
    """
    
    # Create logs directory
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Set up file logging for crashes
    crash_log_file = log_dir / f"crash_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        handlers=[
            logging.FileHandler(crash_log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Global exception handler."""
        # Don't handle KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Log the exception
        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # Format error message
        error_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Write to crash log
        with open(crash_log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"CRASH: {datetime.now().isoformat()}\n")
            f.write(f"{'='*60}\n")
            f.write(error_text)
            f.write("\n")
        
        # Show error dialog if application is running
        try:
            app = QApplication.instance()
            if app:
                # Create a simplified error message for users
                user_message = (
                    f"An unexpected error occurred:\n\n"
                    f"{exc_type.__name__}: {exc_value}\n\n"
                    f"Error details have been saved to:\n"
                    f"{crash_log_file}\n\n"
                    f"Please report this issue with the log file."
                )
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Kollect-It - Error")
                msg.setText("An unexpected error occurred.")
                msg.setInformativeText(str(exc_value))
                msg.setDetailedText(error_text)
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
                
                # Close button exits app, Ok continues (risky but user's choice)
                result = msg.exec_()
                
                if result == QMessageBox.Close:
                    sys.exit(1)
        except Exception:
            # If we can't show dialog, just exit
            sys.exit(1)
    
    # Install the exception hook
    sys.excepthook = handle_exception
    
    logger.info("Global exception handling installed")
    return logger


# =============================================================================
# USAGE IN main.py:
# =============================================================================
#
# Add these lines at the TOP of main.py, after imports:
#
#     from patches.global_exception_handler import setup_exception_handling
#     logger = setup_exception_handling()
#
# OR copy this code directly into main.py and call setup_exception_handling()
# before creating QApplication.
#
# =============================================================================
# STANDALONE VERSION (if you want to paste directly into main.py):
# =============================================================================

STANDALONE_CODE = '''
# Paste this near the top of main.py, after imports

import sys
import traceback
import logging
from datetime import datetime
from pathlib import Path

def setup_exception_handling():
    """Set up global exception handling for the application."""
    
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    crash_log_file = log_dir / f"crash_{datetime.now().strftime('%Y%m%d')}.log"
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Log to file
        with open(crash_log_file, 'a', encoding='utf-8') as f:
            f.write(f"\\n{'='*60}\\n")
            f.write(f"CRASH: {datetime.now().isoformat()}\\n")
            f.write(error_text)
        
        # Show dialog
        try:
            from PyQt5.QtWidgets import QMessageBox, QApplication
            app = QApplication.instance()
            if app:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Kollect-It - Error")
                msg.setText(f"An unexpected error occurred:\\n\\n{exc_type.__name__}: {exc_value}")
                msg.setDetailedText(error_text)
                msg.exec_()
        except:
            pass
        
        sys.exit(1)
    
    sys.excepthook = handle_exception

# Call this BEFORE main()
setup_exception_handling()
'''

if __name__ == "__main__":
    print("Global Exception Handler for Kollect-It")
    print("=" * 50)
    print("\nTo use, add this import at the top of main.py:")
    print("  from patches.global_exception_handler import setup_exception_handling")
    print("\nThen call setup_exception_handling() before creating QApplication")
