export const getApiConfig = () => {
  const isLocalHost = ['localhost', '127.0.0.1', '::1'].includes(window.location.hostname);
  const isFile = window.location.protocol === 'file:';
  const IS_LOCAL = isLocalHost || isFile;
  
  const API_BASE = IS_LOCAL 
    ? 'http://localhost:8000' 
    : 'https://api.marketplace.vanshdeshwal.dev';
    
  const MEDIA_BASE = IS_LOCAL 
    ? (localStorage.getItem('mediaBase') || '') 
    : 'https://marketplacestoragevd.blob.core.windows.net/catalog';
  
  return { API_BASE, MEDIA_BASE, IS_LOCAL };
};

export const getImageSrc = (result) => {
  const { API_BASE, MEDIA_BASE } = getApiConfig();
  
  // Prefer direct image_url from backend if present (points to blob in prod)
  if (result.image_url) return result.image_url;
  
  // Else, try media base + key
  if (MEDIA_BASE && result.image_key) return `${MEDIA_BASE}/${result.image_key}`;
  
  // Fallback: backend image endpoint (dev only)
  return `${API_BASE}/image/${result.idx}`;
};

export const apiRequest = async (endpoint, options = {}) => {
  const { API_BASE } = getApiConfig();
  const url = `${API_BASE}${endpoint}`;
  
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    return data;
  } catch (error) {
    throw new Error(error.message || 'Network error');
  }
};
