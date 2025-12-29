import os
import openai
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import re
from typing import List, Tuple
import time

load_dotenv()

class AudiobookGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis."""
        # Remove markdown formatting
        text = re.sub(r'#{1,6}\s*', '', text)  # Headers
        text = re.sub(r'\*{1,2}([^\*]+)\*{1,2}', r'\1', text)  # Bold/italic
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Code
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
        
        # Clean up extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines
        text = re.sub(r'\s{2,}', ' ', text)  # Multiple spaces
        
        return text.strip()
    
    def chunk_text(self, text: str, max_chars: int = 4000) -> List[str]:
        """Split text into chunks suitable for TTS API limits."""
        text = self.clean_text_for_speech(text)
        
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        sentences = re.split(r'[.!?]+\s+', text)
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) <= max_chars:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks
    
    def create_book_folder(self, book_title: str) -> Path:
        """Create a folder for the book with all content."""
        folder_name = f"{book_title.replace(' ', '_').lower()}_complete"
        book_folder = Path(folder_name)
        book_folder.mkdir(exist_ok=True)
        
        # Create subfolders
        (book_folder / "audio").mkdir(exist_ok=True)
        (book_folder / "text").mkdir(exist_ok=True)
        
        return book_folder
    
    def generate_chapter_audio(self, chapter_text: str, chapter_num: int, 
                             book_folder: Path, voice: str = "alloy", 
                             speed: float = 1.0, voice_instructions: str = None) -> str:
        """Generate audio for a single chapter."""
        chunks = self.chunk_text(chapter_text)
        audio_files = []
        
        # Default child-friendly instructions
        default_instructions = ("Read with excitement and enthusiasm! You're a friendly storyteller reading to children. Use varied intonation, dramatic pauses for suspense, and express emotions clearly. Make it engaging and fun!")
        instructions = voice_instructions if voice_instructions else default_instructions
        
        for i, chunk in enumerate(chunks):
            chunk_filename = book_folder / "audio" / f"chapter_{chapter_num:02d}_part_{i+1:02d}.mp3"
            
            try:
                # Prepare API parameters
                api_params = {
                    "model": "gpt-4o-mini-tts",
                    "voice": voice,
                    "input": chunk,
                    "speed": speed
                }
                
                # Add instructions if provided
                if instructions:
                    api_params["instructions"] = instructions
                
                response = self.client.audio.speech.create(**api_params)
                
                response.stream_to_file(chunk_filename)
                audio_files.append(chunk_filename)
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error generating audio for chapter {chapter_num}, chunk {i+1}: {e}")
                continue
        
        # If multiple chunks, combine them into one chapter file
        if len(audio_files) > 1:
            chapter_filename = book_folder / "audio" / f"chapter_{chapter_num:02d}.mp3"
            self._combine_audio_files(audio_files, chapter_filename)
            
            # Clean up chunk files
            for file in audio_files:
                file.unlink()
                
            return str(chapter_filename)
        elif len(audio_files) == 1:
            # Rename single file to chapter format
            chapter_filename = book_folder / "audio" / f"chapter_{chapter_num:02d}.mp3"
            audio_files[0].rename(chapter_filename)
            return str(chapter_filename)
        
        return None
    
    def _combine_audio_files(self, audio_files: List[Path], output_file: Path):
        """Combine multiple audio files into one using pydub."""
        try:
            from pydub import AudioSegment
            
            combined = AudioSegment.empty()
            for file in audio_files:
                if file.exists():
                    audio = AudioSegment.from_mp3(file)
                    combined += audio
                    combined += AudioSegment.silent(duration=500)  # 500ms pause between chunks
            
            combined.export(output_file, format="mp3")
            
        except ImportError:
            print("pydub not available, keeping separate chunk files")
            # If pydub fails, just use the first chunk
            if audio_files and audio_files[0].exists():
                audio_files[0].rename(output_file)
    
    def save_text_content(self, book_title: str, outline: str, chapters: List[str], 
                         book_folder: Path):
        """Save all text content to the book folder."""
        # Save full book
        full_book = f"# {book_title}\n\n## Outline\n\n{outline}\n\n## Chapters\n\n"
        for i, chapter in enumerate(chapters, 1):
            full_book += f"### Chapter {i}\n\n{chapter}\n\n"
        
        (book_folder / "text" / f"{book_title.replace(' ', '_').lower()}_complete.md").write_text(
            full_book, encoding='utf-8'
        )
        
        # Save individual chapters
        for i, chapter in enumerate(chapters, 1):
            chapter_file = book_folder / "text" / f"chapter_{i:02d}.md"
            chapter_file.write_text(f"# Chapter {i}\n\n{chapter}", encoding='utf-8')
        
        # Save outline
        (book_folder / "text" / "outline.md").write_text(
            f"# {book_title} - Outline\n\n{outline}", encoding='utf-8'
        )
    
    def generate_audiobook(self, book_title: str, outline: str, chapters: List[str],
                          voice: str = "alloy", speed: float = 1.0, 
                          include_outline: bool = True, voice_instructions: str = None) -> Tuple[str, List[str]]:
        """Generate complete audiobook with organized folder structure."""
        
        # Create book folder
        book_folder = self.create_book_folder(book_title)
        
        # Save all text content
        self.save_text_content(book_title, outline, chapters, book_folder)
        
        audio_files = []
        
        # Generate outline audio if requested
        if include_outline:
            outline_audio = self.generate_chapter_audio(
                f"Book Outline. {outline}", 0, book_folder, voice, speed, voice_instructions
            )
            if outline_audio:
                # Rename to outline
                outline_path = book_folder / "audio" / "00_outline.mp3"
                Path(outline_audio).rename(outline_path)
                audio_files.append(str(outline_path))
        
        # Generate chapter audio (first chapter only for now)
        if chapters:
            chapter_audio = self.generate_chapter_audio(
                chapters[0], 1, book_folder, voice, speed, voice_instructions
            )
            if chapter_audio:
                audio_files.append(chapter_audio)
        
        return str(book_folder), audio_files
