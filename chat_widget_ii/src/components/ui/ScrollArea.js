import React, { useState, useEffect, useRef } from 'react';

export const ScrollArea = React.forwardRef(({
  className = '',
  children,
  maxHeight = '400px',
  scrollbarWidth = 'thin',
  scrollbarColor = 'rgba(155, 155, 155, 0.7) transparent',
  fadeTop = true,
  fadeBottom = true,
  ...props
}, ref) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isScrolledToBottom, setIsScrolledToBottom] = useState(false);
  const contentRef = useRef(null);

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    setIsScrolled(scrollTop > 0);
    setIsScrolledToBottom(scrollHeight - scrollTop === clientHeight);
  };

  useEffect(() => {
    const content = contentRef.current;
    if (content) {
      content.addEventListener('scroll', handleScroll);
      return () => content.removeEventListener('scroll', handleScroll);
    }
  }, []);

  return (
    <div className="relative" style={{ maxHeight }}>
      <div
        ref={(node) => {
          contentRef.current = node;
          if (typeof ref === 'function') ref(node);
          else if (ref) ref.current = node;
        }}
        className={`
          overflow-y-auto
          ${className}
          scrollbar-${scrollbarWidth}
          hover:shadow-inner
          transition-all duration-300 ease-in-out
        `}
        style={{
          scrollbarColor,
          maxHeight,
          scrollbarWidth,
        }}
        {...props}
      >
        {children}
      </div>
      {fadeTop && (
        <div
          className={`
            absolute top-0 left-0 right-0 h-8
            bg-gradient-to-b from-white to-transparent
            pointer-events-none
            transition-opacity duration-300
            ${isScrolled ? 'opacity-100' : 'opacity-0'}
          `}
        />
      )}
      {fadeBottom && (
        <div
          className={`
            absolute bottom-0 left-0 right-0 h-8
            bg-gradient-to-t from-white to-transparent
            pointer-events-none
            transition-opacity duration-300
            ${isScrolledToBottom ? 'opacity-0' : 'opacity-100'}
          `}
        />
      )}
    </div>
  );
});