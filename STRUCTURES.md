# Структуры данных личной CRM системы

## 🗄️ Модели базы данных (SQLAlchemy 2.0+)

### **Contact (Контакты)**
```python
class Contact(Base):
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)      # ФИО
    company = Column(String(200))                       # Место работы
    phone = Column(String(50))                          # Телефон
    email = Column(String(100))                         # Email (опционально)
    
    # Отношения
    meetings = relationship("Meeting", back_populates="contact", cascade="all, delete-orphan")
```

**Индексы:**
- `full_name` - для поиска по имени
- `company` - для фильтрации по компании
- `phone` - для быстрого поиска по телефону

### **Meeting (Встречи)**
```python
class Meeting(Base):
    __tablename__ = 'meetings'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    date_time = Column(DateTime, nullable=False)        # Дата и время встречи
    topic = Column(String(500), nullable=False)         # Тема встречи
    location = Column(String(200))                      # Место встречи
    
    # Отношения
    contact = relationship("Contact", back_populates="meetings")
    notes = relationship("Note", back_populates="meeting", cascade="all, delete-orphan")
```

**Индексы:**
- `date_time` - для сортировки и фильтрации по дате
- `contact_id` - для JOIN с контактами
- `topic` - для поиска по теме

### **Note (Заметки)**
```python
class Note(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'), nullable=False)
    date = Column(Date, nullable=False)                 # Дата заметки
    text = Column(Text, nullable=False)                 # Текст заметки
    
    # Отношения
    meeting = relationship("Meeting", back_populates="notes")
```

**Индексы:**
- `meeting_id` - для связи с встречами
- `date` - для сортировки заметок по дате

## 🔗 Схема отношений

```
Contact (1) ──── (∞) Meeting (1) ──── (∞) Note
    │                    │
    └─ full_name         ├─ date_time
       company           ├─ topic
       phone             └─ location
       email
```

**Каскадные операции:**
- Удаление Contact → удаление всех связанных Meeting → удаление всех связанных Note
- Удаление Meeting → удаление всех связанных Note

## 📊 GraphQL схемы (Graphene-Python)

### **Типы данных**

```python
# ContactType
class ContactType(ObjectType):
    id = Int()
    full_name = String()
    company = String()
    phone = String()
    email = String()
    meetings = List(lambda: MeetingType)  # Список встреч контакта

# MeetingType  
class MeetingType(ObjectType):
    id = Int()
    contact = Field(ContactType)          # Контакт встречи
    date_time = DateTime()
    topic = String()
    location = String()
    notes = List(lambda: NoteType)        # Список заметок встречи

# NoteType
class NoteType(ObjectType):
    id = Int()
    meeting = Field(MeetingType)          # Встреча заметки
    date = Date()
    text = String()
```

### **Запросы (Queries)**

```python
class Query(ObjectType):
    # Контакты
    contact = Field(ContactType, id=Int(required=True))
    contacts = List(ContactType, 
                   search=String(),
                   company=String(),
                   limit=Int(default_value=100),
                   offset=Int(default_value=0))
    
    # Встречи
    meeting = Field(MeetingType, id=Int(required=True))
    meetings = List(MeetingType,
                   contact_id=Int(),
                   start_date=DateTime(),
                   end_date=DateTime(),
                   limit=Int(default_value=100),
                   offset=Int(default_value=0))
    
    # Заметки
    note = Field(NoteType, id=Int(required=True))
    notes = List(NoteType,
                meeting_id=Int(),
                start_date=Date(),
                end_date=Date(),
                limit=Int(default_value=100),
                offset=Int(default_value=0))
```

### **Мутации (Mutations)**

```python
class CreateContact(Mutation):
    class Arguments:
        full_name = String(required=True)
        company = String()
        phone = String()
        email = String()
    
    contact = Field(ContactType)
    
    def mutate(self, info, **kwargs):
        # Создание контакта
        pass

class CreateMeeting(Mutation):
    class Arguments:
        contact_id = Int(required=True)
        date_time = DateTime(required=True)
        topic = String(required=True)
        location = String()
    
    meeting = Field(MeetingType)
    
    def mutate(self, info, **kwargs):
        # Создание встречи
        pass

class CreateNote(Mutation):
    class Arguments:
        meeting_id = Int(required=True)
        date = Date(required=True)
        text = String(required=True)
    
    note = Field(NoteType)
    
    def mutate(self, info, **kwargs):
        # Создание заметки
        pass
```

## 📄 Выходные документы (GraphQL запросы)

### **1. 📅 Предстоящие встречи на неделю**
```graphql
query UpcomingMeetings($startDate: DateTime!, $endDate: DateTime!) {
  meetings(
    filter: { 
      dateTime: { 
        gte: $startDate, 
        lte: $endDate 
      }
    }
    orderBy: [{ 
      field: dateTime, 
      direction: ASC 
    }]
    limit: 50
  ) {
    id
    dateTime
    topic
    location
    contact {
      id
      fullName
      company
      phone
    }
    notes {
      id
      date
      text
    }
  }
}
```

**Параметры:**
- `startDate`: текущая дата
- `endDate`: текущая дата + 7 дней

### **2. 📋 История встреч и заметок по контакту**
```graphql
query ContactHistory($contactId: Int!) {
  contact(id: $contactId) {
    id
    fullName
    company
    meetings {
      id
      dateTime
      topic
      location
      notes {
        id
        date
        text
      }
    }
  }
}
```

## 🎯 TypeScript типы (Frontend)

```typescript
// Типы для GraphQL ответов
interface Contact {
  id: number
  full_name: string
  company?: string
  phone?: string
  email?: string
  meetings?: Meeting[]
}

interface Meeting {
  id: number
  contact_id: number
  date_time: string  // ISO format
  topic: string
  location?: string
  contact?: Contact
  notes?: Note[]
}

interface Note {
  id: number
  meeting_id: number
  date: string  // YYYY-MM-DD
  text: string
  meeting?: Meeting
}

// Типы для форм
interface ContactForm {
  full_name: string
  company: string
  phone: string
  email: string
}

interface MeetingForm {
  contact_id: number
  date_time: string
  topic: string
  location: string
}

interface NoteForm {
  meeting_id: number
  date: string
  text: string
}
```

## 🔍 Индексы базы данных

```sql
-- Контакты
CREATE INDEX idx_contacts_full_name ON contacts(full_name);
CREATE INDEX idx_contacts_company ON contacts(company);
CREATE INDEX idx_contacts_phone ON contacts(phone);

-- Встречи
CREATE INDEX idx_meetings_date_time ON meetings(date_time);
CREATE INDEX idx_meetings_contact_id ON meetings(contact_id);
CREATE INDEX idx_meetings_topic ON meetings(topic);

-- Заметки
CREATE INDEX idx_notes_meeting_id ON notes(meeting_id);
CREATE INDEX idx_notes_date ON notes(date);
```

## 📈 Оптимизация производительности

1. **Ленивая загрузка** отношений в GraphQL
2. **Пагинация** для списков контактов и встреч
3. **Кэширование** часто запрашиваемых данных
4. **Индексы** для всех полей используемых в WHERE и ORDER BY
5. **Оптимизация JOIN** через правильные индексы

## 🔒 Валидация данных

### **Contact валидация:**
- `full_name`: обязательное, 2-200 символов
- `company`: 0-200 символов
- `phone`: формат телефона (опционально)
- `email`: формат email (опционально)

### **Meeting валидация:**
- `contact_id`: существующий контакт
- `date_time`: будущая дата при создании
- `topic`: обязательное, 1-500 символов
- `location`: 0-200 символов

### **Note валидация:**
- `meeting_id`: существующая встреча
- `date`: валидная дата
- `text`: обязательное, не пустое

## 🌐 REST API (Pyramid Views)

### **Базовые эндпоинты**

#### **Контакты**
```
GET    /api/contacts           - Список контактов с пагинацией
GET    /api/contacts/{id}      - Получить контакт по ID
POST   /api/contacts           - Создать новый контакт
PUT    /api/contacts/{id}      - Обновить контакт
DELETE /api/contacts/{id}      - Удалить контакт
```

#### **Встречи**
```
GET    /api/meetings           - Список встреч с фильтрацией
GET    /api/meetings/{id}      - Получить встречу по ID
POST   /api/meetings           - Создать новую встречу
PUT    /api/meetings/{id}      - Обновить встречу
DELETE /api/meetings/{id}      - Удалить встречу
```

#### **Заметки**
```
GET    /api/notes              - Список заметок
GET    /api/notes/{id}         - Получить заметку по ID
POST   /api/notes              - Создать новую заметку
PUT    /api/notes/{id}         - Обновить заметку
DELETE /api/notes/{id}         - Удалить заметку
```

### **Специальные эндпоинты**

#### **Фильтрация и поиск**
```
GET /api/contacts?search={text}            - Поиск контактов по имени/компании
GET /api/contacts?company={company_name}   - Фильтрация по компании
GET /api/meetings?contact_id={id}          - Встречи конкретного контакта
GET /api/meetings?start_date={date}&end_date={date} - Встречи в диапазоне дат
GET /api/notes?meeting_id={id}             - Заметки конкретной встречи
```

#### **Агрегации и отчеты**
```
GET /api/reports/upcoming-meetings?days=7  - Предстоящие встречи на N дней
GET /api/reports/contact-history/{id}      - Полная история контакта
```

### **Формат запросов и ответов**

#### **Создание контакта (POST /api/contacts)**
```json
{
  "full_name": "Иван Иванов",
  "company": "ООО Рога и Копыта",
  "phone": "+7 (999) 123-45-67",
  "email": "ivan@example.com"
}
```

#### **Ответ (201 Created)**
```json
{
  "id": 1,
  "full_name": "Иван Иванов",
  "company": "ООО Рога и Копыта",
  "phone": "+7 (999) 123-45-67",
  "email": "ivan@example.com",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### **Создание встречи (POST /api/meetings)**
```json
{
  "contact_id": 1,
  "date_time": "2024-01-20T14:30:00Z",
  "topic": "Обсуждение проекта",
  "location": "Офис, кабинет 305"
}
```

#### **Создание заметки (POST /api/notes)**
```json
{
  "meeting_id": 1,
  "date": "2024-01-20",
  "text": "Договорились о следующей встрече через неделю"
}
```

### **Пагинация**

#### **Запрос с пагинацией**
```
GET /api/contacts?page=1&per_page=20
```

#### **Ответ с пагинацией**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### **Коды ответов**

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс создан
- `400 Bad Request` - Неверные данные запроса
- `404 Not Found` - Ресурс не найден
- `422 Unprocessable Entity` - Ошибка валидации
- `500 Internal Server Error` - Серверная ошибка

### **Обработка ошибок**

#### **Ошибка валидации (422)**
```json
{
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": {
    "full_name": ["This field is required"],
    "email": ["Invalid email format"]
  }
}
```

#### **Ресурс не найден (404)**
```json
{
  "error": "NotFound",
  "message": "Contact with id 999 not found"
}
```

### **Заголовки запросов**

```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token}  # Для будущей аутентификации
```

### **Примеры Pyramid View функций**

```python
from pyramid.view import view_config
from pyramid.response import Response
import json

@view_config(route_name='contacts', request_method='GET', renderer='json')
def list_contacts(request):
    """GET /api/contacts - список контактов с пагинацией"""
    page = int(request.params.get('page', 1))
    per_page = int(request.params.get('per_page', 20))
    search = request.params.get('search')
    
    query = request.dbsession.query(Contact)
    
    if search:
        query = query.filter(
            Contact.full_name.ilike(f'%{search}%') |
            Contact.company.ilike(f'%{search}%')
        )
    
    total = query.count()
    contacts = query.offset((page-1)*per_page).limit(per_page).all()
    
    return {
        'data': [contact.to_dict() for contact in contacts],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page,
            'has_next': page * per_page < total,
            'has_prev': page > 1
        }
    }

@view_config(route_name='contact_detail', request_method='GET', renderer='json')
def get_contact(request):
    """GET /api/contacts/{id} - получить контакт по ID"""
    contact_id = int(request.matchdict['id'])
    contact = request.dbsession.query(Contact).get(contact_id)
    
    if not contact:
        request.response.status = 404
        return {'error': 'NotFound', 'message': f'Contact with id {contact_id} not found'}
    
    return contact.to_dict()

@view_config(route_name='contacts', request_method='POST', renderer='json')
def create_contact(request):
    """POST /api/contacts - создать новый контакт"""
    try:
        data = request.json_body
        
        # Валидация
        if not data.get('full_name'):
            request.response.status = 422
            return {'error': 'ValidationError', 'message': 'full_name is required'}
        
        contact = Contact(
            full_name=data['full_name'],
            company=data.get('company'),
            phone=data.get('phone'),
            email=data.get('email')
        )
        
        request.dbsession.add(contact)
        request.dbsession.flush()
        
        request.response.status = 201
        return contact.to_dict()
        
    except Exception as e:
        request.response.status = 400
        return {'error': 'BadRequest', 'message': str(e)}
```

### **Маршрутизация Pyramid**

```python
def includeme(config):
    config.add_route('contacts', '/api/contacts')
    config.add_route('contact_detail', '/api/contacts/{id}')
    config.add_route('meetings', '/api/meetings')
    config.add_route('meeting_detail', '/api/meetings/{id}')
    config.add_route('notes', '/api/notes')
    config.add_route('note_detail', '/api/notes/{id}')
    config.add_route('upcoming_meetings', '/api/reports/upcoming-meetings')
    config.add_route('contact_history', '/api/reports/contact-history/{id}')
    
    config.scan('.views')  # Сканирование view функций
```

### **Методы моделей для сериализации**

```python
class Contact(Base):
    # ... существующие поля ...
    
    def to_dict(self):
        """Сериализация контакта в словарь"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'company': self.company,
            'phone': self.phone,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Десериализация словаря в объект контакта"""
        return cls(
            full_name=data.get('full_name'),
            company=data.get('company'),
            phone=data.get('phone'),
            email=data.get('email')
        )
```

### **CORS настройки**

```python
# В __init__.py Pyramid приложения
from pyramid.config import Configurator

def main(global_config, **settings):
    config = Configurator(settings=settings)
    
    # Включение CORS
    config.add_cors_preflight_handler()
    config.add_route_predicate('cors_preflight', CorsPreflightPredicate)
    
    # Разрешение CORS для всех эндпоинтов
    config.add_route('cors_preflight', '/{catch_all:.*}', 
                     cors_preflight=True, 
                     request_method='OPTIONS')
    
    config.set_cors_policy({
        'allow_origin': ['http://localhost:5173'],  # Vue dev server
        'allow_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization', 'Accept'],
        'allow_credentials': True,
        'max_age': 3600
    })
    
    # ... остальная конфигурация ...
```

### **Аутентификация (задел на будущее)**

```python
# Middleware для проверки JWT токенов
class JWTAuthMiddleware:
    def __init__(self, app, secret_key):
        self.app = app
        self.secret_key = secret_key
    
    def __call__(self, environ, start_response):
        request = Request(environ)
        
        # Пропускаем публичные эндпоинты
        if request.path.startswith('/api/auth/'):
            return self.app(environ, start_response)
        
        # Проверка токена
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                environ['user_id'] = payload['user_id']
            except jwt.InvalidTokenError:
                start_response('401 Unauthorized', [('Content-Type', 'application/json')])
                return [json.dumps({'error': 'Invalid token'}).encode()]
        
        return self.app(environ, start_response)
```

### **Тестирование REST API**

```python
# Пример теста с pytest
def test_list_contacts(client):
    """Тест GET /api/contacts"""
    response = client.get('/api/contacts')
    assert response.status_code == 200
    data = response.json()
    assert 'data' in data
    assert 'pagination' in data

def test_create_contact(client):
    """Тест POST /api/contacts"""
    contact_data = {
        'full_name': 'Тестовый Контакт',
        'company': 'Тестовая Компания'
    }
    response = client.post('/api/contacts', json=contact_data)
    assert response.status_code == 201
    data = response.json()
    assert data['full_name'] == 'Тестовый Контакт'
    assert 'id' in data

def test_get_nonexistent_contact(client):
    """Тест GET /api/contacts/{id} для несуществующего контакта"""
    response = client.get('/api/contacts/999999')
    assert response.status_code == 404
    data = response.json()
    assert data['error'] == 'NotFound'
```

### **Интеграция с фронтендом**

```typescript
// Пример использования REST API во Vue компоненте
import { ref } from 'vue'

const useContactsApi = () => {
  const contacts = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const fetchContacts = async (page = 1, search = '') => {
    loading.value = true
    error.value = null
    
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '20'
      })
      
      if (search) {
        params.append('search', search)
      }
      
      const response = await fetch(`/api/contacts?${params}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`)
      }
      
      const data = await response.json()
      contacts.value = data.data
      return data.pagination
      
    } catch (err) {
      error.value = err.message
      console.error('Failed to fetch contacts:', err)
    } finally {
      loading.value = false
    }
  }
  
  const createContact = async (contactData) => {
    try {
      const response = await fetch('/api/contacts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(contactData)
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Failed to create contact')
      }
      
      return await response.json()
      
    } catch (err) {
      console.error('Failed to create contact:', err)
      throw err
    }
  }
  
  return { contacts, loading, error, fetchContacts, createContact }
}
```