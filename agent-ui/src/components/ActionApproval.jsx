
import React from 'react';

// Icons for different action types
const Icon = ({ path, className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
    <path strokeLinecap="round" strokeLinejoin="round" d={path} />
  </svg>
);
const ACTION_ICONS = {
  trash: <Icon path="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.134-2.033-2.134H8.033C6.91 2.75 6 3.704 6 4.884v.916m7.5 0a48.667 48.667 0 00-7.5 0" className="h-6 w-6 text-yellow-400" />,
  resize: <Icon path="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h18" className="h-6 w-6 text-blue-400" />,
  node: <Icon path="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" className="h-6 w-6 text-red-400" />,
};

const ActionItem = ({ action, onApprove, onReject }) => {
  const actionMeta = {
    POD_CLEANUP: { icon: ACTION_ICONS.trash, color: 'border-yellow-500/50' },
    RIGHTSIZING: { icon: ACTION_ICONS.resize, color: 'border-blue-500/50' },
    NODE_OPTIMIZATION: { icon: ACTION_ICONS.node, color: 'border-red-500/50' },
    PVC_CLEANUP: { icon: ACTION_ICONS.trash, color: 'border-yellow-500/50' },
    HPA_OPTIMIZATION: { icon: ACTION_ICONS.resize, color: 'border-blue-500/50' },
  };
  const meta = actionMeta[action.type] || {};

  return (
    <div className={`bg-gray-800/50 border-l-4 ${meta.color || 'border-gray-500/50'} p-4 rounded-r-lg mb-3 flex flex-col sm:flex-row items-start sm:items-center justify-between`}>
      <div className="flex items-center mb-3 sm:mb-0">
        {meta.icon}
        <div className="ml-4">
          <p className="font-bold text-white">{action.type.replace('_', ' ')}</p>
          <p className="text-sm text-gray-300">Target: <span className="font-mono bg-gray-700 px-1 rounded">{action.target}</span></p>
          <p className="text-sm text-gray-300">Namespace: <span className="font-mono bg-gray-700 px-1 rounded">{action.namespace || 'N/A'}</span></p>
        </div>
      </div>
      <div className="flex items-center self-end sm:self-center">
        <div className="text-right mr-6">
          <p className="text-lg font-bold text-green-400">${action.estimated_savings.toFixed(2)}</p>
          <p className="text-xs text-gray-400">Est. Monthly Savings</p>
        </div>
        <button onClick={() => onReject(action.id)} className="bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded mr-2 transition-colors">Reject</button>
        <button onClick={() => onApprove(action.id)} className="bg-green-600 hover:bg-green-500 text-white font-bold py-2 px-4 rounded transition-colors">Approve</button>
      </div>
    </div>
  );
};

const ActionApproval = ({ actions, onApprove, onReject }) => (
  <div className="bg-gray-800 p-6 rounded-lg shadow-lg mb-8">
    <h2 className="text-2xl font-bold mb-4 text-white">Action Approval (Human-in-the-Loop)</h2>
    <div className="space-y-4">
      {actions.length > 0 ? (
        actions.map(action => (
          <ActionItem key={action.id} action={action} onApprove={onApprove} onReject={onReject} />
        ))
      ) : (
        <div className="text-center py-8 text-gray-400">
          <svg className="mx-auto h-12 w-12 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <h3 className="mt-2 text-lg font-medium text-white">All Clear!</h3>
          <p className="mt-1 text-sm">No pending actions awaiting approval.</p>
        </div>
      )}
    </div>
  </div>
);

export default ActionApproval;