import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import "./API/axiosConfig"; 

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
    <App />
);

