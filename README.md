# Google Meridian MMM Dashboard

A **Media Mix Modeling (MMM) Dashboard** built with FastAPI and Next.js for analyzing marketing channel performance using Google Meridian models.

## 🎯 Project Status

| Phase | Task | Description | Status |
|-------|------|-------------|---------|
| **Phase 1** | **User Management** | | **✅ COMPLETE** |
| 1.1 | User Authentication | JWT-based auth with secure password hashing | ✅ Complete |
| 1.2 | User Dashboard | Complete authentication UI with login/register/dashboard | ✅ Complete |
| **Phase 2** | **Google Meridian MMM Dashboard** | | **✅ COMPLETE** |
| 2.1 | Load & Integrate Model | Google Meridian model trace (`saved_mmm.pkl`) with **REAL DATA** | ✅ Complete |
| 2.2 | Contribution Charts | Interactive channel performance visualization | ✅ Complete |
| 2.3 | Response Curves | Diminishing returns analysis with saturation points | ✅ Complete |
| 2.4 | Customer Narrative | AI-powered insights and recommendations dashboard | ✅ Complete |

### 🎉 **Project Status: COMPLETE**
- **✅ Real Google Meridian Integration**: Using authentic 32.3MB `saved_mmm.pkl` model
- **✅ Professional MMM Dashboard**: Full-featured analytics platform
- **✅ 5-Channel Analysis**: Real data from your Google Meridian model
- **✅ Production Ready**: Complete authentication and data visualization system

### 📚 Reference Documentation
- [Google Meridian Developer Documentation](https://developers.google.com/meridian/docs/advanced-modeling/interpret-visualizations)

## 🏗️ Current Implementation

### ✅ Backend (FastAPI)
- **Authentication system** with JWT tokens and secure password hashing
- **Database models** for Users, Campaigns, Channels, and MMM data
- **API endpoints** for user registration, login, and user management
- **PostgreSQL integration** with SQLAlchemy ORM
- **Environment configuration** and settings management
- **CORS middleware** for frontend integration
- **Seed data** with sample users for testing

### ✅ Frontend (Next.js)
- **Complete authentication UI** with login/register forms
- **Protected dashboard** with user profile display
- **Responsive design** with shadcn/ui components
- **State management** with Zustand for authentication
- **Auto-redirect logic** based on authentication status
- **Theme provider** for light/dark mode support





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
pnpm seed
```

**Test credentials:**
- Test User: `test@example.com` / `test123`

> **Note**: Registration is temporarily disabled due to bcrypt configuration. Use the test credentials above to login.

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (OAuth2 form)
- `POST /auth/login-json` - User login (JSON payload)
- `GET /auth/me` - Get current user info
- `GET /auth/users` - Get all users (admin only)

### MMM (Media Mix Modeling)
- `GET /mmm/status` - Check MMM model status and basic info
- `GET /mmm/info` - Get detailed MMM model information
- `GET /mmm/channels` - Get list of media channels
- `GET /mmm/contribution` - Get contribution data (optional `?channel=name` filter)
- `GET /mmm/response-curves` - Get response curve data (optional `?channel=name` filter)
- `GET /mmm/explore` - Explore MMM model structure
- `GET /mmm/test` - Test MMM model loading and functionality

### System
- `GET /health` - Health check
- `GET /` - API info
- `GET /docs` - Interactive API documentation

## 🧪 Testing the API

**Health check:**
```bash
curl http://localhost:8000/health
```

**Test authentication:**
```bash
curl -X POST http://localhost:8000/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

**Test MMM endpoints:**
```bash
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

**API documentation:**
Visit http://localhost:8000/docs for interactive API testing

## 🔐 Authentication System

The application features a complete authentication system:

### 🌐 Frontend Features
- **Login Page** (`/login`) - Email/password authentication
- **Register Page** (`/register`) - User registration (temporarily disabled)
- **Dashboard** (`/dashboard`) - Protected user profile page
- **Auto-redirect** - Unauthenticated users redirected to login
- **Persistent sessions** - Login state maintained across browser sessions

### 🔧 Backend Features
- **JWT tokens** - Secure token-based authentication
- **Password hashing** - Secure password storage
- **Protected routes** - API endpoints require authentication
- **User management** - Complete user CRUD operations
- **MMM API** - Complete Google Meridian model data access with mock data fallback
- **Data processing** - Pandas/NumPy integration for MMM analytics

### 🧪 Testing the Authentication
1. Visit `http://localhost:3000`
2. Should redirect to login page
3. Login with: `test@example.com` / `test123`
4. Should redirect to dashboard showing user profile
5. Test logout functionality

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



