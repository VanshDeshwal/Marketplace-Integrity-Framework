import React, { useState } from 'react';
import { Upload, X } from 'lucide-react';
import { apiRequest } from '../utils/api';
import { formatFileSize } from '../utils/helpers';
import RandomImageSelector from './RandomImageSelector';

const DuplicateDetection = ({ onResults, onError, isLoading, setIsLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [selectedSampleImage, setSelectedSampleImage] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      // Only set dragActive to false if we're leaving the drop area completely
      if (!e.currentTarget.contains(e.relatedTarget)) {
        setDragActive(false);
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    // Check if we have actual files (local file drag)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleFile(file);
      return;
    }
    
    // Check if we have text/plain data (might be image URL or data)
    if (e.dataTransfer.types.includes('text/plain')) {
      const text = e.dataTransfer.getData('text/plain');
      
      // If it looks like an image URL, try to fetch it and convert to file
      if (text && (text.startsWith('http') || text.startsWith('data:image'))) {
        handleImageUrl(text);
        return;
      }
    }
    
    // Check for image data
    if (e.dataTransfer.types.includes('text/html')) {
      const html = e.dataTransfer.getData('text/html');
      
      // Extract image URL from HTML
      const imgMatch = html.match(/<img[^>]+src="([^"]+)"/);
      if (imgMatch && imgMatch[1]) {
        handleImageUrl(imgMatch[1]);
        return;
      }
    }
    
    onError('No files detected. Please use the sample image selector or drag a local image file.');
  };

  const handleImageUrl = async (imageUrl) => {
    try {
      setIsLoading(true);
      
      const response = await fetch(imageUrl);
      if (!response.ok) throw new Error(`Failed to fetch image: ${response.status}`);
      
      const blob = await response.blob();
      
      // Create a file from the blob
      const fileName = imageUrl.split('/').pop() || 'sample-image.jpg';
      const file = new File([blob], fileName, {
        type: blob.type || 'image/jpeg'
      });
      
      handleFile(file);
    } catch (error) {
      console.error('Failed to convert image URL:', error);
      onError(`Failed to load image: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (!file) {
      onError('No file provided');
      return;
    }
    
    if (!file.type || !file.type.startsWith('image/')) {
      onError(`Please select an image file. Received: ${file.type || 'unknown type'}`);
      return;
    }
    
    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      onError(`File too large. Maximum size is 10MB. Your file: ${(file.size / 1024 / 1024).toFixed(1)}MB`);
      return;
    }
    
    setUploadedFile(file);
    setSelectedSampleImage(null); // Clear sample selection when file is uploaded
  };

  const handleSampleImageSelect = (file, imageInfo) => {
    setUploadedFile(file);
    setSelectedSampleImage(imageInfo);
  };

  const removeFile = () => {
    setUploadedFile(null);
    setSelectedSampleImage(null);
  };

  const findDuplicates = async () => {
    if (!uploadedFile) {
      onError('Please select an image first');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const data = await apiRequest('/dedup/image', {
        method: 'POST',
        body: formData
      });

      onResults(data.results);
    } catch (error) {
      onError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="feature-section">
      <h2>Duplicate Product Detection</h2>
      <p>Upload an image to find duplicate or similar products using advanced image embeddings and FAISS vector search.</p>
      
      {/* Random Image Selector */}
      <RandomImageSelector 
        onImageSelect={handleSampleImageSelect}
        onError={onError}
      />

      <div className="section-divider">
        <span>OR</span>
      </div>
      
      <div 
        className={`file-drop-area ${dragActive ? 'active' : ''} ${uploadedFile ? 'has-file' : ''} ${isLoading ? 'loading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {!uploadedFile ? (
          <>
            <Upload size={48} />
            <div>
              {isLoading ? (
                <>
                  <p>Processing image...</p>
                  <p className="file-hint">Please wait</p>
                </>
              ) : (
                <>
                  <p>Drop image here or click to select</p>
                  <p className="file-hint">Supports JPG, PNG, GIF (max 10MB)</p>
                  <p className="file-hint">You can also drag from the sample images above</p>
                </>
              )}
            </div>
            {!isLoading && (
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="file-input"
              />
            )}
          </>
        ) : (
          <div className="uploaded-file">
            <img 
              src={selectedSampleImage ? selectedSampleImage.url : URL.createObjectURL(uploadedFile)} 
              alt="Uploaded" 
              className="uploaded-preview"
              onError={(e) => {
                console.error('Image load error:', e);
                // Fallback to placeholder if image fails to load
                e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OTk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIGxvYWQgZXJyb3I8L3RleHQ+PC9zdmc+';
              }}
            />
            <div className="file-info">
              <span className="file-name">
                {selectedSampleImage ? selectedSampleImage.name : uploadedFile.name}
              </span>
              <span className="file-size">{formatFileSize(uploadedFile.size)}</span>
              {selectedSampleImage && (
                <span className="file-source">Sample Image</span>
              )}
            </div>
            <button onClick={removeFile} className="remove-file">
              <X size={16} />
            </button>
          </div>
        )}
      </div>

      <div className="action-buttons">
        <button 
          onClick={findDuplicates} 
          disabled={!uploadedFile || isLoading}
          className="primary-button"
        >
          {isLoading ? 'Finding Duplicates...' : 'Find Duplicates'}
        </button>
      </div>
    </div>
  );
};

export default DuplicateDetection;
