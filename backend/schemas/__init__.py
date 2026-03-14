"""
GraphQL схемы для личной CRM системы.
Используется архитектура Model-ViewModel:
- Model: SQLAlchemy модели (backend/models/)
- ViewModel: GraphQL типы (здесь)
"""

from .simple_schema import schema

__all__ = ['schema']