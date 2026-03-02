"""
Backend пакет для личной CRM системы.
"""

from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.events import subscriber
import json


@subscriber(NewRequest)
def add_cors_headers(event):
    """Добавление CORS заголовков ко всем ответам"""
    if event.request.method == 'OPTIONS':
        # Предварительный запрос CORS
        event.request.response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
            'Access-Control-Max-Age': '3600',
        })
    else:
        # Обычные запросы
        event.request.response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
        })


def json_renderer_factory(info):
    """Кастомный JSON рендерер для Pyramid"""
    def _render(value, system):
        request = system.get('request')
        if request is not None:
            response = request.response
            response.content_type = 'application/json'
            
            # Добавляем CORS заголовки
            response.headers.update({
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept',
            })
        
        return json.dumps(value, ensure_ascii=False, default=str)
    return _render


def main(global_config, **settings):
    """
    Функция для создания Pyramid приложения.
    
    Args:
        global_config: Глобальная конфигурация
        **settings: Настройки из .ini файла
        
    Returns:
        Pyramid WSGI приложение
    """
    config = Configurator(settings=settings)
    
    # Регистрируем кастомный JSON рендерер
    config.add_renderer('json', json_renderer_factory)
    
    # Включаем поддержку Jinja2 шаблонов
    config.include('pyramid_jinja2')
    
    # Настраиваем статические файлы
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    # Настраиваем маршруты
    config.add_route('home', '/')
    config.add_route('graphql', '/graphql')
    
    # Включаем REST API
    config.include('backend.views.api', route_prefix='/api')
    
    # Сканируем views
    config.scan('.views')
    
    # Добавляем подписчика на события для CORS
    config.add_subscriber(add_cors_headers, NewRequest)
    
    return config.make_wsgi_app()