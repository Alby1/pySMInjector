pyinstaller --onefile sminject.py
@echo off
move dist\sminject.exe .
rmdir /S /Q build
rmdir /S /Q dist
rmdir /S /Q __pycache__
del sminject.spec
pause