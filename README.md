# Личная CRM система

![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?logo=vuedotjs)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)
![GraphQL](https://img.shields.io/badge/GraphQL-E10098?logo=graphql)
![SQLite](https://img.shields.io/badge/SQLite-07405E?logo=sqlite)

Личная CRM система для учета контактов и взаимодействий с архитектурой MWWM (Model-View-ViewModel-Worker-Model).

## 📋 Функциональность

### 🏷️ Сущности
- **Контакты**: ФИО, место работы, телефон, email
- **Встречи**: Дата и время, тема, место, связанные заметки
- **Заметки**: Дата, текст заметки (относятся к конкретной встрече)

### 🔄 Процессы
- Регистрация всех встреч и важных событий
- Управление контактами и их историей взаимодействий
- Добавление заметок к встречам

### 📄 Выходные документы
1. **📅 Список предстоящих встреч на неделю** с указанием контактов и тем, отсортированный по дате и времени
2. **📋 История всех встреч и заметок по контакту**, отсортированная по дате

## 🏗️ Архитектура

Приложение построено по паттерну **MWWM**:
- **Model**: SQLAlchemy 2.0+ + SQLite
- **View**: Vue.js 3.0 (декларативный) + TypeScript
- **ViewModel**: Vue Composition API + GraphQL Client
- **Worker**: Pyramid + Graphene (GraphQL)
- **Model**: Бизнес-логика + SQLAlchemy ORM

Подробнее в [ARCHITECTURE.md](ARCHITECTURE.md)

## 🛠️ Технологический стек

### Frontend
- **Vue.js 3.0** с Composition API
- **TypeScript** для строгой типизации
- **GraphQL Client** (Urql/Apollo)
- **Pinia** для управления состоянием
- **Vite** для сборки
- **Tailwind CSS** для стилей

### Backend
- **Pyramid** веб-фреймворк
- **SQLAlchemy 2.0+** ORM
- **Graphene-Python** для GraphQL
- **SQLite** база данных
- **Alembic** для миграций

### Инфраструктура
- **Docker** + **Docker Compose**
- **Git** для контроля версий

## 🚀 Быстрый старт

### Предварительные требования
- Node.js 18+
- Python 3.9+
- Docker и Docker Compose (опционально)

### Установка и запуск

#### Вариант 1: Docker (рекомендуется)
```bash
# Клонировать репозиторий
git clone <repository-url>
cd web-is-vue

# Запустить все сервисы
docker-compose up -d

# Приложение будет доступно по адресу:
# Frontend: http://localhost:3000
# Backend GraphQL: http://localhost:8000/graphql
```

#### Вариант 2: Локальная установка

**Backend:**
```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r backend/requirements.txt

# Настроить базу данных
cd backend
alembic upgrade head

# Запустить сервер
pserve development.ini
```

**Frontend:**
```bash
cd frontend

# Установить зависимости
npm install

# Запустить в режиме разработки
npm run dev

# Сборка для продакшена
npm run build
```

## 📁 Структура проекта

```
web-is-vue/
├── frontend/          # Vue.js 3 приложение
├── backend/           # Pyramid приложение
├── database/          # SQLite база данных
├── docs/              # Документация
├── tests/             # Тесты
├── docker-compose.yml # Docker конфигурация
├── ARCHITECTURE.md    # Архитектура приложения
├── STRUCTURES.md      # Структуры данных
└── CONTEXT.md         # Глобальный контекст
```

## 📚 Документация

- [ARCHITECTURE.md](ARCHITECTURE.md) - Детальная архитектура приложения
- [STRUCTURES.md](STRUCTURES.md) - Структуры данных и GraphQL схемы
- [CONTEXT.md](CONTEXT.md) - Глобальный контекст для разработчиков

### GraphQL API документация

После запуска бэкенда, GraphQL Playground доступен по адресу:
```
http://localhost:8000/graphql
```

**Основные запросы:**
```graphql
# Получить все контакты
query {
  contacts {
    id
    full_name
    company
    phone
  }
}

# Получить предстоящие встречи
query UpcomingMeetings($startDate: DateTime!, $endDate: DateTime!) {
  meetings(
    filter: { dateTime: { gte: $startDate, lte: $endDate } }
    orderBy: [{ field: dateTime, direction: ASC }]
  ) {
    id
    dateTime
    topic
    contact { full_name }
  }
}

# Получить историю контакта
query ContactHistory($contactId: Int!) {
  contact(id: $contactId) {
    full_name
    meetings {
      dateTime
      topic
      notes { text }
    }
  }
}
```

## 🧪 Тестирование

```bash
# Запустить тесты бэкенда
cd backend
pytest

# Запустить тесты фронтенда
cd frontend
npm test
```

## 🔧 Конфигурация

### Переменные окружения

**Frontend (.env):**
```env
VITE_GRAPHQL_ENDPOINT=http://localhost:8000/graphql
VITE_APP_TITLE="Личная CRM"
```

**Backend (development.ini):**
```ini
[app:main]
use = egg:backend

sqlalchemy.url = sqlite:///../database/contacts.db
graphql.enable_playground = true
```

## 📈 Разработка

### Создание новой функциональности

1. **Определить GraphQL схему** в `backend/schemas/`
2. **Создать SQLAlchemy модель** в `backend/models/`
3. **Добавить миграцию** через Alembic
4. **Создать Vue компоненты** в `frontend/src/components/`
5. **Добавить TypeScript типы** в `frontend/src/graphql/schema.ts`
6. **Протестировать** функциональность

### Коммиты

Используйте Conventional Commits:
- `feat:` Новая функциональность
- `fix:` Исправление ошибки
- `docs:` Изменения в документации
- `style:` Форматирование кода
- `refactor:` Рефакторинг кода
- `test:` Добавление тестов
- `chore:` Изменения в сборке или зависимостях

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для вашей функциональности (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'feat: add amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - смотрите файл LICENSE для деталей.

## 📞 Поддержка

- **Issues**: [GitHub Issues](https://github.com/your-username/web-is-vue/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/web-is-vue/discussions)

## 🔗 Полезные ссылки

- [Vue.js 3 Documentation](https://vuejs.org/guide/introduction.html)
- [Pyramid Documentation](https://docs.pylonsproject.org/projects/pyramid/en/latest/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [GraphQL Specification](https://spec.graphql.org/)
- [Graphene-Python Documentation](https://docs.graphene-python.org/en/latest/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)