cd "C:\Users\james\Kollect-It Product Application"
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install PyQt5 Pillow python-dotenv requests anthropic python-docx numpy
cd desktop-app
python main.py