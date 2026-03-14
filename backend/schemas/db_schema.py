"""
GraphQL схема, интегрированная с реальной базой данных SQLAlchemy.
Использует архитектуру Model-ViewModel.
"""

import graphene
from graphql import GraphQLError
from datetime import datetime, date

# Импортируем модели
from backend.models.contact import Contact
from backend.models.meeting import Meeting
from backend.models.note import Note


# ==================== БАЗОВЫЕ ТИПЫ ====================

class ErrorType(graphene.ObjectType):
    """
    Тип для ошибок валидации.
    """
    field = graphene.String()
    messages = graphene.List(graphene.String)


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


# ==================== NOTE (ЗАМЕТКИ) ====================

class NoteType(graphene.ObjectType):
    """
    GraphQL тип для Note (заметки).
    """
    id = graphene.ID()
    meeting_id = graphene.Int()
    date = graphene.String()
    text = graphene.String()
    
    # Отношения
    meeting = graphene.Field(lambda: MeetingType)
    
    def resolve_meeting(self, info):
        """
        Резолвер для отношения meeting.
        Загружает Meeting из базы данных.
        """
        # Получаем сессию из контекста
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return None
        
        session = request.dbsession
        return session.query(Meeting).get(self.meeting_id)


class NoteInput(graphene.InputObjectType):
    """
    Входные данные для создания/обновления заметки.
    """
    meeting_id = graphene.Int(required=True)
    date = graphene.String(required=True)
    text = graphene.String(required=True)


class NotePagination(graphene.ObjectType):
    """
    Результат пагинированного запроса заметок.
    """
    data = graphene.List(NoteType)
    pagination = graphene.Field(PaginationInfo)


# ==================== MEETING (ВСТРЕЧИ) ====================

class MeetingType(graphene.ObjectType):
    """
    GraphQL тип для Meeting (встречи).
    """
    id = graphene.ID()
    contact_id = graphene.Int()
    date_time = graphene.String()
    topic = graphene.String()
    location = graphene.String()
    
    # Отношения
    contact = graphene.Field(lambda: ContactType)
    notes = graphene.List(NoteType)
    
    def resolve_contact(self, info):
        """
        Резолвер для отношения contact.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return None
        
        session = request.dbsession
        return session.query(Contact).get(self.contact_id)
    
    def resolve_notes(self, info):
        """
        Резолвер для отношения notes.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return []
        
        session = request.dbsession
        notes = session.query(Note).filter(Note.meeting_id == self.id).all()
        return [
            NoteType(
                id=note.id,
                meeting_id=note.meeting_id,
                date=note.date.isoformat() if note.date else None,
                text=note.text
            )
            for note in notes
        ]


class MeetingInput(graphene.InputObjectType):
    """
    Входные данные для создания/обновления встречи.
    """
    contact_id = graphene.Int(required=True)
    date_time = graphene.String(required=True)
    topic = graphene.String(required=True)
    location = graphene.String()


class MeetingPagination(graphene.ObjectType):
    """
    Результат пагинированного запроса встреч.
    """
    data = graphene.List(MeetingType)
    pagination = graphene.Field(PaginationInfo)


# ==================== CONTACT (КОНТАКТЫ) ====================

class ContactType(graphene.ObjectType):
    """
    GraphQL тип для Contact (контакты).
    """
    id = graphene.ID()
    full_name = graphene.String()
    company = graphene.String()
    phone = graphene.String()
    email = graphene.String()
    
    # Отношения
    meetings = graphene.List(MeetingType)
    meetings_count = graphene.Int()
    notes_count = graphene.Int()
    
    def resolve_meetings(self, info):
        """
        Резолвер для отношения meetings.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return []
        
        session = request.dbsession
        meetings = session.query(Meeting).filter(Meeting.contact_id == self.id).all()
        return [
            MeetingType(
                id=meeting.id,
                contact_id=meeting.contact_id,
                date_time=meeting.date_time.isoformat() if meeting.date_time else None,
                topic=meeting.topic,
                location=meeting.location
            )
            for meeting in meetings
        ]
    
    def resolve_meetings_count(self, info):
        """
        Резолвер для вычисления количества встреч.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return 0
        
        session = request.dbsession
        return session.query(Meeting).filter(Meeting.contact_id == self.id).count()
    
    def resolve_notes_count(self, info):
        """
        Резолвер для вычисления общего количества заметок.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return 0
        
        session = request.dbsession
        # Получаем все встречи контакта
        meetings = session.query(Meeting).filter(Meeting.contact_id == self.id).all()
        total_notes = 0
        for meeting in meetings:
            total_notes += session.query(Note).filter(Note.meeting_id == meeting.id).count()
        return total_notes


class ContactInput(graphene.InputObjectType):
    """
    Входные данные для создания/обновления контакта.
    """
    full_name = graphene.String(required=True)
    company = graphene.String()
    phone = graphene.String()
    email = graphene.String()


class ContactPagination(graphene.ObjectType):
    """
    Результат пагинированного запроса контактов.
    """
    data = graphene.List(ContactType)
    pagination = graphene.Field(PaginationInfo)


# ==================== РЕЗУЛЬТАТЫ ОПЕРАЦИЙ ====================

class CreateContactOutput(graphene.ObjectType):
    """
    Результат создания контакта.
    """
    contact = graphene.Field(ContactType)
    errors = graphene.List(ErrorType)
    success = graphene.Boolean()


class CreateMeetingOutput(graphene.ObjectType):
    """
    Результат создания встречи.
    """
    meeting = graphene.Field(MeetingType)
    errors = graphene.List(ErrorType)
    success = graphene.Boolean()


class CreateNoteOutput(graphene.ObjectType):
    """
    Результат создания заметки.
    """
    note = graphene.Field(NoteType)
    errors = graphene.List(ErrorType)
    success = graphene.Boolean()


# ==================== ФИЛЬТРЫ ====================

class ContactFilter(graphene.InputObjectType):
    """
    Фильтр для запроса контактов.
    """
    search = graphene.String()
    company = graphene.String()


# ==================== ЗАПРОСЫ (QUERIES) ====================

class Query(graphene.ObjectType):
    """
    Запросы GraphQL с интеграцией с базой данных.
    """
    
    # Базовые запросы
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
        per_page=graphene.Int(default_value=20),
        filter=ContactFilter()
    )
    
    # Встречи
    meeting = graphene.Field(
        MeetingType,
        id=graphene.ID(required=True)
    )
    
    meetings = graphene.Field(
        MeetingPagination,
        page=graphene.Int(default_value=1),
        per_page=graphene.Int(default_value=20)
    )
    
    # Заметки
    note = graphene.Field(
        NoteType,
        id=graphene.ID(required=True)
    )
    
    notes = graphene.Field(
        NotePagination,
        page=graphene.Int(default_value=1),
        per_page=graphene.Int(default_value=50)
    )
    
    # Резолверы для базовых запросов
    def resolve_hello(self, info):
        return "GraphQL API with Database Integration"
    
    def resolve_version(self, info):
        return "2.0.0"
    
    # Резолверы для контактов
    def resolve_contact(self, info, id):
        """
        Получить контакт по ID из базы данных.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            raise GraphQLError("Database session not available")
        
        session = request.dbsession
        
        try:
            contact_id = int(id) if isinstance(id, str) and id.isdigit() else id
            contact = session.query(Contact).get(contact_id)
            
            if not contact:
                raise GraphQLError(f"Contact with id {id} not found")
            
            return ContactType(
                id=contact.id,
                full_name=contact.full_name,
                company=contact.company,
                phone=contact.phone,
                email=contact.email
            )
        except Exception as e:
            raise GraphQLError(f"Error fetching contact: {str(e)}")
    
    def resolve_contacts(self, info, page=1, per_page=20, filter=None):
        """
        Получить список контактов из базы данных с пагинацией.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            raise GraphQLError("Database session not available")
        
        session = request.dbsession
        
        try:
            # Базовый запрос
            query = session.query(Contact)
            
            # Применяем фильтры если есть
            if filter:
                if filter.get('search'):
                    search = f"%{filter['search']}%"
                    query = query.filter(
                        (Contact.full_name.ilike(search)) |
                        (Contact.company.ilike(search)) |
                        (Contact.email.ilike(search))
                    )
                
                if filter.get('company'):
                    query = query.filter(Contact.company == filter['company'])
            
            # Получаем общее количество
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
                    email=contact.email
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
            
        except Exception as e:
            raise GraphQLError(f"Error fetching contacts: {str(e)}")
    
    # Резолверы для встреч
    def resolve_meeting(self, info, id):
        """
        Получить встречу по ID из базы данных.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            raise GraphQLError("Database session not available")
        
        session = request.dbsession
        
        try:
            meeting_id = int(id) if isinstance(id, str) and id.isdigit() else id
            meeting = session.query(Meeting).get(meeting_id)
            
            if not meeting:
                raise GraphQLError(f"Meeting with id {id} not found")
            
            return MeetingType(
                id=meeting.id,
                contact_id=meeting.contact_id,
                date_time=meeting.date_time.isoformat() if meeting.date_time else None,
                topic=meeting.topic,
                location=meeting.location
            )
        except Exception as e:
            raise GraphQLError(f"Error fetching meeting: {str(e)}")
    
    def resolve_meetings(self, info, page=1, per_page=20):
        """
        Получить список встреч из базы данных с пагинацией.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            raise GraphQLError("Database session not available")
        
        session = request.dbsession
        
        try:
            query = session.query(Meeting)
            total = query.count()
            
            offset = (page - 1) * per_page
            meetings = query.offset(offset).limit(per_page).all()
            
            meeting_list = [
                MeetingType(
                    id=meeting.id,
                    contact_id=meeting.contact_id,
                    date_time=meeting.date_time.isoformat() if meeting.date_time else None,
                    topic=meeting.topic,
                    location=meeting.location
                )
                for meeting in meetings
            ]
            
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
            
            return MeetingPagination(data=meeting_list, pagination=pagination)
            
        except Exception as e:
            raise GraphQLError(f"Error fetching meetings: {str(e)}")
    
    # Резолверы для заметок
    def resolve_note(self, info, id):
        """
        Получить заметку по ID из базы данных.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            raise GraphQLError("Database session not available")
        
        session = request.dbsession
        
        try:
            note_id = int(id) if isinstance(id, str) and id.isdigit() else id
            note = session.query(Note).get(note_id)
            
            if not note:
                raise GraphQLError(f"Note with id {id} not found")
            
            return NoteType(
                id=note.id,
                meeting_id=note.meeting_id,
                date=note.date.isoformat() if note.date else None,
                text=note.text
            )
        except Exception as e:
            raise GraphQLError(f"Error fetching note: {str(e)}")
    
    def resolve_notes(self, info, page=1, per_page=50):
        """
        Получить список заметок из базы данных с пагинацией.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            raise GraphQLError("Database session not available")
        
        session = request.dbsession
        
        try:
            query = session.query(Note)
            total = query.count()
            
            offset = (page - 1) * per_page
            notes = query.offset(offset).limit(per_page).all()
            
            note_list = [
                NoteType(
                    id=note.id,
                    meeting_id=note.meeting_id,
                    date=note.date.isoformat() if note.date else None,
                    text=note.text
                )
                for note in notes
            ]
            
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
            
            return NotePagination(data=note_list, pagination=pagination)
            
        except Exception as e:
            raise GraphQLError(f"Error fetching notes: {str(e)}")


# ==================== МУТАЦИИ (MUTATIONS) ====================

class Mutation(graphene.ObjectType):
    """
    Мутации GraphQL с интеграцией с базой данных.
    """
    
    # Контакты
    create_contact = graphene.Field(
        CreateContactOutput,
        input=graphene.Argument(ContactInput, required=True)
    )
    
    update_contact = graphene.Field(
        CreateContactOutput,
        id=graphene.ID(required=True),
        input=graphene.Argument(ContactInput, required=True)
    )
    
    delete_contact = graphene.Field(
        graphene.Boolean,
        id=graphene.ID(required=True)
    )
    
    # Встречи
    create_meeting = graphene.Field(
        CreateMeetingOutput,
        input=graphene.Argument(MeetingInput, required=True)
    )
    
    update_meeting = graphene.Field(
        CreateMeetingOutput,
        id=graphene.ID(required=True),
        input=graphene.Argument(MeetingInput, required=True)
    )
    
    delete_meeting = graphene.Field(
        graphene.Boolean,
        id=graphene.ID(required=True)
    )
    
    # Заметки
    create_note = graphene.Field(
        CreateNoteOutput,
        input=graphene.Argument(NoteInput, required=True)
    )
    
    update_note = graphene.Field(
        CreateNoteOutput,
        id=graphene.ID(required=True),
        input=graphene.Argument(NoteInput, required=True)
    )
    
    delete_note = graphene.Field(
        graphene.Boolean,
        id=graphene.ID(required=True)
    )
    
    # Резолверы для контактов
    def resolve_create_contact(self, info, input):
        """
        Создать новый контакт в базе данных.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return CreateContactOutput(
                contact=None,
                errors=[ErrorType(field='general', messages=['Database session not available'])],
                success=False
            )
        
        session = request.dbsession
        
        try:
            # Валидация
            errors = []
            
            if not input.full_name:
                errors.append(ErrorType(field='fullName', messages=['Full name is required']))
            elif len(input.full_name) > 200:
                errors.append(ErrorType(field='fullName', messages=['Full name must be 200 characters or less']))
            
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
                    email=contact.email
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
    
    def resolve_update_contact(self, info, id, input):
        """
        Обновить существующий контакт в базе данных.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return CreateContactOutput(
                contact=None,
                errors=[ErrorType(field='general', messages=['Database session not available'])],
                success=False
            )
        
        session = request.dbsession
        
        try:
            # Находим контакт
            contact_id = int(id) if isinstance(id, str) and id.isdigit() else id
            contact = session.query(Contact).get(contact_id)
            
            if not contact:
                return CreateContactOutput(
                    contact=None,
                    errors=[ErrorType(field='general', messages=[f'Contact with id {id} not found'])],
                    success=False
                )
            
            # Валидация (такая же как при создании)
            errors = []
            
            if not input.full_name:
                errors.append(ErrorType(field='fullName', messages=['Full name is required']))
            elif len(input.full_name) > 200:
                errors.append(ErrorType(field='fullName', messages=['Full name must be 200 characters or less']))
            
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
            
            # Обновляем контакт
            contact.full_name = input.full_name
            contact.company = input.company
            contact.phone = input.phone
            contact.email = input.email
            
            session.commit()
            
            return CreateContactOutput(
                contact=ContactType(
                    id=contact.id,
                    full_name=contact.full_name,
                    company=contact.company,
                    phone=contact.phone,
                    email=contact.email
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
    
    def resolve_delete_contact(self, info, id):
        """
        Удалить контакт из базы данных.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return False
        
        session = request.dbsession
        
        try:
            contact_id = int(id) if isinstance(id, str) and id.isdigit() else id
            contact = session.query(Contact).get(contact_id)
            
            if not contact:
                return False
            
            session.delete(contact)
            session.commit()
            return True
            
        except Exception:
            session.rollback()
            return False
    
    # Резолверы для встреч (аналогично контактам, но короче для примера)
    def resolve_create_meeting(self, info, input):
        """
        Создать новую встречу в базе данных.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return CreateMeetingOutput(
                meeting=None,
                errors=[ErrorType(field='general', messages=['Database session not available'])],
                success=False
            )
        
        session = request.dbsession
        
        try:
            # Валидация
            errors = []
            
            if not input.contact_id:
                errors.append(ErrorType(field='contactId', messages=['Contact ID is required']))
            
            if not input.date_time:
                errors.append(ErrorType(field='dateTime', messages=['Date and time is required']))
            else:
                try:
                    datetime.fromisoformat(input.date_time.replace('Z', '+00:00'))
                except ValueError:
                    errors.append(ErrorType(field='dateTime', messages=['Invalid date format']))
            
            if not input.topic:
                errors.append(ErrorType(field='topic', messages=['Topic is required']))
            elif len(input.topic) > 500:
                errors.append(ErrorType(field='topic', messages=['Topic must be 500 characters or less']))
            
            if input.location and len(input.location) > 200:
                errors.append(ErrorType(field='location', messages=['Location must be 200 characters or less']))
            
            if errors:
                return CreateMeetingOutput(
                    meeting=None,
                    errors=errors,
                    success=False
                )
            
            # Проверяем существование контакта
            contact = session.query(Contact).get(input.contact_id)
            if not contact:
                return CreateMeetingOutput(
                    meeting=None,
                    errors=[ErrorType(field='contactId', messages=[f'Contact with id {input.contact_id} not found'])],
                    success=False
                )
            
            # Создаем встречу
            meeting = Meeting(
                contact_id=input.contact_id,
                date_time=datetime.fromisoformat(input.date_time.replace('Z', '+00:00')),
                topic=input.topic,
                location=input.location
            )
            
            session.add(meeting)
            session.commit()
            
            return CreateMeetingOutput(
                meeting=MeetingType(
                    id=meeting.id,
                    contact_id=meeting.contact_id,
                    date_time=meeting.date_time.isoformat() if meeting.date_time else None,
                    topic=meeting.topic,
                    location=meeting.location
                ),
                errors=[],
                success=True
            )
            
        except Exception as e:
            session.rollback()
            return CreateMeetingOutput(
                meeting=None,
                errors=[ErrorType(field='general', messages=[str(e)])],
                success=False
            )
    
    def resolve_delete_meeting(self, info, id):
        """Удалить встречу."""
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return False
        
        session = request.dbsession
        
        try:
            meeting_id = int(id) if isinstance(id, str) and id.isdigit() else id
            meeting = session.query(Meeting).get(meeting_id)
            
            if not meeting:
                return False
            
            session.delete(meeting)
            session.commit()
            return True
            
        except Exception:
            session.rollback()
            return False
    
    # Резолверы для заметок (аналогично)
    def resolve_create_note(self, info, input):
        """
        Создать новую заметку в базе данных.
        """
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return CreateNoteOutput(
                note=None,
                errors=[ErrorType(field='general', messages=['Database session not available'])],
                success=False
            )
        
        session = request.dbsession
        
        try:
            # Валидация
            errors = []
            
            if not input.meeting_id:
                errors.append(ErrorType(field='meetingId', messages=['Meeting ID is required']))
            
            if not input.date:
                errors.append(ErrorType(field='date', messages=['Date is required']))
            else:
                try:
                    date.fromisoformat(input.date)
                except ValueError:
                    errors.append(ErrorType(field='date', messages=['Invalid date format']))
            
            if not input.text:
                errors.append(ErrorType(field='text', messages=['Text is required']))
            elif not input.text.strip():
                errors.append(ErrorType(field='text', messages=['Text cannot be empty']))
            
            if errors:
                return CreateNoteOutput(
                    note=None,
                    errors=errors,
                    success=False
                )
            
            # Проверяем существование встречи
            meeting = session.query(Meeting).get(input.meeting_id)
            if not meeting:
                return CreateNoteOutput(
                    note=None,
                    errors=[ErrorType(field='meetingId', messages=[f'Meeting with id {input.meeting_id} not found'])],
                    success=False
                )
            
            # Создаем заметку
            note = Note(
                meeting_id=input.meeting_id,
                date=date.fromisoformat(input.date),
                text=input.text
            )
            
            session.add(note)
            session.commit()
            
            return CreateNoteOutput(
                note=NoteType(
                    id=note.id,
                    meeting_id=note.meeting_id,
                    date=note.date.isoformat() if note.date else None,
                    text=note.text
                ),
                errors=[],
                success=True
            )
            
        except Exception as e:
            session.rollback()
            return CreateNoteOutput(
                note=None,
                errors=[ErrorType(field='general', messages=[str(e)])],
                success=False
            )
    
    def resolve_delete_note(self, info, id):
        """Удалить заметку."""
        request = info.context.get('request')
        if not request or not hasattr(request, 'dbsession'):
            return False
        
        session = request.dbsession
        
        try:
            note_id = int(id) if isinstance(id, str) and id.isdigit() else id
            note = session.query(Note).get(note_id)
            
            if not note:
                return False
            
            session.delete(note)
            session.commit()
            return True
            
        except Exception:
            session.rollback()
            return False


# ==================== СХЕМА ====================

# Создаем схему с интеграцией с базой данных
schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=True)