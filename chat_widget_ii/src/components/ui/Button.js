// src/components/ui/Button.js
import React from 'react';

export const Button = ({className, ...props}) => (
    <button
        className={`p-2 rounded transition-all duration-300 ease-in-out transform hover:scale-105 hover:shadow-md ${className}`}
        {...props}
    />
);