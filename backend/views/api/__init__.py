# Маршрутизация для REST API
from pyramid.config import Configurator


def includeme(config: Configurator):
    """Включение REST API маршрутов в Pyramid приложение"""
    
    # Включение версии 1.0 API
    config.include('.v1', route_prefix='/v1.0')