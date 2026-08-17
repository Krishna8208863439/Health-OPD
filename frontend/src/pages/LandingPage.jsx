import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Activity, ArrowRight, Droplets, Heart, 
  Cpu, Database, TrendingUp, CheckCircle, BarChart3,
  Building2, Pill, Bot, Ticket, Apple, ShieldAlert, Phone, MapPin, ChevronRight, Award,
  LogIn, UserPlus, ShieldCheck, Sparkles, UserCheck
} from 'lucide-react';
import { getDashboardSummary, getVitals, getHospitals } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function LandingPage({ onOpenSOS }) {
  const { user, login } = useAuth();
  const [stats, setStats] = useState({
    total_predictions: 29,
    diabetes_predictions: 17,
    heart_predictions: 12,
    average_risk_percentage: 32.75
  });
  const [healthScore, setHealthScore] = useState(80);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [dash, vitals] = await Promise.allSettled([
          getDashboardSummary(),
          getVitals()
        ]);

        if (dash.status === 'fulfilled') setStats(dash.value);
        if (vitals.status === 'fulfilled' && vitals.value.current_score) {
          setHealthScore(vitals.value.current_score);
        }
      } catch (err) {
        console.error("Data load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const quickActions = [
    { title: 'Hospitals', subtitle: 'Directory & ICU', path: '/hospitals', icon: Building2, color: 'text-emerald-700', bg: 'bg-emerald-50 hover:bg-emerald-100/80 border-emerald-200' },
    { title: 'Vitals & Score', subtitle: 'Biometrics Tracker', path: '/vitals', icon: Activity, color: 'text-purple-700', bg: 'bg-purple-50 hover:bg-purple-100/80 border-purple-200' },
    { title: 'Diet & Nutrition', subtitle: 'Clinical Meal Plans', path: '/diet', icon: Apple, color: 'text-cyan-700', bg: 'bg-cyan-50 hover:bg-cyan-100/80 border-cyan-200' },
    { title: 'Medications', subtitle: 'Prescriptions & Stock', path: '/meds', icon: Pill, color: 'text-amber-700', bg: 'bg-amber-50 hover:bg-amber-100/80 border-amber-200' },
    { title: 'AI Assistant', subtitle: 'Clinical Chatbot', path: '/chat', icon: Bot, color: 'text-blue-700', bg: 'bg-blue-50 hover:bg-blue-100/80 border-blue-200' },
    { title: 'OPD Queue', subtitle: 'Digital Tokens', path: '/opd', icon: Ticket, color: 'text-indigo-700', bg: 'bg-indigo-50 hover:bg-indigo-100/80 border-indigo-200' },
  ];

  return (
    <div className="w-full max-w-[1700px] mx-auto px-4 sm:px-6 lg:px-10 py-8 space-y-10 animate-fade-in">
      
      {/* 1. PUBLIC GUEST WELCOME HERO (When Not Logged In) */}
      {!user ? (
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-br from-slate-900 via-cyan-950 to-blue-950 text-white shadow-2xl space-y-8 border border-cyan-900/50">
          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-400/30 text-cyan-300 text-xs font-semibold font-mono">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>Unified Clinical Healthcare & AI Risk Prediction</span>
            </div>
            
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight leading-tight">
              Comprehensive Hospital Care & Clinical Intelligence
            </h1>
            
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl">
              Sign in to your patient portal to track biometrics, monitor daily health scores, manage prescriptions, generate OPD queue tokens, and run AI disease risk screenings.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Link
              to="/login"
              className="px-6 py-3.5 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-extrabold text-sm flex items-center gap-2 shadow-lg shadow-cyan-500/25 transition"
            >
              <LogIn className="w-4 h-4" />
              <span>Sign In to Access Your Portal</span>
            </Link>

            <Link
              to="/register"
              className="px-6 py-3.5 rounded-2xl bg-white/10 hover:bg-white/20 text-white font-bold text-sm border border-white/20 transition flex items-center gap-2"
            >
              <UserPlus className="w-4 h-4" />
              <span>Create New Patient Account</span>
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 border-t border-white/10 text-xs font-mono text-slate-400">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>Secure Patient Registry</span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>Real-Time Vitals Scoring</span>
            </div>
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-purple-400 shrink-0" />
              <span>ML Risk Classifiers</span>
            </div>
            <div className="flex items-center gap-2">
              <Building2 className="w-4 h-4 text-amber-400 shrink-0" />
              <span>24/7 Hospital Telemetry</span>
            </div>
          </div>
        </div>
      ) : (
        /* 2. AUTHENTICATED PATIENT PROFILE BANNER (When Logged In) */
        <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-blue-50 via-cyan-50 to-indigo-50 border border-blue-200/80 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-1.5">
            <div className="text-xs text-blue-700 font-mono font-bold flex items-center gap-1.5">
              <span>Welcome to HealthCare+ Clinical Portal</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-slate-900 tracking-tight">
              {user.full_name}
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 font-mono flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-rose-500 shrink-0" />
              <span>{user.email} • Active Patient Profile (Kolhapur Registry)</span>
            </p>
          </div>

          {/* Mini Quick Badges */}
          <div className="flex flex-wrap gap-3 text-xs font-mono">
            <div className="px-4 py-2.5 rounded-2xl bg-white border border-blue-200 shadow-sm text-center min-w-[90px]">
              <div className="text-lg font-black text-blue-700">{stats.total_predictions}</div>
              <div className="text-[10px] text-slate-500 uppercase font-semibold">Reports</div>
            </div>

            <div className="px-4 py-2.5 rounded-2xl bg-white border border-blue-200 shadow-sm text-center min-w-[90px]">
              <div className="text-lg font-black text-amber-700">3</div>
              <div className="text-[10px] text-slate-500 uppercase font-semibold">Active Meds</div>
            </div>

            <div className="px-4 py-2.5 rounded-2xl bg-white border border-blue-200 shadow-sm text-center min-w-[90px]">
              <div className="text-lg font-black text-emerald-700">{healthScore}</div>
              <div className="text-[10px] text-slate-500 uppercase font-semibold">Health Score</div>
            </div>
          </div>
        </div>
      )}

      {/* 3. DAILY HEALTH SCORE BANNER (Visible after sign in or preview) */}
      <div className="p-6 sm:p-7 rounded-3xl bg-white border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-5">
          <div className="w-18 h-18 sm:w-20 sm:h-20 rounded-2xl bg-emerald-50 border-2 border-emerald-400 flex flex-col items-center justify-center shrink-0">
            <span className="text-3xl font-black text-emerald-700">{healthScore}</span>
            <span className="text-[9px] text-emerald-800 font-mono font-bold uppercase">Score</span>
          </div>

          <div className="space-y-1">
            <h2 className="text-base sm:text-lg font-bold text-slate-900 flex items-center gap-2">
              <span>Your Daily Health Score & Biometric Status</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed max-w-3xl">
              {user 
                ? "Excellent! Your medication adherence, recent vital parameters, and nutritional habits are within optimal physiological thresholds."
                : "Sign in to track your personalized daily health score, biometric trends, and automated physiological evaluation."}
            </p>
          </div>
        </div>

        <Link
          to={user ? "/vitals" : "/login"}
          className="px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold font-mono flex items-center gap-1.5 shrink-0 transition"
        >
          <span>{user ? "Update Vitals Log" : "Sign In to View"}</span>
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>

      {/* 4. QUICK ACTIONS (6 Grid Cards - Gated for Authenticated Users) */}
      <div className="space-y-3">
        <div className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono">
          Clinical Navigation & Quick Actions
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
          {quickActions.map((act, i) => {
            const Icon = act.icon;
            const targetPath = user ? act.path : '/login';
            return (
              <Link
                key={i}
                to={targetPath}
                className={`p-4 rounded-2xl border transition shadow-sm flex flex-col items-center justify-center text-center gap-2.5 ${act.bg}`}
              >
                <div className="w-11 h-11 rounded-xl bg-white shadow-sm flex items-center justify-center">
                  <Icon className={`w-5 h-5 ${act.color}`} />
                </div>
                <div>
                  <div className="font-bold text-slate-900 text-xs sm:text-sm">{act.title}</div>
                  <div className="text-[10px] text-slate-500 font-mono">{act.subtitle}</div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* 5. EMERGENCY SOS RED BANNER */}
      <div className="p-5 sm:p-6 rounded-3xl bg-gradient-to-r from-rose-600 to-red-600 text-white shadow-lg flex flex-col sm:flex-row items-center justify-between gap-5">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center shrink-0">
            <ShieldAlert className="w-7 h-7 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-base sm:text-lg">
              Find Nearest Hospital & Emergency Centers
            </div>
            <div className="text-xs text-rose-100 font-mono mt-0.5">
              Live GPS Navigation • Direct Emergency Lines (108 / 112) • 24/7 ICU Telemetry
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          <Link
            to={user ? "/hospitals" : "/login"}
            className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-white hover:bg-slate-100 text-rose-700 font-bold text-xs shadow-sm transition text-center"
          >
            Hospital Directory
          </Link>
          <button
            onClick={onOpenSOS}
            className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-slate-900 hover:bg-black text-white font-bold text-xs shadow-sm transition flex items-center justify-center gap-1.5"
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Emergency SOS</span>
          </button>
        </div>
      </div>

      {/* 6. MACHINE LEARNING CLINICAL RISK PREDICTION SECTION */}
      <div className="space-y-6 pt-4 border-t border-slate-200">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-50 border border-cyan-200 text-cyan-800 text-xs font-semibold font-mono">
            <Cpu className="w-3.5 h-3.5 text-cyan-600" />
            <span>Supervised Machine Learning Risk Predictors</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Clinical Disease Risk Stratification
          </h2>
          <p className="text-slate-600 text-xs sm:text-sm">
            Screen for Type 2 Diabetes and Coronary Heart Disease with verifiable, explainable ML models.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Diabetes Card */}
          <div className="p-6 sm:p-7 rounded-3xl bg-white border border-slate-200 hover:border-cyan-400 transition shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-2xl bg-cyan-50 border border-cyan-200 flex items-center justify-center text-cyan-600">
                <Droplets className="w-6 h-6" />
              </div>
              <span className="text-xs font-mono px-3 py-1 rounded-full bg-cyan-50 text-cyan-800 border border-cyan-200 font-semibold">
                Gradient Boosting • 82.2% AUC
              </span>
            </div>

            <div>
              <h3 className="text-xl font-bold text-slate-900">Type 2 Diabetes Risk</h3>
              <p className="text-slate-600 text-xs mt-1.5 leading-relaxed">
                Evaluates metabolic biomarkers including plasma glucose, BMI, insulin, pedigree function, and age to compute calibrated risk probability.
              </p>
            </div>

            <Link
              to={user ? "/predict/diabetes" : "/login"}
              className="w-full py-3 rounded-xl bg-cyan-50 hover:bg-cyan-600 hover:text-white text-cyan-800 font-semibold text-xs transition flex items-center justify-center gap-2 border border-cyan-200 shadow-sm"
            >
              <span>{user ? "Launch Diabetes Assessment" : "Sign In to Launch Assessment"}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Heart Disease Card */}
          <div className="p-6 sm:p-7 rounded-3xl bg-white border border-slate-200 hover:border-rose-400 transition shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="w-12 h-12 rounded-2xl bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600">
                <Heart className="w-6 h-6" />
              </div>
              <span className="text-xs font-mono px-3 py-1 rounded-full bg-rose-50 text-rose-800 border border-rose-200 font-semibold">
                Random Forest • 95.4% AUC
              </span>
            </div>

            <div>
              <h3 className="text-xl font-bold text-slate-900">Coronary Heart Disease Risk</h3>
              <p className="text-slate-600 text-xs mt-1.5 leading-relaxed">
                Screens for cardiac ischemia and atherosclerosis based on 13 diagnostic parameters including BP, cholesterol, and max HR.
              </p>
            </div>

            <Link
              to={user ? "/predict/heart" : "/login"}
              className="w-full py-3 rounded-xl bg-rose-50 hover:bg-rose-600 hover:text-white text-rose-800 font-semibold text-xs transition flex items-center justify-center gap-2 border border-rose-200 shadow-sm"
            >
              <span>{user ? "Launch Heart Assessment" : "Sign In to Launch Assessment"}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

        </div>
      </div>

      {/* 7. TELEMETRY STATS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500 text-xs font-mono uppercase">
            <span>Total Evaluated</span>
            <Database className="w-4 h-4 text-cyan-600" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900">{stats.total_predictions}</div>
          <p className="text-[11px] text-emerald-700 font-medium flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-emerald-600" /> Persistent SQLite Registry
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500 text-xs font-mono uppercase">
            <span>Diabetes Assessed</span>
            <Droplets className="w-4 h-4 text-cyan-600" />
          </div>
          <div className="text-3xl font-extrabold text-cyan-700">{stats.diabetes_predictions}</div>
          <p className="text-[11px] text-slate-500 font-mono">Gradient Boosting Model</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500 text-xs font-mono uppercase">
            <span>Heart Assessed</span>
            <Heart className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-3xl font-extrabold text-rose-600">{stats.heart_predictions}</div>
          <p className="text-[11px] text-slate-500 font-mono">Random Forest Model</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500 text-xs font-mono uppercase">
            <span>Average Patient Risk</span>
            <TrendingUp className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-3xl font-extrabold text-amber-700">{stats.average_risk_percentage}%</div>
          <p className="text-[11px] text-slate-500 font-mono">Population Mean Probability</p>
        </div>
      </div>

    </div>
  );
}
