#!/usr/bin/env python3
"""
Тестовый скрипт для проверки моделей SQLAlchemy.
"""

import sys
import os
from datetime import datetime, date, timedelta

# Добавляем backend в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models import init_db, create_tables, get_session, close_session
from models.contact import Contact
from models.meeting import Meeting
from models.note import Note


def test_database_initialization():
    """Тест инициализации базы данных."""
    print("=== Тест инициализации базы данных ===")
    
    # Тест 1: Инициализация с прямым URL
    print("1. Инициализация с прямым URL...")
    engine1 = init_db(database_url='sqlite:///:memory:')
    print(f"   Engine создан: {engine1.url}")
    
    # Тест 2: Инициализация с конфигурационным файлом
    print("\n2. Инициализация с конфигурационным файлом...")
    try:
        engine2 = init_db(config_file='backend/development.ini')
        print(f"   Engine создан: {engine2.url}")
    except Exception as e:
        print(f"   Ошибка (ожидаемо без pyramid): {e}")
    
    # Тест 3: Инициализация по умолчанию
    print("\n3. Инициализация по умолчанию...")
    engine3 = init_db()
    print(f"   Engine создан: {engine3.url}")
    
    return engine3


def test_create_tables():
    """Тест создания таблиц."""
    print("\n=== Тест создания таблиц ===")
    
    # Инициализируем БД в памяти для тестов
    init_db(database_url='sqlite:///:memory:')
    
    # Создаем таблицы
    create_tables()
    print("Таблицы созданы успешно")


def test_crud_operations():
    """Тест CRUD операций."""
    print("\n=== Тест CRUD операций ===")
    
    # Инициализируем БД в памяти
    init_db(database_url='sqlite:///:memory:')
    create_tables()
    
    session = get_session()
    
    try:
        # Создание контакта
        print("1. Создание контакта...")
        contact = Contact(
            full_name="Иван Иванов",
            company="ООО 'Технологии'",
            phone="+7 (999) 123-45-67",
            email="ivan@example.com"
        )
        
        # Валидация
        is_valid, errors = Contact.validate(contact.to_dict())
        if not is_valid:
            print(f"   Ошибки валидации: {errors}")
            return
        
        session.add(contact)
        session.commit()
        print(f"   Контакт создан: {contact}")
        
        # Создание встречи
        print("\n2. Создание встречи...")
        meeting = Meeting(
            contact_id=contact.id,
            date_time=datetime.now() + timedelta(days=1),
            topic="Обсуждение проекта",
            location="Офис компании"
        )
        
        # Валидация
        is_valid, errors = Meeting.validate(meeting.to_dict())
        if not is_valid:
            print(f"   Ошибки валидации: {errors}")
            return
        
        session.add(meeting)
        session.commit()
        print(f"   Встреча создана: {meeting}")
        
        # Создание заметки
        print("\n3. Создание заметки...")
        note = Note(
            meeting_id=meeting.id,
            date=date.today(),
            text="Обсудили основные требования к проекту. Нужно подготовить ТЗ к следующей встрече."
        )
        
        # Валидация
        is_valid, errors = Note.validate(note.to_dict())
        if not is_valid:
            print(f"   Ошибки валидации: {errors}")
            return
        
        session.add(note)
        session.commit()
        print(f"   Заметка создана: {note}")
        
        # Чтение данных
        print("\n4. Чтение данных...")
        
        # Получить контакт с встречами и заметками
        contact_from_db = session.query(Contact).first()
        print(f"   Контакт из БД: {contact_from_db}")
        print(f"   Количество встреч: {contact_from_db.meetings.count()}")
        
        for meeting in contact_from_db.meetings:
            print(f"   - Встреча: {meeting}")
            print(f"     Количество заметок: {meeting.notes.count()}")
            for note in meeting.notes:
                print(f"     * Заметка: {note.get_preview(50)}")
        
        # Тест отношений
        print("\n5. Тест отношений...")
        meeting_from_db = session.query(Meeting).first()
        print(f"   Встреча принадлежит контакту: {meeting_from_db.contact.full_name}")
        
        note_from_db = session.query(Note).first()
        print(f"   Заметка относится к встрече: {note_from_db.meeting.topic}")
        
        # Тест методов to_dict
        print("\n6. Тест методов to_dict...")
        contact_dict = contact_from_db.to_dict()
        print(f"   Контакт как dict: {contact_dict}")
        
        meeting_dict = meeting_from_db.to_dict(include_contact=True, include_notes=True)
        print(f"   Встреча как dict (с контактом и заметками):")
        print(f"     - ID: {meeting_dict['id']}")
        print(f"     - Тема: {meeting_dict['topic']}")
        print(f"     - Контакт: {meeting_dict['contact']['full_name']}")
        print(f"     - Заметок: {len(meeting_dict.get('notes', []))}")
        
        # Тест валидации с ошибками
        print("\n7. Тест валидации с ошибками...")
        invalid_contact_data = {'full_name': ''}
        is_valid, errors = Contact.validate(invalid_contact_data)
        print(f"   Валидация пустого имени: is_valid={is_valid}, errors={errors}")
        
        invalid_meeting_data = {'topic': 'A' * 600}
        is_valid, errors = Meeting.validate(invalid_meeting_data)
        print(f"   Валидация длинной темы: is_valid={is_valid}, errors={errors}")
        
    finally:
        close_session()


def test_upcoming_meetings():
    """Тест проверки предстоящих встреч."""
    print("\n=== Тест предстоящих встреч ===")
    
    # Инициализируем БД в памяти
    init_db(database_url='sqlite:///:memory:')
    create_tables()
    
    session = get_session()
    
    try:
        # Создаем тестовые данные
        contact = Contact(full_name="Тестовый Контакт")
        session.add(contact)
        session.commit()
        
        # Прошедшая встреча
        past_meeting = Meeting(
            contact_id=contact.id,
            date_time=datetime.now() - timedelta(days=1),
            topic="Прошедшая встреча"
        )
        
        # Предстоящая встреча (завтра)
        upcoming_meeting = Meeting(
            contact_id=contact.id,
            date_time=datetime.now() + timedelta(days=1),
            topic="Предстоящая встреча"
        )
        
        # Далекая встреча (через 10 дней)
        future_meeting = Meeting(
            contact_id=contact.id,
            date_time=datetime.now() + timedelta(days=10),
            topic="Далекая встреча"
        )
        
        session.add_all([past_meeting, upcoming_meeting, future_meeting])
        session.commit()
        
        # Проверяем предстоящие встречи
        print("Проверка предстоящих встреч (7 дней):")
        for meeting in session.query(Meeting).all():
            is_upcoming = meeting.is_upcoming(days=7)
            print(f"  - {meeting.topic}: {'Предстоящая' if is_upcoming else 'Не предстоящая'}")
        
    finally:
        close_session()


def main():
    """Основная функция тестирования."""
    print("Тестирование моделей SQLAlchemy для личной CRM системы")
    print("=" * 60)
    
    try:
        # Запускаем тесты
        test_database_initialization()
        test_create_tables()
        test_crud_operations()
        test_upcoming_meetings()
        
        print("\n" + "=" * 60)
        print("Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"\nОшибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())