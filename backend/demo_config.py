#!/usr/bin/env python3
"""
Демонстрация работы с конфигурацией базы данных.
"""

import os
import sys
from models import init_db, create_tables, get_session, close_session
from models.contact import Contact


def demo_different_configurations():
    """Демонстрация различных способов конфигурации."""
    print("=== Демонстрация различных способов конфигурации БД ===\n")
    
    # 1. Прямой URL параметр
    print("1. Конфигурация через прямой URL параметр:")
    engine1 = init_db(database_url='sqlite:///test1.db')
    print(f"   Используется БД: {engine1.url}")
    
    # Создаем таблицы и добавляем тестовые данные
    create_tables()
    session = get_session()
    contact1 = Contact(full_name="Тест через прямой URL")
    session.add(contact1)
    session.commit()
    print(f"   Создан контакт: {contact1}")
    close_session()
    
    # 2. Конфигурационный файл
    print("\n2. Конфигурация через development.ini файл:")
    engine2 = init_db(config_file='development.ini')
    print(f"   Используется БД: {engine2.url}")
    
    # Создаем таблицы и добавляем тестовые данные
    create_tables()
    session = get_session()
    contact2 = Contact(full_name="Тест через development.ini")
    session.add(contact2)
    session.commit()
    print(f"   Создан контакт: {contact2}")
    close_session()
    
    # 3. Переменная окружения
    print("\n3. Конфигурация через переменную окружения DATABASE_URL:")
    os.environ['DATABASE_URL'] = 'sqlite:///test_env.db'
    engine3 = init_db()
    print(f"   Используется БД: {engine3.url}")
    
    # Создаем таблицы и добавляем тестовые данные
    create_tables()
    session = get_session()
    contact3 = Contact(full_name="Тест через переменную окружения")
    session.add(contact3)
    session.commit()
    print(f"   Создан контакт: {contact3}")
    close_session()
    
    # 4. Значение по умолчанию
    print("\n4. Конфигурация по умолчанию (без параметров):")
    # Удаляем переменную окружения для теста
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    
    engine4 = init_db()
    print(f"   Используется БД: {engine4.url}")
    
    # Создаем таблицы и добавляем тестовые данные
    create_tables()
    session = get_session()
    contact4 = Contact(full_name="Тест по умолчанию")
    session.add(contact4)
    session.commit()
    print(f"   Создан контакт: {contact4}")
    close_session()
    
    print("\n=== Все конфигурации протестированы успешно! ===")


def demo_production_config():
    """Демонстрация production конфигурации."""
    print("\n=== Демонстрация production конфигурации ===\n")
    
    # Создаем production.ini файл для демонстрации
    production_config = """[app:main]
use = egg:backend

# Production база данных
sqlalchemy.url = sqlite:///../database/production.db

# Настройки Pyramid для production
pyramid.reload_templates = false
pyramid.debug_authorization = false
pyramid.debug_notfound = false
pyramid.debug_routematch = false
pyramid.default_locale_name = en

# Настройки GraphQL для production
graphql.enable_playground = false
graphql.debug = false
"""
    
    with open('production.ini', 'w') as f:
        f.write(production_config)
    
    print("Создан production.ini файл:")
    print(production_config)
    
    # Тестируем production конфигурацию
    engine = init_db(config_file='production.ini')
    print(f"\nИнициализирована production БД: {engine.url}")
    
    # Очищаем за собой
    if os.path.exists('production.ini'):
        os.remove('production.ini')
    
    print("Production конфигурация протестирована успешно!")


def main():
    """Основная функция демонстрации."""
    print("Демонстрация конфигурации SQLAlchemy моделей")
    print("=" * 60)
    
    try:
        demo_different_configurations()
        demo_production_config()
        
        print("\n" + "=" * 60)
        print("Демонстрация завершена успешно!")
        
        # Очищаем тестовые файлы
        for test_file in ['test1.db', 'test_env.db']:
            if os.path.exists(test_file):
                os.remove(test_file)
                print(f"Удален тестовый файл: {test_file}")
        
    except Exception as e:
        print(f"\nОшибка во время демонстрации: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())