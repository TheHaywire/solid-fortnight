from .base import BaseAgent
from gemini_api import GeminiAPI
import re

class DebuggerAgent(BaseAgent):
    def __init__(self, name, gemini=None):
        super().__init__(name)
        self.gemini = gemini or GeminiAPI()

    def run(self, code, test_results):
        prompt = (
            "You are a world-class debugging expert. "
            "Given the following code and error message, suggest a corrected version of the code. "
            "Return ONLY the corrected code in a markdown code block.\n"
            f"Code:\n{code}\n"
            f"Error: {test_results['details']}"
        )
        response = self.gemini.call(prompt, modality='text')
        match = re.search(r'```(?:[a-zA-Z]+)?\n([\s\S]+?)```', response)
        if match:
            fix = match.group(1).strip()
        else:
            fix = response.strip()
        return fix
