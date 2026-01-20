import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BarChart2, Zap, DollarSign, Activity } from 'lucide-react';
import { API_URL } from '../config';

export default function MetricsDashboard() {
    const [metrics, setMetrics] = useState([]);
    const [summary, setSummary] = useState({ total: 0, avgLatency: 0, cost: 0 });

    const fetchMetrics = async () => {
        try {
            const res = await axios.get(`${API_URL}/metrics/recent?limit=50`);
            const data = res.data; // List of records

            // Transform for chart
            // timestamp is float, convert to meaningful time
            const chartData = data.map((m, i) => ({
                ...m,
                time: new Date(m.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                idx: i
            }));
            setMetrics(chartData);

            // Calculate summary
            const total = data.length;
            const totalLat = data.reduce((acc, curr) => acc + curr.latency_ms, 0);
            const totalCost = data.reduce((acc, curr) => acc + (curr.cost || 0), 0);

            setSummary({
                total,
                avgLatency: total ? Math.round(totalLat / total) : 0,
                cost: totalCost
            });

        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card
                    title="Total Requests"
                    value={summary.total}
                    icon={<BarChart2 className="text-blue-500" />}
                    desc="Last 50 requests"
                />
                <Card
                    title="Avg Latency"
                    value={`${summary.avgLatency}ms`}
                    icon={<Activity className="text-emerald-500" />}
                    desc="Response time"
                />
                <Card
                    title="Est. Cost"
                    value={`$${summary.cost.toFixed(4)}`}
                    icon={<DollarSign className="text-yellow-500" />}
                    desc="LLM usage"
                />
            </div>

            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-[400px]">
                <h3 className="text-lg font-semibold mb-4 text-slate-800">Latency Trend</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={metrics}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
                        <XAxis dataKey="time" fontSize={12} stroke="#888" />
                        <YAxis fontSize={12} stroke="#888" />
                        <Tooltip
                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        />
                        <Line
                            type="monotone"
                            dataKey="latency_ms"
                            stroke="#2563eb"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 6 }}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50 text-slate-500">
                        <tr>
                            <th className="p-4 font-medium">Time</th>
                            <th className="p-4 font-medium">Query</th>
                            <th className="p-4 font-medium">Model</th>
                            <th className="p-4 font-medium">Latency</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {[...metrics].reverse().slice(0, 10).map((m, i) => (
                            <tr key={i} className="hover:bg-slate-50">
                                <td className="p-4 text-gray-500">{m.time}</td>
                                <td className="p-4 font-medium text-slate-800 truncate max-w-[200px]">{m.query}</td>
                                <td className="p-4">
                                    <span className="px-2 py-1 rounded-full bg-slate-100 text-slate-600 text-xs">
                                        {m.model}
                                    </span>
                                </td>
                                <td className="p-4 text-emerald-600 font-medium">{m.latency_ms.toFixed(0)}ms</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function Card({ title, value, icon, desc }) {
    return (
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-start justify-between">
            <div>
                <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
                <h3 className="text-2xl font-bold text-slate-900">{value}</h3>
                <p className="text-xs text-gray-400 mt-1">{desc}</p>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
                {icon}
            </div>
        </div>
    )
}
