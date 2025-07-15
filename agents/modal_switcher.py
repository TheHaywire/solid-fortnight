from .base import BaseAgent
from gemini_api import GeminiAPI

class ModalSwitcherAgent(BaseAgent):
    def __init__(self, name, gemini=None):
        super().__init__(name)
        self.gemini = gemini or GeminiAPI()

    def run(self, subtask):
        prompt = (
            "You are a world-class AI modality selector. "
            "Given the following subtask, decide if it requires text, code, image, or another modality, and return the best modality as a string.\n"
            f"Subtask: {subtask}"
        )
        response = self.gemini.call(prompt, modality='text')
        return response.strip().lower()
