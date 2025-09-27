# MMM Dashboard

A professional Media Mix Modeling analytics platform built with FastAPI and Next.js.

## What This Is

This project implements a complete MMM (Media Mix Modeling) dashboard that loads real Google Meridian model data and provides actionable marketing insights. Users can register, log in, and analyze channel performance through interactive charts and AI-generated recommendations.

## Quick Start

```bash
# 1. Install dependencies
pnpm install

# 2. Set up required files (see Required Setup Files section below)
#    - Place saved_mmm.pkl in apps/api/data/models/
#    - Create .env.local files

# 3. Start all services (database, API, frontend)
pnpm dev

# 4. Seed the database with test users
pnpm seed
```

Visit `http://localhost:3000` and log in with:
- **Email**: `test@example.com`
- **Password**: `test123`

## Features

### Authentication & User Management
- Secure JWT-based authentication with bcrypt password hashing
- User registration with automatic login
- Session persistence across page refreshes
- Professional login/registration UI

### MMM Analytics Dashboard
- **Real Model Data**: Loads actual Google Meridian model (32.3MB `saved_mmm.pkl`)
- **Contribution Charts**: Visual breakdown of channel performance with bar/pie charts
- **Response Curves**: Hill saturation curves showing diminishing returns for each channel
- **Smart Insights**: AI-generated recommendations for budget optimization
- **Export Functionality**: Download insights in JSON, CSV, or TXT formats

### Performance & Quality
- **95% Performance Improvement**: Intelligent model caching (3+ seconds → 40-50ms)
- **Comprehensive Testing**: 38+ unit and integration tests
- **Clean Architecture**: Service interfaces, centralized constants, structured logging
- **Production Ready**: Docker setup, proper error handling, security best practices

## Project Structure

```
├── apps/
│   ├── api/          # FastAPI backend
│   │   ├── app/      # Application code
│   │   ├── data/     # MMM model files
│   │   └── tests/    # Test suite
│   └── web/          # Next.js frontend
│       ├── app/      # App router pages
│       ├── components/ # React components
│       └── hooks/    # Custom hooks
├── packages/
│   ├── ui/           # Shared component library
│   └── docker/       # Database setup
```

## System Architecture

### Data Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │───▶│  Next.js    │───▶│   FastAPI   │
│             │    │  Frontend   │    │   Backend   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           │                   ▼
                           │            ┌─────────────┐
                           │            │ PostgreSQL  │
                           │            │  Database   │
                           │            └─────────────┘
                           │                   │
                           ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐
                   │   Zustand   │    │ Google MMM  │
                   │    Store    │    │ Model (32MB)│
                   └─────────────┘    └─────────────┘
```

### MMM Processing Pipeline
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ saved_mmm   │───▶│ Model Cache │───▶│ Response    │
│ .pkl (32MB) │    │ (LRU)       │    │ Curves      │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   ▼                   ▼
       │            ┌─────────────┐    ┌─────────────┐
       │            │ Channel     │    │ Hill        │
       │            │ Analysis    │    │ Saturation  │
       │            └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Contribution│    │ Smart       │    │ Export      │
│ Charts      │    │ Insights    │    │ Reports     │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Authentication Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Registration│───▶│ Auto-Login  │───▶│  Dashboard  │
│    Form     │    │  (JWT)      │    │   Access    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Validation  │    │ Token       │    │ Session     │
│ & Hashing   │    │ Storage     │    │ Persistence │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Protocol-Based Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                    Service Protocol Layer                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐  │
│ │ UserService     │    │ AuthService     │    │ MMMService   │  │
│ │ Protocol        │    │ Protocol        │    │ Protocol     │  │
│ └─────────────────┘    └─────────────────┘    └──────────────┘  │
│          │                       │                      │       │
│          ▼                       ▼                      ▼       │
│ ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐  │
│ │ UserService     │    │ AuthService     │    │ MMMService   │  │
│ │ Implementation  │    │ Implementation  │    │ Implementation│  │
│ └─────────────────┘    └─────────────────┘    └──────────────┘  │
│          │                       │                      │       │
│          ▼                       ▼                      ▼       │
│ ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐  │
│ │ Mock Service    │    │ Mock Service    │    │ Mock Service │  │
│ │ (Testing)       │    │ (Testing)       │    │ (Testing)    │  │
│ └─────────────────┘    └─────────────────┘    └──────────────┘  │
│                                                                 │
│ Benefits:                                                       │
│ • Dependency Inversion Principle (SOLID)                       │
│ • Easy testing with mock implementations                       │
│ • Clean separation of concerns                                 │
│ • Protocol-based dependency injection                          │
└─────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Protocol-Based Architecture
- **Service Interfaces**: `UserServiceProtocol`, `AuthServiceProtocol`, `MMMServiceProtocol`
- **Dependency Injection**: Protocol-based DI in `api/deps.py`
- **Mock Implementations**: Complete mock services for testing
- **SOLID Compliance**: All 5 principles fully implemented

### 2. MMM Model Integration
- **Real Model**: 32.3MB Google Meridian model (`saved_mmm.pkl`)
- **Data Processing**: Contribution data, response curves, channel analysis
- **Channel Support**: 5-channel analysis from real model data
- **Smart Fallback**: Automatic fallback to mock data when needed

### 3. Authentication System
- **JWT Tokens**: Secure token-based auth with bcrypt hashing
- **Protected Routes**: All MMM endpoints require authentication
- **User Management**: Complete CRUD operations
- **Session Management**: 30-minute token expiration with persistence

### 4. Interactive Dashboard
- **Contribution Charts**: Visual breakdown of channel performance
- **Response Curves**: Diminishing returns analysis with saturation points
- **Smart Insights**: AI-generated recommendations and performance analysis
- **Export Functionality**: Download insights in JSON, CSV, or TXT formats

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration with auto-login
- `POST /api/v1/auth/login` - User login (OAuth2 form)
- `GET /api/v1/auth/me` - Get current user info

### MMM Analytics
- `GET /api/v1/mmm/status` - Model status and info
- `GET /api/v1/mmm/channels` - Channel summary data
- `GET /api/v1/mmm/contribution` - Contribution analysis
- `GET /api/v1/mmm/response-curves` - Response curve data
- `GET /api/v1/export/insights` - Export recommendations

## Development

### Prerequisites
- Node.js 20+
- Python 3.11+
- Docker & Docker Compose
- pnpm

### Required Setup Files

#### 1. MMM Model File
Place your Google Meridian MMM model file at:
```
apps/api/data/models/saved_mmm.pkl
```

**Note**: The model file (`saved_mmm.pkl`) is required for MMM analytics. Without it, the system will use mock data for development.

#### 2. Environment Configuration

**Backend Configuration** - Create `.env.local` in the project root:
```bash
# .env.local

# Database connection string
# Format: postgresql://username:password@host:port/database_name
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mmm_db

# Enable debug mode for development (shows detailed error messages)
DEBUG=true

# Environment identifier (development, staging, production)
ENVIRONMENT=development

# Secret key for JWT token signing (change this to a random string in production)
SECRET_KEY=your-secret-key-here

# CORS allowed origins (comma-separated for multiple origins)
ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend Configuration** - Create `.env.local` in `apps/web/`:
```bash
# apps/web/.env.local

# Backend API URL (where the FastAPI server is running)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Important Notes:**
- **SECRET_KEY**: Generate a secure random string for production (e.g., using `openssl rand -hex 32`)
- **DATABASE_URL**: Matches the PostgreSQL credentials in `docker-compose.yml`
- **NEXT_PUBLIC_API_URL**: Must match the FastAPI server address and port

### Commands

#### Essential Commands
```bash
# Install dependencies
pnpm install

# Start development servers (API + Web + Database)
pnpm dev

# Stop all services
pnpm stop

# Build for production
pnpm build
```

#### Database Commands
```bash
# Seed database with test users
pnpm seed

# Reset database (drop all tables and recreate)
cd apps/api && uv run python reset_db.py

# Create tables only
cd apps/api && uv run python -c "from app.core.database import init_db; init_db()"

# Check database connection
cd apps/api && uv run python -c "from app.core.database import get_db; print('Database connected!')"
```

#### Test Commands
```bash
# Run all tests
cd apps/api && uv run pytest

# Run tests with coverage
cd apps/api && uv run pytest --cov=app --cov-report=html

# Run specific test file
cd apps/api && uv run pytest tests/unit/test_mmm_service.py

# Run integration tests only
cd apps/api && uv run pytest tests/integration/

# Run unit tests only
cd apps/api && uv run pytest tests/unit/

# Run tests in verbose mode
cd apps/api && uv run pytest -v

# Run tests and stop on first failure
cd apps/api && uv run pytest -x
```

#### Code Quality Commands
```bash
# Format code
pnpm format

# Lint code
pnpm lint

# Type checking (API)
cd apps/api && uv run mypy app/

# Type checking (Web)
cd apps/web && pnpm type-check
```

#### Model Inspection Commands
```bash
# Display model info in terminal
pnpm inspect-model

# Save model analysis as JSON
pnpm inspect-model:json-file

# Save model analysis as text file
pnpm inspect-model:file

# Display JSON format in terminal
pnpm inspect-model:json
```

#### Debug Commands
```bash
# Check system status
curl -s http://localhost:8000/health | jq  # API health with JSON formatting
curl -s http://localhost:3000 | grep -o '<title>.*</title>'  # Web app status

# Database debugging
cd apps/api && uv run python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print('PostgreSQL:', result.fetchone()[0])
"

# Check database tables
cd apps/api && uv run python -c "
from app.core.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables:', tables)
for table in tables:
    print(f'{table}: {len(inspector.get_columns(table))} columns')
"

# MMM model debugging
cd apps/api && uv run python -c "
from app.services.mmm_service import MMMService
service = MMMService()
try:
    model = service._load_model()
    print('Model loaded successfully')
    print('Model type:', type(model))
except Exception as e:
    print('Model loading failed:', e)
"

# Check environment variables
cd apps/api && uv run python -c "
import os
from app.core.config import settings
print('Database URL:', settings.DATABASE_URL[:50] + '...')
print('Debug mode:', settings.DEBUG)
print('Environment:', os.getenv('ENVIRONMENT', 'development'))
"

# View recent logs
cd apps/api && tail -f app.log  # If logging to file
docker logs mmm-postgres-1 --tail 20  # Database logs

# Network debugging
netstat -tulpn | grep :8000  # Check API port
netstat -tulpn | grep :3000  # Check Web port
netstat -tulpn | grep :5432  # Check DB port

# Memory and performance
cd apps/api && uv run python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
print(f'CPU usage: {process.cpu_percent()}%')
"
```

#### Development Utilities
```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Access database UI (Adminer)
open http://localhost:8080

# Check running processes
lsof -i :8000  # API server
lsof -i :3000  # Web server
lsof -i :5432  # PostgreSQL

# Kill stuck processes
lsof -ti:8000 | xargs kill -9  # Kill API
lsof -ti:3000 | xargs kill -9  # Kill Web

# Docker debugging
docker ps  # Show running containers
docker logs mmm-postgres-1  # Database logs
docker exec -it mmm-postgres-1 psql -U postgres -d mmm_db  # Direct DB access
```

### Test Users
| Email | Password | Role |
|-------|----------|------|
| `test@example.com` | `test123` | Standard user |
| `admin@example.com` | `admin123` | Administrator |
| `demo@example.com` | `demo123` | Demo account |

## Technical Stack

**Backend**
- FastAPI with Uvicorn
- PostgreSQL with SQLAlchemy ORM
- JWT authentication with bcrypt
- Google Meridian MMM model integration
- Comprehensive test suite (pytest)

**Frontend**
- Next.js 14 with App Router
- TypeScript and Tailwind CSS
- Zustand for state management
- Recharts for data visualization
- shadcn/ui component library

**Infrastructure**
- Docker Compose for local development
- Turbo monorepo with pnpm workspaces
- Automated testing and linting

## Key Features Explained

### Model Caching
The system implements intelligent LRU caching for the MMM model:
- **Before**: 3+ seconds per request (32MB model loaded from disk)
- **After**: 40-50ms per request (model served from memory)
- **Result**: 95%+ performance improvement

### Response Curves
Each marketing channel has unique Hill saturation curves showing:
- Spend vs. returns relationship
- Saturation points where additional spend becomes inefficient
- Marginal ROI at different spend levels

### Smart Insights
The system analyzes channel performance and generates recommendations:
- Identifies top and underperforming channels
- Suggests budget reallocation opportunities
- Warns about channels approaching saturation
- Provides specific ROI and efficiency metrics

## Technical Decisions & Trade-offs

### Key Architectural Decisions

| Decision | Approach | Pros | Cons | Rationale |
|----------|----------|------|------|-----------|
| **Architecture** | Monorepo with Turbo + pnpm workspaces | Shared code, unified builds, type safety | More complex than separate repos | Better developer experience and code sharing |
| **Authentication** | JWT tokens with bcrypt password hashing | Stateless, secure, scalable | Token management complexity | Industry standard for API authentication |
| **MMM Integration** | Smart fallback system (real model → mock data) | Works without Google Meridian package | May not reflect real model behavior in dev | Ensures development continuity |
| **Database** | PostgreSQL with SQLAlchemy ORM | ACID compliance, complex queries, type safety | More setup than SQLite | Production-ready with proper relationships |
| **Frontend State** | Zustand with persistence | Simple, TypeScript-first, persistent auth | Less ecosystem than Redux | Lightweight and sufficient for project scope |

### Production Scaling Strategy

#### Current State vs Production Target
| Aspect | Current | Production Target |
|--------|---------|-------------------|
| **Authentication** | JWT with 30min expiration | JWT with refresh tokens + rate limiting |
| **Database** | Single PostgreSQL instance | PostgreSQL cluster with read replicas |
| **Caching** | LRU model caching (95%+ performance improvement) | Redis for session and computed data caching |
| **Monitoring** | Basic logging | APM with Grafana/Prometheus |
| **Deployment** | Docker Compose | Kubernetes with auto-scaling |

### MMM Model Integration Strategy

| What We're Optimizing | Current Implementation | Production Enhancement |
|----------------------|------------------------|------------------------|
| **Model Loading** | LRU cached in memory (40-50ms after first load) | Pre-load and cache model data in Redis |
| **Data Processing** | Real-time computation of response curves | Background processing with cached results |
| **Channel Analysis** | Extract 5 channels from real model | Support dynamic channel configuration |
| **Performance** | 40-50ms response times (95%+ improvement) | <30ms with Redis and background processing |

### Alternative Approaches Considered

| Alternative | What We Considered | Pros | Cons | Why We Didn't Choose It |
|-------------|-------------------|------|------|-------------------------|
| **Microservices** | Separate auth and MMM services | Better scalability, service isolation | More complex deployment, network overhead | Monolith is simpler for current scope |
| **GraphQL API** | GraphQL instead of REST | Flexible queries, better for complex data | Learning curve, more complex caching | REST meets current requirements |
| **Real-time Updates** | WebSocket for live MMM updates | Real-time dashboard updates | Added complexity, not required | Polling is sufficient for MMM data |
| **NoSQL Database** | MongoDB for MMM model storage | Better for unstructured model data | Different from relational user data | PostgreSQL JSON support is sufficient |

## Production Considerations

This project is designed for easy production deployment:
- Environment-based configuration
- Docker containerization
- Proper error handling and logging
- Security best practices (CORS, input validation, password hashing)
- Database migrations and seeding
- Comprehensive test coverage

For production scaling, consider:
- Redis for session and computed data caching
- Rate limiting for API endpoints
- Load balancing and auto-scaling
- Monitoring and alerting
- CI/CD pipeline

## License

This project is for demonstration purposes. The Google Meridian model data is used under appropriate licensing terms.
