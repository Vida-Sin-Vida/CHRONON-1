import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import Runner from './components/Runner';
import Ledger from './components/Ledger';

export default function App() {
    const [activeTab, setActiveTab] = useState('dashboard');

    return (
        <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col">
            <header className="bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between">
                <h1 className="text-xl font-bold tracking-tight text-blue-400">CHRONON-1 <span className="text-gray-500 text-sm font-normal">Protocol Interface</span></h1>
                <nav className="flex space-x-4">
                    <button onClick={() => setActiveTab('dashboard')} className={`px-3 py-2 rounded-md transition ${activeTab === 'dashboard' ? 'bg-blue-600 text-white' : 'hover:bg-gray-700'}`}>Dashboard</button>
                    <button onClick={() => setActiveTab('runner')} className={`px-3 py-2 rounded-md transition ${activeTab === 'runner' ? 'bg-blue-600 text-white' : 'hover:bg-gray-700'}`}>New Run</button>
                    <button onClick={() => setActiveTab('ledger')} className={`px-3 py-2 rounded-md transition ${activeTab === 'ledger' ? 'bg-blue-600 text-white' : 'hover:bg-gray-700'}`}>Ledger</button>
                </nav>
            </header>

            <main className="flex-1 p-6 overflow-auto">
                {activeTab === 'dashboard' && <Dashboard />}
                {activeTab === 'runner' && <Runner />}
                {activeTab === 'ledger' && <Ledger />}
            </main>
        </div>
    );
}
