# Claudine Server v1

**Production-ready AI voice assistant backend with Clean Architecture, multi-platform client support, and Claude AI integration.**

## 🎯 Vision

Claudine is a personal AI assistant with:
- **Chat-first interface** (WhatsApp-style) with voice option
- **Smart command routing** (#calendar, #note, #scan)
- **Multi-platform clients** (Web, iOS, Android, Windows PWA)
- **Calendar integration** (Google + Microsoft)
- **Claude AI** conversation with streaming responses

## 📊 Current Status: v0.2

### ✅ Completed Features

**v0.1 - OAuth & Calendar Integration:**
- JWT authentication (register, login, user management)
- OAuth 2.0 device flow (Google + Microsoft)
- Calendar CRUD operations (list, create, update, delete events)
- Multi-provider calendar support
- Token refresh handling

**v0.2 - Chat & AI Conversation:**
- Conversation management (create, list, delete)
- Message history and context
- Claude AI integration (Anthropic API)
- Streaming responses via SSE (Server-Sent Events)
- Command parser (#calendar, #note, #scan, #help)
- 4 conversation modes (chat, voice, note, scan)
- Mode-specific system prompts (Dutch optimized)

### 🚧 In Progress

**v0.3 - Cross-Platform Web Client:**
- React 18 + TypeScript + Vite
- Capacitor for mobile (iOS + Android)
- PWA for Windows (no install needed)
- WhatsApp-style responsive UI
- SSE streaming support

### 📋 Roadmap

**v0.4 - Voice I/O:**
- Speech-to-text (Whisper API)
- Text-to-speech (OpenAI TTS)
- Audio file handling

**v0.5 - Document Scanning:**
- OCR integration
- Document processing
- Receipt scanning

**v0.6 - Notes & Organization:**
- Note creation and management
- Tags and categories
- Search functionality

## 🏗️ Architecture

### Backend: Clean Architecture

```
┌─────────────────────────────────────────────────┐
│         Presentation Layer                      │
│  (FastAPI Routes, SSE Streaming)                │
├─────────────────────────────────────────────────┤
│         Application Layer                       │
│  (Use Cases, Business Orchestration)            │
├─────────────────────────────────────────────────┤
│         Domain Layer                            │
│  (Entities, Value Objects, Services)            │
├─────────────────────────────────────────────────┤
│         Infrastructure Layer                    │
│  (Database, OAuth, Claude API, Calendar APIs)   │
└─────────────────────────────────────────────────┘
```

### Frontend: Cross-Platform Stack

```
┌─────────────────────────────────────┐
│  React 18 + TypeScript + Vite       │
├─────────────────────────────────────┤
│  Capacitor (iOS/Android wrapper)    │
├─────────────────────────────────────┤
│  PWA (Windows installable)          │
└─────────────────────────────────────┘

Deployment Targets:
→ Web: Vercel/Netlify
→ iOS: App Store (via Capacitor)
→ Android: Play Store (via Capacitor)
→ Windows: PWA install (Chrome/Edge)
→ Future: Tauri for standalone .exe
```

## 📁 Project Structure

```
claudine-server-v1/
├── app/
│   ├── main.py                          # FastAPI application
│   ├── core/
│   │   ├── config.py                    # Settings & environment
│   │   └── dependencies.py              # DI providers, auth
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── user.py                  # User entity
│   │   │   ├── calendar_event.py        # Calendar event entity
│   │   │   └── conversation.py          # Conversation & Message entities
│   │   └── services/
│   │       └── command_parser.py        # Command routing (#calendar, etc.)
│   ├── application/
│   │   └── use_cases/
│   │       ├── auth_use_cases.py        # Authentication logic
│   │       ├── calendar_oauth_use_cases.py
│   │       ├── calendar_event_use_cases.py
│   │       └── conversation_use_cases.py # Chat & AI logic
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── models.py                # SQLAlchemy models
│   │   │   └── session.py               # Database connection
│   │   ├── repositories/
│   │   │   ├── user_repository.py
│   │   │   ├── oauth_token_repository.py
│   │   │   ├── user_settings_repository.py
│   │   │   └── conversation_repository.py
│   │   └── services/
│   │       ├── jwt.py                   # JWT token handling
│   │       ├── google_oauth.py          # Google OAuth device flow
│   │       ├── microsoft_oauth.py       # Microsoft OAuth device flow
│   │       ├── google_calendar.py       # Google Calendar API v3
│   │       ├── microsoft_calendar.py    # Microsoft Graph Calendar
│   │       └── claude_service.py        # Claude AI integration
│   └── presentation/
│       └── routers/
│           ├── health.py                # Health endpoints
│           ├── auth.py                  # Authentication endpoints
│           ├── calendar.py              # Calendar & OAuth endpoints
│           └── conversation.py          # Chat & AI endpoints
├── alembic/                             # Database migrations
│   └── versions/
│       ├── 001_add_oauth_and_settings_tables.py
│       └── 002_add_conversations_and_messages.py
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- PostgreSQL 15 (running on port 5432)
- Python 3.11+ (for local development)
- Anthropic API key (for Claude AI)

### 1. Clone Repository

```bash
git clone https://github.com/Frank19661129/Claudine-Server-v1.git
cd claudine-server-v1
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# Database
DATABASE_URL=postgresql://claudine:password@claudine-postgres:5432/claudine_v1

# Security
SECRET_KEY=your-secret-key-here

# OAuth - Google Calendar
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth - Microsoft Calendar
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_TENANT_ID=common

# Claude AI
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 3. Start Server

```bash
docker-compose up -d
```

### 4. Verify Health

```bash
curl http://localhost:8003/api/v1/health
# {"status":"healthy","service":"Claudine Server v1","version":"0.2"}
```

### 5. Access API Documentation

- **Swagger UI:** http://localhost:8003/docs
- **ReDoc:** http://localhost:8003/redoc

## 📡 API Endpoints

### Health
- `GET /api/v1/health` - Service health check

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with email/password
- `GET /api/v1/auth/me` - Get current user info

### Calendar OAuth
- `POST /api/v1/calendar/oauth/google/start` - Start Google device flow
- `POST /api/v1/calendar/oauth/google/poll` - Poll for Google token
- `POST /api/v1/calendar/oauth/microsoft/start` - Start Microsoft device flow
- `POST /api/v1/calendar/oauth/microsoft/poll` - Poll for Microsoft token
- `DELETE /api/v1/calendar/oauth/{provider}` - Disconnect provider
- `GET /api/v1/calendar/oauth/connected` - List connected providers

### Calendar Operations
- `GET /api/v1/calendar/calendars` - List calendars
- `GET /api/v1/calendar/events` - List events
- `POST /api/v1/calendar/events` - Create event
- `PUT /api/v1/calendar/events/{id}` - Update event
- `DELETE /api/v1/calendar/events/{id}` - Delete event

### Conversations (Chat & AI)
- `POST /api/v1/conversations` - Create conversation
- `GET /api/v1/conversations` - List conversations
- `GET /api/v1/conversations/{id}` - Get conversation with messages
- `POST /api/v1/conversations/{id}/messages` - Send message (returns complete response)
- `POST /api/v1/conversations/{id}/messages/stream` - Send message (streams response via SSE)
- `GET /api/v1/conversations/{id}/messages` - Get message history
- `DELETE /api/v1/conversations/{id}` - Delete conversation

### Command System

Use `#` keywords for smart routing:
- `#calendar` - Calendar operations
- `#note` - Note taking
- `#scan` - Document scanning
- `#help` - Show available commands

Example messages:
```
"#calendar afspraak maken morgen 14:00 met Jan"
"#note boodschappen melk brood eieren"
"#scan bon voor declaratie"
"#help calendar"
```

## 💻 Development

### Local Development (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Database Migrations

```bash
# Create new migration
alembic revision -m "description"

# Auto-generate from models
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Testing

```bash
pytest
pytest --cov=app  # With coverage
```

## 🗄️ Database Schema

### Tables

- **users** - User accounts (email, hashed_password, provider)
- **oauth_tokens** - Calendar provider tokens (Google/Microsoft)
- **user_settings** - User preferences (primary_calendar_provider, language, timezone)
- **conversations** - Chat conversations (user_id, title, mode, timestamps)
- **messages** - Chat messages (conversation_id, role, content, timestamps)

### Current Version
- Alembic: `002`
- Database: `claudine_v1`

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI 0.109+
- **Language:** Python 3.11+
- **Database:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0+
- **Migrations:** Alembic
- **AI:** Claude 3.5 Sonnet (Anthropic API)
- **OAuth:** Google + Microsoft device flow
- **Testing:** pytest

### Frontend (In Progress)
- **Framework:** React 18
- **Language:** TypeScript
- **Build:** Vite
- **Mobile:** Capacitor
- **State:** Zustand/Jotai
- **Styling:** TailwindCSS
- **API:** Axios + SSE

### DevOps
- **Containerization:** Docker & Docker Compose
- **Deployment:** (TBD - Vercel/Netlify for web, App Stores for mobile)

## 🌐 Port Configuration

- **Server Development:** Port 8003 (external) → 8000 (internal)
- **PostgreSQL:** Port 5432
- **Webclient Dev:** Port 5173 (Vite default)

## 🔐 Security

- JWT authentication with bcrypt password hashing
- OAuth 2.0 device flow (no client secrets exposed to users)
- Token refresh handling
- CORS configuration for web client
- Environment-based secrets

## 🎨 Design Principles

1. **Clean Architecture** - Clear separation of concerns
2. **Domain-Driven Design** - Business logic in domain layer
3. **SOLID Principles** - Maintainable, testable code
4. **API-First** - RESTful API with OpenAPI documentation
5. **Chat-First** - Mobile-friendly conversation interface
6. **Cross-Platform** - Write once, deploy everywhere

## 🔗 Related Repositories

- **Documentation:** [Claudine](https://github.com/Frank19661129/Claudine)
- **Server v0 (Legacy):** [Claudine-Server](https://github.com/Frank19661129/Claudine-Server)
- **Client v0:** [Claudine-Voice](https://github.com/Frank19661129/Claudine-Voice)

## 📝 Contributing

This is a personal project rebuild. See [DECISIONS.md](../Claudine/DECISIONS.md) in the main documentation repository for architectural decisions.

## 📄 License

Private project - All rights reserved

## 🎯 Next Steps

1. **v0.3:** Build React webclient with Capacitor
2. **v0.4:** Add voice input/output
3. **v0.5:** Implement document scanning
4. **v0.6:** Add notes functionality
5. **v0.7:** Mobile app builds (iOS + Android)
6. **v0.8:** Windows PWA optimization
7. **v0.9:** Performance optimization & caching
8. **v1.0:** Production release

---

**Last Updated:** 2025-11-14 | **Version:** 0.2 | **Status:** 🚧 Active Development
