"""
Модели SQLAlchemy для личной CRM системы.
Поддерживает конфигурацию через параметры и .ini файлы.
"""

import os
from typing import Optional
from datetime import datetime, date

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

# Базовый класс для всех моделей
Base = declarative_base()

# Глобальные переменные для engine и session factory
_engine = None
_session_factory = None
Session = None


def init_db(database_url: Optional[str] = None, config_file: Optional[str] = None):
    """
    Инициализация базы данных.
    
    Args:
        database_url: Прямой URL соединения с БД (например, 'sqlite:///contacts.db')
        config_file: Путь к .ini файлу конфигурации (например, 'development.ini')
    
    Приоритет: database_url > config_file > переменные окружения
    """
    global _engine, _session_factory, Session
    
    # Определяем URL базы данных
    db_url = _get_database_url(database_url, config_file)
    
    # Создаем engine с настройками для SQLite
    if db_url.startswith('sqlite'):
        # Для SQLite включаем проверку foreign keys и другие оптимизации
        _engine = create_engine(
            db_url,
            connect_args={'check_same_thread': False} if 'memory' not in db_url else {},
            echo=False  # Установить True для отладки SQL запросов
        )
    else:
        _engine = create_engine(db_url, echo=False)
    
    # Создаем фабрику сессий
    _session_factory = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    Session = scoped_session(_session_factory)
    
    return _engine


def _get_database_url(database_url: Optional[str] = None, config_file: Optional[str] = None) -> str:
    """
    Получить URL базы данных из различных источников.
    
    Приоритет:
    1. Прямой параметр database_url
    2. Конфигурационный файл (.ini)
    3. Переменная окружения DATABASE_URL
    4. Значение по умолчанию (SQLite в текущей директории)
    """
    # 1. Прямой параметр
    if database_url:
        return database_url
    
    # 2. Конфигурационный файл
    if config_file and os.path.exists(config_file):
        try:
            from pyramid.paster import get_appsettings
            settings = get_appsettings(config_file)
            db_url = settings.get('sqlalchemy.url')
            if db_url:
                return db_url
        except ImportError:
            # Если pyramid не установлен, пытаемся прочитать файл напрямую
            import configparser
            config = configparser.ConfigParser()
            config.read(config_file)
            if 'app:main' in config:
                db_url = config['app:main'].get('sqlalchemy.url')
                if db_url:
                    return db_url
    
    # 3. Переменная окружения
    env_db_url = os.environ.get('DATABASE_URL')
    if env_db_url:
        return env_db_url
    
    # 4. Значение по умолчанию
    return 'sqlite:///../database/contacts.db'


def get_session():
    """
    Получить новую сессию базы данных.
    
    Returns:
        SQLAlchemy session object
        
    Raises:
        RuntimeError: Если база данных не инициализирована
    """
    if Session is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return Session()


def close_session():
    """Закрыть текущую сессию базы данных."""
    if Session:
        Session.remove()


def create_tables():
    """Создать все таблицы в базе данных."""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    Base.metadata.create_all(bind=_engine)
    print(f"Tables created successfully using engine: {_engine.url}")


def drop_tables():
    """Удалить все таблицы из базы данных (только для тестов!)."""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    Base.metadata.drop_all(bind=_engine)
    print("All tables dropped.")


# Импортируем модели для удобного доступа
from .contact import Contact
from .meeting import Meeting
from .note import Note

__all__ = [
    'Base',
    'init_db',
    'get_session',
    'close_session',
    'create_tables',
    'drop_tables',
    'Contact',
    'Meeting',
    'Note',
]