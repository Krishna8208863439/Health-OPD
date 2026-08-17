import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  History, Search, Filter, Trash2, Download, Eye, 
  Droplets, Heart, AlertCircle, RefreshCw, CheckCircle 
} from 'lucide-react';
import { getPredictions, deletePrediction, getReportDownloadUrl } from '../services/api';

export default function HistoryPage() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [diseaseFilter, setDiseaseFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [search, setSearch] = useState('');
  const [toastMessage, setToastMessage] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {};
      if (diseaseFilter) params.disease = diseaseFilter;
      if (riskFilter) params.risk_level = riskFilter;
      if (search) params.search = search;

      const res = await getPredictions(params);
      setPredictions(res.predictions || []);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [diseaseFilter, riskFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Are you sure you want to delete prediction record #${id}?`)) {
      return;
    }
    try {
      await deletePrediction(id);
      setPredictions(prev => prev.filter(p => p.id !== id));
      setToastMessage(`Record #${id} successfully deleted.`);
      setTimeout(() => setToastMessage(null), 4000);
    } catch (err) {
      console.error("Failed to delete record:", err);
      alert("Failed to delete record.");
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-10 px-4 space-y-8 animate-fade-in">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center gap-2 text-cyan-700 text-xs font-mono font-semibold">
            <History className="w-4 h-4 text-cyan-600" />
            <span>PATIENT ASSESSMENT REGISTRY</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">Diagnostic History & Records</h1>
          <p className="text-slate-600 text-xs sm:text-sm">
            Search, filter, export PDF reports, and manage persistent patient prediction logs.
          </p>
        </div>

        <button
          onClick={loadData}
          className="px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-semibold flex items-center gap-1.5 transition self-start sm:self-auto shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Toast Notification */}
      {toastMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-600" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <input
            type="text"
            placeholder="Search by disease or risk..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
        </form>

        {/* Filter Dropdowns */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          
          {/* Disease Filter */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-mono">Disease:</span>
            <select
              value={diseaseFilter}
              onChange={(e) => setDiseaseFilter(e.target.value)}
              className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-cyan-600 font-mono"
            >
              <option value="">All Diseases</option>
              <option value="diabetes">Diabetes Only</option>
              <option value="heart">Heart Disease Only</option>
            </select>
          </div>

          {/* Risk Level Filter */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-mono">Risk Tier:</span>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="bg-slate-50 border border-slate-300 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-cyan-600 font-mono"
            >
              <option value="">All Tiers</option>
              <option value="Low">Low Risk</option>
              <option value="Moderate">Moderate Risk</option>
              <option value="High">High Risk</option>
            </select>
          </div>

        </div>

      </div>

      {/* History Data Table */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 border-3 border-cyan-600 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-xs text-slate-500 font-mono">Querying patient records...</span>
          </div>
        ) : predictions.length === 0 ? (
          <div className="py-12 text-center space-y-3">
            <AlertCircle className="w-8 h-8 text-slate-400 mx-auto" />
            <p className="text-slate-800 text-sm font-semibold">No Assessment Records Found</p>
            <p className="text-slate-500 text-xs">Try adjusting your filters or submit a new disease risk check.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-sans">
              <thead>
                <tr className="text-slate-500 uppercase font-mono text-[10px] border-b border-slate-200">
                  <th className="py-3 px-3">ID</th>
                  <th className="py-3 px-3">Target Condition</th>
                  <th className="py-3 px-3">Risk Level</th>
                  <th className="py-3 px-3">Probability</th>
                  <th className="py-3 px-3">Diagnostic Binary</th>
                  <th className="py-3 px-3">Date</th>
                  <th className="py-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {predictions.map((pred) => {
                  const isLow = pred.risk_level === 'Low';
                  const isMod = pred.risk_level === 'Moderate';
                  const pdfUrl = getReportDownloadUrl(pred.id);

                  return (
                    <tr key={pred.id} className="hover:bg-slate-50 transition">
                      <td className="py-3.5 px-3 text-slate-500 font-bold">#{pred.id}</td>
                      <td className="py-3.5 px-3 font-sans font-semibold capitalize text-slate-900">
                        {pred.disease === 'diabetes' ? (
                          <span className="inline-flex items-center gap-1.5 text-cyan-700">
                            <Droplets className="w-3.5 h-3.5 text-cyan-600" /> Diabetes
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 text-rose-700">
                            <Heart className="w-3.5 h-3.5 text-rose-600" /> Heart Disease
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          isLow
                            ? 'bg-emerald-50 text-emerald-800 border border-emerald-300'
                            : (isMod
                              ? 'bg-amber-50 text-amber-800 border border-amber-300'
                              : 'bg-rose-50 text-rose-800 border border-rose-300')
                        }`}>
                          {pred.risk_level}
                        </span>
                      </td>
                      <td className="py-3.5 px-3 text-slate-900 font-bold">
                        {(pred.risk_probability * 100).toFixed(1)}%
                      </td>
                      <td className="py-3.5 px-3 text-slate-500 text-[11px]">
                        {pred.prediction === 1 ? 'Positive (1)' : 'Negative (0)'}
                      </td>
                      <td className="py-3.5 px-3 text-slate-500 text-[11px]">
                        {pred.created_at?.substring(0, 10)}
                      </td>
                      <td className="py-3.5 px-3 text-right">
                        <div className="flex items-center justify-end gap-1.5 font-sans">
                          
                          <Link
                            to={`/result/${pred.id}`}
                            title="View Result Details"
                            className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-cyan-800 transition"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </Link>

                          <a
                            href={pdfUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            title="Download Official PDF Report"
                            className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-emerald-800 transition"
                          >
                            <Download className="w-3.5 h-3.5" />
                          </a>

                          <button
                            onClick={() => handleDelete(pred.id)}
                            title="Delete Record"
                            className="p-1.5 rounded-lg bg-slate-100 hover:bg-rose-100 text-slate-400 hover:text-rose-600 transition"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>

                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
