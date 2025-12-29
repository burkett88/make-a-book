import os
import dspy
from dotenv import load_dotenv

load_dotenv()

class BookOutlineGenerator(dspy.Signature):
    """Generate a comprehensive book outline from a given prompt or topic."""
    
    prompt = dspy.InputField(desc="The book topic, theme, or initial prompt")
    outline = dspy.OutputField(desc="A detailed book outline with chapters and key points")

class OutlineCreator:
    def __init__(self, lm=None):
        # Configure DSPy once per process to avoid cross-thread reconfiguration.
        if lm is None:
            lm = dspy.LM(
                model="anthropic/claude-haiku-4-5",
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        if getattr(dspy.settings, "lm", None) is None:
            dspy.settings.configure(lm=lm)

        # Initialize the predictor
        self.generate_outline = dspy.Predict(BookOutlineGenerator)
    
    def create_outline(self, prompt: str) -> str:
        """Generate a book outline from the given prompt."""
        result = self.generate_outline(prompt=prompt)
        return result.outline
