# shadcn/ui monorepo template

## Task
Implement user authentication.
Implement a user dashboard.

## General structure
- apps
    - api: fastapi
    - web: nextjs frontend
- packages
    - ui: shadcn component library
    - docker: dockerized database setup 

## Getting started
Use the monorepo setup. 
Run: **pnpm turbo run install** 
- installs dependencies for nextjs (/apps/web)
- installs dependencies for fastapi (/apps/api)

Run: **pnpm turbo run dev** 
- spins up docker-compose /packages/docker
    - 5432 for database
    - 8080 for adminer (db ui)
- starts fastapi dev server
- starts next applicaiton in dev
 

## Frontend component library
### Usage

```bash
pnpm dlx shadcn@latest init
```

### Adding components

To add components to your app, run the following command at the root of your `web` app:

```bash
pnpm dlx shadcn@latest add button -c apps/web
```

This will place the ui components in the `packages/ui/src/components` directory.

### Tailwind

Your `tailwind.config.ts` and `globals.css` are already set up to use the components from the `ui` package.

### Using components

To use the components in your app, import them from the `ui` package.

```tsx
import { Button } from "@workspace/ui/components/button"
```


---
# Implementation Response: georgeerol/ui monorepo 


## Quick Overview

| Component | Description | Status |
|-----------|-------------|---------|
| **Authentication System** | JWT-based auth with secure password hashing | Completed |
| **MMM Model Integration** | Real Google Meridian model (32.3MB saved_mmm.pkl) | Completed |
| **Interactive Dashboard** | Contribution charts + Response curves + AI insights | Completed |
| **API Endpoints** | 11 endpoints covering auth and MMM functionality | Completed |
| **Testing Suite** | Comprehensive unit + integration tests | Completed |
| **Production Setup** | Docker + PostgreSQL + Next.js deployment | Completed |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MMM Dashboard Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   Next.js Web   │    │   FastAPI       │    │ PostgreSQL   │ │
│  │   Frontend      │◄──►│   Backend       │◄──►│ Database     │ │
│  │                 │    │                 │    │              │ │
│  │ • Dashboard UI  │    │ • JWT Auth      │    │ • User Data  │ │
│  │ • MMM Charts    │    │ • MMM API       │    │ • MMM Models │ │
│  │ • Auth Forms    │    │ • Data Processing│    │ • Analytics  │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
│           │                       │                      │      │
│           │              ┌─────────────────┐             │      │
│           │              │ Google Meridian │             │      │
│           │              │ MMM Model       │             │      │
│           │              │ (32.3MB pkl)    │             │      │
│           │              └─────────────────┘             │      │
│           │                       │                      │      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Docker Environment                       │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │   Web:3000  │  │  API:8000   │  │  PostgreSQL:5432    │ │ │
│  │  │   Adminer   │  │   Docs      │  │  Adminer:8080       │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

### MMM Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MMM Data Processing Flow                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐  │
│ │ Google Meridian │    │ MMM Model       │    │ Dashboard    │  │
│ │ saved_mmm.pkl   │───►│ Loader          │───►│ Components   │  │
│ │ (32.3MB)        │    │                 │    │              │  │
│ └─────────────────┘    └─────────────────┘    └──────────────┘  │
│          │                       │                      │       │
│          │              ┌─────────────────┐             │       │
│          │              │ Fallback System │             │       │
│          └─────────────►│ Mock Data Gen   │─────────────┘       │
│                         │ (Development)   │                     │
│                         └─────────────────┘                     │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                   Data Extraction Pipeline                  │ │
│ │                                                             │ │
│ │  Real Model ──► Channel Names ──► Contribution Data        │ │
│ │      │              │                    │                 │ │
│ │      │              │                    ▼                 │ │
│ │      │              │            Response Curves           │ │
│ │      │              │                    │                 │ │
│ │      │              │                    ▼                 │ │
│ │      │              └──────────► Saturation Points         │ │
│ │      │                                   │                 │ │
│ │      └─────────────────────────────────► Efficiency Scores │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

### Authentication & Security Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Authentication Security Flow                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐   │
│ │   Login     │───►│ JWT Token   │───►│ Protected Routes    │   │
│ │   Form      │    │ Generation  │    │ (MMM Dashboard)     │   │
│ └─────────────┘    └─────────────┘    └─────────────────────┘   │
│        │                  │                       │             │
│        │                  │              ┌─────────────────┐    │
│        │                  │              │ Token Validation│    │
│        │                  │              │ Middleware      │    │
│        │                  │              └─────────────────┘    │
│        │                  │                       │             │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐   │
│ │ Password    │    │ Bcrypt      │    │ Database            │   │
│ │ Input       │───►│ Hashing     │───►│ Storage             │   │
│ └─────────────┘    └─────────────┘    └─────────────────────┘   │
│                                                                 │
│ Security Features:                                              │
│ • JWT tokens with expiration                                    │
│ • Bcrypt password hashing                                       │
│ • Protected API endpoints                                       │
│ • SQL injection protection                                      │
│ • CORS middleware                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

### Key Components

#### **1. MMM Model Integration (`apps/api/mmm_utils.py`)**
- **MMMModelLoader**: Handles real Google Meridian model loading
- **Smart fallback**: Automatic fallback to mock data when Meridian package unavailable
- **Data extraction**: Contribution data, response curves, channel analysis
- **Real data support**: 32.3MB saved_mmm.pkl with 5-channel analysis

#### **2. Authentication System (`apps/api/auth_utils.py`)**
- **JWT tokens**: Secure token-based authentication with configurable expiration
- **Password security**: Bcrypt hashing with 72-byte limit handling
- **Protected endpoints**: All MMM routes require authentication
- **User management**: Complete CRUD operations for user accounts

#### **3. Interactive Dashboard (`apps/web/components/mmm/`)**
- **Contribution charts**: Top-performing channel visualization
- **Response curves**: Diminishing returns analysis with saturation points
- **AI insights**: Automated recommendations and performance analysis
- **Real-time data**: Live updates from MMM API endpoints

#### **4. API Layer (`apps/api/routes/`)**
- **11 endpoints** covering authentication and MMM functionality
- **RESTful design**: Proper HTTP methods and status codes
- **Error handling**: Comprehensive error responses and logging
- **Documentation**: Auto-generated OpenAPI/Swagger docs

---

## API Documentation

### **Authentication Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | User registration |
| `/auth/login` | POST | User login (OAuth2 form) |
| `/auth/login-json` | POST | User login (JSON payload) |
| `/auth/me` | GET | Get current user info |
| `/auth/users` | GET | Get all users (admin only) |

### **MMM (Media Mix Modeling) Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mmm/status` | GET | Check MMM model status and basic info |
| `/mmm/info` | GET | Get detailed MMM model information |
| `/mmm/channels` | GET | Get list of media channels |
| `/mmm/contribution` | GET | Get contribution data (optional `?channel=name` filter) |
| `/mmm/response-curves` | GET | Get response curve data (optional `?channel=name` filter) |
| `/mmm/explore` | GET | Explore MMM model structure |
| `/mmm/test` | GET | Test MMM model loading and functionality |

### **System Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/` | GET | API info |
| `/docs` | GET | Interactive API documentation |

#### **Authentication Request Format**

```json
{
  "email": "test@example.com",
  "password": "test123"
}
```

#### **Authentication Response Format**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "full_name": "Test User",
    "company": "Test Company",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### **MMM Contribution Response Format**

```json
{
  "channels": ["Google_Search", "Google_Display", "Facebook", "Instagram", "YouTube"],
  "data": [
    {
      "Google_Search": 15420.5,
      "Google_Display": 12340.2,
      "Facebook": 9876.1,
      "Instagram": 7654.3,
      "YouTube": 5432.8
    }
  ],
  "summary": {
    "Google_Search": {
      "mean": 15420.5,
      "total": 802665.0,
      "max": 18500.2,
      "min": 12340.1
    }
  },
  "shape": [52, 5]
}
```

#### **MMM Response Curves Format**

```json
{
  "curves": {
    "Google_Search": {
      "spend": [0, 5000, 10000, 15000, 20000],
      "response": [0, 3200, 5800, 7600, 8900],
      "saturation_point": 45000.0,
      "efficiency": 0.75
    }
  }
}
```

---

## Getting Started

### Prerequisites
- **Node.js 20+** and **pnpm** for frontend development
- **Python 3.12+** for backend development
- **Docker Desktop** for database and services

### Quick Start
```bash
# 1. Install dependencies
pnpm install

# 2. Start development environment
pnpm dev

# 3. Verify it's working
curl http://localhost:8000/health

# 4. Test the authentication
curl -X POST http://localhost:8000/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

This will:
- Install dependencies for all apps and packages
- Spin up PostgreSQL database (port 5432) and Adminer UI (port 8080)
- Start FastAPI backend (port 8000)
- Start Next.js frontend (port 3000)

### Manual Setup (Alternative)

**Start database only:**
```bash
cd packages/docker && docker-compose up -d
```

**Start backend:**
```bash
cd apps/api && uv run uvicorn main:app --host localhost --port 8000 --reload
```

**Start frontend:**
```bash
cd apps/web && pnpm dev
```

### API Testing Examples
```bash
# Health check
curl http://localhost:8000/health

# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}' | jq -r '.access_token')

# Test MMM status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/mmm/status

# Get media channels
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/mmm/channels

# Get contribution data for a specific channel
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/mmm/contribution?channel=Google_Search"
```

### Available Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Next.js MMM Dashboard |
| **Backend API** | http://localhost:8000 | FastAPI with auto-docs |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **Database Admin** | http://localhost:8080 | Adminer PostgreSQL UI |

---

## Development Commands

### Essential Commands
```bash
pnpm dev              # Start all services (recommended)
pnpm build            # Build all applications
pnpm lint             # Run linting across all packages
pnpm stop             # Clean shutdown of all services
```

### Database Commands
```bash
pnpm seed                           # Seed sample data with test users
cd apps/api && uv run python reset_db.py  # Reset database tables
```

### Testing Commands
```bash
cd apps/api && uv run pytest       # Run all tests
cd apps/api && uv run pytest -m unit      # Run unit tests only
cd apps/api && uv run pytest -m integration  # Run integration tests only
cd apps/api && uv run pytest --cov=.      # Run tests with coverage
```

---

## Testing

### **Test Architecture**
- **Comprehensive testing** with pytest and async support
- **Unit tests**: MMM model loading, authentication utilities, data processing
- **Integration tests**: Full API workflow, authentication flow, MMM endpoints
- **Coverage reporting**: 80% minimum coverage requirement
- **Mock data fixtures**: Reliable testing with consistent data

### **Test Categories**

| Category | Count | Description |
|----------|-------|-------------|
| **Unit Tests** | 15+ | Individual component testing |
| **Integration Tests** | 25+ | Full API workflow testing |
| **Authentication Tests** | 10+ | Security and auth flow testing |
| **MMM Tests** | 8+ | Model loading and data processing |

### **Test Commands**
```bash
# Run all tests
cd apps/api && uv run pytest

# Run with coverage
cd apps/api && uv run pytest --cov=. --cov-report=html

# Run specific test categories
cd apps/api && uv run pytest -m unit
cd apps/api && uv run pytest -m integration
cd apps/api && uv run pytest -m auth
cd apps/api && uv run pytest -m mmm
```

---

## Troubleshooting

### Common Issues
| Issue | Solution |
|-------|----------|
| "Cannot connect to Docker daemon" | Ensure Docker Desktop is running |
| Containers fail to start | Try `pnpm stop && pnpm dev` |
| Application not responding | Check logs and ensure all services are running |
| Port conflicts (3000, 8000, 5432) | Stop other services or change ports in config |
| Authentication fails | Verify test credentials: `test@example.com` / `test123` |
| MMM model not loading | Check if `saved_mmm.pkl` exists, system falls back to mock data |

### Debug Commands
```bash
pnpm stop                          # Clean shutdown all services
docker-compose logs                # View all container logs
curl http://localhost:8000/health  # Test backend health
curl http://localhost:3000         # Test frontend availability
```

### Test Credentials
- **Test User**: `test@example.com` / `test123`
- **Admin User**: `admin@example.com` / `admin123`
- **Demo User**: `demo@example.com` / `demo123`

> **Note**: Registration is available but uses the seeded test users for development.

---

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
| **Caching** | No caching layer | Redis for session and MMM data caching |
| **Monitoring** | Basic logging | APM with Grafana/Prometheus |
| **Deployment** | Docker Compose | Kubernetes with auto-scaling |

#### Next Steps
1. **Redis integration** for caching MMM computations
2. **Rate limiting** for API endpoints
3. **Monitoring stack** with metrics and alerting
4. **CI/CD pipeline** with automated testing and deployment
5. **Load balancing** for high availability
6. **Database optimization** with connection pooling and query optimization

### MMM Model Integration Strategy

| What We're Optimizing | Current Implementation | Production Enhancement |
|----------------------|------------------------|------------------------|
| **Model Loading** | Load on demand with fallback to mock data | Pre-load and cache model data in Redis |
| **Data Processing** | Real-time computation of response curves | Background processing with cached results |
| **Channel Analysis** | Extract 5 channels from real model | Support dynamic channel configuration |
| **Performance** | ~100ms response times | <50ms with caching and optimization |

### Security & Monitoring

| Security Area | Current Implementation | Production Enhancement |
|---------------|------------------------|------------------------|
| **Authentication** | JWT tokens with bcrypt hashing | Add refresh tokens and rate limiting |
| **API Security** | CORS middleware and input validation | API gateway with throttling and WAF |
| **Data Protection** | SQL injection protection via ORM | Encryption at rest and in transit |
| **Monitoring** | Basic error logging | Comprehensive APM and security monitoring |

### Alternative Approaches Considered

| Alternative | What We Considered | Pros | Cons | Why We Didn't Choose It |
|-------------|-------------------|------|------|-------------------------|
| **Microservices** | Separate auth and MMM services | Better scalability, service isolation | More complex deployment, network overhead | Monolith is simpler for current scope |
| **GraphQL API** | GraphQL instead of REST | Flexible queries, better for complex data | Learning curve, more complex caching | REST meets current requirements |
| **Real-time Updates** | WebSocket for live MMM updates | Real-time dashboard updates | Added complexity, not required | Polling is sufficient for MMM data |
| **NoSQL Database** | MongoDB for MMM model storage | Better for unstructured model data | Different from relational user data | PostgreSQL JSON support is sufficient |

### What I'd Do Differently

#### With More Time
| Feature | Description |
|---------|-------------|
| **API Versioning** | Implement `/api/v1/` prefix for future compatibility |
| **Advanced Caching** | Redis integration for MMM computations |
| **Real-time Features** | WebSocket for live dashboard updates |
| **Advanced Analytics** | Historical trend analysis and forecasting |

#### With Different Requirements
| Feature | Description |
|---------|-------------|
| **Multi-tenancy** | Support for multiple organizations |
| **Advanced Permissions** | Role-based access control for different MMM models |
| **Export Features** | PDF/Excel export of MMM insights |
| **Integration APIs** | Webhooks and third-party integrations |

#### More Features for Large Scale

##### Dashboard Enhancements
| Feature | Description |
|---------|-------------|
| **Custom Dashboards** | User-configurable dashboard layouts |
| **Advanced Visualizations** | Interactive charts with drill-down capabilities |
| **Comparative Analysis** | Side-by-side channel performance comparison |
| **Forecasting** | Predictive analytics for future performance |

##### DevOps & Infrastructure
| Feature | Description |
|---------|-------------|
| **CI/CD Pipeline** | Automated testing, building, and deployment |
| **Container Orchestration** | Kubernetes deployment with auto-scaling |
| **Monitoring Stack** | Comprehensive observability with Grafana/Prometheus |
| **Backup Strategy** | Automated database backups and disaster recovery |

---

## Reference Documentation

- [Google Meridian Developer Documentation](https://developers.google.com/meridian/docs/advanced-modeling/interpret-visualizations)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)