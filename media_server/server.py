import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# Simple local media server to serve dataset images separately from the backend
# Usage: set MEDIA_DATASET_DIR env var to the dataset root containing train_images/ and test_images/
# Default assumes repo layout: ../dataset/shopee-product-matching

app = FastAPI(title="Local Media Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_DATASET = os.path.join(ROOT, 'dataset', 'shopee-product-matching')
DATASET_DIR = os.environ.get('MEDIA_DATASET_DIR', DEFAULT_DATASET)

@app.get('/health')
async def health():
    return {"status": "ok", "dataset_dir": DATASET_DIR}

@app.get('/{folder}/{name}')
async def get_image(folder: str, name: str):
    if folder not in {"train_images", "test_images"}:
        return JSONResponse({"error": "invalid folder"}, status_code=404)
    path = os.path.join(DATASET_DIR, folder, name)
    if not os.path.exists(path):
        return JSONResponse({"error": "not found"}, status_code=404)
    import mimetypes
    mt = mimetypes.guess_type(path)[0] or 'image/jpeg'
    return FileResponse(path, media_type=mt)
