from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import os
from typing import List, Optional, Dict, Any

app = FastAPI(title="Similarity-Driven Catalog Intelligence - Backend")

# CORS (dev-friendly: allow all; tighten later for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=".*",    # also allow any other origin (dev-friendly)
    allow_credentials=False,     # '*' with credentials is disallowed by browsers
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT_DIR, '..'))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
ARTIFACT_DIR = os.path.join(DATA_DIR, 'siamese_artifacts')
os.makedirs(DATA_DIR, exist_ok=True)
DATASET_DIR = os.path.join(PROJECT_ROOT, 'dataset', 'shopee-product-matching')

# Lazy imports for optional libraries
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    import faiss
except Exception:
    faiss = None

try:
    import open_clip
    import torch
    import torch.nn.functional as F
    from PIL import Image
except Exception:
    open_clip = None
    torch = None
    F = None
    Image = None

import pandas as pd
import pickle
from sklearn.ensemble import IsolationForest


class EmbedRequest(BaseModel):
    title: str


def _load_artifacts():
    """Load artifacts if present. Returns a dict with loaded objects or None keys.
    Expected files (from notebook manifest):
      - meta.csv
      - text_embs.npy
      - image_embs.npy
      - faiss_text.index
      - faiss_image.index
      - threshold_clf.pkl
    """
    out = {
        'meta': None,
        'text_embs': None,
        'image_embs': None,
        'faiss_text': None,
        'faiss_image': None,
        'clf_obj': None,
        'manifest': None,
    }

    if not os.path.exists(ARTIFACT_DIR):
        return out

    # manifest (optional)
    manifest_path = os.path.join(ARTIFACT_DIR, 'manifest.json')
    if os.path.exists(manifest_path):
        try:
            import json
            out['manifest'] = json.load(open(manifest_path, 'r'))
        except Exception:
            out['manifest'] = None

    # meta
    meta_path = os.path.join(ARTIFACT_DIR, 'meta.csv')
    if os.path.exists(meta_path):
        out['meta'] = pd.read_csv(meta_path)

    # embeddings
    txt_path = os.path.join(ARTIFACT_DIR, 'text_embs.npy')
    img_path = os.path.join(ARTIFACT_DIR, 'image_embs.npy')
    if os.path.exists(txt_path):
        out['text_embs'] = np.load(txt_path)
    if os.path.exists(img_path):
        out['image_embs'] = np.load(img_path)

    # faiss indices
    if faiss is not None:
        faiss_text_path = os.path.join(ARTIFACT_DIR, 'faiss_text.index')
        faiss_image_path = os.path.join(ARTIFACT_DIR, 'faiss_image.index')
        if os.path.exists(faiss_text_path):
            try:
                out['faiss_text'] = faiss.read_index(faiss_text_path)
            except Exception:
                out['faiss_text'] = None
        if os.path.exists(faiss_image_path):
            try:
                out['faiss_image'] = faiss.read_index(faiss_image_path)
            except Exception:
                out['faiss_image'] = None

    # classifier
    clf_path = os.path.join(ARTIFACT_DIR, 'threshold_clf.pkl')
    if os.path.exists(clf_path):
        try:
            with open(clf_path, 'rb') as f:
                out['clf_obj'] = pickle.load(f)
        except Exception:
            out['clf_obj'] = None

    return out


# Load models used for query-time embedding if available
TEXT_MODEL_NAME = 'all-MiniLM-L6-v2'
TEXT_MODEL = None
if SentenceTransformer is not None:
    try:
        TEXT_MODEL = SentenceTransformer(TEXT_MODEL_NAME)
    except Exception:
        TEXT_MODEL = None

IMG_MODEL = None
IMG_PREPROCESS = None
if open_clip is not None and torch is not None:
    try:
        IMG_MODEL, _, IMG_PREPROCESS = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
        IMG_MODEL.eval()
        if torch.cuda.is_available():
            IMG_MODEL.to('cuda')
    except Exception:
        IMG_MODEL = None
        IMG_PREPROCESS = None


ART = _load_artifacts()

# Fraud model cache
FRAUD: Dict[str, Any] = {
    'built': False,
    'model': None,
    'seller_ids': None,
    'seller_features': None,
    'counts': None,
    'seller_groups': None,  # dict seller_id -> list of indices
    'features_df': None,    # pandas DataFrame with computed metrics per seller
}


def _build_fraud_model():
    if FRAUD['built']:
        return
    meta = ART.get('meta')
    text_embs = ART.get('text_embs')
    if meta is None or text_embs is None or 'seller_id' not in meta.columns:
        FRAUD['built'] = True  # mark as built (no-op) to avoid repeated attempts
        return
    # Aggregate mean text embedding per seller
    seller_groups = meta.groupby('seller_id').indices
    seller_ids = []
    feats = []
    counts = []
    for sid, idxs in seller_groups.items():
        idxs = np.array(list(idxs), dtype=int)
        vecs = text_embs[idxs]
        mean_vec = vecs.mean(axis=0)
        mean_vec = _norm(mean_vec)
        seller_ids.append(sid)
        feats.append(mean_vec)
        counts.append(int(len(idxs)))
    X = np.vstack(feats).astype('float32') if feats else None
    if X is None or len(X) < 5:
        FRAUD['built'] = True
        return
    model = IsolationForest(n_estimators=200, contamination='auto', random_state=42)
    model.fit(X)
    # Compute additional seller metrics (no training)
    try:
        import math
        image_embs = ART.get('image_embs')
        # helper to compute within-seller mean cosine sim via sampling
        rng = np.random.default_rng(42)
        def mean_sim(idxs: np.ndarray, embs: Optional[np.ndarray], sample_pairs: int = 200) -> float:
            if embs is None or len(idxs) < 2:
                return float('nan')
            idxs = np.array(idxs, dtype=int)
            m = min(sample_pairs, len(idxs) * (len(idxs) - 1) // 2)
            if m <= 0:
                return float('nan')
            # sample pairs
            pairs = set()
            for _ in range(m * 2):
                i, j = rng.integers(0, len(idxs), size=2)
                if i == j:
                    continue
                a, b = sorted((int(idxs[i]), int(idxs[j])))
                pairs.add((a, b))
                if len(pairs) >= m:
                    break
            sims = []
            for a, b in pairs:
                va = _norm(embs[a:a+1])[0]
                vb = _norm(embs[b:b+1])[0]
                sims.append(float((va * vb).sum()))
            if not sims:
                return float('nan')
            return float(np.mean(sims))

        rows = []
        for sid, idxs in seller_groups.items():
            idxs = np.array(list(idxs), dtype=int)
            row = {
                'seller_id': sid,
                'count': int(len(idxs)),
                'mean_text_sim': mean_sim(idxs, text_embs),
                'mean_image_sim': mean_sim(idxs, image_embs),
                'label_entropy': float('nan'),
                'unique_title_ratio': float('nan'),
            }
            # label entropy if available
            try:
                if 'label_group' in meta.columns:
                    from collections import Counter
                    vals = [str(x) for x in meta.iloc[idxs]['label_group'].tolist()]
                    c = Counter(vals)
                    total = sum(c.values()) or 1
                    ent = 0.0
                    for k, v in c.items():
                        p = v / total
                        ent -= p * math.log(p + 1e-12)
                    row['label_entropy'] = float(ent)
            except Exception:
                pass
            # unique title ratio if available
            try:
                if 'title' in meta.columns:
                    titles = [str(x).strip().lower() for x in meta.iloc[idxs]['title'].fillna('').tolist()]
                    uniq = len(set(titles)) or 1
                    row['unique_title_ratio'] = float(uniq / max(1, len(titles)))
            except Exception:
                pass
            # simple risk score (higher is riskier): high count, high similarity, low entropy, low unique titles
            mt = row.get('mean_text_sim')
            mi = row.get('mean_image_sim')
            ent = row.get('label_entropy')
            utr = row.get('unique_title_ratio')
            count = row['count']
            mt = 0.0 if np.isnan(mt) else mt
            mi = 0.0 if np.isnan(mi) else mi
            ent = 0.0 if np.isnan(ent) else ent
            utr = 0.0 if np.isnan(utr) else utr
            row['risk_score'] = float(0.4 * mt + 0.3 * mi + 0.2 * (1.0 - min(ent, 5.0) / 5.0) + 0.1 * (1.0 - utr)) * (1.0 + min(count, 100) / 100.0)
            rows.append(row)
        features_df = pd.DataFrame(rows)
    except Exception:
        features_df = None

    FRAUD.update({
        'built': True,
        'model': model,
        'seller_ids': np.array(seller_ids),
        'seller_features': X,
        'counts': np.array(counts),
        'seller_groups': {k: np.array(list(v), dtype=int) for k, v in seller_groups.items()},
        'features_df': features_df,
    })


@app.get('/health')
def health():
    info = {'status': 'ok', 'artifacts_loaded': {k: (v is not None) for k, v in ART.items()}}
    return info


@app.post('/embed')
def embed_title(req: EmbedRequest):
    if TEXT_MODEL is None:
        return {"error": "Text model not available on server. Install sentence-transformers."}
    emb = TEXT_MODEL.encode([req.title], convert_to_numpy=True)
    return {"embedding": emb[0].tolist()}


def _norm(x: np.ndarray):
    # L2 normalize
    denom = np.linalg.norm(x, axis=-1, keepdims=True)
    denom[denom == 0] = 1.0
    return x / denom


def _image_base_url() -> str:
    """Media base URL for images if configured via env MEDIA_BASE_URL, else empty string."""
    return (os.environ.get('MEDIA_BASE_URL') or '').strip().rstrip('/')


def _get_image_key(idx: int) -> Optional[str]:
    """Return a relative image key like 'train_images/abc.jpg' for a given idx."""
    path = _resolve_image_path(idx)
    if path and os.path.exists(path):
        try:
            rel = os.path.relpath(path, DATASET_DIR)
            return rel.replace('\\', '/').lstrip('/')
        except Exception:
            pass
    # Try to infer from metadata
    meta = ART.get('meta')
    try:
        if meta is None or idx < 0 or idx >= len(meta):
            return None
        row = meta.iloc[int(idx)]
        candidates = ['image_path', 'image', 'file', 'filepath', 'image_name', 'image_file']
        val = None
        for c in candidates:
            if c in row and pd.notna(row[c]) and str(row[c]).strip():
                val = str(row[c]).strip()
                break
        if not val:
            return None
        p = val.replace('\\', '/').lstrip('/')
        base = os.path.basename(p)
        # Prefer known subfolders
        for sub in ['train_images', 'test_images']:
            cand = os.path.join(DATASET_DIR, sub, base)
            if os.path.exists(cand):
                return f"{sub}/{base}"
        # Keep provided hint if contains subfolder
        if p.startswith('train_images/') or p.startswith('test_images/'):
            return p
        return f"train_images/{base}"
    except Exception:
        return None


def _image_url_for_key(key: Optional[str]) -> Optional[str]:
    base = _image_base_url()
    if not base or not key:
        return None
    return base + '/' + key.lstrip('/')

def _resolve_image_path(idx: int):
    meta = ART.get('meta')
    try:
        if meta is None or idx < 0 or idx >= len(meta):
            return None
        row = meta.iloc[int(idx)]
        candidates = ['image', 'image_path', 'file', 'filepath', 'image_name', 'image_file']
        val = None
        for c in candidates:
            if c in row and pd.notna(row[c]) and str(row[c]).strip():
                val = str(row[c]).strip()
                break
        if not val:
            return None
        p = val.replace('\\', '/').lstrip('/')
        # Try as-is under dataset root
        abs_try = p if os.path.isabs(p) else os.path.join(DATASET_DIR, p)
        if os.path.exists(abs_try):
            return abs_try
        # Try common folders
        base = os.path.basename(p)
        for sub in ['train_images', 'test_images']:
            cand = os.path.join(DATASET_DIR, sub, base)
            if os.path.exists(cand):
                return cand
    except Exception:
        return None
    return None


@app.post('/dedup/title')
def dedup_title(title: str = Form(...), top_k: int = Form(5)):
    if ART.get('faiss_text') is None or TEXT_MODEL is None:
        return {"error": "Text FAISS index or text model not available. Ensure artifacts and sentence-transformers are installed."}

    q = TEXT_MODEL.encode([title], convert_to_numpy=True).astype('float32')
    q = _norm(q)
    index = ART['faiss_text']
    D, I = index.search(q, top_k)
    meta_df = ART['meta']
    results = []
    for dist, idx in zip(D[0], I[0]):
        meta = None
        if meta_df is not None and idx < len(meta_df):
            meta = meta_df.iloc[int(idx)].to_dict()
        key = _get_image_key(int(idx))
        url = _image_url_for_key(key)
        results.append({'idx': int(idx), 'score': float(dist), 'meta': meta, 'image_key': key, 'image_url': url})
    return {'query': title, 'results': results}


@app.post('/dedup/image')
async def dedup_image(file: UploadFile = File(...), top_k: int = Form(5)):
    if ART.get('faiss_image') is None:
        return {"error": "Image FAISS index not available. Ensure artifacts are placed in siamese_artifacts."}
    if IMG_MODEL is None or IMG_PREPROCESS is None or Image is None:
        return {"error": "OpenCLIP or image dependencies not installed on server. Install open_clip_torch and pillow to enable image dedup."}

    contents = await file.read()
    from io import BytesIO
    pil = Image.open(BytesIO(contents)).convert('RGB')
    x = IMG_PREPROCESS(pil).unsqueeze(0)
    if torch.cuda.is_available():
        x = x.to('cuda')
    with torch.no_grad():
        emb = IMG_MODEL.encode_image(x)
        emb = emb.detach().cpu().numpy().astype('float32')
    emb = _norm(emb)
    index = ART['faiss_image']
    D, I = index.search(emb, top_k)
    meta_df = ART['meta']
    results = []
    for dist, idx in zip(D[0], I[0]):
        meta = None
        if meta_df is not None and idx < len(meta_df):
            meta = meta_df.iloc[int(idx)].to_dict()
        key = _get_image_key(int(idx))
        url = _image_url_for_key(key)
        results.append({'idx': int(idx), 'score': float(dist), 'meta': meta, 'image_key': key, 'image_url': url})
    return {'results': results}


@app.post('/dedup/fused')
async def dedup_fused(title: Optional[str] = Form(None), file: Optional[UploadFile] = File(None), top_k: int = Form(5), alpha: Optional[float] = Form(None)):
    # Requires at least one of title or file
    if ART.get('faiss_text') is None and ART.get('faiss_image') is None:
        return {"error": "No FAISS indices available."}
    if ART.get('clf_obj') is None:
        return {"error": "Classifier artifact (threshold_clf.pkl) not found. Fused decision requires the classifier."}

    candidates = set()

    text_emb_q = None
    img_emb_q = None

    if title and TEXT_MODEL is not None and ART.get('faiss_text') is not None:
        q = TEXT_MODEL.encode([title], convert_to_numpy=True).astype('float32')
        q = _norm(q)
        D_t, I_t = ART['faiss_text'].search(q, top_k)
        candidates.update([int(x) for x in I_t[0]])
        text_emb_q = q[0]

    if file is not None and IMG_MODEL is not None and ART.get('faiss_image') is not None:
        contents = await file.read()
        from io import BytesIO
        pil = Image.open(BytesIO(contents)).convert('RGB')
        x = IMG_PREPROCESS(pil).unsqueeze(0)
        if torch.cuda.is_available():
            x = x.to('cuda')
        with torch.no_grad():
            emb = IMG_MODEL.encode_image(x)
            emb = emb.detach().cpu().numpy().astype('float32')
        emb = _norm(emb)
        D_i, I_i = ART['faiss_image'].search(emb, top_k)
        candidates.update([int(x) for x in I_i[0]])
        img_emb_q = emb[0]

    if len(candidates) == 0:
        return {'results': []}

    # For each candidate compute features and run classifier
    text_embs = ART.get('text_embs')
    image_embs = ART.get('image_embs')
    clf_obj = ART.get('clf_obj')
    alpha_eff = alpha if (alpha is not None) else clf_obj.get('alpha', 0.5)

    results = []
    for idx in list(candidates)[:200]:
        img_sim = 0.0
        txt_sim = 0.0
        if img_emb_q is not None and image_embs is not None:
            img_sim = float((img_emb_q * _norm(image_embs[idx:idx+1])[0]).sum())
        if text_emb_q is not None and text_embs is not None:
            txt_sim = float((text_emb_q * _norm(text_embs[idx:idx+1])[0]).sum())
        fused = alpha_eff * img_sim + (1.0 - alpha_eff) * txt_sim
        # classifier
        try:
            x = np.array([[img_sim, txt_sim, fused]], dtype=np.float32)
            p = clf_obj['clf'].predict_proba(x)[:,1][0]
            decision = p >= clf_obj.get('best_threshold', 0.5)
        except Exception:
            p = fused
            decision = fused >= 0.5

        meta = None
        if ART['meta'] is not None and idx < len(ART['meta']):
            meta = ART['meta'].iloc[int(idx)].to_dict()
        key = _get_image_key(int(idx))
        url = _image_url_for_key(key)
        results.append({'idx': int(idx), 'image_sim': img_sim, 'text_sim': txt_sim, 'fused_sim': fused, 'prob': float(p), 'decision': bool(decision), 'meta': meta, 'image_key': key, 'image_url': url})

    # sort by prob or fused
    results = sorted(results, key=lambda x: x.get('prob', x.get('fused_sim', 0)), reverse=True)[:top_k]
    return {'results': results, 'alpha': float(alpha_eff)}


@app.post('/search')
async def search(title: Optional[str] = Form(None), file: Optional[UploadFile] = File(None), top_k: int = Form(10), alpha: Optional[float] = Form(None)):
    """Semantic search: title and/or image. Returns top-K by fused score (no classifier decision)."""
    candidates: Dict[int, Dict[str, Any]] = {}
    alpha_eff = 0.5
    if ART.get('clf_obj') is not None:
        alpha_eff = ART['clf_obj'].get('alpha', alpha_eff)
    if alpha is not None:
        alpha_eff = alpha

    text_emb_q = None
    img_emb_q = None

    if title and TEXT_MODEL is not None and ART.get('faiss_text') is not None:
        q = TEXT_MODEL.encode([title], convert_to_numpy=True).astype('float32')
        q = _norm(q)
        D_t, I_t = ART['faiss_text'].search(q, top_k)
        text_emb_q = q[0]
        for score, idx in zip(D_t[0], I_t[0]):
            entry = candidates.setdefault(int(idx), {'idx': int(idx), 'meta': None, 'text_score': 0.0, 'image_score': 0.0})
            entry['text_score'] = max(entry['text_score'], float(score))

    if file is not None and IMG_MODEL is not None and ART.get('faiss_image') is not None:
        contents = await file.read()
        from io import BytesIO
        pil = Image.open(BytesIO(contents)).convert('RGB')
        x = IMG_PREPROCESS(pil).unsqueeze(0)
        if torch.cuda.is_available():
            x = x.to('cuda')
        with torch.no_grad():
            emb = IMG_MODEL.encode_image(x).detach().cpu().numpy().astype('float32')
        emb = _norm(emb)
        img_emb_q = emb[0]
        D_i, I_i = ART['faiss_image'].search(emb, top_k)
        for score, idx in zip(D_i[0], I_i[0]):
            entry = candidates.setdefault(int(idx), {'idx': int(idx), 'meta': None, 'text_score': 0.0, 'image_score': 0.0})
            entry['image_score'] = max(entry['image_score'], float(score))

    meta_df = ART.get('meta')
    text_embs = ART.get('text_embs')
    image_embs = ART.get('image_embs')

    results = []
    for idx, entry in candidates.items():
        # If we have raw embeddings for better fused score, recompute cosine vs candidate
        img_sim = entry['image_score']
        txt_sim = entry['text_score']
        if img_emb_q is not None and image_embs is not None:
            img_sim = float((img_emb_q * _norm(image_embs[idx:idx+1])[0]).sum())
        if text_emb_q is not None and text_embs is not None:
            txt_sim = float((text_emb_q * _norm(text_embs[idx:idx+1])[0]).sum())
        fused = alpha_eff * img_sim + (1.0 - alpha_eff) * txt_sim
        m = None
        if meta_df is not None and idx < len(meta_df):
            m = meta_df.iloc[int(idx)].to_dict()
        key = _get_image_key(int(idx))
        url = _image_url_for_key(key)
        entry.update({'meta': m, 'fused': fused, 'image_score': img_sim, 'text_score': txt_sim, 'image_key': key, 'image_url': url})
        results.append(entry)

    results = sorted(results, key=lambda x: x['fused'], reverse=True)[:top_k]
    return {'results': results, 'alpha': float(alpha_eff)}


@app.get('/fraud/sellers/anomaly')
def fraud_top_anomalies(n: int = 20):
    _build_fraud_model()
    if FRAUD['model'] is None or FRAUD['seller_ids'] is None:
        return {'error': "seller_id not found in metadata; cannot compute seller anomalies."}
    model = FRAUD['model']
    X = FRAUD['seller_features']
    sids = FRAUD['seller_ids']
    counts = FRAUD['counts']
    scores = -model.score_samples(X)  # higher means more anomalous
    order = np.argsort(-scores)
    out = []
    for i in order[:n]:
        out.append({'seller_id': str(sids[i]), 'anomaly_score': float(scores[i]), 'count': int(counts[i])})
    return {'results': out}


# -----------------------------
# Samples: random images for demo
# -----------------------------
@app.get('/samples')
def get_random_samples(count: int = 12):
    """Return a small set of random sample items from the dataset.

    Response: { results: [ { idx: int, title: str|null } ] }
    """
    meta = ART.get('meta')
    if meta is None:
        return {'error': 'metadata unavailable'}
    try:
        n = len(meta)
        if n == 0:
            return {'results': []}
        c = int(count)
        if c < 1:
            c = 1
        c = min(c, 60, n)  # cap for UI
        # sample without replacement
        idxs = np.random.choice(n, size=c, replace=False).tolist()
        results = []
        has_title = hasattr(meta, 'columns') and ('title' in meta.columns)
        for i in idxs:
            try:
                title = None
                if has_title:
                    # robust access in case of numpy/pandas variances
                    try:
                        title = meta.iloc[int(i)]['title']
                    except Exception:
                        try:
                            title = meta.loc[int(i), 'title']
                        except Exception:
                            title = None
                key = _get_image_key(int(i))
                url = _image_url_for_key(key)
                results.append({'idx': int(i), 'title': None if title is None else str(title), 'image_key': key, 'image_url': url})
            except Exception:
                results.append({'idx': int(i), 'title': None, 'image_key': None, 'image_url': None})
        return {'results': results}
    except Exception as e:
        return {'error': f'sampling failed: {e}'}


@app.get('/fraud/seller/{seller_id}')
def fraud_seller(seller_id: str):
    _build_fraud_model()
    if FRAUD['model'] is None or FRAUD['seller_ids'] is None:
        return {'error': "seller_id not found in metadata; cannot compute seller anomaly."}
    sids = FRAUD['seller_ids']
    try:
        idx = np.where(sids.astype(str) == str(seller_id))[0]
        if len(idx) == 0:
            return {'error': 'seller not found'}
        i = int(idx[0])
        model = FRAUD['model']
        x = FRAUD['seller_features'][i:i+1]
        score = -model.score_samples(x)[0]
        return {'seller_id': str(seller_id), 'anomaly_score': float(score), 'count': int(FRAUD['counts'][i])}
    except Exception as e:
        return {'error': str(e)}


@app.get('/fraud/sellers/insights')
def fraud_seller_insights(n: int = 20):
    """Return top-N risky sellers by heuristic risk_score with metrics (no training)."""
    _build_fraud_model()
    df = FRAUD.get('features_df')
    if df is None or len(df) == 0:
        return {'error': 'insights unavailable'}
    d = df.sort_values('risk_score', ascending=False).head(n)
    results = d.to_dict(orient='records')
    # cast to builtin types
    for r in results:
        for k, v in list(r.items()):
            if isinstance(v, (np.floating, np.integer)):
                r[k] = float(v)
            elif k == 'seller_id':
                r[k] = str(v)
    return {'results': results}


@app.get('/fraud/seller/{seller_id}/duplicates')
def fraud_seller_duplicates(seller_id: str, top: int = 50, threshold: float = 0.8, use: str = 'fused'):
    """List within-seller likely duplicate pairs based on cosine similarity thresholds.
    use = 'fused' | 'text' | 'image'
    """
    _build_fraud_model()
    groups = FRAUD.get('seller_groups')
    if groups is None or seller_id not in groups:
        return {'error': 'seller not found'}
    idxs = groups[seller_id]
    if len(idxs) < 2:
        return {'results': []}
    text_embs = ART.get('text_embs')
    image_embs = ART.get('image_embs')
    alpha = 0.5
    if ART.get('clf_obj') is not None:
        alpha = ART['clf_obj'].get('alpha', alpha)
    # Sample pairs if too many
    max_pairs = 2000
    pairs = []
    for i in range(min(len(idxs), 500)):
        for j in range(i+1, min(len(idxs), 500)):
            pairs.append((int(idxs[i]), int(idxs[j])))
            if len(pairs) >= max_pairs:
                break
        if len(pairs) >= max_pairs:
            break
    scored = []
    for a, b in pairs:
        txt = None
        img = None
        if text_embs is not None:
            va = _norm(text_embs[a:a+1])[0]
            vb = _norm(text_embs[b:b+1])[0]
            txt = float((va * vb).sum())
        if image_embs is not None:
            va = _norm(image_embs[a:a+1])[0]
            vb = _norm(image_embs[b:b+1])[0]
            img = float((va * vb).sum())
        fused = None
        if txt is not None and img is not None:
            fused = alpha * img + (1.0 - alpha) * txt
        score = {'text': txt, 'image': img, 'fused': fused}.get(use, fused)
        if score is None:
            score = txt if use == 'text' else img
        if score is None:
            continue
        if score >= threshold:
            scored.append({'a': a, 'b': b, 'score': float(score), 'text': txt, 'image': img, 'fused': fused})
    scored.sort(key=lambda x: x['score'], reverse=True)
    meta = ART.get('meta')
    out = []
    for s in scored[:top]:
        ma = meta.iloc[int(s['a'])].to_dict() if meta is not None else None
        mb = meta.iloc[int(s['b'])].to_dict() if meta is not None else None
        s['a_meta'] = ma
        s['b_meta'] = mb
        a_key = _get_image_key(int(s['a']))
        b_key = _get_image_key(int(s['b']))
        s['a_key'] = a_key
        s['b_key'] = b_key
        s['a_url'] = _image_url_for_key(a_key)
        s['b_url'] = _image_url_for_key(b_key)
        out.append(s)
    return {'results': out, 'alpha': float(alpha), 'used': use, 'threshold': float(threshold)}


@app.get('/image/{idx}')
def get_image(idx: int):
    """Serve the raw image for a given catalog idx (for demo use only)."""
    path = _resolve_image_path(idx)
    if not path or not os.path.exists(path):
        return {"error": "image not found"}
    import mimetypes
    mt = mimetypes.guess_type(path)[0] or 'image/jpeg'
    return FileResponse(path, media_type=mt)
