"""
Исправленная GraphQL схема с правильным именованием полей.
Используем snake_case для Python кода, но GraphQL автоматически конвертирует в camelCase.
"""

import graphene
from graphql import GraphQLError


class ContactType(graphene.ObjectType):
    """
    GraphQL тип для Contact.
    Поля в Python: snake_case
    Поля в GraphQL: автоматически camelCase (full_name -> fullName)
    """
    id = graphene.ID()
    full_name = graphene.String()
    company = graphene.String()
    phone = graphene.String()
    email = graphene.String()
    meetings_count = graphene.Int()


class ContactInput(graphene.InputObjectType):
    """
    Входные данные для создания/обновления контакта.
    """
    full_name = graphene.String(required=True)
    company = graphene.String()
    phone = graphene.String()
    email = graphene.String()


class PaginationInfo(graphene.ObjectType):
    """
    Информация о пагинации.
    """
    page = graphene.Int()
    per_page = graphene.Int()
    total = graphene.Int()
    total_pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()


class ContactPagination(graphene.ObjectType):
    """
    Результат пагинированного запроса контактов.
    """
    data = graphene.List(ContactType)
    pagination = graphene.Field(PaginationInfo)


class ErrorType(graphene.ObjectType):
    """
    Тип для ошибок.
    """
    field = graphene.String()
    messages = graphene.List(graphene.String)


class Query(graphene.ObjectType):
    """
    Запросы GraphQL.
    """
    hello = graphene.String()
    version = graphene.String()
    
    # Контакты
    contact = graphene.Field(
        ContactType,
        id=graphene.ID(required=True)
    )
    
    contacts = graphene.Field(
        ContactPagination,
        page=graphene.Int(default_value=1),
        per_page=graphene.Int(default_value=20)
    )
    
    def resolve_hello(self, info):
        return "GraphQL API for CRM system is working!"
    
    def resolve_version(self, info):
        return "1.0.0"
    
    def resolve_contact(self, info, id):
        """
        Получить контакт по ID.
        В этой упрощенной версии возвращаем моковые данные.
        """
        # В реальной реализации здесь будет работа с базой данных
        return ContactType(
            id=id,
            full_name="John Doe",
            company="Example Corp",
            phone="123-456-7890",
            email="john@example.com",
            meetings_count=3
        )
    
    def resolve_contacts(self, info, page=1, per_page=20):
        """
        Получить список контактов с пагинацией.
        В этой упрощенной версии возвращаем моковые данные.
        """
        # Моковые данные для тестирования
        contact_list = [
            ContactType(
                id="1",
                full_name="John Doe",
                company="Example Corp",
                phone="123-456-7890",
                email="john@example.com",
                meetings_count=3
            ),
            ContactType(
                id="2", 
                full_name="Jane Smith",
                company="Test Company",
                phone="987-654-3210",
                email="jane@test.com",
                meetings_count=1
            )
        ]
        
        # Информация о пагинации
        pagination = PaginationInfo(
            page=page,
            per_page=per_page,
            total=2,
            total_pages=1,
            has_next=False,
            has_prev=False
        )
        
        return ContactPagination(data=contact_list, pagination=pagination)


class CreateContactOutput(graphene.ObjectType):
    """
    Результат создания контакта.
    """
    contact = graphene.Field(ContactType)
    errors = graphene.List(ErrorType)
    success = graphene.Boolean()


class Mutation(graphene.ObjectType):
    """
    Мутации GraphQL.
    """
    
    # Мутация для создания контакта
    # В GraphQL будет доступна как createContact (camelCase)
    create_contact = graphene.Field(
        CreateContactOutput,
        input=graphene.Argument(ContactInput, required=True)
    )
    
    def resolve_create_contact(self, info, input):
        """
        Создать контакт (упрощенная версия).
        """
        # Валидация
        errors = []
        
        if not input.full_name:
            errors.append(ErrorType(field='full_name', messages=['Full name is required']))
        elif len(input.full_name) > 200:
            errors.append(ErrorType(field='full_name', messages=['Full name must be 200 characters or less']))
        
        if input.company and len(input.company) > 200:
            errors.append(ErrorType(field='company', messages=['Company must be 200 characters or less']))
        
        if input.phone and len(input.phone) > 50:
            errors.append(ErrorType(field='phone', messages=['Phone must be 50 characters or less']))
        
        if input.email:
            if len(input.email) > 100:
                errors.append(ErrorType(field='email', messages=['Email must be 100 characters or less']))
            elif '@' not in input.email:
                errors.append(ErrorType(field='email', messages=['Email must be a valid email address']))
        
        if errors:
            return CreateContactOutput(
                contact=None,
                errors=errors,
                success=False
            )
        
        # В реальной реализации здесь будет сохранение в базу данных
        # Возвращаем моковый результат
        return CreateContactOutput(
            contact=ContactType(
                id="999",
                full_name=input.full_name,
                company=input.company,
                phone=input.phone,
                email=input.email,
                meetings_count=0
            ),
            errors=[],
            success=True
        )


# Создаем схему
# auto_camelcase=True (по умолчанию) конвертирует snake_case в camelCase
schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=True)