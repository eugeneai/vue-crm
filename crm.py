#!/usr/bin/env python3
"""
CRM CLI Client - Командный интерфейс для работы с личной CRM системой через REST API.

Использование:
    python crm.py [команда] [опции]

Примеры:
    python crm.py contacts list
    python crm.py contacts create --name "Иван Иванов" --company "ООО Тест"
    python crm.py contacts get 1
    python crm.py contacts update 1 --name "Иван Петров"
    python crm.py contacts delete 1
"""

import argparse
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from requests.exceptions import RequestException, ConnectionError, Timeout
from dataclasses import dataclass
import configparser
from pathlib import Path


# ========== Конфигурация ==========

class Config:
    """Класс для управления конфигурацией CLI клиента"""
    
    DEFAULT_CONFIG = {
        'api': {
            'base_url': 'http://localhost:6543/api/v1.0',
            'timeout': '30'
        },
        'display': {
            'date_format': '%%Y-%%m-%%d %%H:%%M',  # Двойные %% для экранирования
            'items_per_page': '20'
        }
    }
    
    def __init__(self):
        self.config_dir = Path.home() / '.crm-cli'
        self.config_file = self.config_dir / 'config.ini'
        self.config = configparser.ConfigParser()
        
        # Создаем директорию конфигурации если не существует
        self.config_dir.mkdir(exist_ok=True)
        
        # Загружаем конфигурацию
        self.load()
    
    def load(self):
        """Загрузить конфигурацию из файла"""
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            # Создаем конфигурацию по умолчанию
            self.config.read_dict(self.DEFAULT_CONFIG)
            self.save()
    
    def save(self):
        """Сохранить конфигурацию в файл"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section: str, key: str, default: Optional[str] = None) -> str:
        """Получить значение конфигурации"""
        try:
            value = self.config.get(section, key)
            # Заменяем двойные %% на одинарные % для формата даты
            if key == 'date_format':
                value = value.replace('%%', '%')
            return value
        except (configparser.NoSectionError, configparser.NoOptionError):
            default_value = default or self.DEFAULT_CONFIG.get(section, {}).get(key, '')
            if key == 'date_format':
                default_value = default_value.replace('%%', '%')
            return default_value
    
    def set(self, section: str, key: str, value: str):
        """Установить значение конфигурации"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self.save()


# ========== Модель контакта ==========

@dataclass
class Contact:
    """Модель контакта"""
    id: Optional[int] = None
    full_name: str = ''
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь для API"""
        data = {'full_name': self.full_name}
        if self.company:
            data['company'] = self.company
        if self.phone:
            data['phone'] = self.phone
        if self.email:
            data['email'] = self.email
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contact':
        """Создать из словаря API"""
        return cls(
            id=data.get('id'),
            full_name=data.get('full_name', ''),
            company=data.get('company'),
            phone=data.get('phone'),
            email=data.get('email')
        )
    
    def display(self, verbose: bool = False) -> str:
        """Отобразить контакт в читаемом формате"""
        lines = [
            f"👤 {self.full_name}",
            f"   ID: {self.id}" if self.id else ""
        ]
        
        if self.company:
            lines.append(f"   🏢 Компания: {self.company}")
        if self.phone:
            lines.append(f"   📞 Телефон: {self.phone}")
        if self.email:
            lines.append(f"   ✉️  Email: {self.email}")
        
        return "\n".join(filter(None, lines))


# ========== API клиент ==========

class CRMClient:
    """Клиент для работы с CRM REST API"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.get('api', 'base_url')
        self.timeout = int(config.get('api', 'timeout', '30'))
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполнить HTTP запрос к API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # Обработка пустого ответа (204 No Content)
            if response.status_code == 204:
                return {}
            
            # Парсим JSON ответ
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = {'message': response.text}
            
            # Проверяем статус код
            if not response.ok:
                error_msg = data.get('message', data.get('error', 'Unknown error'))
                raise CRMError(f"API Error {response.status_code}: {error_msg}")
            
            return data
            
        except ConnectionError:
            raise CRMError(f"Не удалось подключиться к серверу: {self.base_url}")
        except Timeout:
            raise CRMError(f"Таймаут запроса ({self.timeout} секунд)")
        except RequestException as e:
            raise CRMError(f"Ошибка сети: {str(e)}")
    
    # ========== Контакты ==========
    
    def list_contacts(self, page: int = 1, per_page: int = 20, 
                     search: Optional[str] = None, company: Optional[str] = None) -> Dict[str, Any]:
        """Получить список контактов"""
        params = {'page': page, 'per_page': per_page}
        if search:
            params['search'] = search
        if company:
            params['company'] = company
        
        data = self._request('GET', '/contacts', params=params)
        
        # Конвертируем данные контактов в объекты
        if 'data' in data:
            data['data'] = [Contact.from_dict(contact) for contact in data['data']]
        
        return data
    
    def get_contact(self, contact_id: int) -> Contact:
        """Получить контакт по ID"""
        data = self._request('GET', f'/contacts/{contact_id}')
        return Contact.from_dict(data)
    
    def create_contact(self, contact: Contact) -> Contact:
        """Создать новый контакт"""
        data = self._request('POST', '/contacts', json=contact.to_dict())
        return Contact.from_dict(data)
    
    def update_contact(self, contact_id: int, contact: Contact) -> Contact:
        """Обновить контакт"""
        data = self._request('PUT', f'/contacts/{contact_id}', json=contact.to_dict())
        return Contact.from_dict(data)
    
    def delete_contact(self, contact_id: int) -> None:
        """Удалить контакт"""
        self._request('DELETE', f'/contacts/{contact_id}')


# ========== Ошибки ==========

class CRMError(Exception):
    """Базовый класс ошибок CRM клиента"""
    pass


class ValidationError(CRMError):
    """Ошибка валидации данных"""
    pass


# ========== Валидация ==========

def validate_contact_data(args: argparse.Namespace) -> Contact:
    """Валидация данных контакта"""
    if not args.name:
        raise ValidationError("Имя контакта обязательно (--name)")
    
    contact = Contact(
        full_name=args.name,
        company=args.company if hasattr(args, 'company') else None,
        phone=args.phone if hasattr(args, 'phone') else None,
        email=args.email if hasattr(args, 'email') else None
    )
    
    return contact


# ========== Утилиты отображения ==========

def display_pagination(pagination: Dict[str, Any]):
    """Отобразить информацию о пагинации"""
    if pagination:
        print(f"\n📄 Страница {pagination['page']} из {pagination['total_pages']} "
              f"(всего: {pagination['total']})")
        if pagination['has_next'] or pagination['has_prev']:
            nav = []
            if pagination['has_prev']:
                nav.append("← предыдущая")
            if pagination['has_next']:
                nav.append("следующая →")
            print(f"   Навигация: {', '.join(nav)}")


def display_table(data: List[Any], columns: List[str], get_row_func):
    """Отобразить данные в табличном формате"""
    if not data:
        print("Нет данных для отображения")
        return
    
    # Вычисляем ширину колонок
    col_widths = [len(col) for col in columns]
    
    for item in data:
        row = get_row_func(item)
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Отображаем заголовок
    header = " | ".join(col.ljust(width) for col, width in zip(columns, col_widths))
    print(header)
    print("-" * len(header))
    
    # Отображаем данные
    for item in data:
        row = get_row_func(item)
        print(" | ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths)))


# ========== Команды для контактов ==========

def handle_contacts_list(args: argparse.Namespace, client: CRMClient, config: Config):
    """Обработка команды list контактов"""
    try:
        result = client.list_contacts(
            page=args.page,
            per_page=args.per_page,
            search=args.search,
            company=args.company
        )
        
        contacts = result.get('data', [])
        pagination = result.get('pagination')
        
        if args.format == 'table':
            columns = ['ID', 'Имя', 'Компания', 'Телефон', 'Email']
            def get_row(contact):
                return [
                    contact.id or '',
                    contact.full_name,
                    contact.company or '',
                    contact.phone or '',
                    contact.email or ''
                ]
            display_table(contacts, columns, get_row)
        else:
            for contact in contacts:
                print(contact.display(verbose=args.verbose))
                if args.verbose:
                    print()
        
        if pagination:
            display_pagination(pagination)
            
    except CRMError as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def handle_contacts_get(args: argparse.Namespace, client: CRMClient, config: Config):
    """Обработка команды get контакта"""
    try:
        contact = client.get_contact(args.id)
        print(contact.display(verbose=True))
    except CRMError as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def handle_contacts_create(args: argparse.Namespace, client: CRMClient, config: Config):
    """Обработка команды create контакта"""
    try:
        contact = validate_contact_data(args)
        created_contact = client.create_contact(contact)
        print("✅ Контакт успешно создан:")
        print(created_contact.display(verbose=True))
    except (ValidationError, CRMError) as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def handle_contacts_update(args: argparse.Namespace, client: CRMClient, config: Config):
    """Обработка команды update контакта"""
    try:
        contact = validate_contact_data(args)
        updated_contact = client.update_contact(args.id, contact)
        print("✅ Контакт успешно обновлен:")
        print(updated_contact.display(verbose=True))
    except (ValidationError, CRMError) as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


def handle_contacts_delete(args: argparse.Namespace, client: CRMClient, config: Config):
    """Обработка команды delete контакта"""
    try:
        if not args.yes:
            confirm = input(f"Вы уверены, что хотите удалить контакт с ID {args.id}? (y/N): ")
            if confirm.lower() != 'y':
                print("❌ Удаление отменено")
                return
        
        client.delete_contact(args.id)
        print(f"✅ Контакт с ID {args.id} успешно удален")
    except CRMError as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


# ========== Парсер аргументов ==========

def create_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='CRM CLI Client - Командный интерфейс для работы с личной CRM системой',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s contacts list
  %(prog)s contacts create --name "Иван Иванов" --company "ООО Тест"
  %(prog)s contacts get 1
  %(prog)s contacts update 1 --name "Иван Петров" --phone "+79991234567"
  %(prog)s contacts delete 1 --yes
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Команда', required=True)
    
    # ========== Контакты ==========
    contacts_parser = subparsers.add_parser('contacts', help='Работа с контактами')
    contacts_subparsers = contacts_parser.add_subparsers(dest='subcommand', required=True)
    
    # contacts list
    list_parser = contacts_subparsers.add_parser('list', help='Список контактов')
    list_parser.add_argument('--page', type=int, default=1, help='Номер страницы')
    list_parser.add_argument('--per-page', type=int, default=20, help='Элементов на странице')
    list_parser.add_argument('--search', help='Поиск по имени или компании')
    list_parser.add_argument('--company', help='Фильтр по компании')
    list_parser.add_argument('--format', choices=['table', 'detailed'], default='detailed', help='Формат вывода')
    list_parser.add_argument('--verbose', '-v', action='store_true', help='Подробный вывод')
    
    # contacts get
    get_parser = contacts_subparsers.add_parser('get', help='Получить контакт по ID')
    get_parser.add_argument('id', type=int, help='ID контакта')
    
    # contacts create
    create_parser = contacts_subparsers.add_parser('create', help='Создать новый контакт')
    create_parser.add_argument('--name', required=True, help='ФИО контакта')
    create_parser.add_argument('--company', help='Компания')
    create_parser.add_argument('--phone', help='Телефон')
    create_parser.add_argument('--email', help='Email')
    
    # contacts update
    update_parser = contacts_subparsers.add_parser('update', help='Обновить контакт')
    update_parser.add_argument('id', type=int, help='ID контакта')
    update_parser.add_argument('--name', required=True, help='ФИО контакта')
    update_parser.add_argument('--company', help='Компания')
    update_parser.add_argument('--phone', help='Телефон')
    update_parser.add_argument('--email', help='Email')
    
    # contacts delete
    delete_parser = contacts_subparsers.add_parser('delete', help='Удалить контакт')
    delete_parser.add_argument('id', type=int, help='ID контакта')
    delete_parser.add_argument('--yes', '-y', action='store_true', help='Подтвердить удаление без запроса')
    
    return parser


# ========== Основная функция ==========

def main():
    """Основная функция CLI клиента"""
    # Создаем конфигурацию
    config = Config()
    
    # Создаем API клиент
    client = CRMClient(config)
    
    # Парсим аргументы командной строки
    parser = create_parser()
    args = parser.parse_args()
    
    # Обрабатываем команду
    if args.command == 'contacts':
        if args.subcommand == 'list':
            handle_contacts_list(args, client, config)
        elif args.subcommand == 'get':
            handle_contacts_get(args, client, config)
        elif args.subcommand == 'create':
            handle_contacts_create(args, client, config)
        elif args.subcommand == 'update':
            handle_contacts_update(args, client, config)
        elif args.subcommand == 'delete':
            handle_contacts_delete(args, client, config)


if __name__ == '__main__':
    main()