import os
import sys
from pathlib import Path
from typing import Optional

# pip install azure-storage-blob
try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
except Exception as e:
    print("Missing dependency: azure-storage-blob. Install with 'pip install azure-storage-blob'", file=sys.stderr)
    raise

"""
Uploads dataset images to Azure Blob Storage keeping folder structure:
  <DATASET_ROOT>/train_images/*  -> container/train_images/*
  <DATASET_ROOT>/test_images/*   -> container/test_images/*

Configuration via env vars:
- AZURE_STORAGE_CONNECTION_STRING  (required) or AZURE_STORAGE_ACCOUNT_URL + AZURE_STORAGE_SAS_TOKEN
- AZURE_STORAGE_CONTAINER          (required), e.g. 'catalog'
- DATASET_ROOT                     (optional) defaults to ../dataset/shopee-product-matching

Usage (PowerShell):
  $env:AZURE_STORAGE_CONNECTION_STRING = "<conn_string>"
  $env:AZURE_STORAGE_CONTAINER = "catalog"
  python tools/upload_to_blob.py

Optionally pass dataset root:
  python tools/upload_to_blob.py c:\\Github\\Project\\dataset\\shopee-product-matching
"""

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / 'dataset' / 'shopee-product-matching'


def get_blob_service() -> BlobServiceClient:
    conn = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    if conn:
        return BlobServiceClient.from_connection_string(conn)
    account_url = os.environ.get('AZURE_STORAGE_ACCOUNT_URL')
    sas = os.environ.get('AZURE_STORAGE_SAS_TOKEN')
    if account_url and sas:
        return BlobServiceClient(account_url=account_url, credential=sas)
    raise RuntimeError('Configure AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_URL + AZURE_STORAGE_SAS_TOKEN')


def upload_dir(container_name: str, dataset_root: Path):
    bsc = get_blob_service()
    container = bsc.get_container_client(container_name)
    try:
        container.create_container()
    except Exception:
        pass

    def iter_files(sub: str):
        base = dataset_root / sub
        if not base.exists():
            return
        for p in base.rglob('*'):
            if p.is_file():
                yield sub + '/' + p.relative_to(base).as_posix()

    count = 0
    for sub in ['train_images', 'test_images']:
        for rel in iter_files(sub):
            local = dataset_root / rel
            blob_name = rel
            ctype = 'image/jpeg'
            if local.suffix.lower() in {'.png'}:
                ctype = 'image/png'
            elif local.suffix.lower() in {'.webp'}:
                ctype = 'image/webp'
            settings = ContentSettings(content_type=ctype, cache_control='public, max-age=31536000, immutable')
            with open(local, 'rb') as f:
                container.upload_blob(name=blob_name, data=f, overwrite=True, content_settings=settings)
            count += 1
            if count % 100 == 0:
                print(f"Uploaded {count} files...")
    print(f"Done. Uploaded {count} files to container '{container_name}'.")


if __name__ == '__main__':
    dataset = Path(os.environ.get('DATASET_ROOT') or (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATASET))
    container = os.environ.get('AZURE_STORAGE_CONTAINER')
    if not container:
        raise RuntimeError('Set AZURE_STORAGE_CONTAINER')
    if not dataset.exists():
        raise RuntimeError(f'Dataset root not found: {dataset}')
    upload_dir(container, dataset)
