# models/llm_loader.py

import os
import torch
from transformers import pipeline
from langchain_community.llms import OpenAI, HuggingFacePipeline, CTransformers
from ai_agent.config import Settings
from models.download_gguf_model import download_gguf_model
from ctransformers import AutoModelForCausalLM  # if needed elsewhere

def detect_gpu_layers():
    """Basic GPU availability logic for quantized models."""
    if torch.cuda.is_available():
        return 50  # example default for 7B model
    return 0  # fallback to CPU-only

def load_llm(model_path: str = None, backend: str = None):
    try:
        backend = backend or Settings.llm_backend

        if backend == "openai":
            return OpenAI(
                model_name=Settings.openai_model,
                temperature=0.3
            )

        elif backend == "huggingface":
            pipe = pipeline(
                "text-generation",
                model=Settings.hf_model_name,
                max_new_tokens=256,
                device_map="auto",
                use_auth_token=Settings.hf_auth_token
            )
            return HuggingFacePipeline(pipeline=pipe)

        elif backend == "ctransformers":
            model_path = model_path or Settings.gguf_model_path
            if not os.path.exists(model_path):
                print(f"⚠️ Model not found at {model_path}. Attempting auto-download...")
                model_path = download_gguf_model()

            return CTransformers(
                model=model_path,
                model_type=Settings.gguf_model_type,
                config={
                    'max_new_tokens': 256,
                    'temperature': 0.3,
                    'gpu_layers': detect_gpu_layers()
                }
            )

        else:
            raise ValueError(f"Unsupported LLM backend: {backend}")

    except Exception as e:
        raise RuntimeError(f"❌ Failed to load LLM: {e}")
