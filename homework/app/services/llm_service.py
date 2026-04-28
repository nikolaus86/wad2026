from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings


class LLMService:
    def __init__(self):
        self.settings = get_settings()
        self._llm = get_llm()

    def answer(self, user_input: str) -> str:
        if self._llm is None:
            return (
                "Demo answer: local GGUF model is not installed. "
                "Place model.gguf in the homework folder and set LLM_MODEL_PATH to enable llama-cpp inference. "
                f"Your question was: {user_input}"
            )

        prompt = f"User: {user_input}\nAssistant:"
        result = self._llm(prompt, max_tokens=self.settings.llm_max_tokens, stream=False)
        return result["choices"][0]["text"].strip()


@lru_cache
def get_llm():
    settings = get_settings()
    model_path = Path(settings.llm_model_path)
    if not model_path.exists():
        return None

    from llama_cpp import Llama

    return Llama(model_path=str(model_path), n_ctx=1024, n_threads=4)
