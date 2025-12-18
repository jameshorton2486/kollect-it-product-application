#!/usr/bin/env python3
"""
Help Dialog Module
Displays user instructions and quick start guide.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .theme_modern import ModernPalette


class HelpDialog(QDialog):
    """Help dialog with quick start guide and workflow instructions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kollect-It Product Manager - Help")
        self.setMinimumSize(700, 550)
        self.setStyleSheet(ModernPalette.get_stylesheet())
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("📚 Quick Start Guide")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {ModernPalette.PRIMARY}; padding: 10px;")
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Quick Start
        tabs.addTab(self._create_quickstart_tab(), "🚀 Quick Start")
        
        # Tab 2: Workflow
        tabs.addTab(self._create_workflow_tab(), "📋 Full Workflow")
        
        # Tab 3: Buttons
        tabs.addTab(self._create_buttons_tab(), "🔘 Button Guide")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedWidth(100)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
    
    def _create_quickstart_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = """
<h2>5-Step Product Workflow</h2>

<p><b>Step 1: Load Images</b></p>
<ul>
<li>Drag & drop a product folder onto the drop zone, OR</li>
<li>Click <b>Browse Folder</b> to select a folder, OR</li>
<li>Click <b>Browse Files</b> to select individual images</li>
</ul>

<p><b>Step 2: Edit Images</b></p>
<ul>
<li><b>Click any image</b> → Opens Crop Dialog (rotate, flip, crop)</li>
<li><b>Right-click</b> → Menu with Crop, Remove BG, Delete options</li>
<li><b>Ctrl+Click</b> → Select multiple images</li>
</ul>

<p><b>Step 3: Optimize</b></p>
<ul>
<li>Click <b>⚡ Optimize All</b> to convert images to WebP format</li>
<li>Original files are automatically deleted after optimization</li>
<li>Optimized images appear in a <code>processed/</code> subfolder</li>
</ul>

<p><b>Step 4: Generate Content with AI</b></p>
<ul>
<li>Click <b>🔍 Analyze Images</b> → AI identifies the item</li>
<li>Click <b>✨ Generate with AI</b> → Creates title & description</li>
<li>Click <b>💰 Price Research</b> → Suggests pricing range</li>
</ul>

<p><b>Step 5: Upload & Export</b></p>
<ul>
<li>Click <b>☁ Upload to ImageKit</b> → Images go to CDN</li>
<li>Click <b>📦 Export Package</b> → Saves product to Google Drive</li>
</ul>
"""
        
        label = QLabel(content)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        label.setStyleSheet(f"color: {ModernPalette.TEXT}; font-size: 14px; padding: 10px;")
        
        scroll = QScrollArea()
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_workflow_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = """
<h2>Complete Product Workflow</h2>

<h3>📸 Importing from Camera</h3>
<p>Use <b>+ Add New Product</b> to launch the Import Wizard:</p>
<ol>
<li>Select category (Militaria, Books, Fine Art, Collectibles)</li>
<li>Choose photos from your camera folder</li>
<li>SKU is auto-generated (e.g., MILI-2025-0001)</li>
<li>Click Import to create product folder</li>
</ol>

<h3>🖼️ Image Processing</h3>
<p>After loading images:</p>
<ul>
<li><b>Crop</b> - Click image to open crop dialog</li>
<li><b>Remove Background</b> - Right-click → Remove Background</li>
<li><b>Optimize All</b> - Converts to WebP, deletes originals</li>
</ul>

<h3>🤖 AI-Powered Features</h3>
<ul>
<li><b>Analyze Images</b> - AI examines photos and identifies the item</li>
<li><b>Generate with AI</b> - Creates professional title and description</li>
<li><b>Price Research</b> - Analyzes market and suggests pricing</li>
</ul>

<h3>☁️ Cloud Upload</h3>
<p>Upload to ImageKit stores images on CDN with URLs like:</p>
<code>https://ik.imagekit.io/kollectit/products/MILI/MILI-2025-0001/image.webp</code>

<h3>📦 Export Package</h3>
<p>Creates 3 files in Google Drive:</p>
<ul>
<li><b>product-payload.json</b> - Structured data for website import</li>
<li><b>product-info.txt</b> - Human-readable summary</li>
<li><b>imagekit-urls.txt</b> - List of all image URLs</li>
</ul>
"""
        
        label = QLabel(content)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        label.setStyleSheet(f"color: {ModernPalette.TEXT}; font-size: 14px; padding: 10px;")
        
        scroll = QScrollArea()
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_buttons_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        content = """
<h2>Button Reference</h2>

<h3>Image Action Buttons</h3>
<table border="0" cellpadding="8">
<tr><td><b>✂ Crop Selected</b></td><td>Open crop dialog for selected image</td></tr>
<tr><td><b>🎨 Remove BG</b></td><td>Remove background from selected image</td></tr>
<tr><td><b>⚡ Optimize All</b></td><td>Convert all images to WebP (deletes originals)</td></tr>
<tr><td><b>🗑 Clear All</b></td><td>Clear images from view (doesn't delete files)</td></tr>
</table>

<h3>AI Buttons</h3>
<table border="0" cellpadding="8">
<tr><td><b>🔍 Analyze Images</b></td><td>AI examines photos and identifies item type</td></tr>
<tr><td><b>✨ Generate with AI</b></td><td>Generate title and description automatically</td></tr>
<tr><td><b>💰 Price Research</b></td><td>Get market-based pricing suggestions</td></tr>
</table>

<h3>Export Buttons</h3>
<table border="0" cellpadding="8">
<tr><td><b>☁ Upload to ImageKit</b></td><td>Upload images to CDN (required before export)</td></tr>
<tr><td><b>📦 Export Package</b></td><td>Save product files to Google Drive</td></tr>
</table>

<h3>Mouse Actions on Images</h3>
<table border="0" cellpadding="8">
<tr><td><b>Left Click</b></td><td>Open Crop Dialog</td></tr>
<tr><td><b>Right Click</b></td><td>Show context menu (Crop, Remove BG, Delete, Preview)</td></tr>
<tr><td><b>Ctrl + Click</b></td><td>Multi-select images</td></tr>
<tr><td><b>Delete Key</b></td><td>Delete selected image</td></tr>
</table>

<h3>Keyboard Shortcuts</h3>
<table border="0" cellpadding="8">
<tr><td><b>Ctrl+N</b></td><td>New Product (Import Wizard)</td></tr>
<tr><td><b>Ctrl+O</b></td><td>Open existing product folder</td></tr>
<tr><td><b>Ctrl+S</b></td><td>Save/Export current product</td></tr>
<tr><td><b>Delete</b></td><td>Delete selected image</td></tr>
</table>
"""
        
        label = QLabel(content)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        label.setStyleSheet(f"color: {ModernPalette.TEXT}; font-size: 14px; padding: 10px;")
        
        scroll = QScrollArea()
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        return widget


def show_quick_start(parent=None):
    """Show the quick start dialog."""
    dialog = HelpDialog(parent)
    dialog.exec_()
