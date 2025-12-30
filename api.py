import os
import re
import tempfile
from pathlib import Path

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

load_dotenv()

app = FastAPI(title="Book Foundry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OutlineRequest(BaseModel):
    title: str
    prompt: str


class OutlineFeedbackRequest(BaseModel):
    title: str
    prompt: str
    feedback: str


class OutlineResponse(BaseModel):
    outline: str


class ChapterRequest(BaseModel):
    title: str
    outline: str


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
        outline = outline_creator.create_outline(payload.prompt)
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
        outline = outline_creator.create_outline(updated_prompt)
        return OutlineResponse(outline=outline)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/chapters", response_model=ChapterResponse)
def generate_chapters(payload: ChapterRequest):
    if not payload.outline.strip():
        raise HTTPException(status_code=400, detail="Outline is required")

    try:
        chapters_info = chapter_creator.parse_outline_chapters(payload.outline)

        if not chapters_info:
            chapters_info = [
                ("Chapter 1: Introduction", "Introduction to the topic"),
                ("Chapter 2: Main Content", "Core content and concepts"),
                ("Chapter 3: Conclusion", "Summary and final thoughts"),
            ]

        chapters: list[str] = []
        for title, description in chapters_info:
            chapter_content = chapter_creator.create_chapter(
                payload.outline, title, description
            )
            chapters.append(chapter_content)

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
