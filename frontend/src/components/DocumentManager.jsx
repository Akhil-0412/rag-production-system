import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, Check, AlertCircle, Trash2 } from 'lucide-react';

export default function DocumentManager() {
    const [uploading, setUploading] = useState(false);
    const [status, setStatus] = useState(null); // { type: 'success'|'error', msg: '' }

    const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        setStatus(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await axios.post(`${API_URL}/documents/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            setStatus({
                type: 'success',
                msg: `Uploaded ${res.data.filename} (${res.data.chunks_created} chunks)`
            });
        } catch (err) {
            console.error(err);
            setStatus({
                type: 'error',
                msg: err.response?.data?.detail || "Upload failed."
            });
        } finally {
            setUploading(false);
        }
    };

    const handleReset = async () => {
        if (!confirm("Are you sure you want to delete all vectors?")) return;
        try {
            await axios.delete(`${API_URL}/documents/reset`);
            setStatus({ type: 'success', msg: "Index cleared." });
        } catch (err) {
            setStatus({ type: 'error', msg: "Reset failed." });
        }
    };

    return (
        <div className="p-6 max-w-2xl mx-auto">
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
                <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Upload className="w-8 h-8" />
                </div>

                <h2 className="text-xl font-semibold text-slate-900 mb-2">Upload Documents</h2>
                <p className="text-gray-500 mb-8 max-w-sm mx-auto">
                    Upload PDF, DOCX, or TXT files to add them to the knowledge base.
                </p>

                <label className={`
          inline-flex items-center gap-2 px-6 py-3 rounded-lg font-medium cursor-pointer transition-all
          ${uploading ? 'bg-gray-100 text-gray-400' : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-blue-500/20'}
        `}>
                    {uploading ? 'Uploading...' : 'Select File'}
                    <input
                        type="file"
                        className="hidden"
                        accept=".pdf,.docx,.txt,.md"
                        onChange={handleUpload}
                        disabled={uploading}
                    />
                </label>

                {status && (
                    <div className={`mt-6 p-4 rounded-lg flex items-center gap-3 text-sm text-left
            ${status.type === 'success' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-red-50 text-red-700 border border-red-100'}
          `}>
                        {status.type === 'success' ? <Check className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                        {status.msg}
                    </div>
                )}
            </div>

            <div className="mt-8 flex justify-center">
                <button
                    onClick={handleReset}
                    className="text-red-500 hover:text-red-700 text-sm flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-red-50 transition-colors"
                >
                    <Trash2 className="w-4 h-4" /> Clear Knowledge Base
                </button>
            </div>
        </div>
    );
}
