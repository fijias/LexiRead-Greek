@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto missing
".venv\Scripts\python.exe" -m scripts.setup --language el
exit /b %ERRORLEVEL%
:missing
powershell.exe -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Run INSTALL.bat first to install LexiRead Greek. / Сначала запустите INSTALL.bat для установки LexiRead Greek.','LexiRead Greek')" >nul
exit /b 1
