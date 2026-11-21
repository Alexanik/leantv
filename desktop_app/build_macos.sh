#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "=== Сборка автономного LeanTV (CLI) для macOS ==="

# Добавляем стандартные пути установки pip в PATH
export PATH="$HOME/Library/Python/3.9/bin:$HOME/Library/Python/3.10/bin:$HOME/Library/Python/3.11/bin:$HOME/Library/Python/3.12/bin:$HOME/.local/bin:$PATH"

# Проверка и установка pyinstaller
python3 -m pip install --quiet pyinstaller --no-warn-script-location

# Проверка наличия ресурсов
if [ ! -f "resources/lean_home.apk" ]; then
    echo "Предупреждение: resources/lean_home.apk не найден, копируем из tv_launcher_source..."
    cp ../tv_launcher_source/lean_home.apk resources/lean_home.apk 2>/dev/null || true
fi

# Сборка единого бинарника lean через lean.spec (включает APK и универсальный ADB)
python3 -m PyInstaller --clean --noconfirm lean.spec

echo ""
echo "=== СБОРКА УСПЕШНО ЗАВЕРШЕНА! ==="
echo "Автономный исполняемый файл (ADB + APK внутри): dist/lean"
echo "Размер: $(ls -lh dist/lean | awk '{print $5}')"
echo "Для запуска выполните: ./dist/lean"
