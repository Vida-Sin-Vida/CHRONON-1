import React, { useEffect, useState } from 'react';

export default function Dashboard() {
    const [runs, setRuns] = useState([]);

    useEffect(() => {
        fetchRuns();
        const interval = setInterval(fetchRuns, 2000);
        return () => clearInterval(interval);
    }, []);

    const fetchRuns = async () => {
        try {
            const res = await fetch('/api/runs');
            const data = await res.json();
            setRuns(data);
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold border-b border-gray-700 pb-2">Active Runs</h2>
            <div className="bg-gray-800 rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-700">
                    <thead className="bg-gray-700">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Run ID</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Type</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Time</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Config</th>
                        </tr>
                    </thead>
                    <tbody className="bg-gray-800 divide-y divide-gray-700">
                        {runs.map((run) => (
                            <tr key={run.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-blue-400">{run.id}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">{run.type}</td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                    ${run.status === 'completed' ? 'bg-green-100 text-green-800' :
                                            run.status === 'running' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                                        {run.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{new Date(run.timestamp).toLocaleString()}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                                    {JSON.stringify(run.config).slice(0, 40)}
                                </td>
                            </tr>
                        ))}
                        {runs.length === 0 && (
                            <tr><td colSpan="5" className="px-6 py-4 text-center text-gray-500">No active runs found</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
