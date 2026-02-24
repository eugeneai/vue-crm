# Использование SQLAlchemy моделей

## 📋 Обзор

Модели SQLAlchemy для личной CRM системы расположены в директории `backend/models/`. 
Система поддерживает гибкую конфигурацию подключения к базе данных.

## 🗄️ Модели

### **Contact (Контакты)**
```python
from models.contact import Contact

# Создание контакта
contact = Contact(
    full_name="Иван Иванов",
    company="ООО 'Технологии'",
    phone="+7 (999) 123-45-67",
    email="ivan@example.com"
)

# Валидация
is_valid, errors = Contact.validate(contact.to_dict())

# Конвертация в словарь
contact_dict = contact.to_dict()
```

### **Meeting (Встречи)**
```python
from models.meeting import Meeting
from datetime import datetime

# Создание встречи
meeting = Meeting(
    contact_id=1,
    date_time=datetime.now(),
    topic="Обсуждение проекта",
    location="Офис"
)

# Проверка предстоящих встреч
is_upcoming = meeting.is_upcoming(days=7)

# Конвертация с отношениями
meeting_dict = meeting.to_dict(include_contact=True, include_notes=True)
```

### **Note (Заметки)**
```python
from models.note import Note
from datetime import date

# Создание заметки
note = Note(
    meeting_id=1,
    date=date.today(),
    text="Текст заметки"
)

# Получение превью
preview = note.get_preview(max_length=100)

# Конвертация с встречей
note_dict = note.to_dict(include_meeting=True)
```

## 🔧 Конфигурация базы данных

### **Способы конфигурации (по приоритету):**
1. Прямой параметр `database_url`
2. Конфигурационный файл `.ini`
3. Переменная окружения `DATABASE_URL`
4. Значение по умолчанию (`sqlite:///../database/contacts.db`)

### **Примеры использования:**

**1. Прямой URL параметр:**
```python
from models import init_db, create_tables

# Инициализация с прямым URL
engine = init_db(database_url='sqlite:///test.db')

# Создание таблиц
create_tables()
```

**2. Конфигурационный файл (.ini):**
```python
from models import init_db

# Инициализация через development.ini
engine = init_db(config_file='development.ini')
```

**3. Переменная окружения:**
```bash
# Установка переменной окружения
export DATABASE_URL='sqlite:///production.db'
```

```python
from models import init_db

# Инициализация через переменную окружения
engine = init_db()  # Автоматически использует DATABASE_URL
```

**4. Значение по умолчанию:**
```python
from models import init_db

# Инициализация по умолчанию
engine = init_db()  # Использует sqlite:///../database/contacts.db
```

## 🚀 Быстрый старт

### **Минимальный пример:**
```python
#!/usr/bin/env python3
from models import init_db, create_tables, get_session, close_session
from models.contact import Contact
from models.meeting import Meeting
from models.note import Note
from datetime import datetime, date

# 1. Инициализация БД
init_db(database_url='sqlite:///:memory:')

# 2. Создание таблиц
create_tables()

# 3. Работа с данными
session = get_session()

try:
    # Создание контакта
    contact = Contact(full_name="Тестовый Контакт")
    session.add(contact)
    session.commit()
    
    # Создание встречи
    meeting = Meeting(
        contact_id=contact.id,
        date_time=datetime.now(),
        topic="Тестовая встреча"
    )
    session.add(meeting)
    session.commit()
    
    # Создание заметки
    note = Note(
        meeting_id=meeting.id,
        date=date.today(),
        text="Тестовая заметка"
    )
    session.add(note)
    session.commit()
    
    # Чтение данных
    contacts = session.query(Contact).all()
    for c in contacts:
        print(f"Контакт: {c.full_name}")
        for m in c.meetings:
            print(f"  Встреча: {m.topic}")
            for n in m.notes:
                print(f"    Заметка: {n.text[:50]}...")
                
finally:
    close_session()
```

## 📁 Структура файлов

```
backend/models/
├── __init__.py          # Инициализация и конфигурация БД
├── contact.py           # Модель Contact
├── meeting.py           # Модель Meeting  
└── note.py              # Модель Note
```

## 🔄 Работа с сессиями

### **Получение сессии:**
```python
from models import get_session, close_session

session = get_session()
try:
    # Работа с БД
    contacts = session.query(Contact).all()
finally:
    close_session()  # Важно закрывать сессию!
```

### **Контекстный менеджер (рекомендуется):**
```python
from contextlib import contextmanager
from models import get_session, close_session

@contextmanager
def db_session():
    session = get_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        close_session()

# Использование
with db_session() as session:
    contact = Contact(full_name="Новый контакт")
    session.add(contact)
    # Автоматический commit при успехе
    # Автоматический rollback при ошибке
```

## 🧪 Тестирование

### **Тестовый скрипт:**
```bash
# Запуск тестов
cd /path/to/project
python test_models.py
```

### **Демонстрация конфигурации:**
```bash
cd backend
python demo_config.py
```

## ⚙️ Конфигурационные файлы

### **development.ini (разработка):**
```ini
[app:main]
sqlalchemy.url = sqlite:///../database/contacts.db
graphql.enable_playground = true
graphql.debug = true
```

### **production.ini (продакшн):**
```ini
[app:main]
sqlalchemy.url = sqlite:///../database/production.db
graphql.enable_playground = false
graphql.debug = false
```

## 🔍 Расширенные возможности

### **Валидация данных:**
```python
# Валидация перед сохранением
data = {'full_name': '', 'company': 'Тест'}
is_valid, errors = Contact.validate(data)

if not is_valid:
    print(f"Ошибки: {errors}")
else:
    contact = Contact(**data)
```

### **Каскадные операции:**
```python
# При удалении контакта удаляются все связанные встречи и заметки
session.delete(contact)
session.commit()
```

### **Ленивая загрузка:**
```python
# Динамическая загрузка отношений
contact = session.query(Contact).first()
meetings_count = contact.meetings.count()  # Не загружает все встречи

# Загрузка конкретных встреч
meetings = contact.meetings.filter(Meeting.topic.like('%проект%')).all()
```

## ⚠️ Важные замечания

1. **Всегда закрывайте сессии** с помощью `close_session()`
2. **Используйте валидацию** перед сохранением данных
3. **Тестируйте конфигурацию** в разных окружениях
4. **Резервное копирование** production базы данных
5. **Миграции** используйте через Alembic для изменений схемы

## 📚 Дополнительные ресурсы

- [SQLAlchemy документация](https://docs.sqlalchemy.org/en/20/)
- [Pyramid документация](https://docs.pylonsproject.org/projects/pyramid/en/latest/)
- [Alembic документация](https://alembic.sqlalchemy.org/en/latest/)