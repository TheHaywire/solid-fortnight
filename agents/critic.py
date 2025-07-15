from .base import BaseAgent
from gemini_api import GeminiAPI
import json

class CriticAgent(BaseAgent):
    def __init__(self, name, gemini=None):
        super().__init__(name)
        self.gemini = gemini or GeminiAPI()

    def run(self, code, purpose):
        prompt = (
            "You are a world-class code reviewer. "
            "Given the following code and its intended purpose, review it for correctness, style, and best practices. "
            "Return a JSON object with 'issues', 'suggestions', and 'overall_rating'.\n"
            f"Code:\n{code}\nPurpose: {purpose}"
        )
        response = self.gemini.call(prompt, modality='text')
        try:
            review = json.loads(response)
        except Exception:
            review = {'issues': response.strip(), 'suggestions': '', 'overall_rating': 'N/A'}
        return review 