import dspy

class ChapterGenerator(dspy.Signature):
    """Generate detailed chapters for a book based on the outline."""
    
    book_outline: str = dspy.InputField(
        desc="The complete book outline with chapter headings and descriptions"
    )
    target_duration_minutes: int = dspy.InputField(
        desc="Target total duration in minutes for the entire book"
    )
    chapters: list[str] = dspy.OutputField(
        desc="An array of chapter contents in outline order; one string per chapter"
    )

class ChapterCreator:
    def __init__(self, lm):
        # Configure DSPy once per process to avoid cross-thread reconfiguration.
        if getattr(dspy.settings, "lm", None) is None:
            dspy.settings.configure(lm=lm)
        self.generate_chapters = dspy.Predict(ChapterGenerator)
    
    def create_chapters(self, book_outline: str, target_duration_minutes: int) -> list[str]:
        """Generate all chapters for the outline in a single call."""
        result = self.generate_chapters(
            book_outline=book_outline,
            target_duration_minutes=target_duration_minutes
        )
        chapters = result.chapters
        if chapters is None:
            return []
        if isinstance(chapters, list):
            return chapters
        if isinstance(chapters, tuple):
            return list(chapters)
        if isinstance(chapters, str):
            return [chapters]
        return [str(chapters)]
