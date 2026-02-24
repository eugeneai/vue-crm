# AGENTS.md - Руководство для агентов разработки

## 🚀 Команды сборки и тестирования

### **Frontend (Vue.js 3 + TypeScript)**
```bash
# Установка зависимостей
npm install

# Запуск в режиме разработки
npm run dev

# Сборка для продакшена
npm run build

# Предпросмотр собранного приложения
npm run preview

# Линтинг TypeScript
npm run type-check

# Линтинг и форматирование
npm run lint
npm run format

# Запуск тестов
npm test
npm run test:watch      # Запуск тестов в watch режиме
npm run test:coverage   # Тесты с покрытием кода

# Запуск одного теста
npm test -- --testNamePattern="ComponentName"
# или
npm test -- ComponentName.test.ts
```

### **Backend (Pyramid + Python)**
```bash
# Установка зависимостей
pip install -r backend/requirements.txt
# или с использованием poetry
poetry install

# Запуск сервера разработки
pserve backend/development.ini --reload

# Запуск тестов
pytest
pytest backend/tests/ -v              # Подробный вывод
pytest backend/tests/test_models.py   # Конкретный файл
pytest backend/tests/test_models.py::TestContactModel  # Конкретный класс
pytest -k "test_create_contact"       # По имени теста

# Линтинг Python
black backend/ --check                # Проверка форматирования
isort backend/ --check-only          # Проверка импортов
flake8 backend/                      # Проверка стиля кода
mypy backend/                        # Проверка типов

# Форматирование кода
black backend/
isort backend/

# Миграции базы данных
alembic upgrade head                 # Применить миграции
alembic revision --autogenerate -m "description"  # Создать миграцию
```

### **Полный стек (Docker)**
```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Пересборка образов
docker-compose build

# Просмотр логов
docker-compose logs -f
docker-compose logs frontend
docker-compose logs backend
```

## 📝 Стиль кода

### **Frontend (Vue.js + TypeScript)**
```typescript
// Импорты в порядке: внешние → внутренние, библиотеки → компоненты
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Contact } from '@/graphql/schema'
import ContactCard from '@/components/contacts/ContactCard.vue'

// Именование: PascalCase для компонентов, camelCase для остального
export default defineComponent({
  name: 'ContactList',  // PascalCase для имен компонентов
  components: { ContactCard },
  
  setup() {
    const router = useRouter()
    const contacts = ref<Contact[]>([])
    const isLoading = ref(false)
    
    // Компьютеды с префиксом 'is' для boolean
    const isEmpty = computed(() => contacts.value.length === 0)
    
    // Методы с глаголами
    const fetchContacts = async () => {
      isLoading.value = true
      try {
        const { data } = await contactQuery.executeQuery({})
        contacts.value = data.contacts
      } catch (error) {
        console.error('Failed to fetch contacts:', error)
        // Использовать централизованную обработку ошибок
      } finally {
        isLoading.value = false
      }
    }
    
    return { contacts, isLoading, isEmpty, fetchContacts }
  }
})
```

### **Backend (Python)**
```python
# Импорты в порядке: стандартные → сторонние → внутренние
import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from graphene import ObjectType, String as GString, Int, Field, List as GList

from .base import Base
from .contact import Contact

# Именование: snake_case для всего
class Meeting(Base):
    __tablename__ = 'meetings'
    
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), nullable=False)
    date_time = Column(DateTime, nullable=False)
    topic = Column(String(500), nullable=False)
    location = Column(String(200))
    
    # Отношения
    contact = relationship("Contact", back_populates="meetings")
    notes = relationship("Note", back_populates="meeting", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Meeting(id={self.id}, topic='{self.topic}')>"

# GraphQL схемы
class MeetingType(ObjectType):
    id = Int()
    contact = Field(lambda: ContactType)
    date_time = GString()
    topic = GString()
    location = GString()
    notes = GList(lambda: NoteType)
    
    @staticmethod
    def resolve_contact(meeting, info):
        # Ленивая загрузка отношений
        return meeting.contact
```

### **Обработка ошибок**
```typescript
// Frontend: использовать try/catch с конкретными типами ошибок
try {
  await mutation.executeMutation({ input })
} catch (error) {
  if (error instanceof GraphQLError) {
    showNotification('GraphQL Error', error.message, 'error')
  } else if (error instanceof NetworkError) {
    showNotification('Network Error', 'Please check your connection', 'error')
  } else {
    console.error('Unexpected error:', error)
    showNotification('Error', 'Something went wrong', 'error')
  }
}
```

```python
# Backend: использовать исключения с информативными сообщениями
def create_meeting(contact_id: int, date_time: datetime, topic: str) -> Meeting:
    if not topic or len(topic.strip()) == 0:
        raise ValueError("Meeting topic cannot be empty")
    
    if date_time < datetime.now():
        raise ValueError("Meeting date cannot be in the past")
    
    contact = Contact.query.get(contact_id)
    if not contact:
        raise ValueError(f"Contact with id {contact_id} not found")
    
    try:
        meeting = Meeting(
            contact_id=contact_id,
            date_time=date_time,
            topic=topic.strip()
        )
        db.session.add(meeting)
        db.session.commit()
        return meeting
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Failed to create meeting: {str(e)}")
```

## 🎯 Конвенции именования

### **Файлы**
- Vue компоненты: `PascalCase.vue` (`ContactList.vue`, `MeetingForm.vue`)
- TypeScript файлы: `camelCase.ts` (`contactStore.ts`, `meetingQueries.ts`)
- Python модули: `snake_case.py` (`contact_model.py`, `meeting_schema.py`)
- Тесты: `*.test.ts` или `*_test.py`

### **Переменные и функции**
- TypeScript: `camelCase` для переменных и функций, `PascalCase` для классов/типов
- Python: `snake_case` для всего
- Константы: `UPPER_SNAKE_CASE` в обоих языках

### **GraphQL**
- Типы: `PascalCase` (`ContactType`, `MeetingInput`)
- Поля: `camelCase` (`fullName`, `dateTime`)
- Мутации: `camelCase` с префиксом глагола (`createContact`, `updateMeeting`)

## 🔧 Конфигурационные файлы

### **Frontend (ожидаемые)**
- `package.json` - зависимости и скрипты
- `tsconfig.json` - конфигурация TypeScript
- `vite.config.ts` - конфигурация сборки
- `.eslintrc.js` - правила линтинга
- `.prettierrc` - правила форматирования

### **Backend (ожидаемые)**
- `pyproject.toml` / `setup.py` - зависимости Python
- `requirements.txt` - замороженные зависимости
- `alembic.ini` - конфигурация миграций
- `.flake8` / `.pylintrc` - правила линтинга

## 📁 Структура проекта

Следуйте структуре из [ARCHITECTURE.md](ARCHITECTURE.md):
- `frontend/src/components/` - Vue компоненты
- `frontend/src/stores/` - Pinia хранилища
- `frontend/src/graphql/` - GraphQL запросы и типы
- `backend/models/` - SQLAlchemy модели
- `backend/schemas/` - GraphQL схемы
- `backend/views/` - Pyramid обработчики

## ⚠️ Важные правила

1. **Только запрошенные компоненты** - не создавайте файлы без явного запроса
2. **Следуйте существующим паттернам** - проверяйте соседние файлы перед созданием новых
3. **Тестируйте изменения** - запускайте соответствующие тесты после изменений
4. **Проверяйте линтинг** - запускайте `npm run lint` или `black/isort/flake8`
5. **Документируйте сложную логику** - добавляйте комментарии к нетривиальному коду
6. **Используйте TypeScript/type hints** - всегда указывайте типы

## 🔄 Рабочий процесс

1. Прочитать [CONTEXT.md](CONTEXT.md) для понимания бизнес-логики
2. Проверить [STRUCTURES.md](STRUCTURES.md) для структур данных
3. Следовать конвенциям из этого файла
4. Запустить тесты и линтинг перед завершением работы
5. Обновлять документацию при изменении архитектуры