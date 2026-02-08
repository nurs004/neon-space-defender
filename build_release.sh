#!/bin/bash
# Neon Space Defender - Быстрая сборка APK для публикации
# Использование: ./build_release.sh

set -e

echo "🚀 NEON SPACE DEFENDER - APK Build Script"
echo "=========================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Проверка зависимостей
echo -e "\n${YELLOW}[1/5] Проверка зависимостей...${NC}"
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python не установлен!${NC}"
    exit 1
fi

if ! python -c "import kivy" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Kivy не установлен. Установка...${NC}"
    pip install kivy buildozer cython pillow
fi

echo -e "${GREEN}✓ Все зависимости найдены${NC}"

# 2. Проверка buildozer.spec
echo -e "\n${YELLOW}[2/5] Проверка конфигурации buildozer...${NC}"
if [ ! -f "buildozer.spec" ]; then
    echo -e "${RED}❌ buildozer.spec не найден!${NC}"
    echo "Выполните: buildozer android init"
    exit 1
fi

echo -e "${GREEN}✓ buildozer.spec найден${NC}"

# 3. Очистка старых billdов
echo -e "\n${YELLOW}[3/5] Очистка старых сборок...${NC}"
if [ "$1" == "clean" ]; then
    echo "Удаляю старые артефакты..."
    buildozer android clean
fi

# 4. Сборка Debug APK
echo -e "\n${YELLOW}[4/5] Сборка Debug APK...${NC}"
echo "Это может занять 30-50 минут (первый раз дольше)"

if buildozer android debug; then
    echo -e "${GREEN}✓ Debug APK успешно создан!${NC}"
else
    echo -e "${RED}❌ Ошибка при сборке!${NC}"
    exit 1
fi

# 5. Поиск и вывод пути к APK
echo -e "\n${YELLOW}[5/5] Поиск APK файла...${NC}"
APK_PATH=$(find . -name "*debug.apk" -type f | head -1)

if [ -z "$APK_PATH" ]; then
    echo -e "${RED}❌ APK файл не найден!${NC}"
    exit 1
fi

APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
echo -e "${GREEN}✓ APK успешно создан!${NC}"
echo ""
echo "📱 Информация об APK:"
echo "  Путь: $APK_PATH"
echo "  Размер: $APK_SIZE"
echo ""

# 6. Инструкции по установке на устройство
echo -e "${YELLOW}Следующие шаги:${NC}"
echo ""
echo "1️⃣  Подключите Android-устройство (или включите эмулятор)"
echo ""
echo "2️⃣  Для установки Debug версии выполните:"
echo "   adb install -r \"$APK_PATH\""
echo ""
echo "3️⃣  Для сборки Release версии (подписанной):"
echo "   - Обновите версию в buildozer.spec"
echo "   - Выполните: buildozer android release"
echo "   - Результат будет в: bin/neon_space_defender-*-release.apk"
echo ""
echo "4️⃣  Для загрузки на Google Play:"
echo "   - Посетите: https://play.google.com/console"
echo "   - Создайте приложение"
echo "   - Загрузите подписанное APK"
echo "   - Заполните описание, иконки, скриншоты"
echo "   - Отправьте на review"
echo ""
echo -e "${GREEN}✅ Сборка завершена!${NC}"
