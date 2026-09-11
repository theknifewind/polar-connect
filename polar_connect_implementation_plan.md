# Polar Connect — Backend Implementation Plan & Antigravity Agent Spec

> **Target System:** Polar Connect — AI-Powered Polar Science Knowledge & Outreach Platform (NCPOR)  
> **Source Spec:** Polar Connect SDD v1.0 (Draft — for team build use, by Srijit)  
> **Scope:** Backend implementation only. Frontend contract is fixed and non-negotiable.  
> **Timeline / Constraint:** Single-day build, spec-driven development, zero-budget infrastructure (local ChromaDB + Groq / Gemini fallback).

---

## 1. System Architecture & Tech Stack Overview

```
[ Frontend (Existing 8 Static/React Pages) ]
                       │  HTTPS / REST JSON
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Application Server (Python)            │
│  ├── /api/auth       (Session Cookie, HTTP-only, SHA-256)   │
│  ├── /api/repository (CRUD, Metadata Filters, Ingest Triggers)
│  ├── /api/assistant  (RAG Query Pipeline, Grounding Engine) │
│  ├── /api/learning   (Topics, Lessons, Quizzes & Grading)   │
│  ├── /api/stations   (Static Station Geo & Metadata)        │
│  ├── /api/media      (Stories, Field Notes, Video Metadata) │
│  ├── /api/studio     (6-Channel Draft Gen & Human Approval) │
│  └── /api/stats      (Live Homepage Aggregations)           │
└───────────────┬─────────────────────────────┬───────────────┘
                │                             │
    SQLAlchemy / SQLModel                     │ Local In-Process / HTTP
                ▼                             ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│     PostgreSQL Database      │ │     ChromaDB (Local Index)   │
│ - RepositoryItems            │ │ - Collection: polar_docs     │
│ - Stations                   │ │ - Embeddings: all-MiniLM-L6  │
│ - LearningTopics & Quizzes   │ │ - Metadata: doc_id, type,    │
│ - MediaStories               │ │             region, year     │
│ - StudioJobs & Channels      │ └──────────────────────────────┘
│ - AdminAccounts & Sessions   │
└──────────────────────────────┘
                │
                ▼ Shared LLM Gateway (`llm_gateway.py`)
┌──────────────────────────────────────────────────────────────┐
│ Primary: Groq API (openai/gpt-oss-20b)                      │
│ Fallback: Google Gemini API (gemini-3.5-flash-lite)          │
│ Ingestion: SentenceTransformers (all-MiniLM-L6-v2)           │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Layout to Scaffold

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI entry point, CORS, routers mount, cookie middleware
│   ├── config.py                # Pydantic Settings (.env loader: Groq, Gemini, DB URL, Secret Key)
│   ├── database.py              # SQLAlchemy engine, session maker, base model, init_db
│   ├── models/
│   │   ├── __init__.py
│   │   ├── admin.py             # AdminAccount & Session models
│   │   ├── repository.py        # RepositoryItem model & enum mappings
│   │   ├── station.py           # Station entity model
│   │   ├── learning.py          # LearningTopic & QuizQuestion models
│   │   ├── media.py             # MediaStory model
│   │   └── studio.py            # StudioJob & StudioChannelContent models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── repository.py        # Request/response DTOs matching frontend shape
│   │   ├── assistant.py         # Query request, dual-mode answer & source citation DTOs
│   │   ├── learning.py          # Quiz question & evaluation schemas
│   │   ├── studio.py            # Studio job creation & channel update/approval schemas
│   │   └── stats.py             # Aggregate count response DTO
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py              # Cookie-based session auth, password hashing (bcrypt/argon2)
│   │   └── exceptions.py        # Global uniform error handlers (plain-language responses)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_gateway.py       # Unified LLM provider router (Groq -> Gemini Fallback)
│   │   ├── vector_store.py      # ChromaDB client, collection init, chunk upsert & query
│   │   ├── ingestion.py         # PyPDF/text extractor, chunker (600 tokens/100 overlap), embedder
│   │   ├── assistant_rag.py     # Semantic search, context assembly, grounding prompt, dual output
│   │   └── studio_generator.py  # Single-pass 6-channel prompt generator & validator
│   └── routers/
│       ├── __init__.py
│       ├── auth.py              # /api/auth
│       ├── repository.py        # /api/repository
│       ├── assistant.py         # /api/assistant
│       ├── learning.py          # /api/learning
│       ├── stations.py          # /api/stations
│       ├── media.py             # /api/media
│       ├── studio.py            # /api/studio
│       └── stats.py             # /api/stats
├── uploads/                     # Local disk storage for raw uploaded documents and assets
├── chromadb_data/               # Persistent directory for local ChromaDB
├── seeds/
│   ├── stations_seed.json       # Maitri, Bharati, Himadri baseline data
│   ├── topics_seed.json         # Learning topics & verified quizzes
│   ├── media_seed.json          # Initial field notes & media items
│   └── seed_runner.py           # Populates DB on first boot
├── requirements.txt
├── .env.example
└── Dockerfile / railway.toml
```

---

## 3. Step-by-Step Implementation Roadmap

### Phase 1: Environment, Database & Shared Infrastructure
1. **Config & Environment (`config.py`):**
   - Environment variables: `DATABASE_URL`, `GROQ_API_KEY`, `GEMINI_API_KEY`, `ADMIN_SECRET_KEY`, `UPLOAD_DIR`, `CHROMADB_DIR`.
2. **Database Engine & ORM Models (`models/`):**
   - Set up PostgreSQL via SQLAlchemy / SQLModel.
   - Implement tables strictly according to SDD Section 9:
     - `admin_accounts`: `id`, `email`, `password_hash`, `created_at`.
     - `repository_items`: `id`, `type`, `title`, `summary`, `year`, `region`, `topics` (JSON/Array), `meta`, `file_url`, `file_type`, `raw_text`, `index_status`, timestamps.
     - `stations`: `id`, `name`, `region`, `description`, `established`, `number`, `facts` (JSON), `color`, `map_x`, `map_y`.
     - `learning_topics` & `quiz_questions`: FK relationship, question options array, `correct_answer_index`, explanation.
     - `media_stories`: `id`, `type`, `eyebrow`, `title`, `summary`, `gradient`, `cover_url`.
     - `studio_jobs` & `studio_channel_content`: 1-to-many relationship for `[web, linkedin, instagram, x, education, newsletter]`, with approval flags.
3. **Session Authentication (`core/auth.py`):**
   - Cookie-based session validation using `HttpOnly`, `SameSite=Lax`, and `Secure` flag.
   - Fast dependency `get_current_admin` to protect write routes.
4. **Seed Runner (`seeds/seed_runner.py`):**
   - Preload stations (Maitri, Bharati, Himadri), core learning modules, and baseline admin account (`admin@ncpor.res.in`).

### Phase 2: Core Non-AI Endpoints (Matching Existing Frontend Shapes)
1. **Repository Endpoints (`routers/repository.py`):**
   - `GET /api/repository`: Search across `title` and `summary`; filter by `type`, `region`, `year`, `topics`; return paginated records matching current frontend shape.
   - `GET /api/repository/{id}`: Full item detail.
   - `POST /api/repository`: Admin-protected file upload (`multipart/form-data`) + metadata. Saves file to `/uploads`, extracts text, marks `index_status="pending"`, and calls ingestion.
   - `DELETE /api/repository/{id}`: Admin-protected deletion. Purges database record, local file, and ChromaDB vector segments.
2. **Explorer & Media Endpoints (`routers/stations.py`, `routers/media.py`):**
   - Implement `GET /api/stations`, `GET /api/stations/{id}`, `GET /api/media`, `GET /api/media/{id}` directly returning the models.
3. **Learning & Quiz Endpoints (`routers/learning.py`):**
   - `GET /api/learning/topics`, `GET /api/learning/topics/{id}`.
   - `GET /api/learning/topics/{id}/quiz`: Return questions with `options`, but strip `correctAnswerIndex` to prevent client cheating.
   - `POST /api/learning/topics/{id}/quiz/submit`: Accepts `{answers: [index0, index1, ...]}`. Compares against stored questions, computes percentage score, returns per-question boolean correctness and explanations.
4. **Home Aggregate Statistics (`routers/stats.py`):**
   - `GET /api/stats`: Dynamic SQL count query returning expedition records, research papers, media assets, and learning paths.

### Phase 3: AI, Vector Search & RAG Pipeline
1. **Unified LLM Gateway (`services/llm_gateway.py`):**
   - Single point of contact for model requests (NFR-02, NFR-07).
   - Primary: Groq (`openai/gpt-oss-20b` or configured equivalent).
   - Fallback: Google Gemini (`gemini-3.5-flash-lite`).
   - Unified interface: `llm_gateway.generate(system_prompt: str, user_prompt: str, temperature=0.2) -> str`. Automatic try-primary, catch-error, log, and retry with fallback.
2. **Local Vector Store & Embeddings (`services/vector_store.py`):**
   - Initialize persistent ChromaDB client pointing to `CHROMADB_DIR`.
   - Embedder: `sentence-transformers/all-MiniLM-L6-v2` loaded locally.
   - Metadata filtered queries on `doc_id`. Re-indexing always wipes prior doc chunks before inserting new ones (NFR-03).
3. **Ingestion Service (`services/ingestion.py`):**
   - Extracts text from uploaded PDF/text/markdown files.
   - Token chunking: ~600 tokens chunk size, 100 token overlap.
   - Writes chunks and metadata to ChromaDB, sets `index_status = "indexed"` (or `"failed"` on exception).
4. **Assistant Service (`services/assistant_rag.py` & `routers/assistant.py`):**
   - `POST /api/assistant/query` (Public).
   - Pipeline:
     1. Embed incoming question.
     2. Query ChromaDB for top $k$ (e.g., $k=4$) segments with similarity score threshold.
     3. **Guardrail:** If no chunks meet threshold, return immediate structured response: `"I do not have enough verified NCPOR polar research records to answer this question."` with empty sources.
     4. If context found: Assemble strict grounding system prompt.
     5. Call LLM to return a strict JSON schema:
        ```json
        {
          "detailedAnswer": "...",
          "simplifiedAnswer": "...",
          "usedSourceIds": ["exp-43"]
        }
        ```
     6. Cross-reference `usedSourceIds` against the retrieved chunks to prevent hallucinated citations (SDD 11.3).
     7. Fetch item titles and types from PostgreSQL and return response to frontend.

### Phase 4: Outreach Studio Multi-Channel Generator
1. **Studio Job Creation (`services/studio_generator.py` & `routers/studio.py`):**
   - `POST /api/studio/jobs` (Admin-only).
   - Payload: `{ "repositoryItemId": "exp-43" }`.
   - Reads `raw_text` of the repository item.
   - Prompts the LLM Gateway in a single pass to return JSON with 6 tailored drafts:
     - `web`: Headline + long-form structured article.
     - `linkedin`: Professional executive summary with industry-relevant hashtags.
     - `instagram`: Engaging visual narrative caption with call-to-action.
     - `x`: Punchy post under 280 characters.
     - `education`: "Did You Know?" curiosity-focused framing for students.
     - `newsletter`: Digest-style paragraph with key takeaways.
   - Commits `StudioJob` (status: `Drafted`) and 6 `StudioChannelContent` records.
2. **Review & Approval Flow:**
   - `GET /api/studio/jobs` and `GET /api/studio/jobs/{id}`.
   - `PATCH /api/studio/jobs/{id}`:
     - Payload: `{ "channel": "linkedin", "editedContent": "...", "approved": true }`.
     - Updates the specific channel record.
     - Automatically verifies if all 6 channels are `approved == True`. If yes, marks `StudioJob.status = "Approved"`.

### Phase 5: Verification, Testing & Demo Script
1. **Verification Test Suite:**
   - Run live end-to-end curl/pytest script testing the core golden path:
     1. Login admin -> receive cookie.
     2. Upload expedition PDF (`FR-REP-03`).
     3. Verify `index_status == 'indexed'` (`FR-REP-04`).
     4. Query Assistant with a specific question -> verify detailed/simplified outputs and cited source (`FR-AST-01..05`).
     5. Query Assistant with out-of-domain question -> verify explicit rejection (`FR-AST-06`).
     6. Create Studio job -> verify 6 drafts populated (`FR-STU-01..02`).
     7. Approve 5 channels -> verify job is still `Review`. Approve 6th channel -> verify status changes to `Approved` (`FR-STU-04`).
     8. Submit quiz answers -> verify scoring and corrections (`FR-LRN-04`).