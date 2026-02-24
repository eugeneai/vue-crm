"""
Backend пакет для личной CRM системы.
"""

from pyramid.config import Configurator


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
    
    # Включаем поддержку Jinja2 шаблонов
    config.include('pyramid_jinja2')
    
    # Настраиваем статические файлы
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    # Настраиваем маршруты
    config.add_route('home', '/')
    config.add_route('graphql', '/graphql')
    
    # Сканируем views
    config.scan('.views')
    
    return config.make_wsgi_app()