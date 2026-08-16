import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  LayoutDashboard, Activity, Droplets, Heart, 
  TrendingUp, Users, ArrowRight, ShieldCheck, PieChart, BarChart3, Clock
} from 'lucide-react';
import { getDashboardSummary } from '../services/api';

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const res = await getDashboardSummary();
        setData(res);
      } catch (err) {
        console.error("Failed to load dashboard:", err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading || !data) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm text-slate-400 font-mono">Aggregating database telemetry & patient evaluations...</p>
      </div>
    );
  }

  const riskDist = data.risk_distribution || { Low: 0, Moderate: 0, High: 0 };
  const total = Math.max(data.total_predictions, 1);
  const lowPct = ((riskDist.Low / total) * 100).toFixed(1);
  const modPct = ((riskDist.Moderate / total) * 100).toFixed(1);
  const highPct = ((riskDist.High / total) * 100).toFixed(1);

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 space-y-8 animate-fade-in">
      
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono font-semibold">
            <LayoutDashboard className="w-4 h-4" />
            <span>CLINICAL EPIDEMIOLOGY DASHBOARD</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Platform Health Analytics</h1>
          <p className="text-slate-400 text-xs sm:text-sm">
            Live database aggregates, risk stratifications, and diagnostic activity tracking.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Link
            to="/predict/diabetes"
            className="px-3.5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold transition flex items-center gap-1.5"
          >
            <Droplets className="w-3.5 h-3.5" />
            <span>+ New Diabetes Test</span>
          </Link>
          <Link
            to="/predict/heart"
            className="px-3.5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold transition flex items-center gap-1.5"
          >
            <Heart className="w-3.5 h-3.5" />
            <span>+ New Heart Test</span>
          </Link>
        </div>
      </div>

      {/* 1. Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Total */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 uppercase">
            <span>Total Evaluated</span>
            <Users className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">{data.total_predictions}</div>
          <div className="text-[11px] text-slate-400 font-mono">SQLite Persistent Rows</div>
        </div>

        {/* Diabetes */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 uppercase">
            <span>Diabetes Tests</span>
            <Droplets className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-cyan-400">{data.diabetes_predictions}</div>
          <div className="text-[11px] text-slate-400 font-mono">
            {((data.diabetes_predictions / total) * 100).toFixed(0)}% of platform volume
          </div>
        </div>

        {/* Heart */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 uppercase">
            <span>Heart Tests</span>
            <Heart className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-3xl font-extrabold text-rose-400">{data.heart_predictions}</div>
          <div className="text-[11px] text-slate-400 font-mono">
            {((data.heart_predictions / total) * 100).toFixed(0)}% of platform volume
          </div>
        </div>

        {/* Mean Risk */}
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs font-mono text-slate-400 uppercase">
            <span>Average Patient Risk</span>
            <TrendingUp className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400">{data.average_risk_percentage}%</div>
          <div className="text-[11px] text-slate-400 font-mono">Calibrated Probability Mean</div>
        </div>

      </div>

      {/* 2. Visual Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Risk Stratification Breakdown */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <PieChart className="w-4 h-4 text-cyan-400" />
              <span>Risk Stratification Distribution</span>
            </h3>
            <span className="text-[11px] font-mono text-slate-400">{data.total_predictions} Samples</span>
          </div>

          <div className="space-y-4">
            {/* Low */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-emerald-400 font-semibold flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span> Low Risk (&lt; 35%)
                </span>
                <span className="text-slate-300">{riskDist.Low} patients ({lowPct}%)</span>
              </div>
              <div className="w-full h-3 rounded-full bg-slate-950 overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${lowPct}%` }}></div>
              </div>
            </div>

            {/* Moderate */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-amber-400 font-semibold flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span> Moderate Risk (35% - 70%)
                </span>
                <span className="text-slate-300">{riskDist.Moderate} patients ({modPct}%)</span>
              </div>
              <div className="w-full h-3 rounded-full bg-slate-950 overflow-hidden">
                <div className="h-full bg-amber-500 rounded-full" style={{ width: `${modPct}%` }}></div>
              </div>
            </div>

            {/* High */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-rose-400 font-semibold flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span> High Risk (&gt; 70%)
                </span>
                <span className="text-slate-300">{riskDist.High} patients ({highPct}%)</span>
              </div>
              <div className="w-full h-3 rounded-full bg-slate-950 overflow-hidden">
                <div className="h-full bg-rose-500 rounded-full" style={{ width: `${highPct}%` }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* 7-Day Assessment Activity */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-cyan-400" />
              <span>Assessment Activity Volume</span>
            </h3>
            <span className="text-[11px] font-mono text-slate-400">Recent 7 Days</span>
          </div>

          <div className="grid grid-cols-7 gap-2 pt-4">
            {(data.trend_data || []).map((t, idx) => (
              <div key={idx} className="flex flex-col items-center gap-2">
                <div className="w-full h-28 bg-slate-950/60 rounded-xl flex items-end justify-center p-1 relative group">
                  <div
                    className="w-full bg-gradient-to-t from-cyan-500 to-blue-500 rounded-lg transition-all"
                    style={{ height: `${Math.max(t.total * 6, 8)}%` }}
                  ></div>
                  <div className="opacity-0 group-hover:opacity-100 transition absolute -top-8 bg-slate-800 text-[10px] text-white px-2 py-0.5 rounded font-mono pointer-events-none">
                    {t.total} tests
                  </div>
                </div>
                <span className="text-[10px] font-mono text-slate-400">{t.date.split(' ')[1]}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* 3. Recent Predictions Table */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span>Recent Clinical Assessments</span>
          </h3>
          <Link
            to="/history"
            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            <span>View All History</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-sans">
            <thead>
              <tr className="text-slate-400 uppercase font-mono text-[10px] border-b border-slate-800">
                <th className="py-2.5 px-3">ID</th>
                <th className="py-2.5 px-3">Condition</th>
                <th className="py-2.5 px-3">Risk Level</th>
                <th className="py-2.5 px-3">Probability</th>
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {(data.recent_predictions || []).map((pred) => (
                <tr key={pred.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 px-3 text-slate-400 font-bold">#{pred.id}</td>
                  <td className="py-3 px-3 font-sans font-semibold capitalize text-slate-200">
                    {pred.disease === 'diabetes' ? (
                      <span className="inline-flex items-center gap-1.5 text-cyan-400">
                        <Droplets className="w-3.5 h-3.5" /> Diabetes
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-rose-400">
                        <Heart className="w-3.5 h-3.5" /> Heart Disease
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      pred.risk_level === 'Low'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        : (pred.risk_level === 'Moderate'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/30')
                    }`}>
                      {pred.risk_level}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-200 font-bold">
                    {(pred.risk_probability * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 px-3 text-slate-400">
                    {pred.created_at?.substring(0, 10)}
                  </td>
                  <td className="py-3 px-3 text-right font-sans">
                    <Link
                      to={`/result/${pred.id}`}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
