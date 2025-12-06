import React, { useEffect, useState, useRef } from 'react';

export default function LogViewer({ runId }) {
    const [logs, setLogs] = useState([]);
    const bottomRef = useRef(null);

    useEffect(() => {
        setLogs([]);
        if (!runId) return;

        // Determine WS URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // Use proxy in dev, or direct relative in prod if configured
        const host = window.location.host;
        // If dev server (3000/5173) -> proxy -> ws://localhost:8000
        // If prod -> ws://host/ws
        const wsUrl = `ws://127.0.0.1:8000/ws/runs/${runId}/logs`; // Hardcoded for this demo setup

        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("Connected to logs");
        };

        ws.onmessage = (event) => {
            setLogs(prev => [...prev, event.data]);
        };

        ws.onclose = () => {
            console.log("Disconnected logs");
        };

        return () => {
            ws.close();
        };
    }, [runId]);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    return (
        <div className="h-full overflow-auto p-4 font-mono text-xs text-green-400 bg-black">
            {logs.map((line, i) => (
                <div key={i} className="whitespace-pre-wrap break-all">{line}</div>
            ))}
            <div ref={bottomRef} />
        </div>
    );
}
