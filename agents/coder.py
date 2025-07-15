from .base import BaseAgent
from gemini_api import GeminiAPI
import re

class CoderAgent(BaseAgent):
    def __init__(self, name, gemini=None):
        super().__init__(name)
        self.gemini = gemini or GeminiAPI()

    def run(self, subtask):
        prompt = (
            "You are a world-class software engineer. "
            "Given the following task and context, write production-quality code. "
            "Return ONLY the code in a markdown code block. "
            "If the task is ambiguous, ask for clarification.\n"
            f"Task: {subtask}"
        )
        response = self.gemini.call(prompt, modality='text')
        # Extract code block
        match = re.search(r'```(?:[a-zA-Z]+)?\n([\s\S]+?)```', response)
        if match:
            code = match.group(1).strip()
        else:
            code = response.strip()
        return code
