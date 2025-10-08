import React, { useState, useEffect, useCallback } from 'react';
import { format } from 'date-fns';
import * as api from '../api';
import ReportModal from '../components/ReportModal';
import Notification from '../components/Notification';

// --- NEW HELPER FUNCTION TO SAFELY PARSE THE RUN ID ---
const parseDateFromRunId = (runId) => {
    try {
        // Expects run_YYYYMMDD_HHMMSS format
        const parts = runId.split('_');
        if (parts.length < 3) return null;

        const datePart = parts[1]; // "20251008"
        const timePart = parts[2]; // "090512"

        if (datePart.length !== 8 || timePart.length !== 6) return null;

        const year = datePart.substring(0, 4);
        const month = datePart.substring(4, 6);
        const day = datePart.substring(6, 8);
        const hour = timePart.substring(0, 2);
        const minute = timePart.substring(2, 4);
        const second = timePart.substring(4, 6);

        // Construct a valid ISO 8601 string: "2025-10-08T09:05:12Z"
        const isoString = `${year}-${month}-${day}T${hour}:${minute}:${second}Z`;
        const date = new Date(isoString);
        // Check if the created date is valid
        if (isNaN(date.getTime())) return null;
        return date;
    } catch (e) {
        console.error("Failed to parse date from run_id:", runId, e);
        return null; // Return null if parsing fails
    }
};


const Reports = () => {
    const [runs, setRuns] = useState([]);
    const [selectedReport, setSelectedReport] = useState(null);
    const [notification, setNotification] = useState(null);

    const showNotification = (message, type = 'info') => {
        setNotification({ message, type, id: Date.now() });
    };

    const fetchData = useCallback(async () => {
        try {
            const runsData = await api.getRuns();
            setRuns(runsData);
        } catch (error) {
            showNotification('Failed to fetch reports.', 'error');
        }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll for updates
        return () => clearInterval(interval);
    }, [fetchData]);

    const handleViewDetails = async (runId) => {
        try {
            const detailedRun = await api.getRunDetails(runId);
            setSelectedReport(detailedRun);
        } catch (error) {
            showNotification('Failed to fetch report details.', 'error');
        }
    };
    
    return (
        <>
            {notification && <Notification key={notification.id} message={notification.message} type={notification.type} onClose={() => setNotification(null)} />}
            <ReportModal report={selectedReport} onClose={() => setSelectedReport(null)} />

            <h2 className="text-3xl font-bold text-white mb-6">Past Optimization Reports</h2>
            <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-700">
                    <thead className="bg-gray-700/50">
                        <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Run ID</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Timestamp</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Actions Generated</th>
                            <th scope="col" className="relative px-6 py-3"><span className="sr-only">View</span></th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                        {runs.length > 0 ? runs.map((run) => {
                            // --- CLEANER AND SAFER TIMESTAMP LOGIC ---
                            const timestamp = run.report?.timestamp 
                                ? new Date(run.report.timestamp) 
                                : parseDateFromRunId(run.run_id);

                            return (
                                <tr key={run.run_id} className="hover:bg-gray-700/40">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-blue-400">{run.run_id}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                        {timestamp ? format(timestamp, 'PPpp') : 'Pending...'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                            run.status === 'COMPLETED' ? 'bg-green-900 text-green-300' : 
                                            run.status === 'RUNNING' ? 'bg-yellow-900 text-yellow-300' : 
                                            run.status === 'FAILED' ? 'bg-red-900 text-red-300' : 'bg-gray-700 text-gray-300'
                                        }`}>
                                            {run.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{run.actions.length}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button 
                                            onClick={() => handleViewDetails(run.run_id)} 
                                            disabled={run.status !== 'COMPLETED'}
                                            className="text-blue-400 hover:text-blue-300 disabled:text-gray-500 disabled:cursor-not-allowed"
                                        >
                                            View Details
                                        </button>
                                    </td>
                                </tr>
                            );
                        }) : (
                            <tr><td colSpan="5" className="text-center py-12 text-gray-400">No reports found. Run an analysis to get started.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </>
    );
};

export default Reports;

