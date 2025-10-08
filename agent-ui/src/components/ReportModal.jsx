import React from 'react';
import { format } from 'date-fns';

const StatusBadge = ({ status }) => {
    const statusStyles = {
        APPROVED: 'bg-blue-900 text-blue-300',
        EXECUTED: 'bg-green-900 text-green-300',
        REJECTED: 'bg-red-900 text-red-300',
        FAILED: 'bg-red-900 text-red-300',
        PENDING: 'bg-yellow-900 text-yellow-300',
    };
    return <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusStyles[status] || 'bg-gray-700 text-gray-300'}`}>{status}</span>;
};

const ActionDetailRow = ({ action }) => (
    <div className="p-3 bg-gray-700/50 rounded-md">
        <div className="flex justify-between items-center">
            <div>
                <p className="font-bold text-white">{action.type.replace('_', ' ')}</p>
                <p className="text-xs text-gray-400">Target: <span className="font-mono">{action.target}</span></p>
                <p className="text-xs text-gray-400">Namespace: <span className="font-mono">{action.namespace || 'N/A'}</span></p>
            </div>
            <div className="flex items-center">
                <span className="text-green-400 font-bold mr-4">${action.estimated_savings.toFixed(2)}</span>
                <StatusBadge status={action.status} />
            </div>
        </div>
        {action.type === 'RIGHTSIZING' && action.action_details && (
            <div className="text-xs mt-2 text-gray-400 border-t border-gray-600 pt-2">
                <p>Container: <span className="font-mono text-gray-200">{action.action_details.container}</span></p>
                <div className="flex justify-between mt-1 items-center">
                <span>Current: <span className="font-mono text-yellow-400">{action.action_details.current_requests?.cpu || 'N/A'}, {action.action_details.current_requests?.memory || 'N/A'}</span></span>
                <span className="font-bold mx-2 text-gray-200">&rarr;</span>
                <span>Rec: <span className="font-mono text-green-400">{action.action_details.recommended_requests?.cpu || 'N/A'}, {action.action_details.recommended_requests?.memory || 'N/A'}</span></span>
                </div>
            </div>
        )}
    </div>
);

const ReportModal = ({ report, onClose }) => {
  if (!report) return null;

  const reportDetails = report.report || {};
  const actions = report.actions || [];

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-20" onClick={onClose}>
      <div className="bg-gray-800 rounded-lg shadow-2xl p-8 max-w-3xl w-full mx-4 max-h-[90vh] flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4 flex-shrink-0">
          <h2 className="text-2xl font-bold text-white">Optimization Report</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">&times;</button>
        </div>
        
        <div className="overflow-y-auto pr-2">
            <div className="mb-6 border-b border-gray-700 pb-4">
                <p className="font-mono text-sm text-blue-400">{report.run_id}</p>
                <p className="text-xs text-gray-400">
                  Completed on {reportDetails.timestamp ? format(new Date(reportDetails.timestamp), 'PPpp') : 'In Progress...'}
                </p>
            </div>
            
            <div className="mb-6">
                <h4 className="font-semibold text-lg text-white mb-2">AI Analysis Summary</h4>
                <p className="text-gray-300 bg-gray-900 p-4 rounded-md italic">"{reportDetails.ai_analysis_summary || 'N/A'}"</p>
            </div>

            <div className="mb-6">
                <h4 className="font-semibold text-lg text-white mb-2">Actions from this Run ({actions.length})</h4>
                <div className="space-y-2">
                    {actions.length > 0 ? (
                        actions.map(action => <ActionDetailRow key={action.id} action={action} />)
                    ) : (
                        <p className="text-gray-400 text-center py-4">No actions were generated in this run.</p>
                    )}
                </div>
            </div>
        </div>

        <div className="mt-6 text-right border-t border-gray-700 pt-4 flex-shrink-0">
          <button onClick={onClose} className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded transition-colors">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReportModal;