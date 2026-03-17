import React from 'react';
import { generateAnalysisReport } from './utils/pdfExport';

export const DownloadReportButton = ({ results }) => {
  const handleDownload = () => {
    generateAnalysisReport(results);
  };

  return (
    <button 
      className="btn-download-report" 
      onClick={handleDownload}
      style={{
        background: 'linear-gradient(135deg, #FF6B6B, #EE5A6F)',
        color: 'white',
        border: 'none',
        padding: '14px 28px',
        borderRadius: '12px',
        fontSize: '16px',
        fontWeight: '600',
        cursor: 'pointer',
        boxShadow: '0 4px 15px rgba(255,107,107,0.4)',
        transition: 'all 0.3s ease',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        margin: '20px auto'
      }}
      onMouseOver={(e) => {
        e.target.style.transform = 'translateY(-2px)';
        e.target.style.boxShadow = '0 6px 20px rgba(255,107,107,0.5)';
      }}
      onMouseOut={(e) => {
        e.target.style.transform = 'translateY(0)';
        e.target.style.boxShadow = '0 4px 15px rgba(255,107,107,0.4)';
      }}
    >
      📄 Download PDF Report
    </button>
  );
};
