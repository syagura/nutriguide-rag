from huggingface_hub import hf_hub_download
import os

os.makedirs("storage/vectordb", exist_ok=True)
files = ['index.faiss', 'chunks.pkl', 'bm25.pkl']
for f in files:
    hf_hub_download(
        repo_id='syahrul11/nutriguide-vectordb',
        filename=f,
        repo_type='dataset',
        local_dir='storage/vectordb',
    )

print('Vector files downloaded successfully!')