import React from 'react';

export const ScrollArea = React.forwardRef(({className, children}, ref) => (
    <div
        className={`overflow-y-auto ${className} p-4 transition-all duration-300 ease-in-out hover:shadow-inner hover:bg-gray-50`}
        ref={ref}>
        {children}
    </div>
));