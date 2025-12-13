@echo off
REM Fix for main.py - removes invalid setPlaceholderText call
cd /d "C:\Users\james\Kollect-It Product Application\desktop-app"

echo Fixing main.py...

powershell -Command "(Get-Content main.py) -replace 'self.original_price_spin.setPlaceholderText\(\"Original \(optional\)\"\)', '# Placeholder removed - QDoubleSpinBox does not support this' | Set-Content main.py"

echo Done! Now run: python main.py
pause
