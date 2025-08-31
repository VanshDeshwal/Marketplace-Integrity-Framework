import React from 'react';
import { ExternalLink, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import imageService from '../utils/imageService';
import { truncateText } from '../utils/helpers';

const ResultsContainer = ({ results, activeTab }) => {
  if (!results || results.length === 0) {
    return (
      <div className="results-container empty">
        <p>No results to display. Upload an image or perform a search to see results here.</p>
      </div>
    );
  }

  const renderDuplicateResults = () => (
    <div className="results-grid">
      {results.map((result, index) => {
        // Handle the API response format: { score, meta: { title, posting_id }, image_url }
        const title = result.meta?.title || result.title || 'Untitled Product';
        const postingId = result.meta?.posting_id || result.posting_id;
        const imageUrl = result.image_url || result.image_path || result.image;
        const similarity = result.score || result.similarity || 0;
        
        return (
          <div key={index} className="result-card">
            <div className="result-image">
              <img 
                src={imageUrl} 
                alt={title}
                onError={(e) => imageService.handleImageError(e)}
              />
            </div>
            <div className="result-info">
              <h3>{truncateText(title, 50)}</h3>
              <p className="similarity">Similarity: {(similarity * 100).toFixed(1)}%</p>
              {postingId && (
                <a 
                  href={`https://shopee.com/product/${postingId}`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="external-link"
                >
                  View Product <ExternalLink size={14} />
                </a>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );

  const renderSearchResults = () => (
    <div className="results-grid">
      {results.map((result, index) => (
        <div key={index} className="result-card">
          <div className="result-image">
            <img 
              src={imageService.getImageUrl(result.image_path || result.image)} 
              alt={result.title || 'Product'}
              onError={(e) => imageService.handleImageError(e)}
            />
          </div>
          <div className="result-info">
            <h3>{truncateText(result.title || 'Untitled Product', 50)}</h3>
            <p className="score">Relevance: {(result.score * 100).toFixed(1)}%</p>
            {result.posting_id && (
              <a 
                href={`https://shopee.com/product/${result.posting_id}`} 
                target="_blank" 
                rel="noopener noreferrer"
                className="external-link"
              >
                View Product <ExternalLink size={14} />
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );

  const renderFraudResults = () => (
    <div className="fraud-results">
      {results.map((result, index) => {
        const riskLevel = result.risk_level || 'unknown';
        const fraudScore = result.fraud_score || 0;
        const confidence = result.confidence || 0;
        
        const getRiskColor = (level) => {
          switch (level.toLowerCase()) {
            case 'low': return '#22c55e';
            case 'medium': return '#f59e0b';
            case 'high': return '#ef4444';
            default: return '#6b7280';
          }
        };

        const getRiskIcon = (level) => {
          switch (level.toLowerCase()) {
            case 'low': return <CheckCircle size={24} style={{ color: '#22c55e' }} />;
            case 'medium': return <AlertTriangle size={24} style={{ color: '#f59e0b' }} />;
            case 'high': return <XCircle size={24} style={{ color: '#ef4444' }} />;
            default: return <AlertTriangle size={24} style={{ color: '#6b7280' }} />;
          }
        };

        return (
          <div key={index} className="fraud-result-card">
            <div className="fraud-header">
              <div className="risk-indicator">
                {getRiskIcon(riskLevel)}
                <div>
                  <h3>Risk Level: <span style={{ color: getRiskColor(riskLevel) }}>{riskLevel.toUpperCase()}</span></h3>
                  <p>Fraud Score: {(fraudScore * 100).toFixed(1)}%</p>
                </div>
              </div>
              <div className="confidence-meter">
                <div className="confidence-label">Confidence: {(confidence * 100).toFixed(1)}%</div>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ width: `${confidence * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {result.uploaded_image && (
              <div className="analyzed-image">
                <h4>Analyzed Image:</h4>
                <img 
                  src={URL.createObjectURL(result.uploaded_image)} 
                  alt="Analyzed product"
                  className="fraud-image-preview"
                />
              </div>
            )}

            {result.analysis_details && Object.keys(result.analysis_details).length > 0 && (
              <div className="analysis-details">
                <h4>Analysis Details:</h4>
                <ul>
                  {Object.entries(result.analysis_details).map(([key, value]) => (
                    <li key={key}>
                      <strong>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong> {value}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="fraud-recommendations">
              <h4>Recommendations:</h4>
              {riskLevel.toLowerCase() === 'low' && (
                <div className="recommendation safe">
                  <CheckCircle size={16} />
                  <span>This image shows low fraud indicators. Proceed with normal verification.</span>
                </div>
              )}
              {riskLevel.toLowerCase() === 'medium' && (
                <div className="recommendation warning">
                  <AlertTriangle size={16} />
                  <span>Moderate fraud indicators detected. Additional verification recommended.</span>
                </div>
              )}
              {riskLevel.toLowerCase() === 'high' && (
                <div className="recommendation danger">
                  <XCircle size={16} />
                  <span>High fraud probability. Manual review and additional verification required.</span>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );

  return (
    <div className="results-container">
      <div className="results-header">
        <h3>
          {activeTab === 'duplicate' && 'Duplicate Detection Results'}
          {activeTab === 'semantic' && 'Search Results'}
          {activeTab === 'fraud' && 'Fraud Analysis Results'}
        </h3>
        <span className="results-count">{results.length} result{results.length !== 1 ? 's' : ''}</span>
      </div>
      
      {activeTab === 'duplicate' && renderDuplicateResults()}
      {activeTab === 'semantic' && renderSearchResults()}
      {activeTab === 'fraud' && renderFraudResults()}
    </div>
  );
};

export default ResultsContainer;
