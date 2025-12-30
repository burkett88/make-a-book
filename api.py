import os
import re
import tempfile
import time
import uuid
from pathlib import Path
from threading import Lock

import dspy
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

from src.make_a_book.audiobook_generator import AudiobookGenerator
from src.make_a_book.chapter_generator import ChapterCreator
from src.make_a_book.outline_generator import OutlineCreator
from src.make_a_book.tts_time_estimator import count_words, estimate_tts_seconds

load_dotenv()

app = FastAPI(title="Book Foundry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

audiobook_jobs: dict[str, dict] = {}
audiobook_jobs_lock = Lock()


class OutlineRequest(BaseModel):
    title: str
    prompt: str
    target_duration_minutes: int = 5


class OutlineFeedbackRequest(BaseModel):
    title: str
    prompt: str
    feedback: str
    target_duration_minutes: int = 5


class OutlineResponse(BaseModel):
    outline: str


class ChapterRequest(BaseModel):
    title: str
    outline: str
    target_duration_minutes: int = 5


class ChapterResponse(BaseModel):
    chapters: list[str]


class VoicePreviewRequest(BaseModel):
    voice: str
    speed: float
    instructions: str | None = None
    text: str


class AudiobookRequest(BaseModel):
    title: str
    outline: str
    chapters: list[str]
    voice: str
    speed: float
    include_outline: bool = True
    instructions: str | None = None


class AudiobookResponse(BaseModel):
    folder: str
    audio_files: list[str]


class AudiobookJobResponse(BaseModel):
    job_id: str
    total_chapters: int


class AudiobookStatusResponse(BaseModel):
    status: str
    progress: int
    completed_chapters: int
    total_chapters: int
    elapsed_seconds: int | None = None
    estimated_seconds: int | None = None
    result: AudiobookResponse | None = None
    error: str | None = None

anthropic_lm = dspy.LM(
    model="anthropic/claude-haiku-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)
outline_creator = OutlineCreator(anthropic_lm)
chapter_creator = ChapterCreator(anthropic_lm)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/outline", response_model=OutlineResponse)
def generate_outline(payload: OutlineRequest):
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")

    try:
        outline = outline_creator.create_outline(
            payload.prompt,
            payload.target_duration_minutes,
        )
        return OutlineResponse(outline=outline)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/outline/feedback", response_model=OutlineResponse)
def regenerate_outline(payload: OutlineFeedbackRequest):
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")

    if not payload.feedback.strip():
        raise HTTPException(status_code=400, detail="Feedback is required")

    try:
        updated_prompt = f"{payload.prompt}\n\nUser feedback: {payload.feedback}"
        outline = outline_creator.create_outline(
            updated_prompt,
            payload.target_duration_minutes,
        )
        return OutlineResponse(outline=outline)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/chapters", response_model=ChapterResponse)
def generate_chapters(payload: ChapterRequest):
    if not payload.outline.strip():
        raise HTTPException(status_code=400, detail="Outline is required")

    try:
        chapters = chapter_creator.create_chapters(
            payload.outline,
            payload.target_duration_minutes,
        )
        if not chapters:
            raise HTTPException(status_code=500, detail="No chapters were generated")

        return ChapterResponse(chapters=chapters)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


def _extract_preview_text(text: str) -> str:
    cleaned_text = re.sub(r'#{1,6}\s*', '', text)
    paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip()]
    preview_text = paragraphs[0] if paragraphs else cleaned_text.strip()

    if len(preview_text) > 300:
        sentences = preview_text.split('. ')
        preview_text = '. '.join(sentences[:3]).strip()
        if preview_text and not preview_text.endswith('.'):
            preview_text += '.'

    return preview_text or "This is a preview of the selected voice."


def _update_audiobook_job(job_id: str, **updates: object) -> None:
    with audiobook_jobs_lock:
        job = audiobook_jobs.get(job_id)
        if job is None:
            return
        job.update(updates)


def _run_audiobook_job(job_id: str, payload: AudiobookRequest) -> None:
    _update_audiobook_job(job_id, status="running", started_at=time.time())

    def progress_callback(**kwargs: object) -> None:
        completed = 0
        total = 0
        stage = kwargs.get("stage")
        if stage == "chapter":
            completed = int(kwargs.get("chapter_index", 0))
            total = int(kwargs.get("total_chapters", 0))
        elif stage == "chunk":
            chapter_index = int(kwargs.get("chapter_index", 0))
            completed = max(0, chapter_index - 1)
            with audiobook_jobs_lock:
                total = int(audiobook_jobs.get(job_id, {}).get("total_chapters", 0))
        progress = int(round((completed / total) * 100)) if total else 0
        _update_audiobook_job(
            job_id,
            progress=progress,
            completed_chapters=completed,
            total_chapters=total,
        )

    try:
        audiobook_gen = AudiobookGenerator()
        folder, audio_files = audiobook_gen.generate_audiobook(
            book_title=payload.title,
            outline=payload.outline,
            chapters=payload.chapters,
            voice=payload.voice,
            speed=payload.speed,
            include_outline=payload.include_outline,
            voice_instructions=payload.instructions,
            progress_callback=progress_callback,
        )
        _update_audiobook_job(
            job_id,
            status="completed",
            progress=100,
            completed_at=time.time(),
            result={"folder": folder, "audio_files": audio_files},
        )
    except Exception as exc:
        _update_audiobook_job(job_id, status="error", error=str(exc))


@app.post("/api/voice/preview")
def voice_preview(payload: VoicePreviewRequest, background_tasks: BackgroundTasks):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Preview text is required")

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not configured")

    preview_text = _extract_preview_text(payload.text)

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        api_params = {
            "model": "gpt-4o-mini-tts",
            "voice": payload.voice,
            "input": preview_text,
            "speed": payload.speed,
        }
        if payload.instructions and payload.instructions.strip():
            api_params["instructions"] = payload.instructions

        response = client.audio.speech.create(**api_params)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            response.stream_to_file(temp_file.name)
            temp_path = temp_file.name

        background_tasks.add_task(os.unlink, temp_path)
        return FileResponse(temp_path, media_type="audio/mpeg", filename="preview.mp3")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/audiobook/start", response_model=AudiobookJobResponse)
def start_audiobook_job(payload: AudiobookRequest, background_tasks: BackgroundTasks):
    if not payload.chapters:
        raise HTTPException(status_code=400, detail="Chapters are required")

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not configured")

    job_id = uuid.uuid4().hex
    total_chapters = len(payload.chapters)
    text_for_estimate = " ".join(payload.chapters)
    if payload.include_outline:
        text_for_estimate = f"{payload.outline} {text_for_estimate}"
    word_count = count_words(text_for_estimate)
    estimated_seconds = estimate_tts_seconds(word_count, payload.speed)

    with audiobook_jobs_lock:
        audiobook_jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "completed_chapters": 0,
            "total_chapters": total_chapters,
            "estimated_seconds": estimated_seconds,
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
        }

    background_tasks.add_task(_run_audiobook_job, job_id, payload)
    return AudiobookJobResponse(job_id=job_id, total_chapters=total_chapters)


@app.get("/api/audiobook/status/{job_id}", response_model=AudiobookStatusResponse)
def audiobook_job_status(job_id: str):
    with audiobook_jobs_lock:
        job = audiobook_jobs.get(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Audiobook job not found")

    elapsed_seconds = None
    estimated_seconds = job.get("estimated_seconds")
    if job.get("started_at"):
        end_time = job.get("completed_at") or time.time()
        elapsed_seconds = int(max(0, end_time - job["started_at"]))

    progress = job.get("progress", 0)
    if job.get("status") == "running" and estimated_seconds:
        progress = min(99, int(round((elapsed_seconds or 0) / estimated_seconds * 100)))
    if job.get("status") == "completed":
        progress = 100

    response = dict(job)
    response["progress"] = progress
    response["elapsed_seconds"] = elapsed_seconds
    response["estimated_seconds"] = estimated_seconds
    return AudiobookStatusResponse(**response)


@app.post("/api/audiobook", response_model=AudiobookResponse)
def generate_audiobook(payload: AudiobookRequest):
    if not payload.chapters:
        raise HTTPException(status_code=400, detail="Chapters are required")

    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not configured")

    try:
        audiobook_gen = AudiobookGenerator()
        folder, audio_files = audiobook_gen.generate_audiobook(
            book_title=payload.title,
            outline=payload.outline,
            chapters=payload.chapters,
            voice=payload.voice,
            speed=payload.speed,
            include_outline=payload.include_outline,
            voice_instructions=payload.instructions,
        )
        return AudiobookResponse(folder=folder, audio_files=audio_files)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


frontend_dist = Path(__file__).resolve().parent / "frontend" / "dist"
if frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
