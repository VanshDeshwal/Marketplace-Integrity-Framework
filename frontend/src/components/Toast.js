import React from 'react';
import { X, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';

const Toast = ({ toasts, removeToast }) => {
  // Handle case where toasts is undefined or not an array
  if (!toasts || !Array.isArray(toasts) || toasts.length === 0) {
    return null;
  }

  const getToastIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle size={20} />;
      case 'error': return <XCircle size={20} />;
      case 'warning': return <AlertTriangle size={20} />;
      default: return <Info size={20} />;
    }
  };

  const getToastClass = (type) => {
    switch (type) {
      case 'success': return 'toast-success';
      case 'error': return 'toast-error';
      case 'warning': return 'toast-warning';
      default: return 'toast-info';
    }
  };

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <div 
          key={toast.id} 
          className={`toast ${getToastClass(toast.type)}`}
        >
          <div className="toast-content">
            <div className="toast-icon">
              {getToastIcon(toast.type)}
            </div>
            <div className="toast-message">
              {toast.message}
            </div>
          </div>
          <button 
            onClick={() => removeToast(toast.id)}
            className="toast-close"
          >
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  );
};

export default Toast;
