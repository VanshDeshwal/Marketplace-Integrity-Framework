export const getApiConfig = () => {
  const isLocalHost = ['localhost', '127.0.0.1', '::1'].includes(window.location.hostname);
  const isFile = window.location.protocol === 'file:';
  const IS_LOCAL = isLocalHost || isFile;
  
  const API_BASE = IS_LOCAL 
    ? 'http://localhost:8000' 
    : 'https://api.marketplace.vanshdeshwal.dev';
  
  // Hardcoded Azure Blob base for images (always use blob; no local/backend fallback)
  const MEDIA_BASE = 'https://marketplacestoragevd.blob.core.windows.net/catalog';
  
  return { API_BASE, MEDIA_BASE, IS_LOCAL };
};

export const getImageSrc = (result) => {
  const { API_BASE, MEDIA_BASE } = getApiConfig();

  // Always build from blob base when key/path is available
  if (result.image_key) return `${MEDIA_BASE}/${result.image_key}`;
  if (result.image_path) return `${MEDIA_BASE}/${result.image_path}`;
  // If API provided a full URL, use it (e.g., already a blob URL)
  if (typeof result.image_url === 'string' && /^(https?:)?\/\//.test(result.image_url)) return result.image_url;
  // Otherwise, no image
  return '';
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
