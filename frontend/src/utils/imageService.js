// Image service to handle both Azure Blob Storage and local images
class ImageService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.isAzureBlob = false;
    this.azureBlobUrl = null;
    this.detectStorageType();
  }

  async detectStorageType() {
    try {
      // Check if backend is using Azure Blob Storage
      const response = await fetch(`${this.baseUrl}/storage-info`);
      if (response.ok) {
        const data = await response.json();
        this.isAzureBlob = data.storage_type === 'azure_blob';
        this.azureBlobUrl = data.blob_url;
      }
    } catch (error) {
      // Use local storage fallback
      this.isAzureBlob = false;
    }
  }

  // Get the full URL for an image
  getImageUrl(imagePath) {
    if (!imagePath) return null;

    // If it's already a full URL (Azure Blob or other), return as is
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
      return imagePath;
    }

    // If using Azure Blob Storage
    if (this.isAzureBlob && this.azureBlobUrl) {
      return `${this.azureBlobUrl}/${imagePath}`;
    }

    // Local storage - use media server or backend static files
    return `${this.baseUrl}/images/${imagePath}`;
  }

  // Get random sample images for testing
  async getRandomImages(count = 6) {
    try {
      const response = await fetch(`${this.baseUrl}/random-images?count=${count}`);
      if (response.ok) {
        const data = await response.json();
        return data.images.map(img => ({
          ...img,
          url: this.getImageUrl(img.path)
        }));
      }
    } catch (error) {
      console.error('Failed to fetch random images:', error);
      // Fallback to sample images
      return this.getFallbackImages(count);
    }
    return [];
  }

  // Fallback sample images for demo
  getFallbackImages(count = 6) {
    const sampleImages = [
      { id: '1', name: 'Product 1', path: 'sample1.jpg' },
      { id: '2', name: 'Product 2', path: 'sample2.jpg' },
      { id: '3', name: 'Product 3', path: 'sample3.jpg' },
      { id: '4', name: 'Product 4', path: 'sample4.jpg' },
      { id: '5', name: 'Product 5', path: 'sample5.jpg' },
      { id: '6', name: 'Product 6', path: 'sample6.jpg' },
    ];

    return sampleImages.slice(0, count).map(img => ({
      ...img,
      url: this.getImageUrl(img.path)
    }));
  }

  // Handle image loading errors
  handleImageError(event, fallbackUrl = null) {
    if (fallbackUrl) {
      event.target.src = fallbackUrl;
    } else {
      // Use a placeholder image
      event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIG5vdCBmb3VuZDwvdGV4dD48L3N2Zz4=';
    }
  }
}

// Create singleton instance
const imageService = new ImageService();

export default imageService;
