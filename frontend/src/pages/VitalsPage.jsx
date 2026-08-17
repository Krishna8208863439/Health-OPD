import React, { useState, useEffect } from 'react';
import { Activity, Heart, Droplets, Thermometer, Wind, PlusCircle, CheckCircle, Award } from 'lucide-react';
import { getVitals, logVitals } from '../services/api';

export default function VitalsPage() {
  const [vitalsData, setVitalsData] = useState({ current_score: 85, logs: [] });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState(null);

  const [form, setForm] = useState({
    systolic: 120,
    diastolic: 80,
    heart_rate: 72,
    glucose: 95,
    spo2: 98,
    temperature: 98.6,
    notes: 'Routine clinical check'
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await getVitals();
      setVitalsData(data);
    } catch (err) {
      console.error("Failed to load vitals:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await logVitals(form);
      setSuccessMsg("Vitals logged and Daily Health Score updated successfully!");
      setTimeout(() => setSuccessMsg(null), 4000);
      fetchData();
    } catch (err) {
      console.error("Failed to log vitals:", err);
    } finally {
      setSubmitting(false);
    }
  };

  const score = vitalsData.current_score || 85;
  const scoreColor = score >= 80 ? 'text-emerald-600' : (score >= 60 ? 'text-amber-600' : 'text-rose-600');
  const scoreBg = score >= 80 ? 'bg-emerald-50 border-emerald-200' : (score >= 60 ? 'bg-amber-50 border-amber-200' : 'bg-rose-50 border-rose-200');

  return (
    <div className="w-full max-w-[1700px] mx-auto px-4 sm:px-6 lg:px-10 py-8 space-y-8 animate-fade-in">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center gap-2 text-cyan-700 text-xs font-mono font-semibold">
            <Activity className="w-4 h-4 text-cyan-600" />
            <span>DAILY BIOMETRIC MONITORING & SCORING</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Patient Vitals Tracker & Health Score
          </h1>
          <p className="text-slate-600 text-xs sm:text-sm">
            Record blood pressure, pulse, glucose, oxygen saturation, and body temperature for automated clinical risk analytics.
          </p>
        </div>
      </div>

      {/* Top Banner: Health Score Card */}
      <div className={`p-6 sm:p-8 rounded-3xl border ${scoreBg} flex flex-col md:flex-row items-center justify-between gap-6 shadow-sm`}>
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-3xl bg-white border border-slate-200 shadow-md flex flex-col items-center justify-center shrink-0">
            <span className={`text-3xl sm:text-4xl font-black ${scoreColor}`}>{score}</span>
            <span className="text-[10px] text-slate-500 font-mono font-semibold uppercase">Score</span>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-amber-500" />
              <h2 className="text-lg sm:text-xl font-bold text-slate-900">Your Daily Health Score</h2>
            </div>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-2xl">
              {score >= 80 
                ? "Excellent! Your biometric parameters are in the optimal physiological range. Keep up the active routine!"
                : (score >= 60 
                  ? "Moderate score. Keep an eye on elevated blood pressure or glucose levels."
                  : "Attention needed. One or more vital metrics deviate from baseline thresholds. Consult a physician.")}
            </p>
          </div>
        </div>

        <div className="text-left sm:text-right font-mono text-xs text-slate-500 space-y-1">
          <div>Status: <span className="font-bold text-slate-900">{score >= 80 ? 'Optimal Performance' : 'Monitoring Advised'}</span></div>
          <div className="text-[11px] text-slate-400">Automated Multi-Metric Evaluation</div>
        </div>
      </div>

      {/* Toast */}
      {successMsg && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-600" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Form & Recent Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Form Card */}
        <div className="lg:col-span-1 p-6 sm:p-7 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-5">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <PlusCircle className="w-4 h-4 text-cyan-600" />
            <h3 className="font-bold text-slate-900 text-sm">Log New Measurement</h3>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Systolic BP (mm Hg)</label>
                <input
                  type="number"
                  name="systolic"
                  value={form.systolic}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 font-mono text-slate-900 focus:bg-white"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Diastolic BP (mm Hg)</label>
                <input
                  type="number"
                  name="diastolic"
                  value={form.diastolic}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 font-mono text-slate-900 focus:bg-white"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">Heart Rate (BPM)</label>
                <input
                  type="number"
                  name="heart_rate"
                  value={form.heart_rate}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 font-mono text-slate-900 focus:bg-white"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Glucose (mg/dL)</label>
                <input
                  type="number"
                  name="glucose"
                  value={form.glucose}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 font-mono text-slate-900 focus:bg-white"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">SpO2 Oxygen (%)</label>
                <input
                  type="number"
                  name="spo2"
                  value={form.spo2}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 font-mono text-slate-900 focus:bg-white"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-700 font-semibold mb-1">Temp (°F)</label>
                <input
                  type="number"
                  step="0.1"
                  name="temperature"
                  value={form.temperature}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 font-mono text-slate-900 focus:bg-white"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">Notes / Remarks</label>
              <input
                type="text"
                name="notes"
                value={form.notes}
                onChange={handleChange}
                placeholder="e.g. After aerobic exercise"
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-slate-900 focus:bg-white"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold transition shadow-md shadow-cyan-600/20"
            >
              {submitting ? 'Saving...' : 'Save Vitals Record'}
            </button>
          </form>
        </div>

        {/* Logs Table */}
        <div className="lg:col-span-2 p-6 sm:p-7 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 text-sm">Recent Biometric History</h3>
            <span className="text-[11px] font-mono text-slate-500">Persistent SQLite Registry</span>
          </div>

          {loading ? (
            <div className="py-16 text-center text-xs text-slate-500 font-mono">Loading vitals history...</div>
          ) : vitalsData.logs.length === 0 ? (
            <div className="py-16 text-center text-xs text-slate-500 font-mono">
              No measurements logged yet. Use the form on the left to record your first vital sign.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-sans">
                <thead>
                  <tr className="text-slate-500 uppercase font-mono text-[10px] border-b border-slate-200">
                    <th className="py-3 px-3">BP (Sys/Dia)</th>
                    <th className="py-3 px-3">Heart Rate</th>
                    <th className="py-3 px-3">Glucose</th>
                    <th className="py-3 px-3">SpO2</th>
                    <th className="py-3 px-3">Temp</th>
                    <th className="py-3 px-3">Score</th>
                    <th className="py-3 px-3">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {vitalsData.logs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-50 transition">
                      <td className="py-3 px-3 font-bold text-slate-900">
                        {log.systolic}/{log.diastolic} mm Hg
                      </td>
                      <td className="py-3 px-3 text-rose-600 font-bold">{log.heart_rate} bpm</td>
                      <td className="py-3 px-3 text-cyan-700">{log.glucose} mg/dL</td>
                      <td className="py-3 px-3 text-emerald-700">{log.spo2}%</td>
                      <td className="py-3 px-3 text-slate-700">{log.temperature}°F</td>
                      <td className="py-3 px-3">
                        <span className="px-2.5 py-0.5 rounded font-bold bg-slate-100 text-slate-800 border border-slate-200 text-[10px]">
                          {log.health_score} / 100
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-400 text-[11px]">
                        {log.created_at.substring(0, 10)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
