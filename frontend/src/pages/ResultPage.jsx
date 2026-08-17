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
        <div className="w-10 h-10 border-4 border-cyan-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm text-slate-600 font-mono">Loading clinical assessment #{id}...</p>
      </div>
    );
  }

  if (error || !record) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 mx-auto flex items-center justify-center border border-rose-200">
          <XCircle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Assessment Record Not Found</h2>
        <p className="text-slate-600 text-sm">{error}</p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-slate-300 text-slate-700 text-xs font-semibold shadow-sm"
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
      badgeBg: 'bg-emerald-50 text-emerald-800 border-emerald-300',
      barColor: 'bg-emerald-500',
      icon: CheckCircle,
      title: 'Low Clinical Risk Detected',
      summary: 'Patient biomarkers currently align within standard baseline epidemiological thresholds.'
    },
    Moderate: {
      badgeBg: 'bg-amber-50 text-amber-800 border-amber-300',
      barColor: 'bg-amber-500',
      icon: AlertTriangle,
      title: 'Moderate / Borderline Risk Detected',
      summary: 'Elevated risk parameters identified. Lifestyle adjustments and follow-up screening are advised.'
    },
    High: {
      badgeBg: 'bg-rose-50 text-rose-800 border-rose-300',
      barColor: 'bg-rose-600',
      icon: XCircle,
      title: 'High Risk / Clinical Investigation Recommended',
      summary: 'Significant biometric markers correlate with positive disease indicators in trained cohort.'
    }
  }[riskLevel] || {
    badgeBg: 'bg-slate-100 text-slate-800 border-slate-300',
    barColor: 'bg-cyan-600',
    icon: Activity,
    title: 'Risk Stratification Complete',
    summary: 'Biomarkers processed.'
  };

  const RiskIcon = riskConfig.icon;
  const downloadUrl = getReportDownloadUrl(record.id);

  return (
    <div className="w-full max-w-[1700px] mx-auto px-4 sm:px-6 lg:px-10 py-8 space-y-8 animate-fade-in">
      
      {/* Top Breadcrumb & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div className="flex items-center gap-3">
          <Link
            to={isDiabetes ? '/predict/diabetes' : '/predict/heart'}
            className="p-2 rounded-lg bg-white hover:bg-slate-50 border border-slate-300 text-slate-600 hover:text-slate-900 transition shadow-sm"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-slate-500">
              <span>Assessment Reference: #{record.id}</span>
              <span>•</span>
              <span className="capitalize">{record.disease} Risk</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900">Clinical Risk Evaluation Result</h1>
          </div>
        </div>

        <a
          href={downloadUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs transition shadow-md shadow-cyan-600/20 flex items-center justify-center gap-2 shrink-0"
        >
          <Download className="w-4 h-4" />
          <span>Download PDF Report</span>
        </a>
      </div>

      {/* Main Scorecard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 rounded-3xl bg-white border border-slate-200 shadow-sm">
        
        {/* Left: Large Probability Dial */}
        <div className="flex flex-col items-center justify-center p-6 rounded-2xl bg-slate-50 border border-slate-200 text-center space-y-3">
          <div className="text-xs font-mono text-slate-500 uppercase tracking-wider font-semibold">
            Computed Risk Score
          </div>

          <div className="relative flex items-center justify-center">
            <div className="text-5xl font-black text-slate-900 tracking-tight">
              {riskPercentage}<span className="text-2xl text-slate-400 font-normal">%</span>
            </div>
          </div>

          <div className={`px-3 py-1 rounded-full border text-xs font-bold font-mono uppercase tracking-wider ${riskConfig.badgeBg}`}>
            {riskLevel} Risk Tier
          </div>

          <div className="text-[11px] text-slate-500 font-mono pt-1">
            Raw Probability: {record.risk_probability.toFixed(4)}
          </div>
        </div>

        {/* Right: Risk Classification & Clinical Summary */}
        <div className="md:col-span-2 flex flex-col justify-between space-y-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <RiskIcon className={`w-5 h-5 ${riskLevel === 'Low' ? 'text-emerald-600' : (riskLevel === 'Moderate' ? 'text-amber-600' : 'text-rose-600')}`} />
              <h2 className="text-lg font-bold text-slate-900">{riskConfig.title}</h2>
            </div>
            <p className="text-slate-600 text-xs sm:text-sm leading-relaxed">
              {riskConfig.summary}
            </p>
          </div>

          {/* Model & Execution Meta */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs font-mono">
            <div>
              <div className="text-slate-500 text-[10px] uppercase font-semibold">Engine</div>
              <div className="text-slate-800 font-semibold">{record.model_name || 'Ensemble Classifier'}</div>
            </div>
            <div>
              <div className="text-slate-500 text-[10px] uppercase font-semibold">Binary Class</div>
              <div className="text-slate-800 font-semibold">
                {record.prediction === 1 ? 'Positive (1)' : 'Negative (0)'}
              </div>
            </div>
            <div className="col-span-2 sm:col-span-1">
              <div className="text-slate-500 text-[10px] uppercase font-semibold">Evaluated At</div>
              <div className="text-slate-800 font-semibold">{record.created_at?.substring(0, 10)}</div>
            </div>
          </div>

          {/* Probability Bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-[11px] font-mono text-slate-500">
              <span>Risk Scale (0% - 100%)</span>
              <span>Thresholds: 35% / 70%</span>
            </div>
            <div className="w-full h-3 rounded-full bg-slate-100 border border-slate-200 overflow-hidden p-0.5">
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
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <BarChart2 className="w-4 h-4 text-cyan-600" />
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider font-mono">
                Model Feature Importance Drivers
              </h3>
            </div>
            <span className="text-[11px] font-mono text-slate-500">Gini / Gradient Split %</span>
          </div>

          <div className="space-y-3">
            {record.feature_importance.slice(0, 6).map((feat, index) => (
              <div key={index} className="space-y-1">
                <div className="flex justify-between text-xs font-sans">
                  <span className="font-semibold text-slate-800">{feat.feature}</span>
                  <span className="font-mono text-cyan-700 font-bold">{feat.percentage.toFixed(2)}%</span>
                </div>
                <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden border border-slate-200">
                  <div
                    className="h-full bg-gradient-to-r from-cyan-600 to-blue-600 rounded-full"
                    style={{ width: `${feat.percentage}%` }}
                  ></div>
                </div>
                {feat.description && (
                  <p className="text-[10px] text-slate-500 italic">{feat.description}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Submitted Clinical Inputs Table */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider font-mono border-b border-slate-100 pb-3">
          Submitted Patient Biometric Inputs
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {Object.entries(record.input_data || {}).map(([key, val]) => (
            <div key={key} className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <div className="text-[10px] text-slate-500 font-mono uppercase font-semibold">{key}</div>
              <div className="text-sm font-bold text-slate-900 font-mono mt-0.5">
                {key.toLowerCase() === 'sex'
                  ? (String(val) === '1' || String(val).toLowerCase() === 'male' ? 'Male' : 'Female')
                  : String(val)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
        <Link
          to={isDiabetes ? '/predict/diabetes' : '/predict/heart'}
          className="px-5 py-2.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-semibold transition shadow-sm flex items-center gap-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Assess Another Patient</span>
        </Link>

        <a
          href={downloadUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="px-6 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs transition shadow-md shadow-cyan-600/20 flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          <span>Download PDF Report</span>
        </a>
      </div>

      {/* Verbatim Medical Disclaimer */}
      <div className="p-4 rounded-xl bg-amber-50/90 border border-amber-200/80 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-amber-900 text-xs uppercase tracking-wider font-mono">
            Mandatory Clinical Disclaimer
          </div>
          <p className="text-amber-950 text-[11px] leading-relaxed">
            HealthPredict AI provides machine-learning-based risk estimates for educational and decision-support purposes only. It does not diagnose, treat, cure, or prevent any disease. Always consult a qualified healthcare professional for medical advice.
          </p>
        </div>
      </div>

    </div>
  );
}
