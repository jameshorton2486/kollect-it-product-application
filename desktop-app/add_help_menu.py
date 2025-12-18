# add_help_menu.py
# Run with: python add_help_menu.py
# From: C:\Users\james\Kollect-It Product Application\desktop-app

import re

print("Adding Help menu to main.py...")

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if already modified
if 'help_dialog' in content:
    print("Already has help_dialog import!")
else:
    # Add import
    old_import = "from modules.widgets import DropZone, ImageThumbnail"
    new_import = """from modules.widgets import DropZone, ImageThumbnail
from modules.help_dialog import show_quick_start"""
    
    content = content.replace(old_import, new_import)
    print("  + Added help_dialog import")

# Add Help menu items
if 'Quick Start Guide' not in content:
    # Find the Help menu section and add items
    old_help = 'help_menu = menubar.addMenu("Help")'
    new_help = '''help_menu = menubar.addMenu("Help")
        
        quick_start = QAction("📚 Quick Start Guide", self)
        quick_start.setShortcut("F1")
        quick_start.triggered.connect(lambda: show_quick_start(self))
        help_menu.addAction(quick_start)
        
        help_menu.addSeparator()'''
    
    content = content.replace(old_help, new_help)
    print("  + Added Quick Start Guide to Help menu")

# Save
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nDone! Press F1 or Help → Quick Start Guide to see instructions.")
print("Now run: python main.py")
