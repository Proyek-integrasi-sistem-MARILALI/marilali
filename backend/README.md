# Bali Travel Planner API

AI-powered travel recommendation system for Bali, Indonesia. Provides personalized destination recommendations based on budget, preferences, and real-time weather conditions.

## Features

- **AI-Powered Recommendations**: Intelligent destination suggestions using Langbase RAG
- **Real-Time Weather Integration**: Live weather forecasts from Visual Crossing API
- **Budget Optimization**: Smart filtering based on user budget constraints
- **Confidence Scoring**: 0.85-0.90 accuracy on recommendations
- **User Authentication**: Complete auth flow with JWT tokens
- **Password Reset**: Secure token-based password recovery
- **Email Verification**: MVP email verification system
- **Comprehensive API**: RESTful endpoints with FastAPI

## Prerequisites

- Python 3.12+
- PostgreSQL 12+
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements/dev.txt
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your actual values
# REQUIRED: DATABASE_URL, LANGBASE_API_KEY, VISUAL_CROSSING_API_KEY, JWT_SECRET_KEY
```

### 5. Set Up Database

```bash
# Create PostgreSQL database
createdb travel_planner

# Or using psql
psql -U postgres
CREATE DATABASE travel_planner;
\q

# Run migrations
alembic upgrade head
```

### 6. Start the Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

### Required Variables

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/travel_planner
LANGBASE_API_KEY=your_langbase_api_key
VISUAL_CROSSING_API_KEY=your_visualcrossing_api_key
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

### Optional Variables

```env
COHERE_API_KEY=your_cohere_key (for AI features)
REDIS_URL=redis://localhost:6379/0 (for caching)
DEBUG=True (development only)
```

See `.env.example` for complete list.


### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Register a new user: `POST /api/v1/auth/register`
4. Login: `POST /api/v1/auth/login`
5. Copy the `access_token` from response
6. Click "Authorize" and paste: `Bearer <access_token>`
7. Test endpoints

### Quick Test Scenarios

**1. Get AI Recommendations (Low Budget)**
```bash
POST http://localhost:8000/api/v1/ai/destinations
{
  "budget_max": 50000,
  "start_date": "2025-12-25",
  "end_date": "2025-12-31",
  "preferences": ["temple"],
  "limit": 5
}
```

**2. Get AI Recommendations (No Budget Limit)**
```bash
POST http://localhost:8000/api/v1/ai/destinations
{
  "start_date": "2025-12-25",
  "end_date": "2025-12-31",
  "preferences": ["beach", "cultural sites"],
  "limit": 10
}
```

**3. Password Reset Flow**
```bash
# Step 1: Request reset
POST http://localhost:8000/api/v1/auth/forgot-password
{"email": "user@example.com"}

# Step 2: Reset with token
POST http://localhost:8000/api/v1/auth/reset-password
{"token": "token_from_step1", "new_password": "newPassword123"}
```


## Key API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user profile
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password with token
- `POST /api/v1/auth/verify-email` - Verify user email

### AI Recommendations
- `POST /api/v1/ai/destinations` - Get personalized recommendations
- `GET /api/v1/ai/history` - Get recommendation history
- `POST /api/v1/ai/feedback` - Rate recommendation

### Destinations
- `GET /api/v1/destinations` - List all destinations
- `GET /api/v1/destinations/{id}` - Get destination details
- `GET /api/v1/destinations/search` - Search destinations

### Weather
- `GET /api/v1/weather/forecast` - Get weather forecast
- `GET /api/v1/weather/destinations/{id}` - Get destination weather

### Favorites
- `POST /api/v1/favorites` - Add to favorites
- `GET /api/v1/favorites` - Get user favorites
- `DELETE /api/v1/favorites/{id}` - Remove from favorites
