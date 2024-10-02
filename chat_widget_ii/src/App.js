// src/App.js
import React from 'react';
import ChatbotWidget from './components/ChatbotWidget';
import './App.css';

function App() {
  return (
    <div className="flex justify-center items-center min-h-screen p-4 bg-gray-100">
      <ChatbotWidget />
    </div>
  );
}

export default App;