import React, { useState, useEffect } from 'react';
import { Moon, Sun, Activity } from 'lucide-react';
import Navbar from './components/Navbar';
import TabNavigation from './components/TabNavigation';
import DuplicateDetection from './components/DuplicateDetection';
import SemanticSearch from './components/SemanticSearch';
import FraudAnalysis from './components/FraudAnalysis';
import ResultsContainer from './components/ResultsContainer';
import Toast from './components/Toast';
import { useTheme } from './hooks/useTheme';
import { useToast } from './hooks/useToast';
import { useApi } from './hooks/useApi';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('duplicate');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const { theme, toggleTheme } = useTheme();
  const { toasts, addToast, removeToast } = useToast();
  const { isOnline, checkApiHealth } = useApi();

  const handleResults = (newResults) => {
    setResults(newResults);
  };

  const handleError = (errorMessage) => {
    addToast(errorMessage, 'error');
  };

  const renderActiveTab = () => {
    const commonProps = {
      onResults: handleResults,
      onError: handleError,
      isLoading,
      setIsLoading
    };

    switch (activeTab) {
      case 'duplicate':
        return <DuplicateDetection {...commonProps} />;
      case 'semantic':
        return <SemanticSearch {...commonProps} />;
      case 'fraud':
        return <FraudAnalysis {...commonProps} />;
      default:
        return null;
    }
  };

  return (
    <div className={`app ${theme}`}>
      {/* Navigation Bar */}
      <Navbar 
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isOnline={isOnline}
        theme={theme}
        toggleTheme={toggleTheme}
        onApiStatusClick={checkApiHealth}
      />

      <div className="container">
        {/* Main Content */}
        <div className="main-content">
          <div className="content-area">
            {renderActiveTab()}
            
            <ResultsContainer 
              results={results}
              activeTab={activeTab}
            />
          </div>
        </div>
      </div>

      {/* Toast Notifications */}
      <Toast 
        toasts={toasts}
        removeToast={removeToast}
      />
    </div>
  );
}

export default App;
