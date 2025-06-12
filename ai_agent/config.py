# ai_agent/config.py

import os

class Settings:
    def __init__(self):
        # LLM backend
        self.llm_backend = os.getenv("LLM_BACKEND", "ctransformers")  # or "openai", "huggingface"

        # OpenAI config
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")

        # Hugging Face config
        self.hf_model_name = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        self.embedding_model = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.hf_auth_token = os.getenv("HF_AUTH_TOKEN", None)

        # GGUF model config
        self.gguf_model_dir = os.getenv("GGUF_MODEL_DIR", "models/gguf")
        self.gguf_model_type = os.getenv("GGUF_MODEL_TYPE", "mistral")

        # Ensure directory exists
        os.makedirs(self.gguf_model_dir, exist_ok=True)

        # List available GGUF models
        self.model_list = self._get_model_list()

        # Set default GGUF model path
        self.gguf_model_path = os.getenv(
            "GGUF_MODEL_PATH", 
            os.path.join(self.gguf_model_dir, self.model_list[0]) if self.model_list else ""
        )

    def _get_model_list(self):
        return [f for f in os.listdir(self.gguf_model_dir) if f.endswith(".gguf")]

    def update_selected_model(self, model_filename):
        if model_filename in self.model_list:
            self.gguf_model_path = os.path.join(self.gguf_model_dir, model_filename)
        else:
            raise ValueError(f"Selected model '{model_filename}' not found in {self.gguf_model_dir}")


# Singleton instance used across the app
Settings = Settings()
