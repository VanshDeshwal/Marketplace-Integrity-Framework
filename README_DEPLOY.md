# Deployment and Media Architecture

This project splits concerns so the backend doesn’t serve images. Images and thumbnails are read directly by the browser from a media origin. The API returns `image_key` and (when configured) `image_url` to point clients to media.

## Components

- Frontend (static): GitHub Pages at https://marketplace.vanshdeshwal.dev
- Backend (API): Azure Web App at https://api.marketplace.vanshdeshwal.dev
- Media (images):
  - Production: Azure Blob Storage with a CDN/custom domain, e.g. https://assets.marketplace.vanshdeshwal.dev
  - Local dev: standalone FastAPI media server (see below) or fallback to backend `/image/{idx}`

## Environment variables

Backend:
- `MEDIA_BASE_URL` (optional): when set, API adds `image_url` alongside `image_key` for results. Example: `https://assets.marketplace.vanshdeshwal.dev`.

Frontend:
- Automatically detects local vs hosted.
  - Hosted: uses `https://api.marketplace.vanshdeshwal.dev` and `https://assets.marketplace.vanshdeshwal.dev`.
  - Local: uses `http://localhost:8000` for API and tries `mediaBase` from localStorage for media; otherwise falls back to `/image/{idx}` API.
- To override media base locally: open devtools console and run `localStorage.setItem('mediaBase','http://localhost:9000')` then refresh.

## Azure Blob + CDN setup (prod)

1) Create a Storage Account (RA-GRS suggested). Enable static website or use Blob service endpoints.
2) Create a container, e.g. `catalog` (private or public; if private you’ll need SAS tokens or CDN with origin auth).
3) Upload `train_images/` and `test_images/` folders preserving paths.
4) Front containers: Add Azure CDN (Front Door) for performance and custom domain binding.
5) Configure custom subdomain for media. Suggested names:
   - `assets.marketplace.vanshdeshwal.dev` (generic assets)
   - `images.marketplace.vanshdeshwal.dev` (images only)
   - `media.marketplace.vanshdeshwal.dev` (broad media)
6) On the Azure Web App, set `MEDIA_BASE_URL` app setting to the media domain: `https://assets.marketplace.vanshdeshwal.dev`.

Security options:
- Public container: simplest; ensure no sensitive data.
- Private with SAS: sign URLs in a lightweight edge function or precompute short-lived SAS in API (not implemented here to keep the backend stateless for images).
- Private with CDN origin auth: recommended for prod.

## Local media server

Run a separate server to serve dataset images without going through the API. The frontend will try `localStorage.mediaBase` when running locally.

- File: `media_server/server.py`
- Default dataset root: `../dataset/shopee-product-matching`
- Override with env var `MEDIA_DATASET_DIR`

Run (example):

```powershell
# in repo root
$env:MEDIA_DATASET_DIR = "c:\Github\Project\dataset\shopee-product-matching"
python -m uvicorn media_server.server:app --reload --port 9000
```

Then in browser console:

```js
localStorage.setItem('mediaBase','http://localhost:9000')
location.reload()
```

## CI/CD overview

- Frontend: GitHub Pages uses `frontend/` content; ensure `index.html` is the entry.
- Backend: Azure Web App deploy uses `backend/`; set `MEDIA_BASE_URL` in App Settings; ensure CORS allowed origins include your Pages domain.
- Media: Upload images to Azure Blob container; configure custom domain and (optionally) CDN.

## Notes

- Fraud endpoints require a `seller_id` column in `meta.csv`. If missing, those endpoints will return an error.
- The API still exposes `/image/{idx}` as a dev fallback; in prod the frontend will use blob/CDN URLs.
