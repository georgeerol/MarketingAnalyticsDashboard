# MMM Dashboard - Protocol-Based Architecture

A production-ready **Media Mix Modeling (MMM) Dashboard** built with **SOLID principles** and **protocol-based architecture** for maximum testability, maintainability, and scalability.

## Architecture Highlights

- **Complete SOLID Implementation** - All 5 principles fully implemented
- **Protocol-Based Design** - Full dependency inversion with Python protocols
- **Real Google Meridian Integration** - Actual MMM model data processing
- **Maximum Testability** - Comprehensive mock implementations for all services
- **Type-Safe** - Full IDE support and compile-time checking
- **Production-Ready** - Professional, scalable architecture

## Tech Stack

### Backend (FastAPI)
- **FastAPI** - Modern, fast web framework
- **Python Protocols** - Interface-based dependency inversion
- **SQLAlchemy** - ORM with PostgreSQL
- **JWT Authentication** - Secure token-based auth
- **Google Meridian** - Real MMM model integration
- **Pydantic** - Data validation and serialization

### Frontend (Next.js)
- **Next.js 15** - React framework with Turbopack
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Modern component library
- **Zustand** - State management

### Infrastructure
- **Docker** - Containerized PostgreSQL + Adminer
- **Turbo** - Monorepo build system
- **pnpm** - Fast, efficient package manager

## Project Structure

```
├── apps/
│   ├── api/                          # FastAPI Backend
│   │   ├── app/
│   │   │   ├── core/                 # Core utilities
│   │   │   │   ├── config.py         # Application settings
│   │   │   │   ├── database.py       # Database connection
│   │   │   │   ├── security.py       # JWT & password handling
│   │   │   │   └── logging.py        # Logging configuration
│   │   │   ├── models/               # SQLAlchemy models
│   │   │   │   ├── user.py           # User model
│   │   │   │   ├── campaign.py       # Campaign models
│   │   │   │   └── mmm.py            # MMM models
│   │   │   ├── schemas/              # Pydantic schemas
│   │   │   │   ├── user.py           # User schemas
│   │   │   │   ├── auth.py           # Auth schemas
│   │   │   │   ├── campaign.py       # Campaign schemas
│   │   │   │   └── mmm.py            # MMM schemas
│   │   │   ├── services/             # Business logic layer
│   │   │   │   ├── interfaces.py     # 🆕 Protocol definitions
│   │   │   │   ├── user_service.py   # User business logic
│   │   │   │   ├── auth_service.py   # Auth business logic
│   │   │   │   └── mmm_service.py    # MMM business logic
│   │   │   ├── api/
│   │   │   │   ├── deps.py           # 🆕 Protocol-based DI
│   │   │   │   └── v1/               # API v1 routes
│   │   │   │       ├── auth.py       # 🆕 Protocol-based auth routes
│   │   │   │       ├── users.py      # 🆕 Protocol-based user routes
│   │   │   │       └── mmm.py        # 🆕 Protocol-based MMM routes
│   │   │   └── main.py               # FastAPI application
│   │   ├── tests/
│   │   │   ├── mocks/                # 🆕 Protocol-based mocks
│   │   │   │   ├── mock_user_service.py
│   │   │   │   ├── mock_auth_service.py
│   │   │   │   └── mock_mmm_service.py
│   │   │   ├── fixtures/             # 🆕 Test fixtures
│   │   │   └── protocol_tests/       # 🆕 Protocol tests
│   │   └── data/models/
│   │       └── saved_mmm.pkl         # Real Google Meridian model
│   └── web/                          # Next.js Frontend
│       ├── app/                      # App router
│       ├── components/               # React components
│       └── lib/                      # Utilities
├── packages/
│   ├── ui/                           # Shared component library
│   ├── docker/                       # Docker services
│   └── typescript-config/            # Shared TS config
└── README.md
```

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)
- Each service has **one clear purpose**
- `UserService` → User management only
- `AuthService` → Authentication only  
- `MMMService` → MMM model operations only

### Open/Closed Principle (OCP)
- Services are **open for extension, closed for modification**
- New implementations can be added without changing existing code
- Protocol-based design enables easy feature additions

### Liskov Substitution Principle (LSP)
- **Any protocol implementation is substitutable**
- `MockUserService` can replace `UserService` seamlessly
- Tests and production use the same interfaces

### Interface Segregation Principle (ISP)
- **Focused, specific protocol interfaces**
- `UserServiceProtocol` only contains user operations
- `AuthServiceProtocol` only contains auth operations
- No forced dependencies on unused methods

### Dependency Inversion Principle (DIP)
- **ALL layers depend on abstractions, not concretions**
- Routes depend on `AuthServiceProtocol`, not `AuthService`
- `AuthService` depends on `UserServiceProtocol`, not `UserService`
- Complete dependency inversion achieved

## Protocol-Based Testing

### Mock Implementations
```python
# Easy to create and use
user_service: UserServiceProtocol = MockUserService()
auth_service: AuthServiceProtocol = MockAuthService(user_service)
mmm_service: MMMServiceProtocol = MockMMMService()

# All implement their protocols
assert isinstance(user_service, UserServiceProtocol)  # True
assert isinstance(auth_service, AuthServiceProtocol)  # True
assert isinstance(mmm_service, MMMServiceProtocol)    # True
```

### Testing Benefits
- **No External Dependencies** - Tests run without database/network/files
- **Fast Execution** - Microsecond-level mock operations
- **Predictable Results** - Deterministic behavior for reliable tests
- **Easy Setup** - Simple mock creation with sensible defaults
- **Complete Isolation** - Tests don't interfere with each other
- **Error Simulation** - Easy to test error conditions and edge cases

## Getting Started

### Prerequisites
- **Node.js 20+**
- **Python 3.12+**
- **Docker** (for PostgreSQL)
- **pnpm** (recommended package manager)

### Installation

1. **Clone and install dependencies:**
```bash
git clone <repository-url>
cd software-coding-task
pnpm install
```

2. **Start all services:**
```bash
pnpm dev
```

This starts:
- **PostgreSQL** (port 5432)
- **Adminer** (port 8080) - Database UI
- **FastAPI** (port 8000) - Backend API
- **Next.js** (port 3000) - Frontend

### First Time Setup

1. **Seed the database:**
```bash
pnpm seed
```

2. **Access the application:**
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Database UI:** http://localhost:8080

3. **Login with seeded user:**
- **Email:** `test@example.com`
- **Password:** `test12345`

## MMM Dashboard Features

### Real Google Meridian Integration
- **Actual MMM Model** - Uses real `saved_mmm.pkl` file
- **5 Media Channels** - Google Search, Display, Facebook, Instagram, YouTube
- **156 Time Periods** - Weekly contribution data
- **Real Calculations** - ROI × Media Spend for contributions
- **Response Curves** - Saturation analysis with real model parameters

### Dashboard Capabilities
- **Contribution Analysis** - Channel contribution over time
- **Response Curves** - Spend vs. conversion relationships
- **Channel Summary** - Performance metrics and efficiency scores
- **Model Status** - Real-time model health and information
- **Channel Explorer** - Detailed channel-specific analysis

## Development

### API Development
```bash
cd apps/api

# Run backend only
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Run specific test types
uv run pytest tests/unit/          # Unit tests
uv run pytest tests/integration/   # Integration tests
uv run pytest tests/protocol_tests/ # Protocol tests
```

### Frontend Development
```bash
cd apps/web

# Run frontend only
pnpm dev

# Build for production
pnpm build

# Run linting
pnpm lint
```

### Testing the Protocol Architecture
```python
# Test protocol compliance
from app.services.interfaces import UserServiceProtocol
from tests.mocks import MockUserService

user_service = MockUserService()
assert isinstance(user_service, UserServiceProtocol)  # True

# Test service composition
from tests.mocks import MockAuthService
auth_service = MockAuthService(user_service)

# Test authentication
user = auth_service.authenticate_user("admin@test.com", "admin_password")
assert user.is_admin  # True
```

## Architecture Patterns

### Dependency Injection Flow
```
HTTP Request
      ↓
FastAPI Route Handler (accepts protocols)
      ↓
Dependency Injection (api/deps.py returns protocols)
      ↓
Service Layer (implements protocols)
      ↓
Real/Mock Implementations (swappable via protocols)
      ↓
Database/External Systems
```

### Protocol Definition Example
```python
@runtime_checkable
class UserServiceProtocol(Protocol):
    """Protocol for user management operations."""
    
    def get_user_by_email(self, email: str) -> Optional[User]: ...
    def create_user(self, user_data: UserCreate) -> User: ...
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]: ...
```

### Service Implementation
```python
class UserService(UserServiceProtocol):
    """Real implementation using database."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

class MockUserService(UserServiceProtocol):
    """Mock implementation for testing."""
    
    def __init__(self):
        self.users = {}
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.users.get(email)
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (OAuth2 compatible)
- `POST /api/v1/auth/login-json` - JSON login with user data
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh access token

### User Management Endpoints
- `GET /api/v1/users/` - List users (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID (admin only)
- `PUT /api/v1/users/{user_id}` - Update user (admin only)
- `PUT /api/v1/users/me` - Update current user

### MMM Endpoints
- `GET /api/v1/mmm/status` - Model status and health
- `GET /api/v1/mmm/info` - Detailed model information
- `GET /api/v1/mmm/channels` - Available media channels
- `GET /api/v1/mmm/contribution` - Channel contribution data
- `GET /api/v1/mmm/response-curves` - Response curve analysis
- `GET /api/v1/mmm/channels/summary` - Channel performance summary

## 🧪 Testing

### Running Tests
```bash
# All tests
pnpm test

# Backend tests only
cd apps/api && uv run pytest

# Frontend tests only  
cd apps/web && pnpm test

# Protocol-specific tests
cd apps/api && uv run pytest tests/protocol_tests/
```

### Test Categories
- **Unit Tests** - Individual service testing with mocks
- **Integration Tests** - API endpoint testing
- **Protocol Tests** - Interface compliance and flexibility
- **E2E Tests** - Full application workflow testing

## Production Deployment

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME="MMM Dashboard API"
APP_VERSION="1.0.0"
```

### Docker Deployment
```bash
# Build images
docker build -t mmm-api apps/api/
docker build -t mmm-web apps/web/

# Run with docker-compose
docker-compose up -d
```

## Contributing

### Code Standards
- **SOLID Principles** - All new code must follow SOLID principles
- **Protocol-Based** - Use protocols for all service interfaces
- **Type Safety** - Full type annotations required
- **Testing** - Comprehensive test coverage with mocks
- **Documentation** - Clear docstrings and comments

### Adding New Features
1. **Define Protocol** - Create interface in `services/interfaces.py`
2. **Implement Service** - Create real implementation
3. **Create Mock** - Add mock implementation for testing
4. **Update Dependencies** - Add to `api/deps.py`
5. **Create Routes** - Add API endpoints using protocols
6. **Write Tests** - Unit, integration, and protocol tests

## License

This project is licensed under the MIT License.

## Acknowledgments

- **SOLID Principles** - Robert C. Martin
- **Clean Architecture** - Robert C. Martin  
- **Protocol-Based Design** - Python typing system
- **Google Meridian** - MMM modeling framework
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework
- **shadcn/ui** - Component library

---

**Built using SOLID principles and protocol-based architecture for maximum maintainability and testability.**
