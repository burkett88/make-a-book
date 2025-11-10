import os
import dspy
from dotenv import load_dotenv

load_dotenv()

class BookOutlineGenerator(dspy.Signature):
    """Generate a comprehensive book outline from a given prompt or topic."""
    
    prompt = dspy.InputField(desc="The book topic, theme, or initial prompt")
    outline = dspy.OutputField(desc="A detailed book outline with chapters and key points")

class OutlineCreator:
    def __init__(self):
        # Configure DSPy with Anthropic
        anthropic_lm = dspy.LM(
            model="anthropic/claude-sonnet-4-5-20250929",
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        dspy.settings.configure(lm=anthropic_lm)
        
        # Initialize the predictor
        self.generate_outline = dspy.Predict(BookOutlineGenerator)
    
    def create_outline(self, prompt: str) -> str:
        """Generate a book outline from the given prompt."""
        result = self.generate_outline(prompt=prompt)
        return result.outline