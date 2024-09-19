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
      'p-2 rounded-full transition-transform duration-300 ease-in-out transform focus:outline-none focus:ring-2 focus:ring-offset-1';
    const variantClasses = {
      primary:
        'bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 text-white shadow-md hover:shadow-lg',
      secondary:
        'bg-gradient-to-r from-green-400 via-blue-500 to-purple-600 text-white shadow-md hover:shadow-lg',
    };
    const disabledClasses = disabled
      ? 'opacity-50 cursor-not-allowed'
      : 'hover:scale-105';
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
        <span className="flex items-center justify-center space-x-1">
          <Sparkles className="w-4 h-4 animate-pulse" />
          <span className="text-sm">{children}</span>
        </span>
      </button>
    );
  }
);