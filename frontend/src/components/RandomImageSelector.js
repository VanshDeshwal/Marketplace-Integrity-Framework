import React, { useState, useEffect } from 'react';
import { Shuffle, Image as ImageIcon } from 'lucide-react';
import imageService from '../utils/imageService';

const RandomImageSelector = ({ onImageSelect, onError }) => {
  const [randomImages, setRandomImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  const loadRandomImages = async () => {
    setLoading(true);
    try {
      const images = await imageService.getRandomImages(6);
      setRandomImages(images);
    } catch (error) {
      onError('Failed to load random images');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRandomImages();
  }, []);

  const handleImageSelect = (image) => {
    setSelectedImage(image);
    // Convert the image to a file-like object for the parent component
    fetch(image.url)
      .then(response => response.blob())
      .then(blob => {
        const file = new File([blob], image.name || 'sample-image.jpg', {
          type: blob.type || 'image/jpeg'
        });
        onImageSelect(file, image);
      })
      .catch(error => {
        onError('Failed to load selected image');
      });
  };

  const handleDragStart = (e, image) => {
    // Set multiple data types for better compatibility
    e.dataTransfer.setData('text/plain', image.url);
    e.dataTransfer.setData('text/html', `<img src="${image.url}" alt="${image.name}" />`);
    e.dataTransfer.setData('application/json', JSON.stringify(image));
    e.dataTransfer.effectAllowed = 'copy';
  };

  const handleImageError = (event) => {
    imageService.handleImageError(event);
  };

  return (
    <div className="random-image-selector">
      <div className="selector-header">
        <div className="header-content">
          <ImageIcon size={20} />
          <h3>Try with Sample Images</h3>
        </div>
        <button 
          onClick={loadRandomImages} 
          disabled={loading}
          className="shuffle-button"
          title="Load new random images"
        >
          <Shuffle size={16} />
          {loading ? 'Loading...' : 'Shuffle'}
        </button>
      </div>

      <div className="images-grid">
        {randomImages.map((image) => (
          <div 
            key={image.id}
            className={`image-card ${selectedImage?.id === image.id ? 'selected' : ''}`}
            onClick={() => handleImageSelect(image)}
            draggable={true}
            onDragStart={(e) => handleDragStart(e, image)}
            title={`Click to select or drag to upload area. ${image.name || 'Sample Image'}`}
          >
            <img
              src={image.url}
              alt={image.name || 'Sample product'}
              onError={handleImageError}
              loading="lazy"
              draggable={false} // Prevent default image drag behavior
            />
            <div className="image-overlay">
              <span className="image-name">{image.name || 'Sample Image'}</span>
              <span className="drag-hint">Click or Drag</span>
            </div>
          </div>
        ))}
      </div>
      
      {randomImages.length === 0 && !loading && (
        <div className="no-images">
          <ImageIcon size={24} />
          <p>No sample images available</p>
          <button onClick={loadRandomImages} className="retry-button">
            Try Again
          </button>
        </div>
      )}
    </div>
  );
};

export default RandomImageSelector;
