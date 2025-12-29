import dspy
from typing import List

class ChapterGenerator(dspy.Signature):
    """Generate a detailed chapter for a book based on the outline and chapter topic."""
    
    book_outline = dspy.InputField(desc="The complete book outline")
    chapter_title = dspy.InputField(desc="The title of the chapter to generate")
    chapter_description = dspy.InputField(desc="Brief description of what this chapter should cover")
    chapter = dspy.OutputField(desc="A complete, well-written chapter with detailed content")

class ChapterCreator:
    def __init__(self, lm):
        # Configure DSPy once per process to avoid cross-thread reconfiguration.
        if getattr(dspy.settings, "lm", None) is None:
            dspy.settings.configure(lm=lm)
        self.generate_chapter = dspy.Predict(ChapterGenerator)
    
    def create_chapter(self, book_outline: str, chapter_title: str, chapter_description: str) -> str:
        """Generate a detailed chapter based on the outline and chapter information."""
        result = self.generate_chapter(
            book_outline=book_outline,
            chapter_title=chapter_title,
            chapter_description=chapter_description
        )
        return result.chapter
    
    def parse_outline_chapters(self, outline: str) -> List[tuple]:
        """Extract chapter titles and descriptions from the outline."""
        lines = outline.split('\n')
        chapters = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Normalize markdown headings or list prefixes.
            normalized = line.lstrip('#').strip()
            normalized = normalized.lstrip('-*0123456789. ').strip()

            if normalized.lower().startswith('chapter'):
                if ':' in normalized:
                    description_part = normalized.split(':', 1)[1].strip()
                    chapters.append((normalized, description_part))
                else:
                    chapters.append((normalized, ""))
        
        return chapters
