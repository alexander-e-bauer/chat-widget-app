import React from 'react';

export const Input = ({className, ...props}) => (
    <input
        className={`border p-2 rounded transition-all duration-300 ease-in-out focus:ring-2 focus:ring-black text-black ${className}`} {...props} />
);