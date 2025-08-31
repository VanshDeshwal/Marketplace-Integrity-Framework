import React, { useState } from 'react';
import { Upload, X, AlertTriangle } from 'lucide-react';
import { apiRequest } from '../utils/api';
import { formatFileSize } from '../utils/helpers';

const FraudAnalysis = ({ onResults, onError, isLoading, setIsLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (!file.type.startsWith('image/')) {
      onError('Please select an image file');
      return;
    }
    setUploadedFile(file);
  };

  const removeFile = () => {
    setUploadedFile(null);
  };

  const analyzeFraud = async () => {
    if (!uploadedFile) {
      onError('Please select an image first');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      const data = await apiRequest('/analyze-fraud', {
        method: 'POST',
        body: formData
      });

      // Transform fraud analysis results for display
      const fraudResults = [{
        fraud_score: data.fraud_score,
        fraud_probability: data.fraud_probability,
        risk_level: data.risk_level,
        confidence: data.confidence,
        analysis_details: data.analysis_details || {},
        uploaded_image: uploadedFile
      }];

      onResults(fraudResults);
    } catch (error) {
      onError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="feature-section">
      <h2>Fraud Detection Analysis</h2>
      <p>Upload a product image to analyze potential fraud indicators using machine learning models trained on marketplace data.</p>
      
      <div 
        className={`file-drop-area ${dragActive ? 'active' : ''} ${uploadedFile ? 'has-file' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {!uploadedFile ? (
          <>
            <AlertTriangle size={48} />
            <div>
              <p>Drop product image here or click to select</p>
              <p className="file-hint">Supports JPG, PNG, GIF (max 10MB)</p>
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="file-input"
            />
          </>
        ) : (
          <div className="uploaded-file">
            <img 
              src={URL.createObjectURL(uploadedFile)} 
              alt="Uploaded" 
              className="uploaded-preview"
            />
            <div className="file-info">
              <span className="file-name">{uploadedFile.name}</span>
              <span className="file-size">{formatFileSize(uploadedFile.size)}</span>
            </div>
            <button onClick={removeFile} className="remove-file">
              <X size={16} />
            </button>
          </div>
        )}
      </div>

      <div className="action-buttons">
        <button 
          onClick={analyzeFraud} 
          disabled={!uploadedFile || isLoading}
          className="primary-button danger"
        >
          {isLoading ? 'Analyzing...' : 'Analyze for Fraud'}
        </button>
      </div>

      <div className="fraud-info">
        <h3>What we analyze:</h3>
        <ul>
          <li><strong>Image Quality:</strong> Blur, compression artifacts, unusual editing</li>
          <li><strong>Product Authenticity:</strong> Brand consistency, packaging quality</li>
          <li><strong>Visual Anomalies:</strong> Watermarks, stock photo indicators</li>
          <li><strong>Context Clues:</strong> Background, lighting, staging quality</li>
        </ul>
      </div>
    </div>
  );
};

export default FraudAnalysis;
