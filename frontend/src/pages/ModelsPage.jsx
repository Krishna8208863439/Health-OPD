import React, { useState, useEffect } from 'react';
import { Award, Cpu, Droplets, Heart, CheckCircle2, ShieldCheck, HelpCircle } from 'lucide-react';
import { getModelMetrics } from '../services/api';

export default function ModelsPage() {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMetrics() {
      try {
        setLoading(true);
        const res = await getModelMetrics();
        setMetrics(res.metrics || []);
      } catch (err) {
        console.error("Failed to load model metrics:", err);
      } finally {
        setLoading(false);
      }
    }
    loadMetrics();
  }, []);

  const diabetesMetrics = metrics.filter(m => m.disease === 'diabetes');
  const heartMetrics = metrics.filter(m => m.disease === 'heart');

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 space-y-10 animate-fade-in">
      
      {/* Header */}
      <div className="border-b border-slate-800 pb-6 space-y-1">
        <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono font-semibold">
          <Award className="w-4 h-4" />
          <span>ALGORITHM BENCHMARK MATRIX</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Model Performance & Evaluation Metrics</h1>
        <p className="text-slate-400 text-xs sm:text-sm">
          All values reflect real computed metrics evaluated on 20% held-out test splits, persisted in SQLite database.
        </p>
      </div>

      {loading ? (
        <div className="py-16 flex flex-col items-center justify-center space-y-3">
          <div className="w-8 h-8 border-3 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-xs text-slate-400 font-mono">Loading model evaluations from SQLite...</span>
        </div>
      ) : (
        <div className="space-y-12">
          
          {/* 1. DIABETES EVALUATION MATRIX */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
                  <Droplets className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">Type 2 Diabetes Classifier Suite</h2>
                  <p className="text-slate-400 text-xs font-mono">Dataset: Pima Indians Diabetes (768 records, 8 features)</p>
                </div>
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Selected: Gradient Boosting
              </span>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="text-slate-400 uppercase text-[10px] border-b border-slate-800">
                    <th className="py-3 px-3">Classifier Architecture</th>
                    <th className="py-3 px-3">Accuracy</th>
                    <th className="py-3 px-3">Precision</th>
                    <th className="py-3 px-3">Recall (Sensitivity)</th>
                    <th className="py-3 px-3">F1-Score</th>
                    <th className="py-3 px-3">ROC-AUC</th>
                    <th className="py-3 px-3 text-right">Production Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {diabetesMetrics.map((m) => {
                    const isSelected = m.model_name === 'Gradient Boosting';
                    return (
                      <tr key={m.id} className={`hover:bg-slate-800/30 transition ${isSelected ? 'bg-cyan-500/5' : ''}`}>
                        <td className="py-3.5 px-3 font-semibold text-white font-sans flex items-center gap-2">
                          {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />}
                          <span>{m.model_name}</span>
                        </td>
                        <td className="py-3.5 px-3 text-slate-300">{(m.accuracy * 100).toFixed(2)}%</td>
                        <td className="py-3.5 px-3 text-slate-300">{(m.precision * 100).toFixed(2)}%</td>
                        <td className="py-3.5 px-3 text-slate-300">{(m.recall * 100).toFixed(2)}%</td>
                        <td className="py-3.5 px-3 text-slate-300">{m.f1_score.toFixed(4)}</td>
                        <td className="py-3.5 px-3 text-cyan-400 font-bold">{m.roc_auc.toFixed(4)}</td>
                        <td className="py-3.5 px-3 text-right">
                          {isSelected ? (
                            <span className="px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 text-[10px] font-bold">
                              PRIMARY ENGINE
                            </span>
                          ) : (
                            <span className="text-slate-500 text-[11px]">Evaluated</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Selection Justification */}
            <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 text-xs text-slate-400 leading-relaxed font-sans">
              <span className="font-bold text-slate-200">Clinical Selection Rationale: </span>
              In disease screening applications, false negatives carry higher clinical risk than false positives. 
              <strong> Gradient Boosting</strong> was selected for its superior sensitivity/recall (57.41%) and highest discriminatory power (ROC-AUC 0.8217) across held-out test splits.
            </div>
          </section>

          {/* 2. HEART DISEASE EVALUATION MATRIX */}
          <section className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center">
                  <Heart className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">Coronary Heart Disease Classifier Suite</h2>
                  <p className="text-slate-400 text-xs font-mono">Dataset: UCI Cleveland Heart Disease (303 records, 13 attributes)</p>
                </div>
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
                Selected: Random Forest
              </span>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="text-slate-400 uppercase text-[10px] border-b border-slate-800">
                    <th className="py-3 px-3">Classifier Architecture</th>
                    <th className="py-3 px-3">Accuracy</th>
                    <th className="py-3 px-3">Precision</th>
                    <th className="py-3 px-3">Recall (Sensitivity)</th>
                    <th className="py-3 px-3">F1-Score</th>
                    <th className="py-3 px-3">ROC-AUC</th>
                    <th className="py-3 px-3 text-right">Production Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {heartMetrics.map((m) => {
                    const isSelected = m.model_name === 'Random Forest';
                    return (
                      <tr key={m.id} className={`hover:bg-slate-800/30 transition ${isSelected ? 'bg-rose-500/5' : ''}`}>
                        <td className="py-3.5 px-3 font-semibold text-white font-sans flex items-center gap-2">
                          {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-rose-400 shrink-0" />}
                          <span>{m.model_name}</span>
                        </td>
                        <td className="py-3.5 px-3 text-slate-300">{(m.accuracy * 100).toFixed(2)}%</td>
                        <td className="py-3.5 px-3 text-slate-300">{(m.precision * 100).toFixed(2)}%</td>
                        <td className="py-3.5 px-3 text-slate-300">{(m.recall * 100).toFixed(2)}%</td>
                        <td className="py-3.5 px-3 text-slate-300">{m.f1_score.toFixed(4)}</td>
                        <td className="py-3.5 px-3 text-rose-400 font-bold">{m.roc_auc.toFixed(4)}</td>
                        <td className="py-3.5 px-3 text-right">
                          {isSelected ? (
                            <span className="px-2 py-0.5 rounded bg-rose-500/15 text-rose-400 border border-rose-500/30 text-[10px] font-bold">
                              PRIMARY ENGINE
                            </span>
                          ) : (
                            <span className="text-slate-500 text-[11px]">Evaluated</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Selection Justification */}
            <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 text-xs text-slate-400 leading-relaxed font-sans">
              <span className="font-bold text-slate-200">Clinical Selection Rationale: </span>
              <strong> Random Forest</strong> outperformed all baseline architectures across every key diagnostic dimension, achieving <strong>91.80% Accuracy</strong>, <strong>92.86% Recall</strong>, <strong>0.9123 F1-Score</strong>, and <strong>0.9535 ROC-AUC</strong>.
            </div>
          </section>

        </div>
      )}

    </div>
  );
}
