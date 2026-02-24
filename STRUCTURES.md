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