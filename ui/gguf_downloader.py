# ui/guf_downloader.py 

import os
import streamlit as st
from models.download_gguf_model import download_gguf_model

def render_gguf_model_downloader(settings):
    st.sidebar.header("⬇️ GGUF Model Downloader")

    # Predefined HuggingFace-hosted GGUF model files
    predefined_models = {
        "mistral-7b-instruct-v0.2.Q4_K_M.gguf": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "llama-2-7b-chat.Q4_K_M.gguf": "https://huggingface.co/TheBloke/LLaMa-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf",
        "mixtral-8x7b-instruct.Q5_K_M.gguf": "https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-GGUF/resolve/main/mixtral-8x7b-instruct.Q5_K_M.gguf",
    }

    model_choice = st.sidebar.selectbox(
        "Select or enter a .gguf model filename",
        options=list(predefined_models.keys()) + ["Other (manual entry)"]
    )

    custom_model_name = ""
    model_url = ""
    is_ready = False

    if model_choice == "Other (manual entry)":
        custom_model_name = st.sidebar.text_input("Enter GGUF filename (e.g., custom-model.Q4_K_M.gguf)")
        model_url = st.sidebar.text_input("Paste direct download URL")
        is_ready = bool(custom_model_name and model_url)
    else:
        custom_model_name = model_choice
        model_url = predefined_models[model_choice]
        is_ready = True

    # Download trigger
    if st.sidebar.button("⬇️ Download Selected GGUF Model") and is_ready:
        model_path = os.path.join(settings.gguf_model_dir, custom_model_name)
        st.sidebar.info(f"Downloading `{custom_model_name}`...")

        progress_bar = st.sidebar.progress(0.0)

        def update_progress(p):
            progress_bar.progress(p)

        status = download_gguf_model(model_url, model_path, progress_callback=update_progress)
        st.sidebar.success(status)

        # Refresh settings.model_list if model was new
        if custom_model_name not in settings.model_list:
            settings.model_list.append(custom_model_name)
