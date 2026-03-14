"""
Базовые типы и утилиты для GraphQL схем.
"""

import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql import GraphQLError
from datetime import datetime, date
import json


class DateTimeScalar(graphene.Scalar):
    """
    Кастомный скаляр для datetime.
    """
    
    @staticmethod
    def serialize(dt):
        if isinstance(dt, datetime):
            return dt.isoformat()
        return dt
    
    @staticmethod
    def parse_literal(node):
        if isinstance(node, graphene.StringValue):
            return datetime.fromisoformat(node.value)
        return None
    
    @staticmethod
    def parse_value(value):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


class DateScalar(graphene.Scalar):
    """
    Кастомный скаляр для date.
    """
    
    @staticmethod
    def serialize(d):
        if isinstance(d, date):
            return d.isoformat()
        return d
    
    @staticmethod
    def parse_literal(node):
        if isinstance(node, graphene.StringValue):
            return date.fromisoformat(node.value)
        return None
    
    @staticmethod
    def parse_value(value):
        if isinstance(value, str):
            return date.fromisoformat(value)
        return value


class PaginationInfo(graphene.ObjectType):
    """
    Информация о пагинации.
    """
    page = graphene.Int(description="Текущая страница")
    per_page = graphene.Int(description="Количество элементов на странице")
    total = graphene.Int(description="Общее количество элементов")
    total_pages = graphene.Int(description="Общее количество страниц")
    has_next = graphene.Boolean(description="Есть ли следующая страница")
    has_prev = graphene.Boolean(description="Есть ли предыдущая страница")


class ErrorType(graphene.ObjectType):
    """
    Тип для ошибок GraphQL.
    """
    field = graphene.String(description="Поле с ошибкой")
    messages = graphene.List(graphene.String, description="Сообщения об ошибках")


class ValidationError(GraphQLError):
    """
    Кастомная ошибка валидации.
    """
    def __init__(self, errors):
        super().__init__("Validation error")
        self.errors = errors
    
    def format_error(self):
        error = super().format_error()
        error['extensions'] = {
            'code': 'VALIDATION_ERROR',
            'errors': self.errors
        }
        return error


def get_session(info):
    """
    Получить сессию базы данных из контекста GraphQL.
    """
    request = info.context.get('request')
    if request and hasattr(request, 'dbsession'):
        return request.dbsession
    raise GraphQLError("Database session not available")


def validate_model_data(model_class, data, session=None, instance_id=None):
    """
    Валидация данных модели.
    
    Args:
        model_class: Класс модели SQLAlchemy
        data: Данные для валидации
        session: Сессия базы данных (опционально)
        instance_id: ID существующего экземпляра (для обновления)
    
    Returns:
        tuple: (is_valid, errors_dict)
    """
    errors = {}
    
    # Используем метод validate модели, если он существует
    if hasattr(model_class, 'validate'):
        is_valid, error_list = model_class.validate(data)
        if not is_valid:
            # Преобразуем список ошибок в словарь
            for error in error_list:
                # Пытаемся определить поле из сообщения об ошибке
                field = 'general'
                for field_name in ['full_name', 'company', 'phone', 'email', 'contact_id', 'date_time', 'topic', 'text']:
                    if field_name in error.lower():
                        field = field_name
                        break
                
                if field not in errors:
                    errors[field] = []
                errors[field].append(error)
    
    # Дополнительные проверки для связанных полей
    if session and 'contact_id' in data:
        from backend.models.contact import Contact
        contact = session.query(Contact).get(data['contact_id'])
        if not contact:
            if 'contact_id' not in errors:
                errors['contact_id'] = []
            errors['contact_id'].append(f"Contact with id {data['contact_id']} not found")
    
    if session and 'meeting_id' in data:
        from backend.models.meeting import Meeting
        meeting = session.query(Meeting).get(data['meeting_id'])
        if not meeting:
            if 'meeting_id' not in errors:
                errors['meeting_id'] = []
            errors['meeting_id'].append(f"Meeting with id {data['meeting_id']} not found")
    
    return len(errors) == 0, errors


def format_validation_errors(errors_dict):
    """
    Форматирование ошибок валидации для GraphQL.
    
    Args:
        errors_dict: Словарь ошибок {field: [messages]}
    
    Returns:
        list: Список объектов ErrorType
    """
    return [
        ErrorType(field=field, messages=messages)
        for field, messages in errors_dict.items()
    ]


class BaseSQLAlchemyObjectType(SQLAlchemyObjectType):
    """
    Базовый класс для всех SQLAlchemy ObjectType.
    """
    class Meta:
        abstract = True
    
    @classmethod
    def get_node(cls, info, id):
        """
        Получить объект по ID для Relay Node.
        """
        session = get_session(info)
        return session.query(cls._meta.model).get(int(id))


# Регистрируем кастомные скаляры
graphene.DateTime = DateTimeScalar
graphene.Date = DateScalar