#!/bin/bash
# Демонстрационный скрипт для CLI клиента CRM

echo "🚀 Демонстрация CLI клиента CRM"
echo "================================"

# Проверяем наличие файла
if [ ! -f "crm.py" ]; then
    echo "❌ Файл crm.py не найден"
    exit 1
fi

echo ""
echo "1. 📋 Показываем справку"
echo "-----------------------"
python crm.py --help

echo ""
echo "2. 📋 Показываем справку по команде contacts"
echo "-------------------------------------------"
python crm.py contacts --help

echo ""
echo "3. 📋 Показываем справку по команде list"
echo "---------------------------------------"
python crm.py contacts list --help

echo ""
echo "4. 🔧 Проверяем конфигурацию"
echo "---------------------------"
CONFIG_FILE="$HOME/.crm-cli/config.ini"
if [ -f "$CONFIG_FILE" ]; then
    echo "✅ Файл конфигурации: $CONFIG_FILE"
    echo "Содержимое:"
    cat "$CONFIG_FILE"
else
    echo "❌ Файл конфигурации не найден"
fi

echo ""
echo "5. 🧪 Примеры команд (требуют запущенного сервера)"
echo "------------------------------------------------"
echo "# Создать контакт:"
echo "  python crm.py contacts create --name \"Иван Иванов\" --company \"ООО Тест\""
echo ""
echo "# Получить список контактов:"
echo "  python crm.py contacts list"
echo ""
echo "# Получить контакт по ID:"
echo "  python crm.py contacts get 1"
echo ""
echo "# Обновить контакт:"
echo "  python crm.py contacts update 1 --name \"Иван Петров\" --phone \"+79991234567\""
echo ""
echo "# Удалить контакт:"
echo "  python crm.py contacts delete 1"
echo ""
echo "# Поиск контактов:"
echo "  python crm.py contacts list --search \"Иван\" --format table"
echo ""
echo "# Пагинация:"
echo "  python crm.py contacts list --page 2 --per-page 10"

echo ""
echo "6. ⚠️  Важные замечания"
echo "----------------------"
echo "• Для работы CLI необходим запущенный сервер CRM"
echo "• Сервер по умолчанию: http://localhost:6543"
echo "• Конфигурация хранится в ~/.crm-cli/config.ini"
echo "• Можно изменить URL сервера в конфигурации"

echo ""
echo "7. 🚀 Запуск сервера (если установлены зависимости)"
echo "-------------------------------------------------"
echo "# Перейдите в директорию backend:"
echo "  cd backend"
echo ""
echo "# Создайте виртуальное окружение:"
echo "  python -m venv venv"
echo "  source venv/bin/activate  # Linux/Mac"
echo "  # или venv\\Scripts\\activate  # Windows"
echo ""
echo "# Установите зависимости:"
echo "  pip install -r requirements.txt"
echo ""
echo "# Запустите сервер:"
echo "  pserve development.ini --reload"

echo ""
echo "✅ Демонстрация завершена!"
echo ""
echo "📚 Дополнительная информация:"
echo "• Руководство по CLI: CLI_GUIDE.md"
echo "• Руководство по REST API: REST_API_GUIDE.md"
echo "• Документация структур: STRUCTURES.md"