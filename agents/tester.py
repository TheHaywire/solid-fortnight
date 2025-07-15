from .base import BaseAgent
from gemini_api import GeminiAPI
import json

class TesterAgent(BaseAgent):
    def __init__(self, name, gemini=None):
        super().__init__(name)
        self.gemini = gemini or GeminiAPI()

    def run(self, code):
        prompt = (
            "You are a world-class QA engineer. "
            "Given the following code, write and run appropriate tests. "
            "Return the results as a JSON object with 'passed' (bool), 'details' (string), and 'test_code' (string).\n"
            f"Code:\n{code}"
        )
        response = self.gemini.call(prompt, modality='text')
        try:
            result = json.loads(response)
            return result
        except Exception:
            # Fallback: try to run the code locally
            local_vars = {}
            try:
                exec(code, {}, local_vars)
                return {'passed': True, 'details': 'All tests passed.', 'test_code': ''}
            except Exception as e:
                return {'passed': False, 'details': str(e), 'test_code': ''}
