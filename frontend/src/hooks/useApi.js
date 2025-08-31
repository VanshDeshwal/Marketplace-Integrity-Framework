import { useState, useCallback, useEffect, useRef } from 'react';
import { getApiConfig } from '../utils/api';

export const useApi = () => {
  const [isOnline, setIsOnline] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const lastCheckTime = useRef(0);
  const checkInterval = useRef(null);

  const checkApiHealth = useCallback(async () => {
    const now = Date.now();
    
    // Throttle: Don't check more than once every 10 seconds
    if (isChecking || (now - lastCheckTime.current) < 10000) {
      return;
    }
    
    lastCheckTime.current = now;
    setIsChecking(true);
    
    try {
      const { API_BASE } = getApiConfig();
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
      
      const response = await fetch(`${API_BASE}/health`, { 
        cache: 'no-store',
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) throw new Error(`API responded with status ${response.status}`);
      
      const data = await response.json();
      
      setIsOnline(true);
    } catch (error) {
      console.warn('API health check failed:', error.message);
      setIsOnline(false);
    } finally {
      setIsChecking(false);
    }
  }, [isChecking]);

  // Check API health on mount and periodically
  useEffect(() => {
    // Check immediately on mount (but only once)
    if (lastCheckTime.current === 0) {
      checkApiHealth();
    }
    
    // Clear any existing interval
    if (checkInterval.current) {
      clearInterval(checkInterval.current);
    }
    
    // Check every 60 seconds (much less frequent)
    checkInterval.current = setInterval(() => {
      checkApiHealth();
    }, 60000);
    
    return () => {
      if (checkInterval.current) {
        clearInterval(checkInterval.current);
      }
    };
  }, []); // Remove checkApiHealth from dependencies to prevent recreating interval

  // Manual refresh function for when user clicks the status
  const refreshStatus = useCallback(() => {
    lastCheckTime.current = 0; // Reset throttle
    checkApiHealth();
  }, [checkApiHealth]);

  return { isOnline, checkApiHealth: refreshStatus, isChecking };
};
