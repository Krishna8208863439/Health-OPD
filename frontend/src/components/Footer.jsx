import React from 'react';
import { Activity, ShieldAlert, Heart, Lock } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-950 border-t border-slate-800/80 text-slate-400 font-sans text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        
        {/* Upper Footer: Branding & Details */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center">
                <Activity className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-white text-base">
                HealthPredict <span className="text-cyan-400">AI</span>
              </span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed">
              An evidence-based clinical decision-support platform powered by machine learning algorithms (Gradient Boosting & Random Forest) trained on validated medical registries.
            </p>
          </div>

          <div className="space-y-2">
            <h4 className="font-bold text-slate-200 uppercase tracking-wider text-[11px] font-mono">
              Supported Predictive Engines
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-400">
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                <span>Type 2 Diabetes Risk Prediction (Pima Indians NIDDK)</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                <span>Coronary Heart Disease Risk (Cleveland Heart Study)</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
                <span>Native Gini & Gradient Feature Explainability</span>
              </li>
            </ul>
          </div>

          <div className="space-y-2">
            <h4 className="font-bold text-slate-200 uppercase tracking-wider text-[11px] font-mono flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-emerald-400" />
              Privacy & Anti-Fabrication
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every inference probability, feature weight, and evaluation metric is computed deterministically by verified serialized estimators stored in local SQLite database.
            </p>
          </div>
        </div>

        {/* Verbatim Medical Disclaimer (Non-Negotiable per Phase 10 & Global Rule 7) */}
        <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-bold text-amber-300 text-xs uppercase tracking-wider font-mono">
              Mandatory Clinical Disclaimer
            </div>
            <p className="text-slate-300 text-[11px] leading-relaxed">
              HealthPredict AI provides machine-learning-based risk estimates for educational and decision-support purposes only. It does not diagnose, treat, cure, or prevent any disease. Always consult a qualified healthcare professional for medical advice.
            </p>
          </div>
        </div>

        {/* Copyright */}
        <div className="text-center text-[11px] text-slate-500 pt-2 border-t border-slate-900">
          © 2026 HealthPredict AI. All rights reserved. Open-Source Clinical Machine Learning Platform.
        </div>
      </div>
    </footer>
  );
}
