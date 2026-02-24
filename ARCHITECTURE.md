# Архитектура личной CRM системы

## 🏗️ Общая архитектура (MWWM)

Приложение построено по паттерну **Model-View-ViewModel-Worker-Model** (MWWM):

### **Model (Модель данных)**
- **SQLAlchemy 2.0+** модели для работы с базой данных
- **SQLite** как легковесная база данных
- **Graphene-Python** для GraphQL схем

### **View (Представление)**
- **Vue.js 3.0** с декларативным подходом
- **Компонентная архитектура** с Composition API
- **TypeScript** для строгой типизации

### **ViewModel (Модель представления)**
- **Vue Composition API** для реактивной логики
- **GraphQL клиент** (Urql/Apollo) для связи с бэкендом
- **Pinia** для управления состоянием

### **Worker (Рабочий слой)**
- **Pyramid** веб-фреймворк для обработки запросов
- **GraphQL эндпоинты** через Graphene
- **Бизнес-логика** и валидация данных

### **Model (Серверная модель)**
- **SQLAlchemy ORM** для работы с БД
- **Миграции** через Alembic
- **Оптимизация запросов** и индексы

## 📁 Структура проекта

```
web-is-vue/
├── frontend/                 # Vue.js 3 приложение
│   ├── src/
│   │   ├── components/       # Переиспользуемые компоненты
│   │   │   ├── ui/          # Базовые UI компоненты
│   │   │   ├── contacts/    # Компоненты для работы с контактами
│   │   │   ├── meetings/    # Компоненты для работы со встречами
│   │   │   └── notes/       # Компоненты для работы с заметками
│   │   ├── views/           # Страницы приложения
│   │   │   ├── Dashboard.vue    # Главная страница
│   │   │   ├── Contacts.vue     # Список контактов
│   │   │   ├── ContactDetail.vue # Детали контакта
│   │   │   └── Calendar.vue     # Календарь встреч
│   │   ├── stores/          # Состояние приложения (Pinia)
│   │   │   ├── contacts.ts
│   │   │   ├── meetings.ts
│   │   │   └── notes.ts
│   │   ├── composables/     # Composition API функции
│   │   │   ├── useContacts.ts
│   │   │   ├── useMeetings.ts
│   │   │   └── useNotes.ts
│   │   ├── graphql/         # GraphQL схемы и запросы
│   │   │   ├── schema.ts    # Типы TypeScript
│   │   │   ├── queries.ts   # GraphQL запросы
│   │   │   └── mutations.ts # GraphQL мутации
│   │   ├── router/          # Маршрутизация
│   │   │   └── index.ts
│   │   ├── App.vue          # Корневой компонент
│   │   └── main.ts          # Точка входа
│   ├── public/              # Статические файлы
│   ├── index.html           # HTML шаблон
│   ├── package.json         # Зависимости
│   ├── tsconfig.json        # Конфигурация TypeScript
│   ├── vite.config.ts       # Конфигурация Vite
│   └── .env                 # Переменные окружения
├── backend/                 # Pyramid приложение
│   ├── models/              # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── base.py          # Базовый класс модели
│   │   ├── contact.py       # Модель Contact
│   │   ├── meeting.py       # Модель Meeting
│   │   └── note.py          # Модель Note
│   ├── schemas/             # GraphQL схемы
│   │   ├── __init__.py
│   │   ├── contact_schema.py
│   │   ├── meeting_schema.py
│   │   └── note_schema.py
│   ├── views/               # Pyramid views
│   │   ├── __init__.py
│   │   └── graphql.py       # GraphQL эндпоинт
│   ├── __init__.py          # Инициализация приложения
│   ├── development.ini      # Конфигурация разработки
│   ├── production.ini       # Конфигурация продакшена
│   └── setup.py             # Установка пакета
├── database/                # База данных
│   ├── migrations/          # Миграции Alembic
│   └── contacts.db          # SQLite база данных
├── docs/                    # Документация
│   ├── api/                 # API документация
│   └── architecture/        # Архитектурные решения
├── tests/                   # Тесты
│   ├── frontend/           # Тесты фронтенда
│   └── backend/            # Тесты бэкенда
├── docker-compose.yml       # Docker Compose конфигурация
├── Dockerfile.frontend      # Docker образ фронтенда
├── Dockerfile.backend       # Docker образ бэкенда
├── .gitignore              # Игнорируемые файлы Git
├── README.md               # Основная документация
├── ARCHITECTURE.md         # Этот файл
├── STRUCTURES.md           # Структуры данных
└── CONTEXT.md              # Глобальный контекст
```

## 🔄 Поток данных

1. **Пользовательский интерфейс** → Vue компоненты отправляют GraphQL запросы
2. **GraphQL клиент** → Передает запросы на бэкенд через HTTP
3. **Pyramid приложение** → Принимает GraphQL запросы через Graphene
4. **GraphQL резолверы** → Выполняют бизнес-логику и обращаются к БД
5. **SQLAlchemy** → Выполняет SQL запросы к SQLite
6. **Обратный путь** → Данные возвращаются через ту же цепочку

## 🛡️ Безопасность

- **CORS** настройки для фронтенд-бэкенд взаимодействия
- **Валидация данных** на всех уровнях
- **SQL инъекции** предотвращаются через SQLAlchemy
- **GraphQL инъекции** предотвращаются через Graphene

## 📊 Масштабируемость

- **Микросервисная готовность** - компоненты разделены
- **Кэширование** - возможность добавления Redis
- **Асинхронность** - поддержка async/await в SQLAlchemy 2.0
- **Горизонтальное масштабирование** - Stateless бэкенд

## 🔧 Технологический стек

### **Frontend**
- Vue.js 3.0 + Composition API + TypeScript
- GraphQL Client (Urql/Apollo)
- Pinia для state management
- Vite для сборки
- Tailwind CSS для стилей

### **Backend**
- Pyramid веб-фреймворк
- SQLAlchemy 2.0+ ORM
- Graphene-Python для GraphQL
- SQLite база данных
- Alembic для миграций

### **Инфраструктура**
- Docker + Docker Compose
- Git для контроля версий
- GitHub Actions для CI/CD

## 🎯 Ключевые принципы

1. **Декларативность** - максимальное использование декларативного подхода Vue 3
2. **Типизация** - строгая типизация через TypeScript и Python type hints
3. **Компонентность** - переиспользуемые компоненты и модули
4. **Тестируемость** - изолированные, тестируемые компоненты
5. **Документированность** - полная документация всех компонентов