import React, { useState } from 'react';
import LogViewer from './LogViewer';

export default function Runner() {
    const [commandType, setCommandType] = useState('simulate');
    const [config, setConfig] = useState('{"eps": 0.001, "output": "data/raw/pype_sim.csv"}');
    const [activeRunId, setActiveRunId] = useState(null);

    const handleLaunch = async () => {
        try {
            const args = JSON.parse(config);
            const res = await fetch('/api/runs/launch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command_type: commandType, args })
            });
            const data = await res.json();
            setActiveRunId(data.run_id);
        } catch (e) {
            alert("Launch failed: " + e);
        }
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-full">
            <div className="bg-gray-800 p-6 rounded-lg shadow h-fit">
                <h3 className="text-xl font-bold mb-4">Launch New Run</h3>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-300">Command Type</label>
                        <select
                            value={commandType}
                            onChange={e => setCommandType(e.target.value)}
                            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-600 bg-gray-700 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md text-white"
                        >
                            <option value="simulate">Simulate</option>
                            <option value="ingest">Ingest</option>
                            <option value="preprocess">Preprocess</option>
                            <option value="analyze">Analyze</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300">Configuration (JSON)</label>
                        <textarea
                            value={config}
                            onChange={e => setConfig(e.target.value)}
                            rows={8}
                            className="mt-1 block w-full border border-gray-600 rounded-md shadow-sm py-2 px-3 bg-gray-900 text-gray-100 font-mono text-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                        <p className="mt-2 text-xs text-gray-400">
                            Arguments passed to CLI. E.g. {"{ 'input_file': '...', 'eps': 0.0 }"}
                        </p>
                    </div>

                    <button
                        onClick={handleLaunch}
                        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        Launch Process
                    </button>
                </div>
            </div>

            <div className="bg-gray-900 border border-gray-700 rounded-lg p-2 h-[600px] flex flex-col">
                <h4 className="text-sm font-medium text-gray-400 mb-2 px-2">Live Logs {activeRunId && `(Run ${activeRunId})`}</h4>
                <div className="flex-1 bg-black rounded overflow-hidden">
                    {activeRunId ? (
                        <LogViewer runId={activeRunId} />
                    ) : (
                        <div className="h-full flex items-center justify-center text-gray-600">
                            Waiting to start...
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
