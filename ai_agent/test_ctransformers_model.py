# test_ctransformers_model.py

from ai_agent.config import settings
from langchain_community.llms import CTransformers

def test_ctransformers_model():
    try:
        print("🔍 Loading model...")
        llm = CTransformers(
            model=settings.gguf_model_path,
            model_type=settings.gguf_model_type,
            config={"max_new_tokens": 64, "temperature": 0.3}
        )

        print("✅ Model loaded successfully.")
        prompt = "What are the benefits of AI in cybersecurity?"
        response = llm(prompt)
        print(f"\n🧠 Response:\n{response}")

    except Exception as e:
        print(f"❌ Failed to load model: {e}")

if __name__ == "__main__":
    test_ctransformers_model()
