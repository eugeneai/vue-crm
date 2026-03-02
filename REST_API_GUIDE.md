# Руководство по REST API v1.0

## 📋 Обзор

REST API версии 1.0 предоставляет полный набор эндпоинтов для работы с личной CRM системой. API реализован на Pyramid с поддержкой CORS и JSON форматом данных.

## 🚀 Быстрый старт

### Установка зависимостей
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Запуск сервера
```bash
pserve development.ini --reload
```

Сервер будет доступен по адресу: `http://localhost:6543`

## 🌐 Базовые эндпоинты

### Контакты
```
GET    /api/v1.0/contacts           # Список контактов
GET    /api/v1.0/contacts/{id}      # Контакт по ID
POST   /api/v1.0/contacts           # Создать контакт
PUT    /api/v1.0/contacts/{id}      # Обновить контакт
DELETE /api/v1.0/contacts/{id}      # Удалить контакт
```

### Встречи
```
GET    /api/v1.0/meetings           # Список встреч
GET    /api/v1.0/meetings/{id}      # Встреча по ID
POST   /api/v1.0/meetings           # Создать встречу
PUT    /api/v1.0/meetings/{id}      # Обновить встречу
DELETE /api/v1.0/meetings/{id}      # Удалить встречу
```

### Заметки
```
GET    /api/v1.0/notes              # Список заметок
GET    /api/v1.0/notes/{id}         # Заметка по ID
POST   /api/v1.0/notes              # Создать заметку
PUT    /api/v1.0/notes/{id}         # Обновить заметку
DELETE /api/v1.0/notes/{id}         # Удалить заметку
```

### Отчеты
```
GET /api/v1.0/reports/upcoming-meetings    # Предстоящие встречи
GET /api/v1.0/reports/contact-history/{id} # История контакта
```

## 📝 Примеры использования

### Получить список контактов с пагинацией
```bash
curl "http://localhost:6543/api/v1.0/contacts?page=1&per_page=20"
```

### Создать новый контакт
```bash
curl -X POST "http://localhost:6543/api/v1.0/contacts" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Иван Иванов",
    "company": "ООО Рога и Копыта",
    "phone": "+7 (999) 123-45-67",
    "email": "ivan@example.com"
  }'
```

### Получить предстоящие встречи
```bash
curl "http://localhost:6543/api/v1.0/reports/upcoming-meetings?days=7"
```

### Получить историю контакта
```bash
curl "http://localhost:6543/api/v1.0/reports/contact-history/1"
```

## 🔍 Параметры запросов

### Пагинация
- `page` - номер страницы (по умолчанию: 1)
- `per_page` - элементов на странице (по умолчанию: 20)

### Фильтрация контактов
- `search` - поиск по имени или компании
- `company` - фильтрация по компании

### Фильтрация встреч
- `contact_id` - встречи конкретного контакта
- `start_date` - начало периода (ISO формат)
- `end_date` - конец периода (ISO формат)

### Фильтрация заметок
- `meeting_id` - заметки конкретной встречи
- `start_date` - начало периода (YYYY-MM-DD)
- `end_date` - конец периода (YYYY-MM-DD)

### Отчеты
- `days` - количество дней для предстоящих встреч (по умолчанию: 7)

## 📊 Форматы данных

### Контакт
```json
{
  "id": 1,
  "full_name": "Иван Иванов",
  "company": "ООО Рога и Копыта",
  "phone": "+7 (999) 123-45-67",
  "email": "ivan@example.com"
}
```

### Встреча
```json
{
  "id": 1,
  "contact_id": 1,
  "date_time": "2024-01-20T14:30:00",
  "topic": "Обсуждение проекта",
  "location": "Офис, кабинет 305"
}
```

### Заметка
```json
{
  "id": 1,
  "meeting_id": 1,
  "date": "2024-01-20",
  "text": "Договорились о следующей встрече через неделю"
}
```

## 🛡️ Валидация данных

### Контакт
- `full_name`: обязательное, 2-200 символов
- `company`: 0-200 символов
- `phone`: 0-50 символов
- `email`: 0-100 символов

### Встреча
- `contact_id`: обязательное, существующий контакт
- `date_time`: обязательное, будущая дата при создании
- `topic`: обязательное, 1-500 символов
- `location`: 0-200 символов

### Заметка
- `meeting_id`: обязательное, существующая встреча
- `date`: обязательное, валидная дата
- `text`: обязательное, не пустое

## ⚠️ Коды ответов

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс создан
- `400 Bad Request` - Неверные данные запроса
- `404 Not Found` - Ресурс не найден
- `422 Unprocessable Entity` - Ошибка валидации
- `500 Internal Server Error` - Серверная ошибка

## 🔧 CORS поддержка

API поддерживает CORS для кросс-доменных запросов. Разрешены все домены (`*`).

### Разрешенные методы:
- GET, POST, PUT, DELETE, OPTIONS

### Разрешенные заголовки:
- Content-Type, Authorization, Accept

## 🧪 Тестирование

### Проверка структуры API
```bash
python test_api_structure.py
```

### Пример теста с curl
```bash
# Проверка доступности API
curl -I "http://localhost:6543/api/v1.0/contacts"

# Создание тестового контакта
curl -X POST "http://localhost:6543/api/v1.0/contacts" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Тестовый Контакт"}'
```

## 📁 Структура файлов

```
backend/
├── __init__.py              # Конфигурация Pyramid
├── views/
│   ├── __init__.py
│   └── api/
│       ├── __init__.py      # Маршрутизация API
│       └── v1/
│           ├── __init__.py  # Маршруты v1.0
│           └── views.py     # View функции
├── models/
│   ├── contact.py          # Модель Contact
│   ├── meeting.py          # Модель Meeting
│   └── note.py             # Модель Note
└── development.ini         # Конфигурация разработки
```

## 🔄 Интеграция с фронтендом

### Пример использования во Vue.js
```javascript
// composition API
import { ref } from 'vue'

export function useContactsApi() {
  const contacts = ref([])
  const loading = ref(false)
  
  const fetchContacts = async (page = 1) => {
    loading.value = true
    try {
      const response = await fetch(`/api/v1.0/contacts?page=${page}`)
      const data = await response.json()
      contacts.value = data.data
      return data.pagination
    } finally {
      loading.value = false
    }
  }
  
  return { contacts, loading, fetchContacts }
}
```

## 📚 Дополнительная информация

- Полная документация структур данных: [STRUCTURES.md](STRUCTURES.md)
- Архитектура приложения: [ARCHITECTURE.md](ARCHITECTURE.md)
- Контекст разработки: [CONTEXT.md](CONTEXT.md)

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте, что сервер запущен: `pserve development.ini --reload`
2. Проверьте логи сервера в консоли
3. Убедитесь, что база данных существует и доступна
4. Проверьте правильность формата JSON в запросах