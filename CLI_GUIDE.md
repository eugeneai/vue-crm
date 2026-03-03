# Руководство по CLI клиенту CRM

## 📋 Обзор

CLI клиент `crm.py` предоставляет командный интерфейс для работы с личной CRM системой через REST API. Клиент поддерживает все основные операции CRUD для контактов.

## 🚀 Быстрый старт

### Установка зависимостей
```bash
# Установите requests если еще не установлен
pip install requests
```

### Запуск сервера CRM
```bash
cd backend
# Установите зависимости и запустите сервер
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
pserve development.ini --reload
```

### Использование CLI клиента
```bash
# Показать справку
python crm.py --help

# Показать справку по команде contacts
python crm.py contacts --help

# Показать справку по конкретной подкоманде
python crm.py contacts list --help
```

## 📝 Команды для работы с контактами

### 📋 Получить список контактов
```bash
# Базовый список
python crm.py contacts list

# С пагинацией
python crm.py contacts list --page 2 --per-page 10

# С поиском
python crm.py contacts list --search "Иван"

# С фильтрацией по компании
python crm.py contacts list --company "ООО Тест"

# В табличном формате
python crm.py contacts list --format table

# Подробный вывод
python crm.py contacts list --verbose
```

### 👤 Получить контакт по ID
```bash
python crm.py contacts get 1
```

### ➕ Создать новый контакт
```bash
# Минимальные данные
python crm.py contacts create --name "Иван Иванов"

# Полные данные
python crm.py contacts create \
  --name "Иван Иванов" \
  --company "ООО Рога и Копыта" \
  --phone "+7 (999) 123-45-67" \
  --email "ivan@example.com"
```

### ✏️ Обновить контакт
```bash
# Обновить имя
python crm.py contacts update 1 --name "Иван Петров"

# Обновить несколько полей
python crm.py contacts update 1 \
  --name "Иван Петров" \
  --company "ООО Новая Компания" \
  --phone "+7 (999) 987-65-43"
```

### ❌ Удалить контакт
```bash
# С подтверждением
python crm.py contacts delete 1

# Без подтверждения
python crm.py contacts delete 1 --yes
```

## ⚙️ Конфигурация

### Файл конфигурации
CLI клиент автоматически создает файл конфигурации в `~/.crm-cli/config.ini` при первом запуске.

### Настройки по умолчанию
```ini
[api]
base_url = http://localhost:6543/api/v1.0
timeout = 30

[display]
date_format = %Y-%m-%d %H:%M
items_per_page = 20
```

### Изменение настроек
Вы можете вручную отредактировать файл конфигурации или использовать следующие переменные окружения:

- `CRM_API_URL` - URL API сервера
- `CRM_API_TIMEOUT` - Таймаут запросов в секундах

## 🧪 Примеры использования

### Пример 1: Создание и управление контактами
```bash
# Создать контакт
python crm.py contacts create --name "Алексей Смирнов" --company "ООО Альфа"

# Получить список
python crm.py contacts list

# Обновить контакт
python crm.py contacts update 1 --phone "+7 (999) 111-22-33"

# Удалить контакт
python crm.py contacts delete 1
```

### Пример 2: Поиск и фильтрация
```bash
# Найти всех Иванов
python crm.py contacts list --search "Иван" --format table

# Найти контакты из определенной компании
python crm.py contacts list --company "ООО Альфа" --verbose

# Просмотреть вторую страницу результатов
python crm.py contacts list --page 2 --per-page 5
```

## 🔧 Интеграция с другими инструментами

### Использование в скриптах
```bash
#!/bin/bash
# Скрипт для экспорта контактов в CSV

echo "ID,Имя,Компания,Телефон,Email" > contacts.csv

# Получить все страницы контактов
page=1
while true; do
  python crm.py contacts list --page $page --per-page 100 --format table > temp.txt
  
  # Проверяем, есть ли данные
  if ! grep -q "ID.*Имя" temp.txt; then
    break
  fi
  
  # Парсим и добавляем в CSV
  tail -n +3 temp.txt >> contacts.csv
  
  page=$((page + 1))
done

echo "Экспорт завершен: contacts.csv"
```

### Использование с jq для обработки JSON
```bash
# Получить контакты в JSON формате (требуется модификация CLI)
# python crm.py contacts list --format json | jq '.data[] | {id, name: .full_name}'
```

## ⚠️ Обработка ошибок

### Типичные ошибки и решения

1. **Сервер не доступен**
   ```
   ❌ Ошибка: Не удалось подключиться к серверу: http://localhost:6543
   ```
   **Решение:** Убедитесь, что сервер CRM запущен.

2. **Неверный формат данных**
   ```
   ❌ Ошибка: Имя контакта обязательно (--name)
   ```
   **Решение:** Укажите обязательные параметры.

3. **Ресурс не найден**
   ```
   ❌ Ошибка: API Error 404: Контакт с ID 999 не найден
   ```
   **Решение:** Проверьте правильность ID.

4. **Ошибка валидации**
   ```
   ❌ Ошибка: API Error 422: Ошибка валидации данных
   ```
   **Решение:** Проверьте формат входных данных.

## 📊 Форматы вывода

### Подробный формат (по умолчанию)
```
👤 Иван Иванов
   ID: 1
   🏢 Компания: ООО Рога и Копыта
   📞 Телефон: +7 (999) 123-45-67
   ✉️  Email: ivan@example.com
```

### Табличный формат (`--format table`)
```
ID | Имя          | Компания            | Телефон         | Email
---|--------------|---------------------|-----------------|-------------------
1  | Иван Иванов  | ООО Рога и Копыта   | +7 (999) 123-45-67 | ivan@example.com
2  | Петр Петров  | ООО Альфа           | +7 (999) 987-65-43 | petr@example.com
```

### Пагинация
При выводе списков отображается информация о пагинации:
```
📄 Страница 1 из 5 (всего: 95)
   Навигация: следующая →
```

## 🔄 Расширение функциональности

### Добавление новых команд
Вы можете расширить CLI клиент, добавив новые команды в файл `crm.py`:

1. Добавьте новую функцию-обработчик
2. Добавьте парсер аргументов в `create_parser()`
3. Добавьте обработку команды в `main()`

### Пример добавления команды для встреч
```python
# В create_parser()
meetings_parser = subparsers.add_parser('meetings', help='Работа со встречами')
meetings_subparsers = meetings_parser.add_subparsers(dest='subcommand', required=True)

# В main()
if args.command == 'meetings':
    if args.subcommand == 'list':
        handle_meetings_list(args, client, config)
```

## 📚 Дополнительная информация

### Ссылки
- [Документация REST API](REST_API_GUIDE.md)
- [Структуры данных](STRUCTURES.md)
- [Архитектура приложения](ARCHITECTURE.md)

### Поддержка
При возникновении проблем:
1. Проверьте, что сервер CRM запущен
2. Проверьте настройки в `~/.crm-cli/config.ini`
3. Запустите с `--verbose` для подробного вывода
4. Проверьте логи сервера CRM

---

**Версия CLI:** 1.0.0  
**Требуемая версия Python:** 3.8+  
**Зависимости:** requests  
**Автор:** EugeneAI Assistant