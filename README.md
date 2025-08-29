# Coaching Sessions Backend

A Django-based backend system for managing 1:1 coaching sessions between Experts and Students.

## 🏗️ Architecture

This project follows SOLID principles and implements several design patterns:

- **Strategy Pattern**: Different validation strategies for sessions
- **Factory Pattern**: Service creation with dependency injection
- **Repository Pattern**: Clean separation of data access
- **Observer Pattern**: Celery tasks for async operations

## 🚀 Features

- **Session Booking**: Book coaching sessions with overlap prevention
- **Idempotent Operations**: Safe double-click handling
- **Session Management**: Join, progress, and end sessions
- **Automated Summaries**: Celery tasks generate session summaries
- **Comprehensive Testing**: Full test coverage for all scenarios

## ��️ Tech Stack

- **Django 5.2+**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database
- **Celery + Redis**: Task queue and caching
- **Docker Compose**: Development environment

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.9+
- PostgreSQL (if running locally)

## 🚀 Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd coaching_sessions_backend
```

2. Start the services:
```bash
docker-compose up -d
```

3. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

4. Create superuser (optional):
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Create test data:
```bash
docker-compose exec web python scripts/create_test_data.py
```

6. Access the application:
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DB_NAME=coaching_sessions
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_PORT=5432
export CELERY_BROKER_URL=redis://localhost:6379/0
export CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start Celery worker:
```bash
celery -A coaching_sessions worker --loglevel=info
```

5. Run the development server:
```bash
python manage.py runserver
```

## �� API Endpoints

### Book Session
```http
POST /api/sessions/book/
Content-Type: application/json

{
    "expert_id": "uuid",
    "student_id": "uuid",
    "start_at": "2024-01-15T10:00:00Z",
    "end_at": "2024-01-15T11:00:00Z"
}
```

### Join Session
```http
POST /api/sessions/join/
Content-Type: application/json

{
    "session_id": "uuid"
}
```

### End Session
```http
POST /api/sessions/end/
Content-Type: application/json

{
    "session_id": "uuid"
}
```

## �� Testing

Run tests with:
```bash
# Using Docker
docker-compose exec web python manage.py test

# Local development
python manage.py test
```

### Test Coverage

The test suite covers:
- ✅ Happy path booking
- ✅ Overlap rejection
- ✅ Idempotent double-click handling
- ✅ Session flow (join → end)
- ✅ Error handling
- ✅ Edge cases

## �� Overlap Strategy

**Database-level constraints** ensure no overlapping sessions for the same expert:

1. **Unique constraint** on (expert, start_at, end_at) with status filtering
2. **Application-level validation** using the `SessionOverlapValidator` service
3. **Atomic transactions** prevent race conditions

## 🔄 Idempotency Strategy

**Student-based idempotency** ensures safe double-click handling:

1. **Same student + same slot** → Return existing session (200)
2. **Different student + overlapping slot** → Reject (409)
3. **Database indexes** optimize overlap queries

## 🎯 Design Patterns

### Service Layer
- `SessionValidationService`: Abstract validation interface
- `SessionOverlapValidator`: Concrete overlap validation
- `SessionIdempotencyService`: Idempotent session creation
- `SessionStateService`: State transition management

### Dependency Injection
Services accept validators as constructor parameters, enabling:
- Easy testing with mock validators
- Different validation strategies
- Loose coupling between components

### Repository Pattern
Clean separation between business logic and data access:
- Models handle data structure
- Services handle business rules
- Views handle HTTP concerns

## 🚧 Future Improvements

With more time, I would implement:

1. **Authentication & Authorization**: JWT tokens, role-based access
2. **Rate Limiting**: Prevent abuse of booking endpoints
3. **WebSocket Support**: Real-time session updates
4. **Payment Integration**: Stripe/PayPal for paid sessions
5. **Notification System**: Email/SMS reminders
6. **Analytics Dashboard**: Session metrics and insights
7. **API Documentation**: OpenAPI/Swagger specs
8. **Monitoring**: Logging, metrics, health checks

## 📝 License

This project is for demonstration purposes.