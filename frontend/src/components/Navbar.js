import React from 'react';
import { Activity, Moon, Sun, Shield, ExternalLink } from 'lucide-react';

const Navbar = ({ 
  activeTab, 
  onTabChange, 
  isOnline, 
  theme, 
  toggleTheme,
  onApiStatusClick 
}) => {
  const tabs = [
    { id: 'duplicate', label: 'Duplicate Detection', icon: '🔍' },
    { id: 'semantic', label: 'Semantic Search', icon: '🔗' },
    { id: 'fraud', label: 'Fraud Analysis', icon: '🚨' }
  ];

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Brand Section */}
        <div className="navbar-brand">
          <Shield className="brand-icon" size={24} />
          <div className="brand-text">
            <h1 className="brand-title">Marketplace Integrity Framework</h1>
            <p className="brand-subtitle">ML-powered product analysis & fraud detection</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="navbar-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Status & Controls */}
        <div className="navbar-controls">
          {/* API Status */}
          <a 
            href={process.env.REACT_APP_API_URL ? `${process.env.REACT_APP_API_URL}/docs` : 'http://localhost:8000/docs'}
            target="_blank"
            rel="noopener noreferrer"
            className="api-status-link"
            title="View API Documentation (Right-click to refresh status)"
            onContextMenu={(e) => {
              e.preventDefault();
              if (onApiStatusClick) onApiStatusClick();
            }}
          >
            <div className="api-status">
              <Activity 
                size={16} 
                className={`status-icon ${isOnline ? 'online' : 'offline'}`}
              />
              <span className={`status-text ${isOnline ? 'online' : 'offline'}`}>
                {isOnline ? 'API Online' : 'API Offline'}
              </span>
              <ExternalLink size={12} className="external-icon" />
            </div>
          </a>

          {/* Theme Toggle */}
          <button 
            onClick={toggleTheme} 
            className="theme-toggle-btn"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
          >
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
