from .base import BaseAgent
from gemini_api import GeminiAPI

class DocumenterAgent(BaseAgent):
    def __init__(self, name, gemini=None):
        super().__init__(name)
        self.gemini = gemini or GeminiAPI()

    def run(self, code):
        prompt = (
            "You are a world-class technical writer. "
            "Given the following code, generate clear, professional documentation, including usage examples if appropriate. "
            "Return the documentation as markdown text.\n"
            f"Code:\n{code}"
        )
        docs = self.gemini.call(prompt, modality='text')
        return docs
