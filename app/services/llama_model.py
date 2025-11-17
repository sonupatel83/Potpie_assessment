import llama_model
from ..config import Config

class llama_modelService:
    def __init__(self):
        llama_model.api_key = Config.llama_model_API_KEY

    def generate_text(self, prompt, model="text-davinci-003", max_tokens=150):
        response = llama_model.Completion.create(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens
        )
        return response.choices[0].text.strip()
