// src/components/ChatbotWidget.js
import React, { useState, useEffect, useRef } from 'react';
import { Send } from 'lucide-react';
import { Input } from "./ui/Input";
import { Button } from "./ui/Button";
import { ScrollArea } from "./ui/ScrollArea";

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
   setMessages([...messages, newMessage]);
   setInput('');

   try {
     const response = await fetch('/api/chat', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ message: input }),
     });

     if (response.ok) {
       const data = await response.json();
       setMessages(prevMessages => [...prevMessages, { text: data.response, sender: 'bot' }]);
     } else {
       console.error('Error:', response.statusText);
     }
   } catch (error) {
     console.error('Error:', error);
   }
 };

 return (
   <div className="w-96 h-[500px] border border-gray-300 rounded-lg flex flex-col bg-white shadow-lg transition-all duration-300 ease-in-out hover:shadow-xl">
     <div className="bg-black text-white p-4 rounded-t-lg transition-all duration-300 ease-in-out">
       <h2 className="text-xl font-bold">Chatbot</h2>
     </div>
     <ScrollArea className="flex-grow p-4" ref={scrollAreaRef}>
       {messages.map((message, index) => (
         <div
           key={index}
           className={`mb-4 ${
             message.sender === 'user' ? 'text-right' : 'text-left'
           }`}
         >
           <span
             className={`inline-block p-2 rounded-lg transition-all duration-300 ease-in-out ${
               message.sender === 'user'
                 ? 'bg-black text-white'
                 : 'bg-gray-200 text-black'
             } transform hover:scale-105`}
           >
             {message.text}
           </span>
         </div>
       ))}
     </ScrollArea>
     <div className="p-4 border-t border-gray-300">
       <div className="flex">
         <Input
           type="text"
           value={input}
           onChange={(e) => setInput(e.target.value)}
           onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
           placeholder="Type your message..."
           className="flex-grow mr-2 transition-all duration-300 ease-in-out focus:ring-2 focus:ring-black"
         />
         <Button
           onClick={sendMessage}
           className="bg-black text-white hover:bg-gray-800 transition-all duration-300 ease-in-out transform hover:scale-105"
         >
           <Send className="h-4 w-4" />
         </Button>
       </div>
     </div>
   </div>
 );
};

export default ChatbotWidget;