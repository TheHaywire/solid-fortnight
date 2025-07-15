from .base import BaseAgent
from gemini_api import GeminiAPI

class ResearchAgent(BaseAgent):
    def __init__(self, name, web_search_func, gemini=None):
        super().__init__(name)
        self.web_search_func = web_search_func
        self.gemini = gemini or GeminiAPI()

    def run(self, query):
        # Use the web_search_func to get search results
        search_results = self.web_search_func(query)
        # Summarize findings and recommend open-source solutions using Gemini
        prompt = (
            "You are a world-class technical researcher and solution finder. "
            "Given the following web search results, do the following as markdown:\n"
            "1. Summarize the most relevant findings, best practices, and actionable insights as bullet points.\n"
            "2. In a 'Recommendations' section, list the top open-source libraries, tools, or repositories for the task, with install commands and links.\n"
            f"Web search results:\n{search_results}\n"
            f"Query: {query}"
        )
        summary = self.gemini.call(prompt, modality='text')
        return summary

    def fetch_and_install(self, recommendation):
        # Stub: To be implemented by DeploymentAgent
        pass 