# View функции для REST API v1.0
import json
from datetime import datetime, timedelta
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy import or_, and_

from backend.models.contact import Contact
from backend.models.meeting import Meeting
from backend.models.note import Note


# ========== Вспомогательные функции ==========

def json_response(data, status=200):
    """Создание JSON ответа"""
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        status=status,
        content_type='application/json'
    )


def validate_contact_data(data):
    """Валидация данных контакта"""
    errors = {}
    
    if not data.get('full_name'):
        errors['full_name'] = ['Это поле обязательно']
    elif len(data['full_name']) < 2 or len(data['full_name']) > 200:
        errors['full_name'] = ['Длина должна быть от 2 до 200 символов']
    
    if data.get('company') and len(data['company']) > 200:
        errors['company'] = ['Длина не должна превышать 200 символов']
    
    if data.get('phone') and len(data['phone']) > 50:
        errors['phone'] = ['Длина не должна превышать 50 символов']
    
    if data.get('email') and len(data['email']) > 100:
        errors['email'] = ['Длина не должна превышать 100 символов']
    
    return errors


def validate_meeting_data(data, dbsession):
    """Валидация данных встречи"""
    errors = {}
    
    if not data.get('contact_id'):
        errors['contact_id'] = ['Это поле обязательно']
    else:
        contact = dbsession.query(Contact).get(data['contact_id'])
        if not contact:
            errors['contact_id'] = ['Контакт с указанным ID не найден']
    
    if not data.get('date_time'):
        errors['date_time'] = ['Это поле обязательно']
    else:
        try:
            meeting_date = datetime.fromisoformat(data['date_time'].replace('Z', '+00:00'))
            if meeting_date < datetime.now():
                errors['date_time'] = ['Дата встречи не может быть в прошлом']
        except (ValueError, TypeError):
            errors['date_time'] = ['Неверный формат даты. Используйте ISO формат']
    
    if not data.get('topic'):
        errors['topic'] = ['Это поле обязательно']
    elif len(data['topic']) < 1 or len(data['topic']) > 500:
        errors['topic'] = ['Длина должна быть от 1 до 500 символов']
    
    if data.get('location') and len(data['location']) > 200:
        errors['location'] = ['Длина не должна превышать 200 символов']
    
    return errors


def validate_note_data(data, dbsession):
    """Валидация данных заметки"""
    errors = {}
    
    if not data.get('meeting_id'):
        errors['meeting_id'] = ['Это поле обязательно']
    else:
        meeting = dbsession.query(Meeting).get(data['meeting_id'])
        if not meeting:
            errors['meeting_id'] = ['Встреча с указанным ID не найден']
    
    if not data.get('date'):
        errors['date'] = ['Это поле обязательно']
    else:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except (ValueError, TypeError):
            errors['date'] = ['Неверный формат даты. Используйте YYYY-MM-DD']
    
    if not data.get('text'):
        errors['text'] = ['Это поле обязательно']
    elif not data['text'].strip():
        errors['text'] = ['Текст не может быть пустым']
    
    return errors


# ========== Контакты ==========

@view_config(route_name='api_v1_contacts', request_method='GET', renderer='json')
def list_contacts(request):
    """GET /api/v1.0/contacts - список контактов с пагинацией"""
    try:
        page = int(request.params.get('page', 1))
        per_page = int(request.params.get('per_page', 20))
        search = request.params.get('search', '')
        company = request.params.get('company', '')
        
        query = request.dbsession.query(Contact)
        
        # Поиск по имени или компании
        if search:
            query = query.filter(
                or_(
                    Contact.full_name.ilike(f'%{search}%'),
                    Contact.company.ilike(f'%{search}%')
                )
            )
        
        # Фильтрация по компании
        if company:
            query = query.filter(Contact.company.ilike(f'%{company}%'))
        
        # Подсчет общего количества
        total = query.count()
        
        # Пагинация
        contacts = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Сериализация
        contacts_data = [contact.to_dict() for contact in contacts]
        
        return {
            'data': contacts_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page if per_page > 0 else 0,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            }
        }
        
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_contact_detail', request_method='GET', renderer='json')
def get_contact(request):
    """GET /api/v1.0/contacts/{id} - получить контакт по ID"""
    try:
        contact_id = int(request.matchdict['id'])
        contact = request.dbsession.query(Contact).get(contact_id)
        
        if not contact:
            request.response.status = 404
            return {'error': 'NotFound', 'message': f'Контакт с ID {contact_id} не найден'}
        
        return contact.to_dict()
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат ID'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_contacts', request_method='POST', renderer='json')
def create_contact(request):
    """POST /api/v1.0/contacts - создать новый контакт"""
    try:
        data = request.json_body
        
        # Валидация
        errors = validate_contact_data(data)
        if errors:
            request.response.status = 422
            return {
                'error': 'ValidationError',
                'message': 'Ошибка валидации данных',
                'details': errors
            }
        
        # Создание контакта
        contact = Contact(
            full_name=data['full_name'].strip(),
            company=data.get('company', '').strip() if data.get('company') else None,
            phone=data.get('phone', '').strip() if data.get('phone') else None,
            email=data.get('email', '').strip() if data.get('email') else None
        )
        
        request.dbsession.add(contact)
        request.dbsession.flush()
        
        request.response.status = 201
        return contact.to_dict()
        
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_contact_detail', request_method='PUT', renderer='json')
def update_contact(request):
    """PUT /api/v1.0/contacts/{id} - обновить контакт"""
    try:
        contact_id = int(request.matchdict['id'])
        contact = request.dbsession.query(Contact).get(contact_id)
        
        if not contact:
            request.response.status = 404
            return {'error': 'NotFound', 'message': f'Контакт с ID {contact_id} не найден'}
        
        data = request.json_body
        
        # Валидация
        errors = validate_contact_data(data)
        if errors:
            request.response.status = 422
            return {
                'error': 'ValidationError',
                'message': 'Ошибка валидации данных',
                'details': errors
            }
        
        # Обновление полей
        contact.full_name = data['full_name'].strip()
        contact.company = data.get('company', '').strip() if data.get('company') else None
        contact.phone = data.get('phone', '').strip() if data.get('phone') else None
        contact.email = data.get('email', '').strip() if data.get('email') else None
        
        request.dbsession.flush()
        
        return contact.to_dict()
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат ID'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_contact_detail', request_method='DELETE', renderer='json')
def delete_contact(request):
    """DELETE /api/v1.0/contacts/{id} - удалить контакт"""
    try:
        contact_id = int(request.matchdict['id'])
        contact = request.dbsession.query(Contact).get(contact_id)
        
        if not contact:
            request.response.status = 404
            return {'error': 'NotFound', 'message': f'Контакт с ID {contact_id} не найден'}
        
        # Каскадное удаление встреч и заметок
        request.dbsession.delete(contact)
        request.dbsession.flush()
        
        request.response.status = 204
        return Response(status=204)
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат ID'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


# ========== Встречи ==========

@view_config(route_name='api_v1_meetings', request_method='GET', renderer='json')
def list_meetings(request):
    """GET /api/v1.0/meetings - список встреч с фильтрацией"""
    try:
        page = int(request.params.get('page', 1))
        per_page = int(request.params.get('per_page', 20))
        contact_id = request.params.get('contact_id')
        start_date = request.params.get('start_date')
        end_date = request.params.get('end_date')
        
        query = request.dbsession.query(Meeting)
        
        # Фильтрация по контакту
        if contact_id:
            try:
                query = query.filter(Meeting.contact_id == int(contact_id))
            except ValueError:
                request.response.status = 400
                return {'error': 'BadRequest', 'message': 'Неверный формат contact_id'}
        
        # Фильтрация по дате
        if start_date or end_date:
            filters = []
            
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    filters.append(Meeting.date_time >= start_dt)
                except (ValueError, TypeError):
                    request.response.status = 400
                    return {'error': 'BadRequest', 'message': 'Неверный формат start_date'}
            
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    filters.append(Meeting.date_time <= end_dt)
                except (ValueError, TypeError):
                    request.response.status = 400
                    return {'error': 'BadRequest', 'message': 'Неверный формат end_date'}
            
            query = query.filter(and_(*filters))
        
        # Сортировка по дате (новые сначала)
        query = query.order_by(Meeting.date_time.desc())
        
        # Подсчет общего количества
        total = query.count()
        
        # Пагинация
        meetings = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Сериализация
        meetings_data = [meeting.to_dict() for meeting in meetings]
        
        return {
            'data': meetings_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page if per_page > 0 else 0,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            }
        }
        
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_meeting_detail', request_method='GET', renderer='json')
def get_meeting(request):
    """GET /api/v1.0/meetings/{id} - получить встречу по ID"""
    try:
        meeting_id = int(request.matchdict['id'])
        meeting = request.dbsession.query(Meeting).get(meeting_id)
        
        if not meeting:
            request.response.status = 404
            return {'error': 'NotFound', 'message': f'Встреча с ID {meeting_id} не найдена'}
        
        return meeting.to_dict()
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат ID'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_meetings', request_method='POST', renderer='json')
def create_meeting(request):
    """POST /api/v1.0/meetings - создать новую встречу"""
    try:
        data = request.json_body
        
        # Валидация
        errors = validate_meeting_data(data, request.dbsession)
        if errors:
            request.response.status = 422
            return {
                'error': 'ValidationError',
                'message': 'Ошибка валидации данных',
                'details': errors
            }
        
        # Создание встречи
        meeting_date = datetime.fromisoformat(data['date_time'].replace('Z', '+00:00'))
        
        meeting = Meeting(
            contact_id=data['contact_id'],
            date_time=meeting_date,
            topic=data['topic'].strip(),
            location=data.get('location', '').strip() if data.get('location') else None
        )
        
        request.dbsession.add(meeting)
        request.dbsession.flush()
        
        request.response.status = 201
        return meeting.to_dict()
        
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_meeting_detail', request_method='PUT', renderer='json')
def update_meeting(request):
    """PUT /api/v1.0/meetings/{id} - обновить встречу"""
    try:
        meeting_id = int(request.matchdict['id'])
        meeting = request.dbsession.query(Meeting).get(meeting_id)
        
        if not meeting:
            request.response.status = 404
            return {'error': 'NotFound', 'message': f'Встреча с ID {meeting_id} не найдена'}
        
        data = request.json_body
        
        # Валидация
        errors = validate_meeting_data(data, request.dbsession)
        if errors:
            request.response.status = 422
            return {
                'error': 'ValidationError',
                'message': 'Ошибка валидации данных',
                'details': errors
            }
        
        # Обновление полей
        meeting.contact_id = data['contact_id']
        meeting.date_time = datetime.fromisoformat(data['date_time'].replace('Z', '+00:00'))
        meeting.topic = data['topic'].strip()
        meeting.location = data.get('location', '').strip() if data.get('location') else None
        
        request.dbsession.flush()
        
        return meeting.to_dict()
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат ID'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_meeting_detail', request_method='DELETE', renderer='json')
def delete_meeting(request):
    """DELETE /api/v1.0/meetings/{id} - удалить встречу"""
    try:
        meeting_id = int(request.matchdict['id'])
        meeting = request.dbsession.query(Meeting).get(meeting_id)
        
        if not meeting:
            request.response.status = 404
            return {'error': 'NotFound', 'message': f'Встреча с ID {meeting_id} не найдена'}
        
        # Каскадное удаление заметок
        request.dbsession.delete(meeting)
        request.dbsession.flush()
        
        request.response.status = 204
        return Response(status=204)
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат ID'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


# ========== Заметки ==========

@view_config(route_name='api_v1_notes', request_method='GET', renderer='json')
def list_notes(request):
    """GET /api/v1.0/notes - список заметок"""
    try:
        page = int(request.params.get('page', 1))
        per_page = int(request.params.get('per_page', 20))
        meeting_id = request.params.get('meeting_id')
        start_date = request.params.get('start_date')
        end_date = request.params.get('end_date')
        
        query = request.dbsession.query(Note)
        
        # Фильтрация по встрече
        if meeting_id:
            try:
                query = query.filter(Note.meeting_id == int(meeting_id))
            except ValueError:
                request.response.status = 400
                return {'error': 'BadRequest', 'message': 'Неверный формат meeting_id'}
        
        # Фильтрация по дате
        if start_date or end_date:
            filters = []
            
            if start_date:
                try:
                    start_d = datetime.strptime(start_date, '%Y-%m-%d').date()
                    filters.append(Note.date >= start_d)
                except (ValueError, TypeError):
                    request.response.status = 400
                    return {'error': 'BadRequest', 'message': 'Неверный формат start_date. Используйте YYYY-MM-DD'}
            
            if end_date:
                try:
                    end_d = datetime.strptime(end_date, '%Y-%m-%d').date()
                    filters.append(Note.date <= end_d)
                except (ValueError, TypeError):
                    request.response.status = 400
                    return {'error': 'BadRequest', 'message': 'Неверный формат end_date. Используйте YYYY-MM-DD'}
            
            query = query.filter(and_(*filters))
        
        # Сортировка по дате (новые сначала)
        query = query.order_by(Note.date.desc())
        
        # Подсчет общего количества
        total = query.count()
        
        # Пагинация
        notes = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # Сериализация
        notes_data = [note.to_dict() for note in notes]
        
        return {
            'data': notes_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page if per_page > 0 else 0,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            }
        }
        
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_note_detail', request_method='GET', renderer='json')
def get_note(request):
    """GET /api/v1.0/notes/{id} - получить заметку по ID"""
    try:
        note_id = int(request.matchdict['id'])
        note = request.dbsession.query(Note).get(note_id)
        
        if not note:
            request.response.status = 404
            return {'error': 'NotFound', 'message': f'Заметка с ID {note_id} не найдена'}
        
        return note.to_dict()
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат ID'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_notes', request_method='POST', renderer='json')
def create_note(request):
    """POST /api/v1.0/notes - создать новую заметку"""
    try:
        data = request.json_body
        
        # Валидация
        errors = validate_note_data(data, request.dbsession)
        if errors:
            request.response.status = 422
            return {
                'error': 'ValidationError',
                'message': 'Ошибка валидации данных',
                'details': errors
            }
        
        # Создание заметки
        note_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        
        note = Note(
            meeting_id=data['meeting_id'],
            date=note_date,
            text=data['text'].strip()
        )
        
        request.dbsession.add(note)
        request.dbsession.flush()
        
        request.response.status = 201
        return note.to_dict()
        
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_note_detail', request_method='PUT', renderer='json')
def update_note(request):
    """PUT /api/v1.0/notes/{id} - обновить заметку"""
    try:
        note_id = int(request.matchdict['id'])
        note = request.dbsession.query(Note).get(note_id)
        
        if not note:
            request.response.status = 404
            return {'error': 'NotFound', 'message': f'Заметка с ID {note_id} не найдена'}
        
        data = request.json_body
        
        # Валидация
        errors = validate_note_data(data, request.dbsession)
        if errors:
            request.response.status = 422
            return {
                'error': 'ValidationError',
                'message': 'Ошибка валидации данных',
                'details': errors
            }
        
        # Обновление полей
        note.meeting_id = data['meeting_id']
        note.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        note.text = data['text'].strip()
        
        request.dbsession.flush()
        
        return note.to_dict()
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат ID'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_note_detail', request_method='DELETE', renderer='json')
def delete_note(request):
    """DELETE /api/v1.0/notes/{id} - удалить заметку"""
    try:
        note_id = int(request.matchdict['id'])
        note = request.dbsession.query(Note).get(note_id)
        
        if not note:
            request.response.status = 404
            return {'error': 'NotFound', 'message': f'Заметка с ID {note_id} не найдена'}
        
        request.dbsession.delete(note)
        request.dbsession.flush()
        
        request.response.status = 204
        return Response(status=204)
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат ID'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


# ========== Отчеты ==========

@view_config(route_name='api_v1_upcoming_meetings', request_method='GET', renderer='json')
def upcoming_meetings(request):
    """GET /api/v1.0/reports/upcoming-meetings - предстоящие встречи"""
    try:
        days = int(request.params.get('days', 7))
        
        # Вычисление дат
        now = datetime.now()
        end_date = now + timedelta(days=days)
        
        # Запрос предстоящих встреч
        meetings = request.dbsession.query(Meeting).filter(
            Meeting.date_time >= now,
            Meeting.date_time <= end_date
        ).order_by(Meeting.date_time.asc()).all()
        
        # Сериализация с детальной информацией
        meetings_data = []
        for meeting in meetings:
            meeting_dict = meeting.to_dict()
            
            # Добавляем информацию о контакте
            if meeting.contact:
                meeting_dict['contact'] = meeting.contact.to_dict()
            
            # Добавляем заметки
            if meeting.notes:
                meeting_dict['notes'] = [note.to_dict() for note in meeting.notes]
            
            meetings_data.append(meeting_dict)
        
        return {
            'data': meetings_data,
            'period': {
                'start': now.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'total': len(meetings_data)
        }
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат параметра days'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}


@view_config(route_name='api_v1_contact_history', request_method='GET', renderer='json')
def contact_history(request):
    """GET /api/v1.0/reports/contact-history/{id} - история контакта"""
    try:
        contact_id = int(request.matchdict['id'])
        contact = request.dbsession.query(Contact).get(contact_id)
        
        if not contact:
            request.response.status = 404
            return {'error': 'NotFound', 'message': f'Контакт с ID {contact_id} не найден'}
        
        # Получаем все встречи контакта
        meetings = request.dbsession.query(Meeting).filter(
            Meeting.contact_id == contact_id
        ).order_by(Meeting.date_time.desc()).all()
        
        # Сериализация встреч с заметками
        meetings_data = []
        for meeting in meetings:
            meeting_dict = meeting.to_dict()
            
            # Добавляем заметки
            if meeting.notes:
                meeting_dict['notes'] = [note.to_dict() for note in meeting.notes]
            
            meetings_data.append(meeting_dict)
        
        # Информация о контакте
        contact_data = contact.to_dict()
        contact_data['meetings'] = meetings_data
        
        return {
            'contact': contact_data,
            'statistics': {
                'total_meetings': len(meetings),
                'total_notes': sum(len(meeting.notes) for meeting in meetings),
                'last_meeting': meetings[0].date_time.isoformat() if meetings else None,
                'first_meeting': meetings[-1].date_time.isoformat() if meetings else None
            }
        }
        
    except ValueError:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': 'Неверный формат ID'}
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}