import React from 'react';
import { formatRelative } from 'date-fns';

const ActivityFeed = ({ activities }) => (
  <div className="bg-gray-800 p-6 rounded-lg shadow-lg mt-8">
    <h3 className="text-xl font-bold mb-4 text-white">Recent Activity</h3>
    <ul className="space-y-3 max-h-96 overflow-y-auto">
      {activities.length > 0 ? activities.map(act => (
        <li key={act.id} className="flex items-center text-sm">
          {act.status === 'EXECUTED' && <span className="text-green-400 font-bold">✔</span>}
          {act.status === 'REJECTED' && <span className="text-red-400 font-bold">✗</span>}
          {act.status === 'FAILED' && <span className="text-red-400 font-bold">!</span>}
          <span className="ml-3 text-gray-300">
            <span className={`font-semibold ${act.status === 'REJECTED' || act.status === 'FAILED' ? 'text-red-400' : 'text-green-400'}`}>{act.status.charAt(0) + act.status.slice(1).toLowerCase()}</span> {act.type.replace('_', ' ')} on <span className="font-mono bg-gray-700 px-1 rounded">{act.target}</span>
          </span>
          <span className="ml-auto text-xs text-gray-500">{act.executed_at ? formatRelative(new Date(act.executed_at), new Date()) : ''}</span>
        </li>
      )) : (
        <p className="text-gray-400 text-center py-4">No recent activities to display.</p>
      )}
    </ul>
  </div>
);

export default ActivityFeed;