import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App.jsx';
import { IdiomaProvider } from './i18n.jsx';
import './styles.css';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <IdiomaProvider>
        <App />
      </IdiomaProvider>
    </BrowserRouter>
  </React.StrictMode>
);
