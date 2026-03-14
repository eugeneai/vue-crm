"""
Простая GraphQL схема без graphene-sqlalchemy для тестирования.
"""

import graphene
from graphql import GraphQLError


class ContactType(graphene.ObjectType):
    """
    Простой GraphQL тип для Contact.
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
        """
        # Получаем сессию из контекста
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            raise GraphQLError("Database session not available")
        
        session = request.dbsession
        from backend.models.contact import Contact
        
        contact_id = int(id) if isinstance(id, str) and id.isdigit() else id
        contact = session.query(Contact).get(contact_id)
        
        if not contact:
            raise GraphQLError(f"Contact with id {id} not found")
        
        return ContactType(
            id=contact.id,
            full_name=contact.full_name,
            company=contact.company,
            phone=contact.phone,
            email=contact.email,
            meetings_count=contact.meetings.count() if hasattr(contact, 'meetings') else 0
        )
    
    def resolve_contacts(self, info, page=1, per_page=20):
        """
        Получить список контактов с пагинацией.
        """
        # Получаем сессию из контекста
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            raise GraphQLError("Database session not available")
        
        session = request.dbsession
        from backend.models.contact import Contact
        
        # Запрос контактов
        query = session.query(Contact)
        total = query.count()
        
        # Пагинация
        offset = (page - 1) * per_page
        contacts = query.offset(offset).limit(per_page).all()
        
        # Конвертируем в GraphQL типы
        contact_list = [
            ContactType(
                id=contact.id,
                full_name=contact.full_name,
                company=contact.company,
                phone=contact.phone,
                email=contact.email,
                meetings_count=contact.meetings.count() if hasattr(contact, 'meetings') else 0
            )
            for contact in contacts
        ]
        
        # Информация о пагинации
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        pagination = PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
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
    
    # Простая мутация
    create_contact_simple = graphene.Field(
        CreateContactOutput,
        input=graphene.Argument(ContactInput, required=True)
    )
    
    def resolve_create_contact_simple(self, info, input):
        """
        Создать контакт (простая версия).
        """
        # Получаем сессию из контекста
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return CreateContactOutput(
                contact=None,
                errors=[ErrorType(field='general', messages=['Database session not available'])],
                success=False
            )
        
        session = request.dbsession
        from backend.models.contact import Contact
        
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
        
        try:
            # Создаем контакт
            contact = Contact(
                full_name=input.full_name,
                company=input.company,
                phone=input.phone,
                email=input.email
            )
            
            session.add(contact)
            session.commit()
            
            # Возвращаем результат
            return CreateContactOutput(
                contact=ContactType(
                    id=contact.id,
                    full_name=contact.full_name,
                    company=contact.company,
                    phone=contact.phone,
                    email=contact.email,
                    meetings_count=0
                ),
                errors=[],
                success=True
            )
        
        except Exception as e:
            session.rollback()
            return CreateContactOutput(
                contact=None,
                errors=[ErrorType(field='general', messages=[str(e)])],
                success=False
            )


# Создаем схему
# auto_camelcase=True автоматически конвертирует snake_case в camelCase
schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=True)