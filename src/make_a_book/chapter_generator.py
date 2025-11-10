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
        # Use the same language model as the outline generator
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
            if line.startswith('Chapter') or line.startswith('chapter'):
                # Simple parsing - could be enhanced based on outline format
                if ':' in line:
                    title_part = line.split(':')[0].strip()
                    description_part = line.split(':', 1)[1].strip()
                    chapters.append((title_part, description_part))
                else:
                    chapters.append((line, ""))
        
        return chapters