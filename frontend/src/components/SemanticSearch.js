import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { apiRequest } from '../utils/api';
import { debounce } from '../utils/helpers';

const SemanticSearch = ({ onResults, onError, isLoading, setIsLoading }) => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('text');

  const performSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) {
      onError('Please enter a search query');
      return;
    }

    setIsLoading(true);
    try {
      const endpoint = searchType === 'text' ? '/search-text' : '/search-image';
      const data = await apiRequest(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery.trim() })
      });

      onResults(data.results);
    } catch (error) {
      onError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Debounced search for real-time results
  const debouncedSearch = debounce(performSearch, 500);

  const handleQueryChange = (e) => {
    const newQuery = e.target.value;
    setQuery(newQuery);
    
    // Only auto-search for text queries longer than 2 characters
    if (searchType === 'text' && newQuery.trim().length > 2) {
      debouncedSearch(newQuery);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    performSearch();
  };

  return (
    <div className="feature-section">
      <h2>Semantic Search</h2>
      <p>Search products by meaning using advanced text embeddings and OpenCLIP models for natural language understanding.</p>
      
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-type-selector">
          <label className={`search-type ${searchType === 'text' ? 'active' : ''}`}>
            <input
              type="radio"
              value="text"
              checked={searchType === 'text'}
              onChange={(e) => setSearchType(e.target.value)}
            />
            Text Search
          </label>
          <label className={`search-type ${searchType === 'image' ? 'active' : ''}`}>
            <input
              type="radio"
              value="image"
              checked={searchType === 'image'}
              onChange={(e) => setSearchType(e.target.value)}
            />
            Image Description Search
          </label>
        </div>

        <div className="search-input-container">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            value={query}
            onChange={handleQueryChange}
            placeholder={
              searchType === 'text' 
                ? 'Search for products... (e.g., "red sneakers", "gaming laptop")'
                : 'Describe the image content... (e.g., "blue shirt on white background")'
            }
            className="search-input"
            disabled={isLoading}
          />
        </div>

        <div className="action-buttons">
          <button 
            type="submit" 
            disabled={!query.trim() || isLoading}
            className="primary-button"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {searchType === 'text' && (
        <div className="search-hints">
          <p><strong>Tips:</strong></p>
          <ul>
            <li>Use natural language: "comfortable running shoes for women"</li>
            <li>Describe features: "wireless noise-canceling headphones"</li>
            <li>Include colors, brands, or specific attributes</li>
          </ul>
        </div>
      )}

      {searchType === 'image' && (
        <div className="search-hints">
          <p><strong>Tips:</strong></p>
          <ul>
            <li>Describe visual elements: "red dress on mannequin"</li>
            <li>Include background details: "shoes on wooden floor"</li>
            <li>Mention positioning: "phone lying flat on desk"</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default SemanticSearch;
