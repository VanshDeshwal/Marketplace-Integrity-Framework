import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATASET_CSV = os.path.join(ROOT, 'dataset', 'shopee-product-matching', 'train.csv')
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def build():
    print('Loading dataset:', DATASET_CSV)
    df = pd.read_csv(DATASET_CSV)
    # Expecting columns: image, title, label_group, etc.
    titles = df['title'].fillna('').astype(str).tolist()
    meta = df[['image', 'label_group']].to_dict(orient='records')

    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(titles, convert_to_numpy=True, show_progress_bar=True)
    embeddings = embeddings.astype('float32')

    emb_path = os.path.join(DATA_DIR, 'embeddings.npy')
    meta_path = os.path.join(DATA_DIR, 'meta.npy')
    idx_path = os.path.join(DATA_DIR, 'faiss_index.idx')

    np.save(emb_path, embeddings)
    np.save(meta_path, np.array(meta, dtype=object))

    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    faiss.write_index(index, idx_path)

    print('Saved embeddings to', emb_path)
    print('Saved meta to', meta_path)
    print('Saved index to', idx_path)

if __name__ == '__main__':
    build()
