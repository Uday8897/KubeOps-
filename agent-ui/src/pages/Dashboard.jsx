import React, { useState, useEffect, useCallback } from 'react';
import * as api from '../api';
import StatCards from '../components/StatCards';
import ActionCard from '../components/ActionCard';
import ActivityFeed from '../components/ActivityFeed';
import Notification from '../components/Notification';

function Dashboard() {
  const [stats, setStats] = useState({ totalSavings: 0, actionsExecuted: 0, pendingActions: 0 });
  const [pendingActions, setPendingActions] = useState([]);
  const [activities, setActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type, id: Date.now() });
  };

  const fetchData = useCallback(async () => {
    try {
      const [statsData, pendingData, activityData] = await Promise.all([
        api.getStats(),
        api.getPendingActions(),
        api.getActivityLog(),
      ]);
      setStats(statsData);
      setPendingActions(pendingData);
      setActivities(activityData);
    } catch (error) {
      showNotification('Failed to fetch dashboard data.', 'error');
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleAction = async (actionId, endpoint) => {
    const actionName = endpoint === 'approveAction' ? 'approve' : 'reject';
    try {
      await api[endpoint](actionId);
      showNotification(`Action ${actionName}d successfully!`, 'success');
      fetchData();
    } catch (error) {
      showNotification(`Error: ${error.message}`, 'error');
    }
  };
  
  const handleRunOptimization = async () => {
    setIsLoading(true);
    showNotification('New analysis run has been started...', 'info');
    try {
      const response = await api.runOptimization(false);
      showNotification(`Analysis run '${response.run_id}' is scheduled.`, 'success');
      setTimeout(fetchData, 3000);
    } catch (error) {
      showNotification(`Error starting analysis: ${error.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {notification && <Notification key={notification.id} message={notification.message} type={notification.type} onClose={() => setNotification(null)} />}
      
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-white">Dashboard</h2>
        <button onClick={handleRunOptimization} disabled={isLoading} className="bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded transition-colors flex items-center shadow-lg">
          {isLoading && <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>}
          {isLoading ? 'Analyzing...' : 'Run New Analysis'}
        </button>
      </div>
      
      <StatCards stats={stats} />
      
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg my-8">
        <h2 className="text-2xl font-bold mb-4 text-white">Action Approval (Human-in-the-Loop)</h2>
        {pendingActions.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pendingActions.map(action => (
              <ActionCard key={action.id} action={action} onApprove={(id) => handleAction(id, 'approveAction')} onReject={(id) => handleAction(id, 'rejectAction')} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-400">
            <svg className="mx-auto h-12 w-12 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <h3 className="mt-2 text-lg font-medium text-white">All Clear!</h3>
            <p className="mt-1 text-sm">No pending actions awaiting approval.</p>
          </div>
        )}
      </div>
      
      <ActivityFeed activities={activities} />
    </>
  );
}

export default Dashboard;
