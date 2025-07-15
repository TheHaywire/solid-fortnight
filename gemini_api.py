import os
from dotenv import load_dotenv
import requests

load_dotenv()

class GeminiAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    def call(self, prompt, modality='text'):
        if not self.api_key:
            # Fallback to stub if no API key
            return f"[Gemini {modality} response to: {prompt}]"
        if modality == 'text':
            return self._call_text(prompt)
        # Add other modalities as needed
        return f"[Gemini {modality} response to: {prompt}]"

    def _call_text(self, prompt):
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            # Parse Gemini's response format
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"[Gemini API error: {e}]"
