   // src/App.js
   import React from 'react';
   import ChatbotWidget from './components/ChatbotWidget';
   import './App.css';

   function App() {
     return (
       <div className="App">
         <header className="App-header">
           <h1>React Chatbot Widget</h1>
           <ChatbotWidget />
         </header>
       </div>
     );
   }

   export default App;