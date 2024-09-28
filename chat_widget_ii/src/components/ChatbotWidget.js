import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2, Home, MessageSquare, Settings, X } from 'lucide-react';
import MarkdownRenderer from "./MarkdownRenderer";

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

const RadialMenu = ({ onSelect, isOpen, onClose }) => {
  const items = [
    { icon: <Home size={24} />, label: 'Home', value: 'home' },
    { icon: <MessageSquare size={24} />, label: 'Chatbot', value: 'chatbot' },
    { icon: <Settings size={24} />, label: 'Settings', value: 'settings' },
  ];

  return (
    <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center transition-opacity duration-300 ${isOpen ? 'opacity-100 z-50' : 'opacity-0 -z-10'}`}>
      <div className="relative w-64 h-64">
        {items.map((item, index) => {
          const angle = (index / items.length) * 2 * Math.PI - Math.PI / 2;
          const x = Math.cos(angle) * 100;
          const y = Math.sin(angle) * 100;
          return (
            <button
              key={item.value}
              className="absolute w-16 h-16 rounded-full bg-white shadow-lg flex items-center justify-center transform transition-all duration-300 hover:scale-110"
              style={{
                left: `calc(50% + ${x}px - 32px)`,
                top: `calc(50% + ${y}px - 32px)`,
              }}
              onClick={() => onSelect(item.value)}
            >
              {item.icon}
            </button>
          );
        })}
        <button
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-16 h-16 rounded-full bg-black text-white flex items-center justify-center"
          onClick={onClose}
        >
          <X size={24} />
        </button>
      </div>
    </div>
  );
};
const ChatbotWidget = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (input.trim() === '' || isLoading) return;

    const newMessage = { text: input, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInput('');
    setIsLoading(true);

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
        setMessages((prevMessages) => [...prevMessages, { text: 'Oops, something went wrong!', sender: 'bot' }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages((prevMessages) => [...prevMessages, { text: 'Oops, something went wrong!', sender: 'bot' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white shadow-lg rounded-lg overflow-hidden font-mono w-full sm:max-w-md">
      <div className="bg-white p-4 border-b border-gray-200">
        <h2 className="text-xl font-bold text-black">AI Assistant</h2>
      </div>
      <ScrollArea className="flex-grow p-4 space-y-4 overflow-x-hidden h-[400px]" ref={scrollAreaRef}>
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
      <div
        className={`p-3 rounded-lg text-sm break-words ${
          message.sender === 'user'
            ? 'bg-black text-white'
            : 'bg-gray-100 text-black border border-gray-200'
        } shadow-sm animate-messageAppear text-left`}
      >
        <MarkdownRenderer content={message.text} />
      </div>
    </div>
  </div>
))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center space-x-2">
              <Loader2 className="animate-spin" />
              <span className="text-gray-500">Typing...</span>
            </div>
          </div>
        )}
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
            disabled={isLoading}
          />
          <Button
            onClick={sendMessage}
            className="bg-black text-white hover:bg-gray-800 focus:ring-black hover:scale-105 disabled:opacity-50"
            disabled={isLoading}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotWidget;