# Todo API - Phase 1 (CRUD Operations)

A scalable Todo application built with FastAPI and PostgreSQL, designed with clean architecture principles and support for future enhancements like database migrations and authorization.

## 🏗️ Project Structure

```
todoapp1/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment settings
│   ├── database.py          # Database connection and session management
│   ├── models/              # SQLAlchemy database models
│   │   ├── __init__.py
│   │   └── todo.py          # Todo model definition
│   ├── schemas/             # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   └── todo.py          # Request/response schemas
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   └── todo_service.py  # Todo CRUD operations
│   └── routes/              # API endpoints
│       ├── __init__.py
│       └── todo_routes.py   # Todo REST API routes
├── alembic/                 # Database migration files
├── alembic.ini              # Alembic configuration
├── .env                     # Environment variables (not in git)
├── .gitignore              # Git ignore rules
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## ✨ Features

### Todo Model Fields:
- **id**: Auto-generated primary key
- **title**: Todo title (required, max 60 characters)
- **description**: Detailed description (required)
- **status**: Enum (Pending, Done, Cancelled) - always starts with Pending
- **due_date**: Optional due date (must be in future)
- **created_at**: Auto-generated timestamp
- **updated_at**: Auto-updated timestamp

### API Endpoints:
- `POST /todos/` - Create a new todo
- `GET /todos/` - Get all todos (with filtering by status and pagination)
- `GET /todos/{id}` - Get a specific todo by ID
- `PUT /todos/{id}` - Update a todo (partial update supported)
- `DELETE /todos/{id}` - Delete a todo

### Validations:
- Title: Max 60 characters, required
- Description: Required
- Due date: Must be in the future
- Status: Always starts with Pending

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL 15+

### Step 1: Database Setup

**Option A: Using PostgreSQL Command Line**
```bash
# Create database
psql -U postgres
CREATE DATABASE todoapp;
\q
```

**Option B: Using pgAdmin**
- Open pgAdmin
- Create new database named "todoapp"

### Step 2: Configure Environment Variables

Edit the `.env` file with your database credentials:

```env
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@localhost:5432/todoapp
APP_NAME=Todo API
DEBUG=True
```

**Example:**
```env
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/todoapp
APP_NAME=Todo API
DEBUG=True
```

### Step 3: Activate Virtual Environment

```bash
# Activate virtual environment
source venv/bin/activate
```

### Step 4: Run Database Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration with todos table"

# Apply migration to database
alembic upgrade head
```

**What does this do?**
- Creates migration files in `alembic/versions/`
- Creates the `todos` table in your database with all fields
- Sets up indexes and constraints

### Step 5: Run the Application

```bash
# Start the server
uvicorn app.main:app --reload

# Server will start at: http://localhost:8000
```

## 📖 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs (Interactive API documentation)
- **ReDoc**: http://localhost:8000/redoc (Alternative documentation)
- **Root endpoint**: http://localhost:8000/ (Health check)

## 🧪 Testing the API

### Using Swagger UI (Recommended for Beginners)

1. Go to http://localhost:8000/docs
2. Try creating a todo:
   - Click on `POST /todos/`
   - Click "Try it out"
   - Enter JSON:
     ```json
     {
       "title": "Buy groceries",
       "description": "Milk, eggs, bread",
       "due_date": "2026-02-10T10:00:00Z"
     }
     ```
   - Click "Execute"

### Using cURL

```bash
# Create a todo
curl -X POST "http://localhost:8000/todos/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "due_date": "2026-02-10T10:00:00Z"
  }'

# Get all todos
curl http://localhost:8000/todos/

# Get todos filtered by status
curl "http://localhost:8000/todos/?status_filter=Pending"

# Get a specific todo
curl http://localhost:8000/todos/1

# Update a todo
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Done"
  }'

# Delete a todo
curl -X DELETE http://localhost:8000/todos/1
```

## 🏛️ Architecture Explanation

### Layered Architecture

This project follows a **3-tier architecture**:

1. **Routes Layer** (`app/routes/`):
   - Handles HTTP requests/responses
   - Validates input data using Pydantic schemas
   - Calls service layer for business logic

2. **Service Layer** (`app/services/`):
   - Contains business logic
   - Orchestrates database operations
   - Enforces business rules (e.g., status always starts with Pending)

3. **Data Layer** (`app/models/`):
   - SQLAlchemy models representing database tables
   - Database schema definitions

### Why This Structure?

- **Separation of Concerns**: Each layer has a specific responsibility
- **Testability**: Easy to unit test each layer independently
- **Scalability**: Can easily add authentication, caching, etc.
- **Maintainability**: Changes in one layer don't affect others

### Key Components Explained

#### 1. **config.py** - Configuration Management
- Loads settings from `.env` file
- Provides type-safe configuration using Pydantic
- Single source of truth for settings

#### 2. **database.py** - Database Connection
- Creates SQLAlchemy engine and session factory
- Provides `get_db()` dependency for FastAPI routes
- Manages database connection lifecycle

#### 3. **models/todo.py** - Database Model
- Defines the `todos` table structure
- Uses SQLAlchemy ORM
- Includes TodoStatus enum

#### 4. **schemas/todo.py** - Data Validation
- Pydantic models for request/response validation
- Enforces data types and constraints
- Provides automatic API documentation

#### 5. **services/todo_service.py** - Business Logic
- CRUD operations (Create, Read, Update, Delete)
- Business rules enforcement
- Database query logic

#### 6. **routes/todo_routes.py** - API Endpoints
- REST API endpoints definition
- HTTP method handlers
- Route parameters and query strings

## 🔧 Alembic Migrations

### What is Alembic?
Alembic is a database migration tool that:
- Tracks database schema changes over time
- Allows version control for database structure
- Enables easy rollback of changes

### Common Alembic Commands

```bash
# Create a new migration (auto-detect changes)
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### When to Create Migrations?

- After modifying models (adding/removing fields)
- Before deploying to production
- When collaborating with team members

## 📦 Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool
- **Psycopg2-binary**: PostgreSQL adapter for Python
- **Pydantic**: Data validation and settings management
- **Python-dotenv**: Environment variable management

## 🔮 Future Enhancements (Phase 2+)

- [ ] User authentication and authorization (JWT)
- [ ] Multi-user support with user-specific todos
- [ ] Pagination improvements
- [ ] Todo categories/tags
- [ ] Search functionality
- [ ] Sorting options
- [ ] API rate limiting
- [ ] Caching layer (Redis)
- [ ] Background tasks (Celery)
- [ ] File attachments
- [ ] Email notifications

## 🐛 Troubleshooting

### Issue: "psql command not found"
**Solution**: Add PostgreSQL to PATH or use full path:
```bash
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

### Issue: "could not connect to server"
**Solution**: Start PostgreSQL service:
```bash
brew services start postgresql@15
```

### Issue: "database does not exist"
**Solution**: Create the database first using psql or pgAdmin

### Issue: "ImportError" or "ModuleNotFoundError"
**Solution**: Ensure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 Notes

- The `.env` file contains sensitive data and is not tracked in git
- Always run `alembic upgrade head` after pulling new migrations
- Use `--reload` flag in development for auto-restart on code changes
- Remove `DEBUG=True` in production environments

## 🤝 Contributing

This is a learning project. Feel free to experiment and modify!

## 📄 License

This project is for educational purposes.
