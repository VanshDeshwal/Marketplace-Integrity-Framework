# This file exposes an `app` object for Azure Web Apps (Python) to discover.
try:
    from app.main import app  # FastAPI instance
except Exception as e:
    # Fallback minimal app to avoid startup failure during deployment diagnostics
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/health")
    def health():
        return {"status": "fallback", "error": str(e)}
