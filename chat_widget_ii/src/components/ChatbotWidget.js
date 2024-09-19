import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User } from 'lucide-react';

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
    className={`w-full px-4 py-2 rounded-md border text-sm focus:outline-none focus:ring-2 transition-all duration-200 ease-in-out ${className}`}
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
  const scrollAreaRef = useRef(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (input.trim() === '') return;

    const newMessage = { text: input, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInput('');

    try {
      const response = await fetch('https://chat-widget-app-8c3cca0ff3c0.herokuapp.com/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages((prevMessages) => [...prevMessages, { text: data.response, sender: 'bot' }]);
      } else {
        console.error('Error:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="w-full h-screen flex flex-col bg-white shadow-lg overflow-hidden border border-gray-200 font-mono sm:max-w-3xl sm:mx-auto sm:rounded-lg">
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
        body { font-family: 'JetBrains Mono', monospace; }
      `}</style>
      <div className="bg-white p-4 border-b border-gray-200">
        <h2 className="text-xl font-bold text-black">AI Assistant</h2>
      </div>
      <ScrollArea className="flex-grow p-4 space-y-4 overflow-x-hidden" ref={scrollAreaRef}>
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`flex items-start space-x-2 max-w-full sm:max-w-[80%] ${
                message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'
              } animate-fadeIn`}
            >
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                message.sender === 'user' ? 'bg-black' : 'bg-gray-200'
              }`}>
                {message.sender === 'user' ?
                  <User size={16} className="text-white" /> :
                  <Bot size={16} className="text-black" />
                }
              </div>
              <span
                className={`p-3 rounded-lg text-sm break-words ${
                  message.sender === 'user'
                    ? 'bg-black text-white'
                    : 'bg-gray-100 text-black border border-gray-200'
                } shadow-sm animate-messageAppear text-left`}
              >
                {message.text}
              </span>
            </div>
          </div>
        ))}
      </ScrollArea>
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <Input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            className="flex-grow bg-white text-black placeholder-gray-400 border-gray-300 focus:ring-black focus:border-black"
          />
          <Button
            onClick={sendMessage}
            className="bg-black text-white hover:bg-gray-800 focus:ring-black hover:scale-105"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotWidget;