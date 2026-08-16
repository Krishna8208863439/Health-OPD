import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Activity, Download, ArrowLeft, ShieldAlert, CheckCircle, 
  AlertTriangle, XCircle, Heart, Droplets, RefreshCw, BarChart2
} from 'lucide-react';
import { getPredictionById, getReportDownloadUrl } from '../services/api';

export default function ResultPage() {
  const { id } = useParams();
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadResult() {
      try {
        setLoading(true);
        const data = await getPredictionById(id);
        setRecord(data);
      } catch (err) {
        console.error("Could not fetch prediction result:", err);
        setError("Prediction record not found or could not be loaded.");
      } finally {
        setLoading(false);
      }
    }
    loadResult();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm text-slate-400 font-mono">Loading clinical assessment #{id}...</p>
      </div>
    );
  }

  if (error || !record) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-rose-500/10 text-rose-400 mx-auto flex items-center justify-center">
          <XCircle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-white">Assessment Record Not Found</h2>
        <p className="text-slate-400 text-sm">{error}</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 text-slate-200 text-xs font-semibold"
        >
          <ArrowLeft className="w-4 h-4" /> Return to Home
        </Link>
      </div>
    );
  }

  const isDiabetes = record.disease === 'diabetes';
  const riskLevel = record.risk_level;
  const riskPercentage = (record.risk_probability * 100).toFixed(1);

  // Styling based on risk level
  const riskConfig = {
    Low: {
      badgeBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      barColor: 'bg-emerald-500',
      icon: CheckCircle,
      title: 'Low Clinical Risk Detected',
      summary: 'Patient biomarkers currently align within standard baseline epidemiological thresholds.'
    },
    Moderate: {
      badgeBg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      barColor: 'bg-amber-500',
      icon: AlertTriangle,
      title: 'Moderate / Borderline Risk Detected',
      summary: 'Elevated risk parameters identified. Lifestyle adjustments and follow-up screening are advised.'
    },
    High: {
      badgeBg: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      barColor: 'bg-rose-500',
      icon: XCircle,
      title: 'High Risk / Clinical Investigation Recommended',
      summary: 'Significant biometric markers correlate with positive disease indicators in trained cohort.'
    }
  }[riskLevel] || {
    badgeBg: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
    barColor: 'bg-cyan-500',
    icon: Activity,
    title: 'Risk Stratification Complete',
    summary: 'Biomarkers processed.'
  };

  const RiskIcon = riskConfig.icon;
  const downloadUrl = getReportDownloadUrl(record.id);

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-8 animate-fade-in">
      
      {/* Top Breadcrumb & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Link
            to={isDiabetes ? '/predict/diabetes' : '/predict/heart'}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-400 hover:text-white transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
              <span>Assessment Reference: #{record.id}</span>
              <span>•</span>
              <span className="capitalize">{record.disease} Risk</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-white">Clinical Risk Evaluation Result</h1>
          </div>
        </div>

        <a
          href={downloadUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 shrink-0"
        >
          <Download className="w-4 h-4" />
          <span>Download PDF Report</span>
        </a>
      </div>

      {/* Main Scorecard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 rounded-3xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
        
        {/* Left: Large Probability Dial */}
        <div className="flex flex-col items-center justify-center p-6 rounded-2xl bg-slate-950/70 border border-slate-800/80 text-center space-y-3">
          <div className="text-xs font-mono text-slate-400 uppercase tracking-wider">
            Computed Risk Score
          </div>

          <div className="relative flex items-center justify-center">
            <div className="text-5xl font-black text-white tracking-tight">
              {riskPercentage}<span className="text-2xl text-slate-500 font-normal">%</span>
            </div>
          </div>

          <div className={`px-3 py-1 rounded-full border text-xs font-bold font-mono uppercase tracking-wider ${riskConfig.badgeBg}`}>
            {riskLevel} Risk Tier
          </div>

          <div className="text-[11px] text-slate-400 font-mono pt-1">
            Raw Probability: {record.risk_probability.toFixed(4)}
          </div>
        </div>

        {/* Right: Risk Classification & Clinical Summary */}
        <div className="md:col-span-2 flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <RiskIcon className={`w-5 h-5 ${riskLevel === 'Low' ? 'text-emerald-400' : (riskLevel === 'Moderate' ? 'text-amber-400' : 'text-rose-400')}`} />
              <h2 className="text-lg font-bold text-white">{riskConfig.title}</h2>
            </div>
            <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
              {riskConfig.summary}
            </p>
          </div>

          {/* Model & Execution Meta */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-slate-950/50 border border-slate-800 text-xs font-mono">
            <div>
              <div className="text-slate-500 text-[10px] uppercase">Engine</div>
              <div className="text-slate-200 font-semibold">{record.model_name || 'Ensemble Classifier'}</div>
            </div>
            <div>
              <div className="text-slate-500 text-[10px] uppercase">Binary Class</div>
              <div className="text-slate-200 font-semibold">
                {record.prediction === 1 ? 'Positive (1)' : 'Negative (0)'}
              </div>
            </div>
            <div className="col-span-2 sm:col-span-1">
              <div className="text-slate-500 text-[10px] uppercase">Evaluated At</div>
              <div className="text-slate-200 font-semibold">{record.created_at?.substring(0, 10)}</div>
            </div>
          </div>

          {/* Probability Bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-[11px] font-mono text-slate-400">
              <span>Risk Scale (0% - 100%)</span>
              <span>Threshold: 35% / 70%</span>
            </div>
            <div className="w-full h-3 rounded-full bg-slate-950 border border-slate-800 overflow-hidden p-0.5">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${riskConfig.barColor}`}
                style={{ width: `${Math.min(Math.max(riskPercentage, 5), 100)}%` }}
              ></div>
            </div>
          </div>
        </div>

      </div>

      {/* Feature Importance Explainability Section */}
      {record.feature_importance && record.feature_importance.length > 0 && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                Model Feature Importance Drivers
              </h3>
            </div>
            <span className="text-[11px] font-mono text-slate-400">Gini / Gradient Split %</span>
          </div>

          <div className="space-y-3">
            {record.feature_importance.slice(0, 6).map((feat, index) => (
              <div key={index} className="space-y-1">
                <div className="flex justify-between text-xs font-sans">
                  <span className="font-semibold text-slate-200">{feat.feature}</span>
                  <span className="font-mono text-cyan-400 font-bold">{feat.percentage.toFixed(2)}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
                    style={{ width: `${feat.percentage}%` }}
                  ></div>
                </div>
                {feat.description && (
                  <p className="text-[10px] text-slate-400 italic">{feat.description}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Submitted Clinical Inputs Table */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono border-b border-slate-800 pb-3">
          Submitted Patient Biometric Inputs
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {Object.entries(record.input_data || {}).map(([key, val]) => (
            <div key={key} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="text-[10px] text-slate-400 font-mono uppercase">{key}</div>
              <div className="text-sm font-bold text-slate-100 font-mono mt-0.5">{String(val)}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
        <Link
          to={isDiabetes ? '/predict/diabetes' : '/predict/heart'}
          className="px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold transition flex items-center gap-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Assess Another Patient</span>
        </Link>

        <a
          href={downloadUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition shadow-lg shadow-cyan-500/20 flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          <span>Download PDF Report</span>
        </a>
      </div>

      {/* Verbatim Medical Disclaimer */}
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

    </div>
  );
}
