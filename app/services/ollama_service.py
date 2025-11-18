import requests
from ..config import Config
from ..logger import logging

class OllamaService:
    def __init__(self):
        self.api_url = Config.OLLAMA_API_URL
        self.model = Config.OLLAMA_MODEL

    def generate_text(self, prompt, model=None, max_tokens=None):
        """
        Generate text using Ollama API
        """
        if model is None:
            model = self.model
        
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300  # 5 minute timeout for long responses
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama API error: {e}")
            raise

    def chat(self, messages, model=None):
        """
        Chat completion using Ollama API
        """
        if model is None:
            model = self.model
        
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False
                },
                timeout=300
            )
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "").strip()
        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama API error: {e}")
            raise

    def analyze_code(self, file_name, content):
        """
        Analyze code using Ollama
        """
        prompt = f"""Analyze the following GitHub Pull Request file for potential issues:
File Name: {file_name}
Content:
{content}

Please provide:
1. Code style issues
2. Potential bugs
3. Performance improvements
4. Best practices recommendations
"""
        return self.generate_text(prompt)

