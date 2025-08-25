Quick backend (local) instructions

1. Create a python venv and install requirements

   On Windows PowerShell:

   ```powershell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
   ```

2. Build embeddings and index (reads dataset from `dataset/shopee-product-matching/train.csv`):

   ```powershell
   python -m app.build_index
   ```

3. Run the server:

   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```
