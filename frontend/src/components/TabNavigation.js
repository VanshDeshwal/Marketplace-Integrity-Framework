import React from 'react';
import { Search, Copy, Shield } from 'lucide-react';

const TabNavigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    {
      id: 'duplicate',
      label: 'Duplicate Detection',
      icon: Copy,
      description: 'Find duplicate products'
    },
    {
      id: 'semantic',
      label: 'Semantic Search',
      icon: Search,
      description: 'Search by meaning'
    },
    {
      id: 'fraud',
      label: 'Fraud Analysis',
      icon: Shield,
      description: 'Detect fraudulent listings'
    }
  ];

  return (
    <div className="tab-navigation">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        return (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id)}
          >
            <Icon className="tab-icon" size={20} />
            <div className="tab-content">
              <div className="tab-label">{tab.label}</div>
              <div className="tab-description">{tab.description}</div>
            </div>
          </button>
        );
      })}
    </div>
  );
};

export default TabNavigation;
