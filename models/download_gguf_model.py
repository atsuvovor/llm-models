# models/download_gguf_model.py

import os
import requests

def download_gguf_model(url: str, path: str, progress_callback=None):
    if os.path.exists(path):
        return "✅ Model already exists."

    os.makedirs(os.path.dirname(path), exist_ok=True)
    response = requests.get(url, stream=True)

    if response.status_code != 200:
        return f"❌ Failed to download model. Status code: {response.status_code}"

    total_size = int(response.headers.get('content-length', 0))
    block_size = 8192# 2024
    downloaded_size = 0

    with open(path, 'wb') as file:
        for data in response.iter_content(block_size):
            file.write(data)
            downloaded_size += len(data)
            if progress_callback:
                progress_callback(min(downloaded_size / total_size, 1.0))

    return f"✅ Download complete: {os.path.basename(path)}"

