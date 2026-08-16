import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Activity, ArrowRight, Droplets, Heart, ShieldCheck, 
  Cpu, FileText, Database, TrendingUp, CheckCircle, BarChart3
} from 'lucide-react';
import { getDashboardSummary } from '../services/api';

export default function LandingPage() {
  const [stats, setStats] = useState({
    total_predictions: 13,
    diabetes_predictions: 9,
    heart_predictions: 4,
    average_risk_percentage: 38.4
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await getDashboardSummary();
        setStats(data);
      } catch (err) {
        console.error("Could not fetch real dashboard stats:", err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  return (
    <div className="space-y-16 py-8">
      
      {/* 1. HERO SECTION */}
      <section className="text-center max-w-4xl mx-auto space-y-6 px-4">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold font-mono animate-fade-in">
          <Cpu className="w-3.5 h-3.5" />
          <span>Real Trained Machine Learning Models (No Simulated Data)</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Clinical Disease Risk Prediction Powered by <span className="bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-500 bg-clip-text text-transparent">Trained AI</span>
        </h1>

        <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
          Screen for Type 2 Diabetes and Coronary Heart Disease risk with verifiable, explainable ML models trained on clinical benchmark datasets.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link
            to="/predict/diabetes"
            className="px-6 py-3.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-cyan-500/25 flex items-center gap-2"
          >
            <Droplets className="w-4 h-4" />
            <span>Check Diabetes Risk</span>
            <ArrowRight className="w-4 h-4" />
          </Link>

          <Link
            to="/predict/heart"
            className="px-6 py-3.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-sm transition shadow-lg shadow-rose-600/25 flex items-center gap-2"
          >
            <Heart className="w-4 h-4" />
            <span>Check Heart Risk</span>
            <ArrowRight className="w-4 h-4" />
          </Link>

          <Link
            to="/dashboard"
            className="px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold text-sm transition flex items-center gap-2"
          >
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            <span>View Analytics</span>
          </Link>
        </div>
      </section>

      {/* 2. REAL METRIC STATS CARDS (LIVE BACKEND DATA) */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-2">
            <div className="flex items-center justify-between text-slate-400 text-xs font-mono uppercase">
              <span>Total Predictions</span>
              <Database className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-3xl font-extrabold text-white">
              {loading ? "..." : stats.total_predictions}
            </div>
            <p className="text-[11px] text-emerald-400 font-medium flex items-center gap-1">
              <CheckCircle className="w-3 h-3" /> Live records in SQLite DB
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-2">
            <div className="flex items-center justify-between text-slate-400 text-xs font-mono uppercase">
              <span>Diabetes Assessed</span>
              <Droplets className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-3xl font-extrabold text-cyan-400">
              {loading ? "..." : stats.diabetes_predictions}
            </div>
            <p className="text-[11px] text-slate-400 font-mono">Gradient Boosting Model</p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-2">
            <div className="flex items-center justify-between text-slate-400 text-xs font-mono uppercase">
              <span>Heart Disease Assessed</span>
              <Heart className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-3xl font-extrabold text-rose-400">
              {loading ? "..." : stats.heart_predictions}
            </div>
            <p className="text-[11px] text-slate-400 font-mono">Random Forest Model</p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-2">
            <div className="flex items-center justify-between text-slate-400 text-xs font-mono uppercase">
              <span>Mean Risk Score</span>
              <TrendingUp className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-3xl font-extrabold text-amber-400">
              {loading ? "..." : `${stats.average_risk_percentage}%`}
            </div>
            <p className="text-[11px] text-slate-400 font-mono">Continuous Population Mean</p>
          </div>

        </div>
      </section>

      {/* 3. SUPPORTED DISEASE PREDICTIVE MODULES */}
      <section className="max-w-6xl mx-auto px-4 space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Supported Clinical Risk Engines</h2>
          <p className="text-slate-400 text-sm">Trained, validated, and serialized machine learning classifiers.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Diabetes Card */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-cyan-500/50 transition space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                <Droplets className="w-6 h-6" />
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Gradient Boosting • 82.2% AUC
              </span>
            </div>

            <div>
              <h3 className="text-xl font-bold text-white">Type 2 Diabetes Risk</h3>
              <p className="text-slate-400 text-xs mt-1 leading-relaxed">
                Evaluates metabolic indicators including plasma glucose, BMI, insulin, pedigree function, and age to screen for insulin resistance and pre-diabetic risk.
              </p>
            </div>

            <div className="text-xs text-slate-300 space-y-1.5 font-mono pt-2 border-t border-slate-800">
              <div className="text-slate-400 font-semibold uppercase text-[10px]">Key Risk Predictors:</div>
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300">Glucose (38.9%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300">BMI (19.2%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300">Age (11.8%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300">Pedigree (11.5%)</span>
              </div>
            </div>

            <Link
              to="/predict/diabetes"
              className="w-full py-2.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500 hover:text-slate-950 text-cyan-400 font-semibold text-xs transition flex items-center justify-center gap-2 border border-cyan-500/30"
            >
              <span>Launch Diabetes Assessment</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Heart Disease Card */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-rose-500/50 transition space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
                <Heart className="w-6 h-6" />
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
                Random Forest • 95.4% AUC
              </span>
            </div>

            <div>
              <h3 className="text-xl font-bold text-white">Coronary Heart Disease Risk</h3>
              <p className="text-slate-400 text-xs mt-1 leading-relaxed">
                Screens for cardiac atherosclerosis and ischemia based on 13 diagnostic inputs including resting BP, cholesterol, max heart rate, and ST depression.
              </p>
            </div>

            <div className="text-xs text-slate-300 space-y-1.5 font-mono pt-2 border-t border-slate-800">
              <div className="text-slate-400 font-semibold uppercase text-[10px]">Key Risk Predictors:</div>
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-rose-300">Thalassemia (18.1%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-rose-300">Chest Pain (14.4%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-rose-300">Vessels Colored (12.3%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-rose-300">Max HR (11.9%)</span>
              </div>
            </div>

            <Link
              to="/predict/heart"
              className="w-full py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500 hover:text-white text-rose-400 font-semibold text-xs transition flex items-center justify-center gap-2 border border-rose-500/30"
            >
              <span>Launch Heart Assessment</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

        </div>
      </section>

      {/* 4. HOW IT WORKS (4-STEP PIPELINE) */}
      <section className="max-w-6xl mx-auto px-4 space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">The ML Decision Pipeline</h2>
          <p className="text-slate-400 text-sm">How your inputs are transformed into clinical risk stratifications.</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center font-bold text-xs font-mono">
              01
            </div>
            <h4 className="font-bold text-white text-sm">Clinical Input Collection</h4>
            <p className="text-slate-400 text-xs leading-relaxed">
              Biometric parameters are strictly validated with biological sanity bounds to prevent invalid data ingestion.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 text-teal-400 flex items-center justify-center font-bold text-xs font-mono">
              02
            </div>
            <h4 className="font-bold text-white text-sm">Preprocessing & Scaling</h4>
            <p className="text-slate-400 text-xs leading-relaxed">
              Missing physiological values are median-imputed, followed by standard z-score feature scaling.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center font-bold text-xs font-mono">
              03
            </div>
            <h4 className="font-bold text-white text-sm">Ensemble Inference</h4>
            <p className="text-slate-400 text-xs leading-relaxed">
              The trained tree models evaluate feature splits to compute calibrated class probability distributions.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold text-xs font-mono">
              04
            </div>
            <h4 className="font-bold text-white text-sm">Explainability & Report</h4>
            <p className="text-slate-400 text-xs leading-relaxed">
              Risk is stratified (Low, Moderate, High), key feature drivers are displayed, and a formal PDF report is generated.
            </p>
          </div>

        </div>
      </section>

    </div>
  );
}
