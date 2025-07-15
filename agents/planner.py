from .base import BaseAgent
from gemini_api import GeminiAPI

class PlannerAgent(BaseAgent):
    def __init__(self, name, gemini=None):
        super().__init__(name)
        self.gemini = gemini or GeminiAPI()

    def run(self, user_request):
        prompt = (
            "You are a senior software architect. "
            "Break down the following user request into clear, actionable subtasks, one per line. "
            "User request: " + user_request
        )
        response = self.gemini.call(prompt, modality='text')
        # Split response into lines and clean up
        subtasks = [line.strip('- ').strip() for line in response.split('\n') if line.strip()]
        return subtasks
