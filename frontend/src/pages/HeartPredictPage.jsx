import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart, ArrowRight, AlertCircle, Sparkles, Activity } from 'lucide-react';
import { predictHeart } from '../services/api';

export default function HeartPredictPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    age: 52,
    sex: 1,
    cp: 2,
    trestbps: 130,
    chol: 225,
    fbs: 0,
    restecg: 0,
    thalach: 155,
    exang: 0,
    oldpeak: 1.0,
    slope: 2,
    ca: 0,
    thal: 3
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const presets = [
    {
      name: "Healthy Profile",
      data: { age: 35, sex: 0, cp: 1, trestbps: 115, chol: 180, fbs: 0, restecg: 0, thalach: 175, exang: 0, oldpeak: 0.0, slope: 1, ca: 0, thal: 3 }
    },
    {
      name: "Moderate Risk",
      data: { age: 52, sex: 1, cp: 3, trestbps: 135, chol: 230, fbs: 0, restecg: 1, thalach: 145, exang: 0, oldpeak: 1.2, slope: 2, ca: 1, thal: 6 }
    },
    {
      name: "Critical Cardiac Alert",
      data: { age: 67, sex: 1, cp: 4, trestbps: 160, chol: 286, fbs: 1, restecg: 2, thalach: 108, exang: 1, oldpeak: 3.5, slope: 2, ca: 3, thal: 7 }
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

    if (formData.age < 1 || formData.age > 125) {
      setError("Age must be between 1 and 125");
      return;
    }
    if (formData.trestbps < 50 || formData.trestbps > 260) {
      setError("Resting blood pressure must be between 50 and 260 mm Hg");
      return;
    }
    if (formData.chol < 80 || formData.chol > 650) {
      setError("Cholesterol must be between 80 and 650 mg/dl");
      return;
    }

    try {
      setLoading(true);
      const result = await predictHeart(formData);
      navigate(`/result/${result.id}`);
    } catch (err) {
      console.error("Heart prediction error:", err);
      const msg = err.response?.data?.message || err.message || "Failed to submit heart assessment.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-rose-700 text-xs font-mono font-semibold">
            <Heart className="w-4 h-4 text-rose-600" />
            <span>CARDIOVASCULAR SCREENING MODULE</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">Coronary Heart Disease Risk Calculator</h1>
          <p className="text-slate-600 text-xs sm:text-sm">
            Trained Random Forest Classifier • Cleveland Heart Disease Registry (14 Attributes)
          </p>
        </div>

        {/* Clinical Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-500 font-mono flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-rose-600" /> Presets:
          </span>
          {presets.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => loadPreset(p.data)}
              className="px-2.5 py-1 rounded-lg bg-white hover:bg-slate-50 border border-slate-300 text-xs text-slate-700 font-medium transition shadow-sm"
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Input Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
          
          {/* Age */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Age (Years) <span className="text-rose-600">*</span>
            </label>
            <input
              type="number"
              name="age"
              value={formData.age}
              onChange={handleChange}
              min="1"
              max="125"
              required
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            />
          </div>

          {/* Sex */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Biological Sex <span className="text-rose-600">*</span>
            </label>
            <select
              name="sex"
              value={formData.sex}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            >
              <option value={1}>Male (1)</option>
              <option value={0}>Female (0)</option>
            </select>
          </div>

          {/* Chest Pain Type (cp) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Chest Pain Type (cp) <span className="text-rose-600">*</span>
            </label>
            <select
              name="cp"
              value={formData.cp}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            >
              <option value={1}>1: Typical Angina</option>
              <option value={2}>2: Atypical Angina</option>
              <option value={3}>3: Non-Anginal Pain</option>
              <option value={4}>4: Asymptomatic (Silent Ischemia)</option>
            </select>
          </div>

          {/* Resting BP (trestbps) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Resting BP (mm Hg) <span className="text-rose-600">*</span>
            </label>
            <input
              type="number"
              name="trestbps"
              value={formData.trestbps}
              onChange={handleChange}
              min="50"
              max="260"
              required
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            />
          </div>

          {/* Cholesterol (chol) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Serum Cholesterol (mg/dL) <span className="text-rose-600">*</span>
            </label>
            <input
              type="number"
              name="chol"
              value={formData.chol}
              onChange={handleChange}
              min="80"
              max="650"
              required
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            />
          </div>

          {/* Fasting Blood Sugar (fbs) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Fasting Blood Sugar &gt; 120 mg/dL
            </label>
            <select
              name="fbs"
              value={formData.fbs}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            >
              <option value={0}>False / Normal (0)</option>
              <option value={1}>True / Elevated (1)</option>
            </select>
          </div>

          {/* Resting ECG (restecg) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Resting ECG Result
            </label>
            <select
              name="restecg"
              value={formData.restecg}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            >
              <option value={0}>0: Normal</option>
              <option value={1}>1: ST-T wave abnormality</option>
              <option value={2}>2: Left ventricular hypertrophy</option>
            </select>
          </div>

          {/* Max Heart Rate (thalach) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Max Heart Rate Achieved (bpm) <span className="text-rose-600">*</span>
            </label>
            <input
              type="number"
              name="thalach"
              value={formData.thalach}
              onChange={handleChange}
              min="50"
              max="250"
              required
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            />
          </div>

          {/* Exercise Induced Angina (exang) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Exercise Induced Angina
            </label>
            <select
              name="exang"
              value={formData.exang}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            >
              <option value={0}>No (0)</option>
              <option value={1}>Yes (1)</option>
            </select>
          </div>

          {/* ST Depression (oldpeak) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              ST Depression (oldpeak)
            </label>
            <input
              type="number"
              name="oldpeak"
              value={formData.oldpeak}
              onChange={handleChange}
              min="0.0"
              max="10.0"
              step="0.1"
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            />
          </div>

          {/* ST Slope (slope) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Peak Exercise ST Slope
            </label>
            <select
              name="slope"
              value={formData.slope}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            >
              <option value={1}>1: Upsloping</option>
              <option value={2}>2: Flat</option>
              <option value={3}>3: Downsloping</option>
            </select>
          </div>

          {/* Major Vessels (ca) */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-800">
              Major Vessels Colored (0–3)
            </label>
            <select
              name="ca"
              value={formData.ca}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            >
              <option value={0}>0 Vessels</option>
              <option value={1}>1 Vessel</option>
              <option value={2}>2 Vessels</option>
              <option value={3}>3 Vessels</option>
            </select>
          </div>

          {/* Thalassemia (thal) */}
          <div className="space-y-1.5 lg:col-span-3">
            <label className="block text-xs font-semibold text-slate-800">
              Thalassemia Status (thal) <span className="text-rose-600">*</span>
            </label>
            <select
              name="thal"
              value={formData.thal}
              onChange={handleChange}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm text-slate-900 focus:outline-none focus:border-rose-600 focus:bg-white font-mono"
            >
              <option value={3}>3: Normal Blood Flow</option>
              <option value={6}>6: Fixed Defect (Non-Reversible)</option>
              <option value={7}>7: Reversible Defect</option>
            </select>
          </div>

        </div>

        {/* Submit Button */}
        <div className="flex items-center justify-end gap-4">
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-3.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold text-sm transition shadow-md shadow-rose-600/20 flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Evaluating Cardiac Risk...</span>
              </>
            ) : (
              <>
                <Activity className="w-4 h-4" />
                <span>Calculate Heart Disease Risk</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

      </form>
    </div>
  );
}
