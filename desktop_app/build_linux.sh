#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "=== Сборка автономного LeanTV (CLI) для Linux ==="

export PATH="$HOME/.local/bin:$PATH"

python3 -m pip install --quiet pyinstaller --no-warn-script-location

python3 -m PyInstaller --clean --noconfirm lean.spec

echo ""
echo "=== СБОРКА УСПЕШНО ЗАВЕРШЕНА! ==="
echo "Автономный файл (ADB + APK внутри): dist/lean"
echo "Для запуска выполните: ./dist/lean"
