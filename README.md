# Fleet Recruiter AI Agent

Python lives at the repository root and is managed with `uv`. The TanStack Start frontend lives in `ui/`.

## Backend

```sh
uv run fleet-recruiter-ai-agent
```

The current backend scaffold includes Pydantic models for candidate/job-fit validation and Pydantic settings support via `FLEET_` environment variables.

## Frontend

```sh
cd ui
npm run dev
```

The frontend was initialized from TanStack Start's official React `start-basic` example.
