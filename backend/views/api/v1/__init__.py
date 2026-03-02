# REST API версии 1.0
from pyramid.config import Configurator


def includeme(config: Configurator):
    """Включение маршрутов REST API v1.0"""
    
    # Контакты
    config.add_route('api_v1_contacts', '/contacts')
    config.add_route('api_v1_contact_detail', '/contacts/{id}')
    
    # Встречи
    config.add_route('api_v1_meetings', '/meetings')
    config.add_route('api_v1_meeting_detail', '/meetings/{id}')
    
    # Заметки
    config.add_route('api_v1_notes', '/notes')
    config.add_route('api_v1_note_detail', '/notes/{id}')
    
    # Отчеты
    config.add_route('api_v1_upcoming_meetings', '/reports/upcoming-meetings')
    config.add_route('api_v1_contact_history', '/reports/contact-history/{id}')
    
    # Сканирование view функций
    config.scan('.views')