Similarity-Driven E-commerce Catalog Intelligence

Local-first MVP with FastAPI backend and static HTML/CSS/JS frontend.

Run locally
- Backend: from backend/, run `uvicorn app.main:app --reload --port 8000`
- Frontend: open frontend/index.html (or serve statically)

Frontend UX
- Tabs: Duplicate, Search, Fraud
- Drag-and-drop image uploads with preview
- Alpha and Top-K controls
- API status box (top-right): green when connected, click to open /docs
- Auto-detects environment: uses http://localhost:8000 locally, https://api.marketplace.vanshdeshwal.dev when hosted

Deployment
Frontend (GitHub Pages)
- Custom domain: marketplace.vanshdeshwal.dev
- Workflow: .github/workflows/frontend-pages.yml auto-deploys on pushes touching frontend/
- CNAME file included under frontend/CNAME

Backend (Azure Web App)
- Custom domain: api.marketplace.vanshdeshwal.dev (configure DNS + Azure custom domain)
- Add repository secrets:
	- AZURE_WEBAPP_NAME: Azure Web App name
	- AZURE_WEBAPP_PUBLISH_PROFILE: Publish Profile XML (contents) from Azure Portal
- Workflow: .github/workflows/backend-azure.yml packages backend/ and deploys
- Exposes FastAPI app at backend/application.py for Azure discovery

CI/CD
- Frontend and backend deploy on push to main affecting respective folders

