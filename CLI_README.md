# CLI клиент для CRM системы

## 🎯 Обзор

CLI клиент `crm.py` предоставляет удобный командный интерфейс для работы с личной CRM системой через REST API. Клиент поддерживает полный CRUD для контактов с пагинацией, поиском и фильтрацией.

## 📁 Структура проекта

```
crm.py                    # Основной файл CLI клиента (18.5 КБ)
test_cli.py              # Тестовый скрипт для проверки CLI
demo_cli.sh              # Демонстрационный скрипт
CLI_GUIDE.md             # Подробное руководство по использованию
CLI_README.md            # Этот файл
```

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install requests
```

### 2. Запуск сервера CRM
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
pserve development.ini --reload
```

### 3. Использование CLI клиента
```bash
# Показать справку
python crm.py --help

# Создать контакт
python crm.py contacts create --name "Иван Иванов" --company "ООО Тест"

# Получить список контактов
python crm.py contacts list

# Получить контакт по ID
python crm.py contacts get 1

# Обновить контакт
python crm.py contacts update 1 --name "Иван Петров"

# Удалить контакт
python crm.py contacts delete 1
```

## 🌟 Особенности

### ✅ Реализовано
1. **Полный CRUD для контактов** - создание, чтение, обновление, удаление
2. **Пагинация** - поддержка `--page` и `--per-page` параметров
3. **Поиск и фильтрация** - поиск по имени/компании, фильтрация по компании
4. **Несколько форматов вывода** - табличный и подробный форматы
5. **Конфигурация** - автоматическое создание конфигурационного файла
6. **Обработка ошибок** - понятные сообщения об ошибках
7. **Подтверждение удаления** - запрос подтверждения при удалении
8. **Подробный вывод** - опция `--verbose` для детальной информации

### 📊 Форматы вывода
- **Подробный формат (по умолчанию)**: Читаемый формат с эмодзи
- **Табличный формат (`--format table`)**: Компактная таблица для больших списков

### ⚙️ Конфигурация
- Автоматическое создание `~/.crm-cli/config.ini`
- Настройки API (URL, таймаут)
- Настройки отображения (формат даты, элементов на странице)

## 📝 Примеры использования

### Базовые операции
```bash
# Создание
python crm.py contacts create --name "Алексей Смирнов" --company "ООО Альфа"

# Чтение
python crm.py contacts list
python crm.py contacts get 1

# Обновление
python crm.py contacts update 1 --phone "+7 (999) 111-22-33"

# Удаление
python crm.py contacts delete 1
```

### Поиск и фильтрация
```bash
# Поиск по имени
python crm.py contacts list --search "Иван"

# Фильтрация по компании
python crm.py contacts list --company "ООО Альфа"

# Комбинированный поиск
python crm.py contacts list --search "Иван" --company "ООО Тест"
```

### Пагинация и форматирование
```bash
# Пагинация
python crm.py contacts list --page 2 --per-page 10

# Табличный формат
python crm.py contacts list --format table

# Подробный вывод
python crm.py contacts list --verbose
```

## 🧪 Тестирование

### Запуск тестов
```bash
python test_cli.py
```

### Ожидаемый вывод
```
✅ Все тесты пройдены успешно!
✅ CLI клиент готов к использованию!
```

### Проверенные функции
1. Структура CLI клиента
2. Импорты модулей
3. Модель Contact
4. Директория конфигурации
5. Вывод справки
6. Справка команды contacts
7. Справка команды list

## 🔧 Технические детали

### Архитектура
```
crm.py
├── Config              # Управление конфигурацией
├── Contact             # Модель контакта
├── CRMClient           # API клиент
├── CRMError            # Обработка ошибок
├── Валидация           # Валидация входных данных
├── Утилиты отображения # Форматирование вывода
├── Команды             # Обработчики команд
└── Парсер аргументов   # Разбор командной строки
```

### Модель Contact
```python
@dataclass
class Contact:
    id: Optional[int] = None
    full_name: str = ''
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contact': ...
    def display(self, verbose: bool = False) -> str: ...
```

### API клиент
```python
class CRMClient:
    def list_contacts(self, page=1, per_page=20, search=None, company=None): ...
    def get_contact(self, contact_id: int) -> Contact: ...
    def create_contact(self, contact: Contact) -> Contact: ...
    def update_contact(self, contact_id: int, contact: Contact) -> Contact: ...
    def delete_contact(self, contact_id: int) -> None: ...
```

## 📚 Документация

### Основная документация
- [CLI_GUIDE.md](CLI_GUIDE.md) - Подробное руководство по использованию
- [REST_API_GUIDE.md](REST_API_GUIDE.md) - Руководство по REST API
- [STRUCTURES.md](STRUCTURES.md) - Структуры данных и API
- [ARCHITECTURE.md](ARCHITECTURE.md) - Архитектура приложения

### Быстрые ссылки
- `python crm.py --help` - Основная справка
- `python crm.py contacts --help` - Справка по команде contacts
- `python crm.py contacts list --help` - Справка по команде list

## 🔄 Расширение

### Добавление новых команд
1. Добавьте функцию-обработчик в раздел "Команды"
2. Добавьте парсер аргументов в `create_parser()`
3. Добавьте обработку команды в `main()`

### Пример добавления команды для встреч
```python
# В create_parser()
meetings_parser = subparsers.add_parser('meetings', help='Работа со встречами')

# В main()
if args.command == 'meetings':
    handle_meetings(args, client, config)
```

## ⚠️ Устранение неисправностей

### Общие проблемы
1. **Сервер не доступен** - Проверьте, что сервер CRM запущен
2. **Ошибка конфигурации** - Проверьте `~/.crm-cli/config.ini`
3. **Неверные параметры** - Используйте `--help` для проверки синтаксиса

### Логирование
Для отладки можно добавить логирование в `CRMClient._request()`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Поддержка

### Полезные команды
```bash
# Проверить подключение к серверу
curl http://localhost:6543/api/v1.0/contacts

# Просмотреть конфигурацию
cat ~/.crm-cli/config.ini

# Запустить демонстрацию
./demo_cli.sh
```

### Дополнительная помощь
- Проверьте логи сервера CRM
- Убедитесь, что порт 6543 не занят
- Проверьте формат JSON в запросах

---

**Версия:** 1.0.0  
**Python:** 3.8+  
**Зависимости:** requests  
**Лицензия:** MIT  
**Автор:** EugeneAI Assistant  
**Дата:** $(date)