# KnowledgeHub API

KnowledgeHub API is a backend service built with **FastAPI** that provides user authentication, post management, and permission control.  
This project is designed as an **engineering-oriented backend project** for backend internship / new-grad job applications.

---

## Features

- User registration and login with JWT authentication  
- OAuth2 Password Flow  
- Password hashing with bcrypt  
- Create / Read / Update / Delete posts  
- Public / Private post visibility  
- Pagination support  
- Database migrations with Alembic  
- Automated testing with pytest  
- Code quality tools: ruff, pre-commit  

---

## Tech Stack

- Python 3.11+  
- FastAPI  
- SQLAlchemy  
- Alembic  
- PostgreSQL / SQLite  
- JWT (python-jose)  
- pytest  

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/runyiy/knowledgehub-api.git
cd knowledgehub-api
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### Environment Variables
- Create a .env file in the project root:
```env
DATABASE_URL=sqlite:///./dev.db
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

- If using PostgreSQL:
```bash
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/knowledgehub
```

## Database Migration
### 1. Apply migrations:
```bash
alembic upgrade head
```
### 2. Create a new migration:
```bash
alembic revision --autogenerate -m "your message"
```
### 3. Rollback last migration:
```bash
alembic downgrade -1
```
## Run the Application
```bash
uvicorn app.main:app --reload
```
### Open in browser:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Example Requests
### 1. Register
```bash
curl -X POST "http://127.0.0.1:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'
```
### 2. Login
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=123456"
```
#### Response:
```JSON
{
  "access_token": "YOUR_TOKEN",
  "token_type": "bearer"
}
```
### 3. Create Post
```bash
TOKEN=YOUR_TOKEN

curl -X POST "http://127.0.0.1:8000/api/posts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","content":"World","visibility":"public"}'
```
### 4. List Posts
```bash
curl "http://127.0.0.1:8000/api/posts?limit=10&offset=0"
```

## Running Tests
```bash
pytest
```
## Code Quality
```bash
ruff check .
ruff format .
```
### If using pre-commit:
```bash
pre-commit install
pre-commit run --all-files
```
### Project Structure
```Plain text
app/        # application source code 
alembic/    # database migrations
tests/      # test cases
```





