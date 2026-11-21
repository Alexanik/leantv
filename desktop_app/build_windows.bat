@echo off
chcp 65001 > nul
echo === Сборка автономного LeanTV (CLI) для Windows ===

python -m pip install --quiet pyinstaller --no-warn-script-location

python -m PyInstaller --clean --noconfirm lean.spec

echo.
echo === СБОРКА УСПЕШНО ЗАВЕРШЕНА! ===
echo Автономный файл (ADB + APK внутри): dist\lean.exe
echo Для запуска выполните: dist\lean.exe
pause
