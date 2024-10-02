import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2, RefreshCw, Moon, Sun } from 'lucide-react';

import MarkdownRenderer from "./MarkdownRenderer";
import io from 'socket.io-client';

const API_URL = 'https://chat-widget-app-8c3cca0ff3c0.herokuapp.com/api/chat'

const Button = React.forwardRef(({ className, children, ...props }, ref) => (
  <button
    className={`px-3 py-2 rounded-md font-medium text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-200 ease-in-out ${className}`}
    ref={ref}
    {...props}
  >
    {children}
  </button>
));

const Input = React.forwardRef(({ className, ...props }, ref) => (
  <input
    className={`w-full px-4 py-2 rounded-md border text-base sm:text-sm focus:outline-none focus:ring-2 transition-all duration-200 ease-in-out ${className}`}
    ref={ref}
    {...props}
  />
));


const ScrollArea = React.forwardRef(({ className, children }, ref) => (
  <div
    className={`overflow-y-auto ${className}`}
    ref={ref}
  >
    {children}
  </div>
));


const ChatbotWidget = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const scrollAreaRef = useRef(null);
  const conversationIdRef = useRef(null);
  const [isTyping, setIsTyping] = useState(false);
  const socket = useRef(null);

    const startNewConversation = () => {
    // Generate a new conversation ID
    const newConversationId = `conversation-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    conversationIdRef.current = newConversationId;
    localStorage.setItem('conversationId', newConversationId);

    // Clear the messages
    setMessages([]);

    // Log the new conversation ID
    console.log("Started new conversation with ID:", newConversationId);
  };


  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
  // Generate a unique conversation ID when the component mounts
  const storedConversationId = localStorage.getItem('conversationId');
  if (storedConversationId) {
    conversationIdRef.current = storedConversationId;
  } else {
    const newConversationId = `conversation-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    conversationIdRef.current = newConversationId;
    localStorage.setItem('conversationId', newConversationId);
  }
  console.log("Current conversation ID:", conversationIdRef.current);
}, []);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerHeight < 500) { // Assuming keyboard is shown
        if (scrollAreaRef.current) {
          scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
        }
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  useEffect(() => {
  const originalStyle = window.getComputedStyle(document.body).overflow;
  document.body.style.overflow = 'hidden';

  return () => {
    document.body.style.overflow = originalStyle;
  };
}, []);

  useEffect(() => {
  socket.current = io(API_URL);
  socket.current.on('typing', () => setIsTyping(true));
  socket.current.on('stop_typing', () => setIsTyping(false));

  return () => socket.current.disconnect();
}, []);




  const sendMessage = async () => {
    if (input.trim() === '' || isLoading) return;

    const newMessage = { text: input, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInput('');
    setIsLoading(true);

      try {
    console.log("Sending message with conversation ID:", conversationIdRef.current);
    const response = await fetch(`${API_URL}/api/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: input,
    conversationId: conversationIdRef.current
  }),
});

    if (response.ok) {
      const data = await response.json();
      console.log("Received response:", data);
      setMessages((prevMessages) => [...prevMessages, { text: data.response, sender: 'bot' }]);
    } else {
      console.error('Error:', response.statusText);
      const errorData = await response.json();
      console.error('Error details:', errorData);
      setMessages((prevMessages) => [...prevMessages, { text: `Error: ${errorData.error || 'Unknown error'}`, sender: 'bot' }]);
    }
  } catch (error) {
    console.error('Error:', error);
    setMessages((prevMessages) => [...prevMessages, { text: `Error: ${error.message}`, sender: 'bot' }]);
  } finally {
    setIsLoading(false);
  }
};

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`font-sans ${darkMode ? 'dark' : ''}`}>
      <div className={`bg-white dark:bg-gray-800 shadow-lg rounded-lg overflow-hidden w-full h-full sm:max-w-md sm:h-[600px] flex flex-col fixed inset-0 sm:relative sm:inset-auto transition-colors duration-200`}>
        <div className={`bg-gray-50 dark:bg-gray-700 p-4 border-b border-gray-200 dark:border-gray-600 flex justify-between items-center`}>
          <h2 className={`text-xl font-bold text-gray-800 dark:text-white`}>AI Assistant</h2>
          <div className="flex space-x-2">
            <Button
              onClick={startNewConversation}
              className="bg-gray-200 text-gray-600 dark:bg-gray-600 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-500 focus:ring-gray-400 hover:scale-105"
              title="Start New Conversation"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button
              onClick={toggleDarkMode}
              className="bg-gray-200 text-gray-600 dark:bg-gray-600 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-500 focus:ring-gray-400 hover:scale-105"
              title="Toggle Dark Mode"
            >
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </div>
        </div>
        <ScrollArea className="flex-grow p-4 space-y-4 overflow-y-auto overflow-x-hidden bg-gray-50 dark:bg-gray-800" ref={scrollAreaRef}>
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`flex items-start space-x-2 max-w-[80%] ${
                  message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'
                } animate-fadeIn`}
              >
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.sender === 'user' ? 'bg-blue-500 dark:bg-blue-400' : 'bg-gray-300 dark:bg-gray-600'
                }`}>
                  {message.sender === 'user' ?
                    <User size={16} className="text-white" /> :
                    <Bot size={16} className="text-gray-800 dark:text-gray-200" />
                  }
                </div>
                <div
                  className={`p-3 rounded-lg text-sm break-words ${
                    message.sender === 'user'
                      ? 'bg-blue-500 text-white dark:bg-blue-400'
                      : 'bg-white text-gray-800 dark:bg-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-600'
                  } shadow-sm animate-messageAppear`}
                >
                  <MarkdownRenderer content={message.text} />
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
                <Loader2 className="animate-spin" />
                <span>Thinking...</span>
              </div>
            </div>
          )}
        </ScrollArea>
        <div className={`p-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600`}>
          <div className="flex items-center space-x-2">
            <Input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type your message..."
              className="flex-grow bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 border-gray-300 dark:border-gray-600 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500 dark:focus:border-blue-400"
              disabled={isLoading}
            />
            <Button
              onClick={sendMessage}
              className="bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-400 hover:scale-105 disabled:opacity-50 dark:bg-blue-400 dark:hover:bg-blue-500"
              disabled={isLoading}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotWidget;



