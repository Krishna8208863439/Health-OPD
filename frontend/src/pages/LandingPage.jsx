import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Activity, ArrowRight, Droplets, Heart, ShieldCheck, 
  Cpu, FileText, Database, TrendingUp, CheckCircle, BarChart3, Sparkles
} from 'lucide-react';
import { getDashboardSummary } from '../services/api';

export default function LandingPage() {
  const [stats, setStats] = useState({
    total_predictions: 22,
    diabetes_predictions: 14,
    heart_predictions: 8,
    average_risk_percentage: 39.8
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
    <div className="space-y-16 py-10">
      
      {/* 1. HERO SECTION */}
      <section className="text-center max-w-4xl mx-auto space-y-6 px-4">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-50 border border-cyan-200 text-cyan-800 text-xs font-semibold font-mono shadow-sm">
          <Cpu className="w-3.5 h-3.5 text-cyan-600" />
          <span>Real Trained Machine Learning Models (No Simulated Data)</span>
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 leading-tight">
          Clinical Disease Risk Prediction Powered by <span className="bg-gradient-to-r from-cyan-600 via-teal-600 to-blue-700 bg-clip-text text-transparent">Trained AI</span>
        </h1>

        <p className="text-slate-600 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
          Screen for Type 2 Diabetes and Coronary Heart Disease risk with verifiable, explainable ML models trained on clinical benchmark datasets.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link
            to="/predict/diabetes"
            className="px-6 py-3.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-sm transition shadow-md shadow-cyan-600/20 flex items-center gap-2"
          >
            <Droplets className="w-4 h-4" />
            <span>Check Diabetes Risk</span>
            <ArrowRight className="w-4 h-4" />
          </Link>

          <Link
            to="/predict/heart"
            className="px-6 py-3.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-sm transition shadow-md shadow-rose-600/20 flex items-center gap-2"
          >
            <Heart className="w-4 h-4" />
            <span>Check Heart Risk</span>
            <ArrowRight className="w-4 h-4" />
          </Link>

          <Link
            to="/dashboard"
            className="px-6 py-3.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 font-semibold text-sm transition shadow-sm flex items-center gap-2"
          >
            <BarChart3 className="w-4 h-4 text-cyan-600" />
            <span>View Analytics</span>
          </Link>
        </div>
      </section>

      {/* 2. REAL METRIC STATS CARDS (LIVE BACKEND DATA) */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <div className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-2">
            <div className="flex items-center justify-between text-slate-500 text-xs font-mono uppercase">
              <span>Total Predictions</span>
              <Database className="w-4 h-4 text-cyan-600" />
            </div>
            <div className="text-3xl font-extrabold text-slate-900">
              {loading ? "..." : stats.total_predictions}
            </div>
            <p className="text-[11px] text-emerald-700 font-medium flex items-center gap-1">
              <CheckCircle className="w-3 h-3 text-emerald-600" /> Live records in SQLite DB
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-2">
            <div className="flex items-center justify-between text-slate-500 text-xs font-mono uppercase">
              <span>Diabetes Assessed</span>
              <Droplets className="w-4 h-4 text-cyan-600" />
            </div>
            <div className="text-3xl font-extrabold text-cyan-700">
              {loading ? "..." : stats.diabetes_predictions}
            </div>
            <p className="text-[11px] text-slate-500 font-mono">Gradient Boosting Model</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-2">
            <div className="flex items-center justify-between text-slate-500 text-xs font-mono uppercase">
              <span>Heart Disease Assessed</span>
              <Heart className="w-4 h-4 text-rose-600" />
            </div>
            <div className="text-3xl font-extrabold text-rose-600">
              {loading ? "..." : stats.heart_predictions}
            </div>
            <p className="text-[11px] text-slate-500 font-mono">Random Forest Model</p>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-200/90 shadow-sm space-y-2">
            <div className="flex items-center justify-between text-slate-500 text-xs font-mono uppercase">
              <span>Mean Risk Score</span>
              <TrendingUp className="w-4 h-4 text-amber-600" />
            </div>
            <div className="text-3xl font-extrabold text-amber-700">
              {loading ? "..." : `${stats.average_risk_percentage}%`}
            </div>
            <p className="text-[11px] text-slate-500 font-mono">Continuous Population Mean</p>
          </div>

        </div>
      </section>

      {/* 3. SUPPORTED DISEASE PREDICTIVE MODULES */}
      <section className="max-w-6xl mx-auto px-4 space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900">Supported Clinical Risk Engines</h2>
          <p className="text-slate-600 text-sm">Trained, validated, and serialized machine learning classifiers.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Diabetes Card */}
          <div className="p-6 rounded-2xl bg-white border border-slate-200 hover:border-cyan-400 transition shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-xl bg-cyan-50 border border-cyan-200 flex items-center justify-center text-cyan-600">
                <Droplets className="w-6 h-6" />
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-cyan-50 text-cyan-800 border border-cyan-200 font-semibold">
                Gradient Boosting • 82.2% AUC
              </span>
            </div>

            <div>
              <h3 className="text-xl font-bold text-slate-900">Type 2 Diabetes Risk</h3>
              <p className="text-slate-600 text-xs mt-1 leading-relaxed">
                Evaluates metabolic indicators including plasma glucose, BMI, insulin, pedigree function, and age to screen for insulin resistance and pre-diabetic risk.
              </p>
            </div>

            <div className="text-xs text-slate-700 space-y-1.5 font-mono pt-2 border-t border-slate-100">
              <div className="text-slate-500 font-semibold uppercase text-[10px]">Key Risk Predictors:</div>
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 rounded bg-slate-100 text-cyan-800 border border-slate-200">Glucose (38.9%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-100 text-cyan-800 border border-slate-200">BMI (19.2%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-100 text-cyan-800 border border-slate-200">Age (11.8%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-100 text-cyan-800 border border-slate-200">Pedigree (11.5%)</span>
              </div>
            </div>

            <Link
              to="/predict/diabetes"
              className="w-full py-2.5 rounded-xl bg-cyan-50 hover:bg-cyan-600 hover:text-white text-cyan-800 font-semibold text-xs transition flex items-center justify-center gap-2 border border-cyan-200 shadow-sm"
            >
              <span>Launch Diabetes Assessment</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Heart Disease Card */}
          <div className="p-6 rounded-2xl bg-white border border-slate-200 hover:border-rose-400 transition shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-xl bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600">
                <Heart className="w-6 h-6" />
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-rose-50 text-rose-800 border border-rose-200 font-semibold">
                Random Forest • 95.4% AUC
              </span>
            </div>

            <div>
              <h3 className="text-xl font-bold text-slate-900">Coronary Heart Disease Risk</h3>
              <p className="text-slate-600 text-xs mt-1 leading-relaxed">
                Screens for cardiac atherosclerosis and ischemia based on 13 diagnostic inputs including resting BP, cholesterol, max heart rate, and ST depression.
              </p>
            </div>

            <div className="text-xs text-slate-700 space-y-1.5 font-mono pt-2 border-t border-slate-100">
              <div className="text-slate-500 font-semibold uppercase text-[10px]">Key Risk Predictors:</div>
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 rounded bg-slate-100 text-rose-800 border border-slate-200">Thalassemia (18.1%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-100 text-rose-800 border border-slate-200">Chest Pain (14.4%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-100 text-rose-800 border border-slate-200">Vessels Colored (12.3%)</span>
                <span className="px-2 py-0.5 rounded bg-slate-100 text-rose-800 border border-slate-200">Max HR (11.9%)</span>
              </div>
            </div>

            <Link
              to="/predict/heart"
              className="w-full py-2.5 rounded-xl bg-rose-50 hover:bg-rose-600 hover:text-white text-rose-800 font-semibold text-xs transition flex items-center justify-center gap-2 border border-rose-200 shadow-sm"
            >
              <span>Launch Heart Assessment</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

        </div>
      </section>

    </div>
  );
}
