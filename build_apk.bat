@echo off
REM Neon Space Defender - Buildozer Setup для Android

echo ============================================
echo NEON SPACE DEFENDER - APK Builder
echo ============================================
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python не установлен!
    exit /b 1
)

echo [1/4] Установка зависимостей...
pip install kivy buildozer cython openpyxl
pip install --upgrade setuptools pip

echo [2/4] Проверка структуры проекта...
if not exist "data" mkdir data
echo Created data directory

echo [3/4] Создание временных файлов...
REM Создаем простую иконку в Python
python -c "
from PIL import Image, ImageDraw
import os

# Создаем папку
os.makedirs('data', exist_ok=True)

# Иконка (512x512 для Google Play)
img = Image.new('RGBA', (512, 512), (10, 15, 30, 255))
draw = ImageDraw.Draw(img)

# Цвет киана
cyan = (0, 255, 255, 255)
pink = (255, 0, 255, 255)

# Рисуем звёзды
for i in range(20):
    import random
    x = random.randint(50, 450)
    y = random.randint(50, 450)
    draw.ellipse([x, y, x+5, y+5], fill=(200, 200, 200, 255))

# Рисуем текст
draw.text((50, 200), 'NEON', fill=cyan, font=None)
draw.text((50, 280), 'SPACE', fill=cyan, font=None)
draw.text((50, 360), 'DEFENDER', fill=pink, font=None)

img.save('data/icon.png')
print('✓ Icon created: data/icon.png')

# Presplash (1200x1920)
splash = Image.new('RGB', (1200, 1920), (10, 15, 30))
splash.save('data/presplash.png')
print('✓ Presplash created: data/presplash.png')
" 2>nul || echo ⚠ PIL not installed (optional)

echo.
echo [4/4] ГОТОВО К СБОРКЕ!
echo.
echo ============================================
echo ИНСТРУКЦИИ ДЛЯ СБОРКИ:
echo ============================================
echo.
echo ВАРИАНТ 1 - Linux/Mac (Рекомендуется):
echo   cd /path/to/my_mini_game
echo   buildozer android debug
echo   (Создаст файл: bin/neonspacedefender-1.0.0-debug.apk)
echo.
echo ВАРИАНТ 2 - Windows:
echo   1. Используйте WSL2 (Windows Subsystem for Linux)
echo   2. Или используйте виртуальную машину Linux
echo   3. Или облачный сервис (BeeWare)
echo.
echo ВАРИАНТ 3 - Облачная сборка (EASIEST):
echo   Используйте https://briefcase.readthedocs.io/
echo   или облачный сервис типа App Center
echo.
echo ============================================
echo АЛЬТЕРНАТИВА - Online APK Builder:
echo ============================================
echo 1. Загрузите файлы на https://anvil.kivy.org/
echo 2. Или используйте https://www.buildozer.ai/
echo.
echo ============================================
pause
