import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Jan', Users: 4000, Conversations: 2400, Satisfaction: 2400 },
  { name: 'Feb', Users: 3000, Conversations: 1398, Satisfaction: 2210 },
  { name: 'Mar', Users: 2000, Conversations: 9800, Satisfaction: 2290 },
  { name: 'Apr', Users: 2780, Conversations: 3908, Satisfaction: 2000 },
  { name: 'May', Users: 1890, Conversations: 4800, Satisfaction: 2181 },
  { name: 'Jun', Users: 2390, Conversations: 3800, Satisfaction: 2500 },
  { name: 'Jul', Users: 3490, Conversations: 4300, Satisfaction: 2100 },
];

const Dashboard = () => {
  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">Dashboard</h2>
      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-2 text-gray-700 dark:text-gray-300">Key Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-100 dark:bg-blue-800 p-4 rounded-lg">
            <h4 className="text-lg font-medium text-blue-800 dark:text-blue-200">Total Users</h4>
            <p className="text-3xl font-bold text-blue-600 dark:text-blue-300">15,234</p>
          </div>
          <div className="bg-green-100 dark:bg-green-800 p-4 rounded-lg">
            <h4 className="text-lg font-medium text-green-800 dark:text-green-200">Active Conversations</h4>
            <p className="text-3xl font-bold text-green-600 dark:text-green-300">1,234</p>
          </div>
          <div className="bg-purple-100 dark:bg-purple-800 p-4 rounded-lg">
            <h4 className="text-lg font-medium text-purple-800 dark:text-purple-200">Satisfaction Rate</h4>
            <p className="text-3xl font-bold text-purple-600 dark:text-purple-300">92%</p>
          </div>
        </div>
      </div>
      <div>
        <h3 className="text-xl font-semibold mb-2 text-gray-700 dark:text-gray-300">Monthly Overview</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="Users" fill="#3b82f6" />
            <Bar dataKey="Conversations" fill="#10b981" />
            <Bar dataKey="Satisfaction" fill="#8b5cf6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Dashboard;