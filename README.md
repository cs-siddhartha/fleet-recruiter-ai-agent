# Fleet Recruiter AI Agent

AI recruiter app for evaluating a PDF resume against a backend-owned job description.

Python lives at the repository root and is managed with `uv`. The TanStack Start frontend lives in `ui/`.

## Environment

Create a root `.env` file:

```env
OPENAI_API_KEY=your_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
REDIS_URL=redis://localhost:6379/0
MEMORY_NAMESPACE=fleet-recruiter
MEMORY_TOP_K=5
MEMORY_SEMANTIC_WEIGHT=0.6
MEMORY_LEXICAL_WEIGHT=0.4
SEMANTIC_CHUNK_SIMILARITY_THRESHOLD=0.72
SEMANTIC_CHUNK_MAX_CHARS=1800
```

Redis will hold persisted memory chunks and metadata. FAISS will provide semantic
vector search, while BM25 will provide lexical text search. The two result sets
will be fused into one ranked memory lookup in a later implementation increment.

## Backend

```sh
uv run uvicorn fleet_recruiter_ai_agent.api.app:app --reload
```

The backend exposes job catalog and evaluation endpoints under `/api`. Jobs are seeded in Python; users do not submit JDs. The recruiter runs as an OpenAI tool-calling agent after PDF parsing.

## Frontend

```sh
cd ui
npm run dev
```

The frontend shows jobs, lets a user upload a PDF resume, polls evaluation status, and renders the scorecard. In dev, `/api` is proxied to the FastAPI backend on port `8000`.
By default the UI calls `http://127.0.0.1:8000`; override with `VITE_API_BASE_URL` if needed.

## Flow

```mermaid
sequenceDiagram
    participant User as User
    participant UI as TanStack Frontend
    participant API as FastAPI Backend
    participant Store as In-Memory Store
    participant PDF as PyMuPDF4LLM
    participant LLM as OpenAI
    participant GH as GitHub Public API

    User->>UI: Open app
    UI->>API: GET /api/jobs
    API-->>UI: Seeded jobs
    User->>UI: Click job
    UI->>API: GET /api/jobs/:job_id
    API-->>UI: Job detail + JD

    User->>UI: Upload PDF resume
    UI->>API: POST /api/jobs/:job_id/evaluations
    API->>Store: Create pending evaluation
    API-->>UI: evaluation_id

    API->>PDF: Extract resume markdown
    PDF-->>API: Parsed resume text
    API->>Store: Save parsed resume text

    API->>LLM: Start recruiter agent with tool definitions
    LLM->>API: tool_call analyze_jd
    API-->>LLM: JDAnalysis
    LLM->>API: tool_call analyze_resume
    API-->>LLM: ResumeAnalysis
    LLM->>API: tool_call enrich_github_profiles
    API->>GH: Fetch public GitHub profile/repo signals
    GH-->>API: Profile + repository signals
    API-->>LLM: GitHub signals
    LLM->>API: tool_call evaluate_scorecard
    API-->>LLM: CandidateScorecard
    LLM-->>API: CandidateScorecard
    API->>Store: Save completed evaluation

    loop Poll status
        UI->>API: GET /api/evaluations/:evaluation_id
        API->>Store: Read evaluation
        Store-->>API: Status or result
        API-->>UI: EvaluationRecord
    end

    UI-->>User: Render scorecard
```
