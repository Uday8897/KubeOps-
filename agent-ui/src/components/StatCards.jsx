import React from 'react';

const Icon = ({ path, className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
    <path strokeLinecap="round" strokeLinejoin="round" d={path} />
  </svg>
);
const ICONS = {
  dollar: <Icon path="M12 6v12m-3-2.818l.879.879A3 3 0 1013 19.518l.879-.879M12 6a3 3 0 00-3 3v.382m6 0V9a3 3 0 00-3-3z" className="h-6 w-6 text-green-400" />,
  check: <Icon path="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" className="h-6 w-6 text-blue-400" />,
  pending: <Icon path="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" className="h-6 w-6 text-yellow-400" />,
};

const StatCard = ({ title, value, icon }) => (
  <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
    <div className="flex items-center">
      <div className="bg-gray-700 p-3 rounded-full">{icon}</div>
      <div className="ml-4">
        <p className="text-sm font-medium text-gray-400">{title}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
      </div>
    </div>
  </div>
);

const StatCards = ({ stats }) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
    <StatCard title="Total Monthly Savings" value={`$${stats.totalSavings.toFixed(2)}`} icon={ICONS.dollar} />
    <StatCard title="Actions Executed" value={stats.actionsExecuted} icon={ICONS.check} />
    <StatCard title="Pending Actions" value={stats.pendingActions} icon={ICONS.pending} />
  </div>
);

export default StatCards;