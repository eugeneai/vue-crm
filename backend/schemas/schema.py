"""
Основная GraphQL схема для CRM системы.
"""

import graphene
from .contact_schema import ContactQuery, ContactMutation


class Query(
    ContactQuery,
    graphene.ObjectType
):
    """
    Корневой Query тип.
    Содержит все запросы системы.
    """
    # Базовые поля для проверки работоспособности
    hello = graphene.String(description="Простой тестовый запрос")
    version = graphene.String(description="Версия API")
    
    def resolve_hello(self, info):
        """
        Простой тестовый резолвер.
        """
        return "GraphQL API for CRM system is working!"
    
    def resolve_version(self, info):
        """
        Резолвер для версии API.
        """
        return "1.0.0"


class Mutation(
    ContactMutation,
    graphene.ObjectType
):
    """
    Корневой Mutation тип.
    Содержит все мутации системы.
    """
    pass


# Создаем схему
schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    # Включаем интроспекцию для GraphiQL
    auto_camelcase=False  # Сохраняем snake_case для совместимости с Python
)