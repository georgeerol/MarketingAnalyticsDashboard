# Google Meridian MMM Dashboard

A **Media Mix Modeling (MMM) Dashboard** built with FastAPI and Next.js for analyzing marketing channel performance using Google Meridian models.

## 🎯 Project Status

### ✅ Phase 1: User Management (Backend Complete)
1. **✅ User authentication** - JWT-based auth with bcrypt password hashing
2. **🔄 User dashboard** - Backend ready, frontend pending

### 🔄 Phase 2: Google Meridian MMM Dashboard  
3. **📋 Load and integrate** the Google Meridian model trace (`saved_mmm.pkl`)
4. **📋 Create contribution charts** (pick one type)
5. **📋 Implement response curves** showing diminishing returns
6. **📋 Build compelling customer narrative** for channel performance

### 📚 Reference Documentation
- [Google Meridian Developer Documentation](https://developers.google.com/meridian/docs/advanced-modeling/interpret-visualizations)

## 🏗️ Current Implementation

### ✅ Backend (FastAPI)
- **Authentication system** with JWT tokens and password hashing
- **Database models** for Users, Campaigns, Channels, and MMM data
- **API endpoints** for user registration, login, and user management
- **PostgreSQL integration** with SQLAlchemy ORM
- **Environment configuration** and settings management
- **CORS middleware** for frontend integration

### 📋 Frontend (Next.js)
- **Basic setup** with shadcn/ui components
- **Theme provider** for light/dark mode
- **Authentication UI** - pending implementation
- **Dashboard pages** - pending implementation





## General structure
- apps
    - api: fastapi
    - web: nextjs frontend
- packages
    - ui: shadcn component library
    - docker: dockerized database setup 

## 🚀 Getting Started

### Prerequisites
- Node.js 20+ and pnpm
- Python 3.12+
- Docker (for database)

### Quick Start

**1. Install dependencies:**
```bash
pnpm install
```

**2. Start development environment:**
```bash
pnpm dev
```

This will:
- Install dependencies for all apps and packages
- Spin up PostgreSQL database (port 5432) and Adminer UI (port 8080)
- Start FastAPI backend (port 8000)
- Start Next.js frontend (port 3000)

### 🔧 Manual Setup (Alternative)

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

## 🔗 Service URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:8080 (adminer)

## 🗄️ Database Management

**Reset database tables:**
```bash
cd apps/api && uv run python reset_db.py
```

**Seed sample data:**
```bash
cd apps/api && uv run python seed.py
```

**Sample login credentials:**
- Admin: `admin@example.com` / `admin123`
- Demo: `demo@example.com` / `demo123`

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (OAuth2 form)
- `POST /auth/login-json` - User login (JSON payload)
- `GET /auth/me` - Get current user info
- `GET /auth/users` - Get all users (admin only)

### System
- `GET /health` - Health check
- `GET /` - API info
- `GET /docs` - Interactive API documentation

## 🧪 Testing the API

**Health check:**
```bash
curl http://localhost:8000/health
```

**API documentation:**
Visit http://localhost:8000/docs for interactive API testing

**Note**: Authentication endpoints are implemented but may need debugging for bcrypt password validation. Use the interactive docs for testing.

## 🎨 Frontend Component Library
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



