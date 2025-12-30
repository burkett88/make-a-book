# Book Foundry

A professional, editorial-style web app for generating book outlines, chapters, and audiobook previews using AI.

## Stack
- Frontend: React + Vite (in `frontend/`)
- Backend: FastAPI (in `api.py`)
- Text generation: Anthropic via DSPy
- Audio: OpenAI TTS

## Run Locally
From the repo root:

Backend
```sh
uv sync
uv run uvicorn api:app --reload
```

Frontend
```sh
cd frontend
npm install
npm run dev
```

The frontend expects the API at `http://localhost:8000`. Override with `VITE_API_URL` if needed.

## Environment Variables
Create a `.env` file in the repo root:
```
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

## Fly.io Deployment (scale to zero)
This repo includes a Dockerfile and `fly.toml` configured for Fly Machines auto start/stop.

```sh
fly launch --no-deploy
fly secrets set ANTHROPIC_API_KEY=... OPENAI_API_KEY=...
fly deploy
```

Update `app` in `fly.toml` if you need a different Fly app name.

## API Endpoints
- `GET /api/health` health check
- `POST /api/outline` generate outline
- `POST /api/outline/feedback` regenerate outline with feedback
- `POST /api/chapters` generate chapters from outline
- `POST /api/voice/preview` generate a voice preview MP3
- `POST /api/audiobook` generate audiobook assets (blocking)
- `POST /api/audiobook/start` start audiobook generation job
- `GET /api/audiobook/status/{job_id}` check audiobook job progress/result

## Notes
- Chapter parsing expects outline lines starting with “Chapter …” (markdown headings and list prefixes are supported).
