# RoyyaAI — Project Documentation
**AI-Powered Copilot for Vannamei Shrimp Farmers**
Last Updated: June 2026

---

## What is RoyyaAI?

RoyyaAI is a SaaS platform that helps Vannamei shrimp farmers (primarily in Andhra Pradesh, India) manage their ponds using AI. Farmers can:
- Track daily water quality (DO, pH, salinity, temperature, etc.)
- Get an automatic pond health score after each log entry
- Ask an AI assistant questions in Telugu or English
- View analytics like FCR, biomass, days to harvest
- Access a RAG-powered knowledge base of shrimp farming best practices

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.11) |
| Database | PostgreSQL (via Docker) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Auth | JWT (PyJWT) + bcrypt |
| AI Chat | OpenAI gpt-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | Qdrant |
| Cache/Queue | Redis |
| Frontend | Next.js 16 + Tailwind CSS |
| State Management | Zustand + TanStack Query |
| Mobile (planned) | Flutter |

---

## Project Structure

```
c:\UNKNOWN\RoyyaAI\
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── farms.py
│   │   │   ├── logs.py
│   │   │   ├── ai.py
│   │   │   └── analytics.py
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── organization.py
│   │   │   ├── user.py
│   │   │   ├── farm.py
│   │   │   ├── pond.py
│   │   │   ├── daily_log.py
│   │   │   └── conversation.py
│   │   ├── services/             # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── farm_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── analytics_service.py
│   │   │   └── health_scorer.py
│   │   ├── rag/                  # RAG pipeline
│   │   │   ├── embedder.py
│   │   │   ├── qdrant_store.py
│   │   │   ├── ingestion.py
│   │   │   └── retriever.py
│   │   ├── agents/
│   │   │   └── prompts.py        # AI system prompt
│   │   ├── schemas/              # Pydantic schemas
│   │   └── core/
│   │       ├── config.py         # Settings (pydantic-settings)
│   │       ├── database.py       # Async SQLAlchemy engine
│   │       ├── security.py       # JWT + bcrypt
│   │       └── deps.py           # FastAPI dependencies
│   ├── alembic/versions/         # DB migrations
│   │   ├── 0001_initial_auth.py
│   │   ├── 0002_farms_ponds_logs.py
│   │   ├── 0003_ai_conversations.py
│   │   └── 0004_health_score.py
│   ├── knowledge_base/           # RAG source documents
│   │   ├── water_quality.txt
│   │   ├── diseases.txt
│   │   ├── feeding.txt
│   │   ├── stocking_harvest.txt
│   │   └── pond_preparation.txt
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── login/page.tsx
│       │   ├── register/page.tsx
│       │   └── dashboard/
│       │       ├── page.tsx              # Dashboard home
│       │       ├── farms/page.tsx        # Farm list
│       │       ├── farms/[farm_id]/page.tsx         # Farm detail + ponds
│       │       ├── farms/[farm_id]/ponds/[pond_id]/page.tsx  # Pond detail + logs
│       │       ├── analytics/page.tsx    # Analytics
│       │       └── chat/page.tsx         # AI chat
│       ├── components/
│       │   ├── Sidebar.tsx
│       │   ├── Providers.tsx
│       │   └── ClientToaster.tsx
│       ├── lib/api.ts            # Axios client
│       └── store/auth.ts         # Zustand auth store
├── docker-compose.yml
├── .env
└── commands.txt
```

---

## Database Schema

### organizations
| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| name | String | Farm organization name |
| slug | String | URL-safe name |
| is_active | Boolean | |
| created_at | DateTime | |

### users
| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| organization_id | UUID | FK → organizations |
| email | String | Unique |
| full_name | String | |
| hashed_password | String | bcrypt |
| role | Enum | super_admin / farm_owner / farm_manager / technician |
| preferred_language | String | en / te |

### farms
| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| organization_id | UUID | FK → organizations |
| name | String | |
| location | String | Village name |
| district | String | |
| state | String | |
| total_area_acres | Float | Optional |

### ponds
| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| farm_id | UUID | FK → farms |
| name | String | |
| area_acres | Float | |
| depth_feet | Float | |
| pond_type | String | earthen / lined / hdpe / concrete |
| water_source | String | borewell / canal / river / sea |
| status | Enum | active / harvested / fallow / preparation |

### stockings
| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| pond_id | UUID | FK → ponds |
| stocking_date | Date | |
| pl_count | Integer | Number of PLs stocked |
| stocking_density | Float | PL/m² |
| pl_source | String | Hatchery name |
| pl_age_days | Integer | PL age at stocking |
| is_active | Boolean | Only one active stocking per pond |

### daily_logs
| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| pond_id | UUID | FK → ponds |
| log_date | Date | |
| doc | Integer | Auto-calculated from stocking date |
| dissolved_oxygen | Float | mg/L |
| ph | Float | |
| salinity | Float | ppt |
| temperature | Float | °C |
| alkalinity | Float | mg/L |
| ammonia | Float | mg/L |
| nitrite | Float | mg/L |
| secchi_depth | Float | cm |
| feed_quantity_kg | Float | |
| feed_brand | String | |
| abw_grams | Float | Average body weight |
| mortality_count | Integer | |
| health_score | Float | 0-100 (auto-calculated) |
| health_status | String | excellent/good/warning/critical |
| notes | Text | |
| created_by | UUID | FK → users |

### ai_conversations
| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | FK → users |
| pond_id | UUID | FK → ponds (optional) |
| role | Enum | user / assistant |
| message | Text | |
| created_at | DateTime | |

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/auth/register | Register user + org, returns JWT |
| POST | /api/v1/auth/login | Login, returns JWT |
| GET | /api/v1/auth/me | Get current user info |

### Farms
| Method | Endpoint | Description |
|---|---|---|
| GET | /api/v1/farms | List all farms |
| POST | /api/v1/farms | Create farm |
| GET | /api/v1/farms/{farm_id} | Get farm |
| PUT | /api/v1/farms/{farm_id} | Update farm |
| DELETE | /api/v1/farms/{farm_id} | Delete farm |
| GET | /api/v1/farms/{farm_id}/ponds | List ponds in farm |
| POST | /api/v1/farms/{farm_id}/ponds | Create pond |
| GET | /api/v1/farms/ponds/{pond_id} | Get pond |
| POST | /api/v1/farms/ponds/{pond_id}/stockings | Add stocking |
| GET | /api/v1/farms/ponds/{pond_id}/stockings/active | Get active stocking |

### Daily Logs
| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/logs/ponds/{pond_id} | Add daily log (auto-calculates DOC + health score) |
| GET | /api/v1/logs/ponds/{pond_id} | List logs (latest 30) |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | /api/v1/analytics/ponds/{pond_id}/summary | Pond summary (DOC, biomass, FCR, days to harvest) |
| GET | /api/v1/analytics/ponds/{pond_id}/water-quality | Water quality trend data |
| GET | /api/v1/analytics/ponds/{pond_id}/growth | Growth trend data |

### AI
| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/ai/chat | Chat with AI (uses pond context + RAG) |
| POST | /api/v1/ai/ingest-knowledge | Index knowledge base into Qdrant (run once) |

---

## Pond Health Scoring

After every daily log, a health score (0-100) is automatically calculated.

### Parameter Weights
| Parameter | Weight | Safe Range | Warning Range |
|---|---|---|---|
| Dissolved Oxygen | 30% | 5.0-8.0 mg/L | 3.0-12.0 mg/L |
| pH | 20% | 7.5-8.5 | 7.0-9.5 |
| Temperature | 15% | 25-30°C | 20-35°C |
| Ammonia | 15% | 0-0.5 mg/L | 0-2.0 mg/L |
| Nitrite | 10% | 0-0.1 mg/L | 0-1.0 mg/L |
| Salinity | 5% | 10-25 ppt | 2-40 ppt |
| Alkalinity | 3% | 80-150 mg/L | 40-200 mg/L |
| Secchi Depth | 2% | 25-45 cm | 15-70 cm |

### Score to Status
| Score | Status |
|---|---|
| 85-100 | Excellent |
| 65-84 | Good |
| 40-64 | Warning |
| 0-39 | Critical |

---

## AI Chat System

- **Model:** OpenAI gpt-4o-mini
- **Language:** Auto-detects Telugu or English from farmer's message
- **Pond Context:** Fetches pond info, active stocking, last 7 daily logs
- **RAG:** Retrieves top-4 relevant chunks from Qdrant knowledge base
- **Conversation History:** Last 6 messages included for context

### Knowledge Base Files
- `water_quality.txt` — DO, pH, salinity safe ranges, emergency actions
- `diseases.txt` — WSSV, AHPND, Vibriosis symptoms and prevention
- `feeding.txt` — feeding schedules by DOC, FCR targets, feed brands
- `stocking_harvest.txt` — stocking density, growth targets, harvest timing
- `pond_preparation.txt` — pond prep steps, aeration, probiotics, biosecurity

---

## Key Business Rules

1. **Multi-tenant:** All data is scoped to `organization_id` — farmers only see their own data
2. **DOC Auto-calculation:** `DOC = log_date - stocking_date` (calculated when saving daily log)
3. **One active stocking per pond:** Adding new stocking deactivates the previous one
4. **Token expiry:** Access token = 60 minutes, Refresh token = 30 days
5. **RAG ingestion:** Must call `/api/v1/ai/ingest-knowledge` once after deployment

---

## Local Development Setup

### Prerequisites
- Python 3.11
- Node.js 18+
- Docker Desktop

### Start Infrastructure
```bash
cd c:\UNKNOWN\RoyyaAI
docker-compose up -d postgres redis qdrant
```

### Start Backend
```bash
cd c:\UNKNOWN\RoyyaAI\backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd c:\UNKNOWN\RoyyaAI\frontend
npm install
npm run dev
# Runs on http://localhost:3001
```

### After first deploy — ingest knowledge base
```
POST /api/v1/ai/ingest-knowledge   (with valid JWT token)
```

---

## Environment Variables (.env)

```
APP_NAME=RoyyaAI
DATABASE_URL=postgresql+asyncpg://royyaai:royyaai_secret@localhost:5432/royyaai_db
JWT_SECRET_KEY=<long-random-secret>
OPENAI_API_KEY=sk-...
QDRANT_HOST=localhost
QDRANT_PORT=6333
REDIS_URL=redis://localhost:6379/0
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]
```

---

## What's Built (Phase 1 MVP)

- [x] User registration and login (JWT auth)
- [x] Multi-tenant organization system
- [x] Farm management (create, list, update)
- [x] Pond management (create, list, update)
- [x] Stocking records
- [x] Daily water quality logs
- [x] DOC auto-calculation
- [x] Pond Health Score (0-100) with alerts
- [x] AI Chat (Telugu/English auto-detect)
- [x] RAG Knowledge Base (Qdrant + OpenAI embeddings)
- [x] Analytics (summary, water quality trend, growth trend)
- [x] Next.js web dashboard (login, farms, ponds, logs, chat, analytics)

## What's Pending (Phase 2)

- [ ] Flutter mobile app
- [ ] WhatsApp alerts (critical health score)
- [ ] Production deployment
- [ ] Push notifications
- [ ] Harvest recording and profit/loss calculator
- [ ] PDF reports per crop cycle
- [ ] Admin panel for super admin
