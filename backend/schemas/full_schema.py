"""
Полная GraphQL схема для CRM системы с Contact, Meeting и Note.
Использует архитектуру Model-ViewModel.
"""

import graphene
from graphql import GraphQLError
from datetime import datetime, date


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
        В реальной реализации будет загружать Meeting из базы данных.
        """
        # В этой упрощенной версии возвращаем None
        # В реальной реализации: return self.meeting
        return None


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
        # В реальной реализации: return self.contact
        return None
    
    def resolve_notes(self, info):
        """
        Резолвер для отношения notes.
        """
        # В реальной реализации: return list(self.notes) или self.notes.all()
        return []


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
        # В реальной реализации: return list(self.meetings) или self.meetings.all()
        return []
    
    def resolve_meetings_count(self, info):
        """
        Резолвер для вычисления количества встреч.
        """
        # В реальной реализации: return self.meetings.count()
        return 0
    
    def resolve_notes_count(self, info):
        """
        Резолвер для вычисления общего количества заметок.
        """
        # В реальной реализации: 
        # total = 0
        # for meeting in self.meetings:
        #     total += meeting.notes.count()
        # return total
        return 0


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
    has_meetings = graphene.Boolean()


class MeetingFilter(graphene.InputObjectType):
    """
    Фильтр для запроса встреч.
    """
    contact_id = graphene.Int()
    upcoming = graphene.Boolean()
    from_date = graphene.String()
    to_date = graphene.String()


class NoteFilter(graphene.InputObjectType):
    """
    Фильтр для запроса заметок.
    """
    meeting_id = graphene.Int()
    contact_id = graphene.Int()
    from_date = graphene.String()
    to_date = graphene.String()


# ==================== ЗАПРОСЫ (QUERIES) ====================

class Query(graphene.ObjectType):
    """
    Запросы GraphQL.
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
        per_page=graphene.Int(default_value=20),
        filter=MeetingFilter()
    )
    
    # Заметки
    note = graphene.Field(
        NoteType,
        id=graphene.ID(required=True)
    )
    
    notes = graphene.Field(
        NotePagination,
        page=graphene.Int(default_value=1),
        per_page=graphene.Int(default_value=50),
        filter=NoteFilter()
    )
    
    # Резолверы для базовых запросов
    def resolve_hello(self, info):
        return "Full GraphQL API for CRM system is working!"
    
    def resolve_version(self, info):
        return "1.1.0"
    
    # Резолверы для контактов
    def resolve_contact(self, info, id):
        """
        Получить контакт по ID.
        """
        # В этой упрощенной версии возвращаем моковые данные
        return ContactType(
            id=id,
            full_name="John Doe",
            company="Example Corp",
            phone="123-456-7890",
            email="john@example.com"
        )
    
    def resolve_contacts(self, info, page=1, per_page=20, filter=None):
        """
        Получить список контактов с пагинацией и фильтрацией.
        """
        # Моковые данные для тестирования
        contact_list = [
            ContactType(
                id="1",
                full_name="John Doe",
                company="Example Corp",
                phone="123-456-7890",
                email="john@example.com"
            ),
            ContactType(
                id="2", 
                full_name="Jane Smith",
                company="Test Company",
                phone="987-654-3210",
                email="jane@test.com"
            )
        ]
        
        # Применяем фильтры если есть
        if filter:
            filtered_contacts = contact_list
            if filter.get('search'):
                search_lower = filter['search'].lower()
                filtered_contacts = [
                    c for c in filtered_contacts 
                    if search_lower in c.full_name.lower() or 
                       (c.company and search_lower in c.company.lower())
                ]
            if filter.get('company'):
                company_lower = filter['company'].lower()
                filtered_contacts = [
                    c for c in filtered_contacts 
                    if c.company and company_lower in c.company.lower()
                ]
            contact_list = filtered_contacts
        
        # Пагинация
        total = len(contact_list)
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        # Применяем пагинацию
        offset = (page - 1) * per_page
        paginated_data = contact_list[offset:offset + per_page]
        
        pagination = PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return ContactPagination(data=paginated_data, pagination=pagination)
    
    # Резолверы для встреч
    def resolve_meeting(self, info, id):
        """
        Получить встречу по ID.
        """
        return MeetingType(
            id=id,
            contact_id=1,
            date_time="2024-01-15T14:30:00",
            topic="Business Discussion",
            location="Conference Room A"
        )
    
    def resolve_meetings(self, info, page=1, per_page=20, filter=None):
        """
        Получить список встреч с пагинацией и фильтрацией.
        """
        # Моковые данные
        meeting_list = [
            MeetingType(
                id="1",
                contact_id=1,
                date_time="2024-01-15T14:30:00",
                topic="Business Discussion",
                location="Conference Room A"
            ),
            MeetingType(
                id="2",
                contact_id=2,
                date_time="2024-01-16T10:00:00",
                topic="Project Review",
                location="Online"
            )
        ]
        
        # Пагинация
        total = len(meeting_list)
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        offset = (page - 1) * per_page
        paginated_data = meeting_list[offset:offset + per_page]
        
        pagination = PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return MeetingPagination(data=paginated_data, pagination=pagination)
    
    # Резолверы для заметок
    def resolve_note(self, info, id):
        """
        Получить заметку по ID.
        """
        return NoteType(
            id=id,
            meeting_id=1,
            date="2024-01-15",
            text="Discussed project timelines and deliverables. Agreed to follow up next week."
        )
    
    def resolve_notes(self, info, page=1, per_page=50, filter=None):
        """
        Получить список заметок с пагинацией и фильтрацией.
        """
        # Моковые данные
        note_list = [
            NoteType(
                id="1",
                meeting_id=1,
                date="2024-01-15",
                text="Discussed project timelines and deliverables. Agreed to follow up next week."
            ),
            NoteType(
                id="2",
                meeting_id=1,
                date="2024-01-15",
                text="Client requested additional features for phase 2."
            )
        ]
        
        # Пагинация
        total = len(note_list)
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        offset = (page - 1) * per_page
        paginated_data = note_list[offset:offset + per_page]
        
        pagination = PaginationInfo(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return NotePagination(data=paginated_data, pagination=pagination)


# ==================== МУТАЦИИ (MUTATIONS) ====================

class Mutation(graphene.ObjectType):
    """
    Мутации GraphQL.
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
        Создать новый контакт.
        """
        errors = []
        
        # Валидация
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
        
        # В реальной реализации здесь будет сохранение в базу данных
        return CreateContactOutput(
            contact=ContactType(
                id="999",
                full_name=input.full_name,
                company=input.company,
                phone=input.phone,
                email=input.email
            ),
            errors=[],
            success=True
        )
    
    def resolve_update_contact(self, info, id, input):
        """
        Обновить существующий контакт.
        """
        # Используем ту же валидацию, что и для создания
        return self.resolve_create_contact(info, input)
    
    def resolve_delete_contact(self, info, id):
        """
        Удалить контакт.
        """
        # В реальной реализации здесь будет удаление из базы данных
        return True
    
    # Резолверы для встреч
    def resolve_create_meeting(self, info, input):
        """
        Создать новую встречу.
        """
        errors = []
        
        # Валидация
        if not input.contact_id:
            errors.append(ErrorType(field='contactId', messages=['Contact ID is required']))
        
        if not input.date_time:
            errors.append(ErrorType(field='dateTime', messages=['Date and time is required']))
        else:
            try:
                # Проверяем формат даты
                datetime.fromisoformat(input.date_time.replace('Z', '+00:00'))
            except ValueError:
                errors.append(ErrorType(field='dateTime', messages=['Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)']))
        
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
        
        # В реальной реализации здесь будет сохранение в базу данных
        return CreateMeetingOutput(
            meeting=MeetingType(
                id="999",
                contact_id=input.contact_id,
                date_time=input.date_time,
                topic=input.topic,
                location=input.location
            ),
            errors=[],
            success=True
        )
    
    def resolve_update_meeting(self, info, id, input):
        """
        Обновить существующую встречу.
        """
        # Используем ту же валидацию, что и для создания
        return self.resolve_create_meeting(info, input)
    
    def resolve_delete_meeting(self, info, id):
        """
        Удалить встречу.
        """
        return True
    
    # Резолверы для заметок
    def resolve_create_note(self, info, input):
        """
        Создать новую заметку.
        """
        errors = []
        
        # Валидация
        if not input.meeting_id:
            errors.append(ErrorType(field='meetingId', messages=['Meeting ID is required']))
        
        if not input.date:
            errors.append(ErrorType(field='date', messages=['Date is required']))
        else:
            try:
                # Проверяем формат даты
                date.fromisoformat(input.date)
            except ValueError:
                errors.append(ErrorType(field='date', messages=['Invalid date format. Use ISO format (YYYY-MM-DD)']))
        
        if not input.text:
            errors.append(ErrorType(field='text', messages=['Text is required']))
        elif not input.text.strip():
            errors.append(ErrorType(field='text', messages=['Text cannot be empty or whitespace only']))
        
        if errors:
            return CreateNoteOutput(
                note=None,
                errors=errors,
                success=False
            )
        
        # В реальной реализации здесь будет сохранение в базу данных
        return CreateNoteOutput(
            note=NoteType(
                id="999",
                meeting_id=input.meeting_id,
                date=input.date,
                text=input.text
            ),
            errors=[],
            success=True
        )
    
    def resolve_update_note(self, info, id, input):
        """
        Обновить существующую заметку.
        """
        # Используем ту же валидацию, что и для создания
        return self.resolve_create_note(info, input)
    
    def resolve_delete_note(self, info, id):
        """
        Удалить заметку.
        """
        return True


# ==================== СХЕМА ====================

# Создаем полную схему
schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=True)