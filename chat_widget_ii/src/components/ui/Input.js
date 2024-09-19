import React, { useState, useRef, useEffect } from 'react';

export const Input = React.forwardRef(({ className, onInputChange, ...props }, ref) => {
  const [isFocused, setIsFocused] = useState(false);
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleChange = (e) => {
    setMessage(e.target.value);
    if (onInputChange) {
      onInputChange(e.target.value);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      // You can add logic here if needed when Enter is pressed
    }
  };

  return (
    <div className="relative w-11/12 max-w-3xl">
      <textarea
        ref={(node) => {
          textareaRef.current = node;
          if (typeof ref === 'function') {
            ref(node);
          } else if (ref) {
            ref.current = node;
          }
        }}
        value={message}
        onChange={handleChange}
        onKeyPress={handleKeyPress}
        className={`
          w-full
          px-4 py-2
          text-base
          bg-gradient-to-r from-purple-50 to-orange-50
          border-2 border-transparent
          rounded-lg
          transition-all duration-300 ease-in-out
          focus:outline-none focus:border-transparent
          placeholder-gray-400
          text-gray-800
          resize-none
          ${isFocused ? 'shadow-lg shadow-purple-200' : 'shadow-sm'}
          ${className}
        `}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder="Type your message..."
        rows={1}
        {...props}
      />
      <div
        className={`
          absolute bottom-0 left-0 w-full h-0.5 
          bg-gradient-to-r from-purple-500 to-orange-500
          transition-all duration-300 
          ${isFocused ? 'scale-x-100' : 'scale-x-0'}
        `}
      ></div>
    </div>
  );
});