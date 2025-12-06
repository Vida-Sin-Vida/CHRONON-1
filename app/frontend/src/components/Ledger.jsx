import React, { useEffect, useState } from 'react';

export default function Ledger() {
    const [rows, setRows] = useState([]);

    useEffect(() => {
        fetch('/api/ledger')
            .then(res => res.json())
            .then(data => setRows(data))
            .catch(err => console.error(err));
    }, []);

    const handleUnblind = async () => {
        const token = prompt("Enter Admin Token to Unblind:");
        if (!token) return;

        try {
            const res = await fetch('/api/unblind', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ admin_token: token })
            });
            const d = await res.json();
            alert(d.status); // or catch 403
        } catch (e) {
            alert("Error: " + e);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center border-b border-gray-700 pb-2">
                <h2 className="text-2xl font-bold">Protocol Ledger</h2>
                <button
                    onClick={handleUnblind}
                    className="bg-red-900 border border-red-700 text-red-100 px-4 py-2 rounded hover:bg-red-800 transition"
                >
                    UNBLIND RESULTS
                </button>
            </div>

            <div className="bg-gray-800 rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-700">
                        <thead className="bg-gray-700">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Timestamp</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Run ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Verdict</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Config Hash</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Code Hash</th>
                            </tr>
                        </thead>
                        <tbody className="bg-gray-800 divide-y divide-gray-700 text-sm text-gray-300">
                            {rows.map((row, idx) => (
                                <tr key={idx}>
                                    <td className="px-6 py-4 whitespace-nowrap">{new Date(row.timestamp).toLocaleString()}</td>
                                    <td className="px-6 py-4 whitespace-nowrap font-mono text-yellow-400">{row.run_id}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">{row.verdict}</td>
                                    <td className="px-6 py-4 whitespace-nowrap font-mono text-gray-500 text-xs">{row.hash_config?.slice(0, 10)}...</td>
                                    <td className="px-6 py-4 whitespace-nowrap font-mono text-gray-500 text-xs">{row.hash_code?.slice(0, 10)}...</td>
                                </tr>
                            ))}
                            {rows.length === 0 && (
                                <tr><td colSpan="5" className="px-6 py-4 text-center text-gray-500">No ledger entries found (start a run correctly)</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
