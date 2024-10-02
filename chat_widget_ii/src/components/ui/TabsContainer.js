import React from 'react';
import { NavLink } from 'react-router-dom';
import { useSpring, animated } from 'react-spring';

function TabsContainer() {
  const fadeIn = useSpring({
    from: { opacity: 0 },
    to: { opacity: 1 },
    config: { duration: 500 }
  });

  return (
    <animated.div style={fadeIn} className="tabs-container bg-gray-100 dark:bg-gray-700 p-2 rounded-t-lg">
      <nav className="flex space-x-2">
        <NavLink to="/" className={({ isActive }) =>
          `px-4 py-2 rounded-full transition-colors duration-200 ${
            isActive 
              ? 'bg-blue-500 text-white' 
              : 'text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`
        }>
          General Chat
        </NavLink>
        <NavLink to="/support" className={({ isActive }) =>
          `px-4 py-2 rounded-full transition-colors duration-200 ${
            isActive 
              ? 'bg-blue-500 text-white' 
              : 'text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`
        }>
          Support Chat
        </NavLink>
        <NavLink to="/sales" className={({ isActive }) =>
          `px-4 py-2 rounded-full transition-colors duration-200 ${
            isActive 
              ? 'bg-blue-500 text-white' 
              : 'text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`
        }>
          Sales Chat
        </NavLink>
      </nav>
    </animated.div>
  );
}

export default TabsContainer;