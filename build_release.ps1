# Neon Space Defender - Быстрая сборка APK для Windows
# Использование: .\build_release.ps1

Write-Host "🚀 NEON SPACE DEFENDER - APK Build Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Проверка Python
Write-Host "`n[1/5] Проверка Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python найден: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python не установлен!" -ForegroundColor Red
    exit 1
}

# Проверка Buildozer
Write-Host "`n[2/5] Проверка Buildozer..." -ForegroundColor Yellow
try {
    $buildozerVersion = buildozer --version 2>&1
    Write-Host "✓ Buildozer найден" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Buildozer не установлен. Установка..." -ForegroundColor Yellow
    pip install buildozer cython pillow kivy
}

# Проверка buildozer.spec
Write-Host "`n[3/5] Проверка конфигурации..." -ForegroundColor Yellow
if (-not (Test-Path "buildozer.spec")) {
    Write-Host "❌ buildozer.spec не найден!" -ForegroundColor Red
    Write-Host "Выполните: buildozer android init" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ buildozer.spec найден" -ForegroundColor Green

# Опция очистки старых сборок
if ($args[0] -eq "clean") {
    Write-Host "`nУдаляю старые артефакты..." -ForegroundColor Yellow
    buildozer android clean
}

# Сборка APK
Write-Host "`n[4/5] Сборка Debug APK..." -ForegroundColor Yellow
Write-Host "Это может занять 30-50 минут (первый раз дольше)" -ForegroundColor Magenta
Write-Host ""

$buildResult = buildozer android debug 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Debug APK успешно создан!" -ForegroundColor Green
} else {
    Write-Host "❌ Ошибка при сборке!" -ForegroundColor Red
    Write-Host $buildResult -ForegroundColor Yellow
    exit 1
}

# Поиск APK
Write-Host "`n[5/5] Поиск APK файла..." -ForegroundColor Yellow
$apkFiles = Get-ChildItem -Recurse -Filter "*debug.apk" 2>/dev/null
if ($apkFiles.Count -eq 0) {
    Write-Host "❌ APK файл не найден!" -ForegroundColor Red
    exit 1
}

$apkPath = $apkFiles[0].FullName
$apkSize = "{0:N2} MB" -f ($apkFiles[0].Length / 1MB)

Write-Host "✓ APK успешно создан!" -ForegroundColor Green
Write-Host ""
Write-Host ("📱 Информация об APK:") -ForegroundColor Cyan
Write-Host "  Путь: $apkPath" -ForegroundColor White
Write-Host "  Размер: $apkSize" -ForegroundColor White
Write-Host ""

# Инструкции
Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Подключите Android-устройство (или включите эмулятор)"
Write-Host ""
Write-Host "2️⃣  Для установки Debug версии выполните:"
Write-Host "   adb install -r ""$apkPath""" -ForegroundColor Cyan
Write-Host ""
Write-Host "3️⃣  Для сборки Release версии (подписанной):"
Write-Host "   - Обновите версию в buildozer.spec" -ForegroundColor White
Write-Host "   - Выполните: buildozer android release" -ForegroundColor White
Write-Host ""
Write-Host "4️⃣  Для загрузки на Google Play:"
Write-Host "   - Посетите: https://play.google.com/console" -ForegroundColor White
Write-Host "   - Создайте приложение" -ForegroundColor White
Write-Host "   - Загрузите подписанное APK (Release версию)" -ForegroundColor White
Write-Host "   - Заполните описание, иконки, скриншоты" -ForegroundColor White
Write-Host "   - Создайте тестовый трек (Internal Testing)" -ForegroundColor White
Write-Host "   - Отправьте на review в Production" -ForegroundColor White
Write-Host ""
Write-Host "✅ Сборка завершена!" -ForegroundColor Green
