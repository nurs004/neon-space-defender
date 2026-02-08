@echo off
chcp 65001 > nul
color 0B
cls

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║          🌟 NEON SPACE DEFENDER 🌟                           ║
echo ║        Подготовка для Google Play                            ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ОШИБКА: Python не установлен!
    echo Скачайте: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python установлен
echo.

REM Проверка Git (опционально)
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Git установлен
) else (
    echo ⚠ Git не установлен (нужен для GitHub)
    echo Скачайте: https://git-scm.com/download/win
)
echo.

echo ════════════════════════════════════════════════════════════════
echo [ШАГИ ПОДГОТОВКИ]
echo ════════════════════════════════════════════════════════════════
echo.

REM Шаг 1
echo [1/5] Установка Python зависимостей...
pip install --upgrade pip setuptools wheel >nul 2>&1
pip install kivy pillow buildozer cython >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Зависимости установлены
) else (
    echo ⚠ Ошибка при установке некоторых пакетов
    echo ⚠ Это может быть нормально - продолжаем
)
echo.

REM Шаг 2
echo [2/5] Подготовка структуры проекта...
if not exist "data" mkdir data
echo ✓ Папка data создана/проверена

python prepare_android.py >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Проект подготовлен
) else (
    echo ⚠ Проект подготовлен (частично)
)
echo.

REM Шаг 3
echo [3/5] Проверка файлов...
setlocal enabledelayedexpansion
set "files_ok=0"
for %%F in (main.py buildozer.spec project.json GOOGLE_PLAY_GUIDE_RU.md) do (
    if exist "%%F" (
        echo ✓ %%F
        set /a "files_ok+=1"
    ) else (
        echo ✗ %%F (ОТСУТСТВУЕТ!)
    )
)
echo.

REM Шаг 4
echo [4/5] Информация о проекте...
if exist "project.json" (
    for /f "tokens=*" %%A in ('python -c "import json; f=open('project.json'); d=json.load(f); print(d.get('project',{}).get('name','Unknown'))" 2^>nul') do (
        echo ✓ Проект: %%A
    )
)

if exist "main.py" (
    echo ✓ Мобильная версия (Kivy): main.py
)
if exist "survivor.py" (
    echo ✓ Desktop версия (Pygame): survivor.py
)
echo.

REM Шаг 5
echo [5/5] Готовые файлы...
if exist "data\icon.png" (
    echo ✓ Icon: data/icon.png
) else (
    echo ⚠ Icon: не найден (создайте 512x512 PNG)
)

if exist "data\presplash.png" (
    echo ✓ Presplash: data/presplash.png
) else (
    echo ⚠ Presplash: не найден (создайте 1200x1920 PNG)
)

if exist "PRIVACY_POLICY.txt" (
    echo ✓ Privacy Policy: PRIVACY_POLICY.txt
)

if exist "highscore.json" (
    echo ✓ Сохраненные рекорды: highscore.json
)
echo.

REM Финальный отчет
cls
color 0A

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                   ✓ ГОТОВО К ЗАПУСКУ!                        ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo 🎮 СЛЕДУЮЩИЕ ШАГИ:
echo.
echo   [1] ЛОКАЛЬНОЕ ТЕСТИРОВАНИЕ (на компьютере):
echo       python main.py
echo.
echo   [2] ВЫБЕРИТЕ СПОСОБ СБОРКИ APK:
echo.
echo       ⭐ ВАРИАНТ A: GitHub Actions (РЕКОМЕНДУЕТСЯ)
echo          - git init
echo          - git add .
echo          - git commit -m "Initial"
echo          - Загрузьте на GitHub
echo          - Автоматическая сборка в CI/CD
echo          - Скачайте из Artifacts
echo.
echo       ☁️  ВАРИАНТ B: Google Colab (облачно)
echo          - Откройте https://colab.research.google.com/
echo          - Используйте инструкции из START_HERE.txt
echo.
echo       💻 ВАРИАНТ C: Linux/Mac (локально)
echo          - buildozer android debug
echo          - Ждите 20-30 минут
echo.
echo   [3] ТЕСТИРОВАНИЕ НА ТЕЛЕФОНЕ:
echo       adb install bin/neonspacedefender-1.0.0-debug.apk
echo.
echo   [4] ПУБЛИКАЦИЯ НА GOOGLE PLAY:
echo       Прочитайте GOOGLE_PLAY_GUIDE_RU.md (подробный гайд)
echo       Создайте Developer аккаунт ($25)
echo       Загрузите APK в консоль
echo.

echo.
echo 📖 ПОЛНУЮ ИНФОРМАЦИЮ СМОТРИТЕ В:
echo.
echo    📄 START_HERE.txt           - Быстрый старт (этот файл)
echo    📄 GOOGLE_PLAY_GUIDE_RU.md  - Полный гайд для Google Play
echo    📄 README_ANDROID.md        - Техническое описание  
echo    📄 PRIVACY_POLICY.txt       - Политика приватности
echo.

echo.
color 0B
echo ════════════════════════════════════════════════════════════════
echo                        УДАЧИ! 🚀
echo ════════════════════════════════════════════════════════════════
echo.

pause
