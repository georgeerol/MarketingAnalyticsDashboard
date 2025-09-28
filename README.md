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

- Secure JWT auth with bcrypt password hashing
- Register and get logged in automatically
- Sessions stay active across page refreshes
- Clean login/registration UI

### MMM Analytics Dashboard

- **Real Model Data**: Loads actual Google Meridian model (32MB `saved_mmm.pkl`)
- **Contribution Charts**: See channel performance with bar/pie charts
- **Response Curves**: Saturation analysis showing diminishing returns for each channel
- **Smart Insights**: AI-generated recommendations for budget optimization
- **Export**: Download insights in JSON, CSV, or TXT formats

### Performance & Quality

- **95% faster**: Smart model caching (3+ seconds → 40-50ms)
- **Well tested**: 128+ test functions across comprehensive test suites
- **Clean code**: Service interfaces, centralized constants, structured logging
- **Production ready**: Docker setup, proper error handling, security best practices

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

The application follows a standard three-tier architecture with clear data flow:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │───▶│  Next.js    │───▶│   FastAPI   │
│             │    │  Frontend   │    │   Backend   │
│             │    │ (Port 3000) │    │ (Port 8000) │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                           │                   ▼
                           │            ┌─────────────┐
                           │            │ PostgreSQL  │
                           │            │  Database   │
                           │            │ (Port 5432) │
                           │            └─────────────┘
                           │                   │
                           ▼                   ▼
                   ┌─────────────┐    ┌─────────────┐
                   │   Zustand   │    │ Google MMM  │
                   │    Store    │    │ Model Cache │
                   │(localStorage)│    │ (LRU Cache) │
                   └─────────────┘    └─────────────┘
                                             ▲
                                             │
                                     ┌─────────────┐
                                     │saved_mmm.pkl│
                                     │   (32MB)    │
                                     │ (Read-only) │
                                     └─────────────┘
```

**Data Flow Components:**

- **Browser**: Users interact with the Next.js app running on port 3000
- **Frontend**: Next.js handles routing, auth, and makes API calls to the backend
- **Backend**: FastAPI server on port 8000 processes requests and validates JWT tokens
- **Database**: PostgreSQL on port 5432 stores user accounts and session data
- **MMM Model**: 32MB Google Meridian model file loaded once and cached in memory
- **State**: Zustand keeps auth state in browser localStorage between sessions
- **Security**: JWT tokens in Authorization headers protect API endpoints

### MMM Processing Pipeline

The MMM model processing pipeline demonstrates significant performance optimization through caching:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ saved_mmm   │───▶│ Model Cache │───▶│   FastAPI   │
│ .pkl (32MB) │    │ (LRU)       │    │ Endpoints   │
└─────────────┘    └─────────────┘    └─────────────┘
                                             │
                   ┌─────────────────────────┼─────────────────────────┐
                   │                         │                         │
                   ▼                         ▼                         ▼
            ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
            │ Channel     │         │ Response    │         │ Export      │
            │ Summary API │         │ Curves API  │         │ Insights API│
            └─────────────┘         └─────────────┘         └─────────────┘
                   │                         │                         │
                   ▼                         ▼                         ▼
            ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
            │ Contribution│         │ Response    │         │ Smart       │
            │ Charts      │         │ Curves      │         │ Insights    │
            │ (Frontend)  │         │ (Frontend)  │         │ (Reports)   │
            └─────────────┘         └─────────────┘         └─────────────┘
```
- **First load**: Takes ~3 seconds to load the 32MB model file
- **After that**: Cached requests are fast at 40-50ms (95% improvement)
- **Three APIs**: Channel summary, response curves, and export endpoints
- **Channels**: Gets 5 marketing channels from `/mmm/channels/summary`
- **Curves**: Shows diminishing returns via `/mmm/response-curves`
- **Export**: Download insights as JSON, CSV, or text from `/export/insights`

### Authentication Flow

Authentication system with automatic login after registration for improved user experience:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Registration│───▶│   FastAPI   │───▶│  Dashboard  │
│    Form     │    │/auth/register│    │   Access    │
│ (Frontend)  │    │(Auto-Login) │    │ (Protected) │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Validation  │    │ JWT Token   │    │localStorage │
│ & Hashing   │    │ Generation  │    │ Persistence │
│ (Backend)   │    │ (Backend)   │    │ (Frontend)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

- **Auto-login**: Register at `/auth/register` and get logged in immediately
- **Security**: Tokens expire after 30 minutes, passwords are bcrypt hashed
- **Stay logged in**: Zustand saves your JWT in localStorage between sessions
- **Protected pages**: Dashboard and MMM pages need a valid JWT token
- **API calls**: Frontend sends JWT as `Authorization: Bearer <token>`
- **Safety**: CORS protection, input validation, and secure headers

### Protocol-Based Architecture

Implementation uses Python protocols for dependency inversion and enhanced testability:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ UserService │    │ AuthService │    │ MMMService  │
│  Protocol   │    │  Protocol   │    │  Protocol   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ UserService │    │ AuthService │    │ MMMService  │
│Implementation│    │Implementation│    │Implementation│
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ MockUser    │    │ MockAuth    │    │ MockMMM     │
│ Service     │    │ Service     │    │ Service     │
│ (Testing)   │    │ (Testing)   │    │ (Testing)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

- **Protocols**: Abstract interfaces in `services/interfaces.py` define what services do
- **Real services**: Concrete implementations handle business logic and database operations
- **Test mocks**: Fake services in `tests/mocks/` let you test without real databases
- **Dependency injection**: FastAPI automatically picks the right service via `api/deps.py`
- **SOLID design**: Dependency inversion makes testing easier and code more flexible

## Key Components

### 1. Protocol-Based Architecture

- **Service Interfaces**: `UserServiceProtocol`, `AuthServiceProtocol`, `MMMServiceProtocol`
- **Dependency Injection**: Protocol-based DI in `api/deps.py`
- **Mock Services**: Complete mock implementations for testing
- **SOLID design**: Follows all 5 SOLID principles

### 2. MMM Model Integration

- **Real Model**: 32.3MB Google Meridian model (`saved_mmm.pkl`)
- **Data Processing**: Contribution data, response curves, channel analysis
- **Channel Support**: 5-channel analysis from real model data
- **Fallback**: Uses mock data when model file isn't available

### 3. Authentication System

- **JWT Tokens**: Secure token-based auth with bcrypt hashing
- **Protected Routes**: All MMM endpoints require authentication
- **User Management**: Complete CRUD operations
- **Sessions**: Tokens expire after 30 minutes but stay saved

### 4. Interactive Dashboard

- **Contribution Charts**: Visual breakdown of channel performance
- **Response Curves**: Saturation analysis with diminishing returns and efficiency metrics
- **Smart Insights**: AI-generated recommendations and performance analysis
- **Export**: Download insights in JSON, CSV, or TXT formats

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - User registration with auto-login
- `POST /api/v1/auth/login` - User login (OAuth2 form)
- `GET /api/v1/auth/me` - Get current user info

### MMM Analytics

- `GET /api/v1/mmm/status` - Model status and info
- `GET /api/v1/mmm/channels` - List of media channels
- `GET /api/v1/mmm/channels/summary` - Channel performance summary
- `GET /api/v1/mmm/contribution` - Contribution analysis data
- `GET /api/v1/mmm/response-curves` - Response curve data
- `GET /api/v1/export/insights` - Export recommendations

## Development

### Prerequisites

- Node.js 20+
- Python 3.12
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
pnpm reset-db

# Initialize database tables
pnpm init-db

# Check database connection
pnpm check-db
```

#### Testing Commands

```bash
# Run all tests
pnpm test

# Run unit tests only
pnpm test:unit

# Run integration tests only
pnpm test:integration

# Run tests with coverage
pnpm test:coverage

# Run tests in verbose mode
pnpm test:verbose
```

#### Code Quality Commands

```bash
# Format code
pnpm format

# Lint code
pnpm lint

# Type checking
pnpm typecheck
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
# System Status Checks
pnpm debug:api-health      # Check API health with JSON formatting
pnpm debug:web-status      # Check web app status
pnpm debug:ports           # Check which processes are using MMM ports

# Database Debugging
pnpm debug:db-version      # Show PostgreSQL version
pnpm debug:db-tables       # List database tables and column counts

# Application Debugging
pnpm debug:model-status    # Check MMM model loading status
pnpm debug:env-vars        # Show environment variables
pnpm debug:memory          # Show memory and CPU usage
pnpm debug:logs            # Show recent database logs

# Comprehensive Check
pnpm debug:all             # Run multiple debug checks at once
```

#### Development Utilities

```bash
# Quick health checks
pnpm debug:api-health      # Check API health (uses curl + jq)
pnpm debug:ports           # Check running processes on MMM ports

# View API documentation
open http://localhost:8000/docs

# Access database UI (Adminer)
open http://localhost:8080

# Manual process management (if needed)
lsof -ti:8000 | xargs kill -9  # Kill API processes
lsof -ti:3000 | xargs kill -9  # Kill Web processes

# Docker debugging
docker ps  # Show running containers
pnpm debug:logs            # Database logs (uses docker logs)
docker exec -it docker-postgres-1 psql -U postgres -d mmm_db  # Direct DB access
```

### Test Users

| Email               | Password   | Role          |
| ------------------- | ---------- | ------------- |
| `test@example.com`  | `test123`  | Standard user |
| `admin@example.com` | `admin123` | Administrator |
| `demo@example.com`  | `demo123`  | Demo account  |

## Production Deployment Options

### Key Architectural Decisions

| Decision | What I Built | What I Considered | Why I Chose This |
|----------|--------------|-------------------|------------------|
| **Architecture** | Monorepo with Turbo + pnpm | Separate repos for API/web | Easier to share types and components |
| **API Style** | REST endpoints | GraphQL | MMM data is pretty straightforward, REST is simpler |
| **Auth** | JWT + bcrypt | OAuth with Google/GitHub | Wanted to show I can build auth from scratch |
| **Database** | PostgreSQL | MongoDB for model data | User data is relational, Postgres handles JSON fine |
| **Updates** | Polling every 30s | WebSocket connections | MMM data doesn't change that often |
| **State** | Zustand | Redux Toolkit | Zustand is way less boilerplate for this size project |
| **Model Caching** | Python LRU cache (3s → 40ms) | Redis from the start | Wanted to see the performance difference first |

### AWS Production Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    AWS Production Environment                                │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │ CloudFront  │    │ Application │    │ API Gateway │    │ EventBridge │                  │
│  │    CDN      │    │ Load Balancer│    │   (REST)    │    │ Scheduler   │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘                  │
│         │                   │                   │                   │                       │
│         ▼                   ▼                   ▼                   ▼                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│  │    S3       │    │    ECS      │    │    ECS      │    │   Lambda    │                  │
│  │ Static Web  │    │ FastAPI     │    │ FastAPI     │    │ Functions   │                  │
│  │   Assets    │    │ Service     │    │ Service     │    │ (Workers)   │                  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘                  │
│         │                   │                   │                   │                       │
│         └───────────────────┼───────────────────┼───────────────────┘                       │
│                             ▼                   ▼                   ▲                       │
│                      ┌─────────────┐    ┌─────────────┐           │                       │
│                      │ ElastiCache │    │     RDS     │           │                       │
│                      │   Redis     │    │ PostgreSQL  │           │                       │
│                      │ (Sessions)  │    │ Multi-AZ    │           │                       │
│                      └─────────────┘    └─────────────┘           │                       │
│                             │                   │                 │                       │
│                             ▼                   ▼                 │                       │
│                      ┌─────────────┐    ┌─────────────┐          │                       │
│                      │ ElastiCache │    │     S3      │          │                       │
│                      │   Redis     │    │   Bucket    │          │                       │
│                      │ (MMM Cache) │    │ (Models &   │          │                       │
│                      └─────────────┘    │  Exports)   │          │                       │
│                             │           └─────────────┘          │                       │
│                             ▼                   │                │                       │
│                      ┌─────────────┐           ▼                │                       │
│                      │     SQS     │    ┌─────────────┐          │                       │
│                      │   Queue     │    │ AWS Cognito │          │                       │
│                      │ (MMM Jobs)  │────│ Identity &  │──────────┘                       │
│                      └─────────────┘    │ Access Mgmt │                                  │
│                                         └─────────────┘                                  │
│                                                                                             │
│ Monitoring & Observability:                                                                │
│ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                  │
│ │ CloudWatch  │    │ X-Ray       │    │ CloudTrail  │    │ AWS Config  │                  │
│ │ (Metrics &  │    │ (Tracing)   │    │ (Audit)     │    │ (Compliance)│                  │
│ │  Logs)      │    │             │    │             │    │             │                  │
│ └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘                  │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Why AWS for Production:**
- **Auto-scaling**: ECS handles traffic spikes without me managing servers
- **Fast caching**: ElastiCache Redis keeps MMM data under 30ms response times
- **Background jobs**: SQS + Lambda for heavy model computations without blocking the API
- **Database reliability**: RDS Multi-AZ means automatic failover if something breaks
- **User management**: Cognito handles auth so I don't have to build user registration flows
- **Global CDN**: CloudFront serves static assets fast worldwide
- **Monitoring built-in**: CloudWatch and X-Ray show me what's slow or breaking
- **Security layers**: API Gateway throttling and WAF protect against attacks
- **Pay for usage**: Lambda only costs money when processing jobs
- **Less ops work**: Managed services mean less infrastructure to maintain
