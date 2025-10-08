import React from 'react';

const Icon = ({ path, className }) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
    <path strokeLinecap="round" strokeLinejoin="round" d={path} />
  </svg>
);
const ACTION_ICONS = {
  trash: <Icon path="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.134-2.033-2.134H8.033C6.91 2.75 6 3.704 6 4.884v.916m7.5 0a48.667 48.667 0 00-7.5 0" className="h-8 w-8 text-yellow-400" />,
  resize: <Icon path="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h18" className="h-8 w-8 text-blue-400" />,
  node: <Icon path="M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" className="h-8 w-8 text-red-400" />,
};

const RightsizingDetails = ({ details }) => (
  <div className="text-xs mt-2 text-gray-400">
    <p>Container: <span className="font-mono text-gray-200">{details.container}</span></p>
    <div className="flex justify-between mt-1">
      <span>Current: <span className="font-mono text-yellow-400">{details.current_requests?.cpu || 'N/A'} CPU, {details.current_requests?.memory || 'N/A'} RAM</span></span>
      <span className="font-bold mx-2 text-gray-200">&rarr;</span>
      <span>Rec: <span className="font-mono text-green-400">{details.recommended_requests?.cpu || 'N/A'} CPU, {details.recommended_requests?.memory || 'N/A'} RAM</span></span>
    </div>
  </div>
);

const ActionCard = ({ action, onApprove, onReject }) => {
  const actionMeta = {
    POD_CLEANUP: { icon: ACTION_ICONS.trash, color: 'border-yellow-500/50' },
    RIGHTSIZING: { icon: ACTION_ICONS.resize, color: 'border-blue-500/50' },
    NODE_OPTIMIZATION: { icon: ACTION_ICONS.node, color: 'border-red-500/50' },
    PVC_CLEANUP: { icon: ACTION_ICONS.trash, color: 'border-yellow-500/50' },
    HPA_OPTIMIZATION: { icon: ACTION_ICONS.resize, color: 'border-blue-500/50' },
  };
  const meta = actionMeta[action.type] || {};

  return (
    <div className={`bg-gray-800/50 border-l-4 ${meta.color || 'border-gray-500/50'} rounded-r-lg p-4 flex flex-col justify-between shadow-lg`}>
      <div>
        <div className="flex items-start justify-between">
            <div className="flex items-center">
              {meta.icon}
              <div className="ml-3">
                <p className="font-bold text-white text-lg">{action.type.replace('_', ' ')}</p>
                <p className="text-xs text-gray-400">Confidence: {(action.confidence * 100).toFixed(0)}%</p>
              </div>
            </div>
            <div className="text-right">
                <p className="text-xl font-bold text-green-400">${action.estimated_savings.toFixed(2)}</p>
                <p className="text-xs text-gray-400">Est. Savings</p>
            </div>
        </div>
        <div className="mt-4 text-sm text-gray-300 space-y-1">
          <p>Target: <span className="font-mono bg-gray-700 px-2 py-0.5 rounded">{action.target}</span></p>
          <p>Namespace: <span className="font-mono bg-gray-700 px-2 py-0.5 rounded">{action.namespace || 'N/A'}</span></p>
        </div>
        {action.type === 'RIGHTSIZING' && <RightsizingDetails details={action.action_details} />}
      </div>
      <div className="flex items-center mt-4 pt-4 border-t border-gray-700/50">
        <button onClick={() => onReject(action.id)} className="w-full bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded mr-2 transition-colors">Reject</button>
        <button onClick={() => onApprove(action.id)} className="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-2 px-4 rounded transition-colors">Approve</button>
      </div>
    </div>
  );
};

export default ActionCard;