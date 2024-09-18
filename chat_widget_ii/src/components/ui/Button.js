// src/components/ui/Button.js
import React from 'react';
import { Sparkles } from 'lucide-react';

export const Button = React.forwardRef(
  (
    {
      variant = 'primary',
      type = 'button',
      disabled = false,
      className = '',
      children,
      ...props
    },
    ref
  ) => {
    const baseClasses =
      'p-4 rounded-full transition-transform duration-500 ease-in-out transform focus:outline-none focus:ring-4 focus:ring-offset-2';
    const variantClasses = {
      primary:
        'bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 text-white shadow-lg hover:shadow-2xl',
      secondary:
        'bg-gradient-to-r from-green-400 via-blue-500 to-purple-600 text-white shadow-lg hover:shadow-2xl',
    };
    const disabledClasses = disabled
      ? 'opacity-50 cursor-not-allowed'
      : 'hover:scale-110';
    const combinedClasses = `
      ${baseClasses}
      ${variantClasses[variant] || ''}
      ${disabledClasses}
      ${className}
    `.trim();

    return (
      <button
        type={type}
        className={combinedClasses}
        disabled={disabled}
        ref={ref}
        {...props}
      >
        <span className="flex items-center justify-center space-x-2">
          <Sparkles className="w-6 h-6 animate-pulse" />
          <span>{children}</span>
        </span>
      </button>
    );
  }
);