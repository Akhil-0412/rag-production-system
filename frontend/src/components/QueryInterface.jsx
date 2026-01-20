import React, { useState } from 'react';
import axios from 'axios';
import { Send, User, Bot, Loader2, BookOpen } from 'lucide-react';

export default function QueryInterface() {
    const [query, setQuery] = useState("");
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);

    // Use environment variable or default to localhost:8000
    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        // Add user message
        const userMsg = { role: 'user', content: query };
        setHistory(prev => [...prev, userMsg]);
        setLimitLoading(true);

        try {
            const res = await axios.post(`${API_URL}/query`, {
                query: query
            });

            const data = res.data;

            const botMsg = {
                role: 'assistant',
                content: data.answer,
                sources: data.sources,
                model: data.model_used,
                latency: data.latency_ms
            };

            setHistory(prev => [...prev, botMsg]);
        } catch (err) {
            console.error(err);
            setHistory(prev => [...prev, { role: 'error', content: "Error fetching response." }]);
        } finally {
            setLimitLoading(false);
            setQuery("");
        }
    };

    // Need to fix setLimitLoading typo to setLoading
    const setLimitLoading = setLoading;

    return (
        <div className="flex flex-col h-[calc(100vh-100px)]">
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                {history.length === 0 && (
                    <div className="text-center text-gray-400 mt-20">
                        <Bot className="w-16 h-16 mx-auto mb-4 opacity-50" />
                        <p>Ask me anything about your documents!</p>
                    </div>
                )}

                {history.map((msg, idx) => (
                    <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 
              ${msg.role === 'user' ? 'bg-blue-600' : msg.role === 'error' ? 'bg-red-500' : 'bg-emerald-600'}`}>
                            {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
                        </div>

                        <div className={`max-w-[80%] rounded-lg p-4 shadow-sm 
              ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-gray-100'}`}>
                            <p className="whitespace-pre-wrap">{msg.content}</p>

                            {msg.role === 'assistant' && (
                                <div className="mt-4 pt-3 border-t border-gray-100 text-sm">
                                    <div className="flex items-center gap-4 text-gray-400 text-xs mb-2">
                                        <span>Model: {msg.model}</span>
                                        <span>Latency: {msg.latency?.toFixed(0)}ms</span>
                                    </div>

                                    {msg.sources && msg.sources.length > 0 && (
                                        <details className="group">
                                            <summary className="cursor-pointer text-blue-500 hover:text-blue-600 flex items-center gap-1 font-medium">
                                                <BookOpen className="w-3 h-3" />
                                                Show Sources ({msg.sources.length})
                                            </summary>
                                            <ul className="mt-2 space-y-2 text-gray-600 bg-gray-50 p-2 rounded">
                                                {msg.sources.map((src, i) => (
                                                    <li key={i} className="text-xs border-b border-gray-100 last:border-0 pb-1 last:pb-0">
                                                        <span className="font-bold text-gray-700">[{src.metadata?.source || "Source"}]</span>:
                                                        <span className="italic ml-1">"{src.text?.substring(0, 100)}..."</span>
                                                        <span className="text-gray-400 ml-2">(Score: {src.score?.toFixed(2)})</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </details>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-4">
                        <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center">
                            <Bot className="w-5 h-5 text-white" />
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-gray-100 flex items-center">
                            <Loader2 className="w-5 h-5 animate-spin text-gray-400 mr-2" />
                            <span className="text-gray-500">Thinking...</span>
                        </div>
                    </div>
                )}
            </div>

            <div className="p-4 bg-white border-t border-gray-200">
                <form onSubmit={handleSearch} className="flex gap-2">
                    <input
                        type="text"
                        className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="Type your question..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium flex items-center gap-2"
                    >
                        <Send className="w-4 h-4" /> Send
                    </button>
                </form>
            </div>
        </div>
    );
}
