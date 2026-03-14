"""
GraphQL схема для модели Contact.
"""

import graphene
from .base import (
    BaseSQLAlchemyObjectType, 
    PaginationInfo, 
    ErrorType,
    validate_model_data,
    format_validation_errors,
    get_session
)
from backend.models.contact import Contact


class ContactType(BaseSQLAlchemyObjectType):
    """
    GraphQL тип для модели Contact.
    """
    class Meta:
        model = Contact
        interfaces = (graphene.relay.Node,)
        exclude_fields = ('meetings',)  # Исключаем отношения, добавим позже
    
    # Можно добавить кастомные поля
    meetings_count = graphene.Int(description="Количество встреч с контактом")
    
    def resolve_meetings_count(self, info):
        """
        Получить количество встреч для контакта.
        """
        return self.meetings.count() if hasattr(self, 'meetings') else 0


class ContactInput(graphene.InputObjectType):
    """
    Входные данные для создания/обновления контакта.
    """
    full_name = graphene.String(required=True, description="ФИО контакта")
    company = graphene.String(description="Место работы")
    phone = graphene.String(description="Телефон")
    email = graphene.String(description="Email")


class ContactFilter(graphene.InputObjectType):
    """
    Фильтр для поиска контактов.
    """
    search = graphene.String(description="Поиск по ФИО или компании")
    company = graphene.String(description="Фильтр по компании")
    has_phone = graphene.Boolean(description="Только контакты с телефоном")
    has_email = graphene.Boolean(description="Только контакты с email")


class ContactPagination(graphene.ObjectType):
    """
    Результат пагинированного запроса контактов.
    """
    data = graphene.List(ContactType, description="Список контактов")
    pagination = graphene.Field(PaginationInfo, description="Информация о пагинации")


class ContactQuery(graphene.ObjectType):
    """
    Запросы для модели Contact.
    """
    
    # Получить контакт по ID
    contact = graphene.Field(
        ContactType,
        id=graphene.ID(required=True, description="ID контакта"),
        description="Получить контакт по ID"
    )
    
    # Получить список контактов с пагинацией и фильтрацией
    contacts = graphene.Field(
        ContactPagination,
        page=graphene.Int(default_value=1, description="Номер страницы"),
        per_page=graphene.Int(default_value=20, description="Количество на странице"),
        filter=graphene.Argument(ContactFilter, description="Фильтры"),
        description="Получить список контактов с пагинацией"
    )
    
    # Поиск контактов
    search_contacts = graphene.List(
        ContactType,
        query=graphene.String(required=True, description="Поисковый запрос"),
        limit=graphene.Int(default_value=10, description="Лимит результатов"),
        description="Поиск контактов"
    )
    
    def resolve_contact(self, info, id):
        """
        Резолвер для получения контакта по ID.
        """
        session = get_session(info)
        contact_id = int(id) if isinstance(id, str) and id.isdigit() else id
        contact = session.query(Contact).get(contact_id)
        
        if not contact:
            raise GraphQLError(f"Contact with id {id} not found")
        
        return contact
    
    def resolve_contacts(self, info, page=1, per_page=20, filter=None):
        """
        Резолвер для получения списка контактов с пагинацией.
        """
        session = get_session(info)
        query = session.query(Contact)
        
        # Применяем фильтры
        if filter:
            if filter.search:
                search_term = f"%{filter.search}%"
                query = query.filter(
                    Contact.full_name.ilike(search_term) |
                    (Contact.company.ilike(search_term) if Contact.company else False)
                )
            
            if filter.company:
                query = query.filter(Contact.company == filter.company)
            
            if filter.has_phone is not None:
                if filter.has_phone:
                    query = query.filter(Contact.phone.isnot(None))
                else:
                    query = query.filter(Contact.phone.is_(None))
            
            if filter.has_email is not None:
                if filter.has_email:
                    query = query.filter(Contact.email.isnot(None))
                else:
                    query = query.filter(Contact.email.is_(None))
        
        # Считаем общее количество
        total = query.count()
        
        # Применяем пагинацию
        offset = (page - 1) * per_page
        contacts = query.offset(offset).limit(per_page).all()
        
        # Рассчитываем информацию о пагинации
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        pagination_info = PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return ContactPagination(data=contacts, pagination=pagination_info)
    
    def resolve_search_contacts(self, info, query, limit=10):
        """
        Резолвер для поиска контактов.
        """
        session = get_session(info)
        search_term = f"%{query}%"
        
        contacts = session.query(Contact).filter(
            Contact.full_name.ilike(search_term) |
            (Contact.company.ilike(search_term) if Contact.company else False) |
            (Contact.phone.ilike(search_term) if Contact.phone else False) |
            (Contact.email.ilike(search_term) if Contact.email else False)
        ).limit(limit).all()
        
        return contacts


class ContactMutation(graphene.ObjectType):
    """
    Мутации для модели Contact.
    """
    
    # Создать контакт
    create_contact = graphene.Field(
        ContactType,
        input=graphene.Argument(ContactInput, required=True, description="Данные контакта"),
        description="Создать новый контакт"
    )
    
    # Обновить контакт
    update_contact = graphene.Field(
        ContactType,
        id=graphene.ID(required=True, description="ID контакта"),
        input=graphene.Argument(ContactInput, required=True, description="Обновленные данные"),
        description="Обновить существующий контакт"
    )
    
    # Удалить контакт
    delete_contact = graphene.Field(
        graphene.Boolean,
        id=graphene.ID(required=True, description="ID контакта"),
        description="Удалить контакт"
    )
    
    class CreateContactOutput(graphene.ObjectType):
        """
        Результат создания контакта.
        """
        contact = graphene.Field(ContactType, description="Созданный контакт")
        errors = graphene.List(ErrorType, description="Ошибки валидации")
        success = graphene.Boolean(description="Успешно ли создание")
    
    class UpdateContactOutput(graphene.ObjectType):
        """
        Результат обновления контакта.
        """
        contact = graphene.Field(ContactType, description="Обновленный контакт")
        errors = graphene.List(ErrorType, description="Ошибки валидации")
        success = graphene.Boolean(description="Успешно ли обновление")
    
    # Альтернативные мутации с детальным выводом
    create_contact_detailed = graphene.Field(
        CreateContactOutput,
        input=graphene.Argument(ContactInput, required=True, description="Данные контакта"),
        description="Создать новый контакт с детальным выводом"
    )
    
    update_contact_detailed = graphene.Field(
        UpdateContactOutput,
        id=graphene.ID(required=True, description="ID контакта"),
        input=graphene.Argument(ContactInput, required=True, description="Обновленные данные"),
        description="Обновить существующий контакт с детальным выводом"
    )
    
    def resolve_create_contact(self, info, input):
        """
        Резолвер для создания контакта.
        """
        session = get_session(info)
        
        # Валидация данных
        is_valid, errors = validate_model_data(Contact, input, session)
        
        if not is_valid:
            raise ValidationError(format_validation_errors(errors))
        
        # Создаем контакт
        contact = Contact(
            full_name=input.full_name,
            company=input.get('company'),
            phone=input.get('phone'),
            email=input.get('email')
        )
        
        session.add(contact)
        session.commit()
        
        return contact
    
    def resolve_update_contact(self, info, id, input):
        """
        Резолвер для обновления контакта.
        """
        session = get_session(info)
        contact_id = int(id) if isinstance(id, str) and id.isdigit() else id
        
        # Находим контакт
        contact = session.query(Contact).get(contact_id)
        
        if not contact:
            raise GraphQLError(f"Contact with id {id} not found")
        
        # Валидация данных
        is_valid, errors = validate_model_data(Contact, input, session, contact_id)
        
        if not is_valid:
            raise ValidationError(format_validation_errors(errors))
        
        # Обновляем контакт
        contact.full_name = input.full_name
        if 'company' in input:
            contact.company = input.company
        if 'phone' in input:
            contact.phone = input.phone
        if 'email' in input:
            contact.email = input.email
        
        session.commit()
        
        return contact
    
    def resolve_delete_contact(self, info, id):
        """
        Резолвер для удаления контакта.
        """
        session = get_session(info)
        contact_id = int(id) if isinstance(id, str) and id.isdigit() else id
        
        # Находим контакт
        contact = session.query(Contact).get(contact_id)
        
        if not contact:
            raise GraphQLError(f"Contact with id {id} not found")
        
        # Удаляем контакт
        session.delete(contact)
        session.commit()
        
        return True
    
    def resolve_create_contact_detailed(self, info, input):
        """
        Резолвер для создания контакта с детальным выводом.
        """
        session = get_session(info)
        
        # Валидация данных
        is_valid, errors = validate_model_data(Contact, input, session)
        
        if not is_valid:
            return ContactMutation.CreateContactOutput(
                contact=None,
                errors=format_validation_errors(errors),
                success=False
            )
        
        try:
            # Создаем контакт
            contact = Contact(
                full_name=input.full_name,
                company=input.get('company'),
                phone=input.get('phone'),
                email=input.get('email')
            )
            
            session.add(contact)
            session.commit()
            
            return ContactMutation.CreateContactOutput(
                contact=contact,
                errors=[],
                success=True
            )
        except Exception as e:
            session.rollback()
            return ContactMutation.CreateContactOutput(
                contact=None,
                errors=[ErrorType(field='general', messages=[str(e)])],
                success=False
            )
    
    def resolve_update_contact_detailed(self, info, id, input):
        """
        Резолвер для обновления контакта с детальным выводом.
        """
        session = get_session(info)
        contact_id = int(id) if isinstance(id, str) and id.isdigit() else id
        
        # Находим контакт
        contact = session.query(Contact).get(contact_id)
        
        if not contact:
            return ContactMutation.UpdateContactOutput(
                contact=None,
                errors=[ErrorType(field='id', messages=[f"Contact with id {id} not found"])],
                success=False
            )
        
        # Валидация данных
        is_valid, errors = validate_model_data(Contact, input, session, contact_id)
        
        if not is_valid:
            return ContactMutation.UpdateContactOutput(
                contact=None,
                errors=format_validation_errors(errors),
                success=False
            )
        
        try:
            # Обновляем контакт
            contact.full_name = input.full_name
            if 'company' in input:
                contact.company = input.company
            if 'phone' in input:
                contact.phone = input.phone
            if 'email' in input:
                contact.email = input.email
            
            session.commit()
            
            return ContactMutation.UpdateContactOutput(
                contact=contact,
                errors=[],
                success=True
            )
        except Exception as e:
            session.rollback()
            return ContactMutation.UpdateContactOutput(
                contact=None,
                errors=[ErrorType(field='general', messages=[str(e)])],
                success=False
            )


# Импортируем GraphQLError здесь, чтобы избежать циклического импорта
from graphql import GraphQLError
from .base import ValidationError