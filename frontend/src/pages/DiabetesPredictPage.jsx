import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Droplets, ArrowRight, AlertCircle, Sparkles, HelpCircle, Activity } from 'lucide-react';
import { predictDiabetes } from '../services/api';

export default function DiabetesPredictPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    Pregnancies: 1,
    Glucose: 110,
    BloodPressure: 72,
    SkinThickness: 24,
    Insulin: 85,
    BMI: 26.5,
    DiabetesPedigreeFunction: 0.35,
    Age: 32
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const presets = [
    {
      name: "Low Risk Profile",
      data: { Pregnancies: 1, Glucose: 78, BloodPressure: 65, SkinThickness: 18, Insulin: 50, BMI: 21.5, DiabetesPedigreeFunction: 0.15, Age: 22 }
    },
    {
      name: "Borderline Profile",
      data: { Pregnancies: 3, Glucose: 135, BloodPressure: 76, SkinThickness: 28, Insulin: 110, BMI: 29.5, DiabetesPedigreeFunction: 0.45, Age: 45 }
    },
    {
      name: "High Risk Profile",
      data: { Pregnancies: 6, Glucose: 190, BloodPressure: 88, SkinThickness: 38, Insulin: 220, BMI: 38.2, DiabetesPedigreeFunction: 1.25, Age: 58 }
    }
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? '' : Number(value)
    }));
  };

  const loadPreset = (presetData) => {
    setFormData(presetData);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Client-side sanity checks
    if (formData.Glucose < 30 || formData.Glucose > 300) {
      setError("Glucose level must be between 30 and 300 mg/dL");
      return;
    }
    if (formData.BMI < 10 || formData.BMI > 75) {
      setError("BMI must be between 10.0 and 75.0 kg/m²");
      return;
    }
    if (formData.Age < 1 || formData.Age > 125) {
      setError("Age must be between 1 and 125");
      return;
    }

    try {
      setLoading(true);
      const result = await predictDiabetes(formData);
      navigate(`/result/${result.id}`);
    } catch (err) {
      console.error("Prediction submission error:", err);
      const msg = err.response?.data?.message || err.message || "Failed to submit assessment.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-mono font-semibold">
            <Droplets className="w-4 h-4" />
            <span>METABOLIC SCREENING MODULE</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Type 2 Diabetes Risk Calculator</h1>
          <p className="text-slate-400 text-xs sm:text-sm">
            Trained Gradient Boosting Ensemble • Pima Indians Diabetes Diagnostic Registry
          </p>
        </div>

        {/* Clinical Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Presets:
          </span>
          {presets.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => loadPreset(p.data)}
              className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs text-slate-300 font-medium transition"
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Error Callout */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Input Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl">
          
          {/* Glucose */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-200">
              Plasma Glucose Concentration (mg/dL) <span className="text-cyan-400">*</span>
            </label>
            <input
              type="number"
              name="Glucose"
              value={formData.Glucose}
              onChange={handleChange}
              min="30"
              max="300"
              step="1"
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
            />
            <p className="text-[10px] text-slate-500">Normal fasting range: 70–99 mg/dL. Pre-diabetes: 100–125.</p>
          </div>

          {/* BMI */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-200">
              Body Mass Index (BMI kg/m²) <span className="text-cyan-400">*</span>
            </label>
            <input
              type="number"
              name="BMI"
              value={formData.BMI}
              onChange={handleChange}
              min="10"
              max="75"
              step="0.1"
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
            />
            <p className="text-[10px] text-slate-500">Calculated as: weight (kg) / [height (m)]².</p>
          </div>

          {/* Age */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-200">
              Patient Age (Years) <span className="text-cyan-400">*</span>
            </label>
            <input
              type="number"
              name="Age"
              value={formData.Age}
              onChange={handleChange}
              min="1"
              max="125"
              step="1"
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
            />
            <p className="text-[10px] text-slate-500">Risk increases above 40 years.</p>
          </div>

          {/* Diabetes Pedigree Function */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-200">
              Diabetes Pedigree Function <span className="text-cyan-400">*</span>
            </label>
            <input
              type="number"
              name="DiabetesPedigreeFunction"
              value={formData.DiabetesPedigreeFunction}
              onChange={handleChange}
              min="0.01"
              max="3.0"
              step="0.01"
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
            />
            <p className="text-[10px] text-slate-500">Family genetic score (typical range: 0.1 to 1.5).</p>
          </div>

          {/* Blood Pressure */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-200">
              Diastolic Blood Pressure (mm Hg)
            </label>
            <input
              type="number"
              name="BloodPressure"
              value={formData.BloodPressure}
              onChange={handleChange}
              min="30"
              max="250"
              step="1"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
            />
            <p className="text-[10px] text-slate-500">Normal diastolic: 60–80 mm Hg.</p>
          </div>

          {/* Serum Insulin */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-200">
              2-Hour Serum Insulin (µU/mL)
            </label>
            <input
              type="number"
              name="Insulin"
              value={formData.Insulin}
              onChange={handleChange}
              min="0"
              max="900"
              step="1"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
            />
            <p className="text-[10px] text-slate-500">Enter 0 if measurement not available (imputed).</p>
          </div>

          {/* Pregnancies */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-200">
              Number of Pregnancies
            </label>
            <input
              type="number"
              name="Pregnancies"
              value={formData.Pregnancies}
              onChange={handleChange}
              min="0"
              max="25"
              step="1"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
            />
            <p className="text-[10px] text-slate-500">Total gestational occurrences.</p>
          </div>

          {/* Skin Thickness */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-200">
              Triceps Skin Fold Thickness (mm)
            </label>
            <input
              type="number"
              name="SkinThickness"
              value={formData.SkinThickness}
              onChange={handleChange}
              min="0"
              max="100"
              step="1"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 font-mono"
            />
            <p className="text-[10px] text-slate-500">Subcutaneous adipose metric (mm).</p>
          </div>

        </div>

        {/* Submit Action */}
        <div className="flex items-center justify-end gap-4">
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-3.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-cyan-500/25 flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></div>
                <span>Computing Inference...</span>
              </>
            ) : (
              <>
                <Activity className="w-4 h-4" />
                <span>Calculate Diabetes Risk</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

      </form>
    </div>
  );
}
