import React, { useState, useEffect } from 'react';
import { Apple, Utensils, Flame, Sparkles, CheckCircle2, ChevronRight } from 'lucide-react';
import { getDietPlans } from '../services/api';

export default function DietPage() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState(null);

  // Calorie calculator state
  const [weight, setWeight] = useState(70);
  const [height, setHeight] = useState(172);
  const [age, setAge] = useState(30);
  const [gender, setGender] = useState('male');
  const [activity, setActivity] = useState(1.375); // Light active

  useEffect(() => {
    async function loadPlans() {
      try {
        setLoading(true);
        const data = await getDietPlans();
        setPlans(data.plans || []);
        if (data.plans && data.plans.length > 0) {
          setSelectedPlan(data.plans[0]);
        }
      } catch (err) {
        console.error("Failed to load diet plans:", err);
      } finally {
        setLoading(false);
      }
    }
    loadPlans();
  }, []);

  // Harris-Benedict BMR formula
  const bmr = gender === 'male'
    ? 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    : 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);

  const tdee = Math.round(bmr * activity);

  return (
    <div className="max-w-6xl mx-auto py-10 px-4 space-y-8 animate-fade-in">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center gap-2 text-cyan-700 text-xs font-mono font-semibold">
            <Apple className="w-4 h-4 text-cyan-600" />
            <span>CLINICAL DIET & NUTRITION PLANNER</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Diet & Wellness Plans / आहार आणि पोषण नियोजन
          </h1>
          <p className="text-slate-600 text-xs sm:text-sm">
            Personalized meal plans for diabetes management, cardiovascular health, and daily vitality.
          </p>
        </div>
      </div>

      {/* Calorie Calculator Card */}
      <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
          <Flame className="w-5 h-5 text-amber-500" />
          <h3 className="font-bold text-slate-900 text-sm">Personal Daily Calorie & Macro Estimator</h3>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
          <div>
            <label className="block text-slate-600 font-semibold mb-1">Weight (kg)</label>
            <input
              type="number"
              value={weight}
              onChange={(e) => setWeight(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-mono text-slate-900"
            />
          </div>

          <div>
            <label className="block text-slate-600 font-semibold mb-1">Height (cm)</label>
            <input
              type="number"
              value={height}
              onChange={(e) => setHeight(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-mono text-slate-900"
            />
          </div>

          <div>
            <label className="block text-slate-600 font-semibold mb-1">Age (Years)</label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-mono text-slate-900"
            />
          </div>

          <div>
            <label className="block text-slate-600 font-semibold mb-1">Gender</label>
            <select
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-mono text-slate-900"
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-600 font-semibold mb-1">Activity Level</label>
            <select
              value={activity}
              onChange={(e) => setActivity(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-mono text-slate-900"
            >
              <option value={1.2}>Sedentary (कमी हालचाल)</option>
              <option value={1.375}>Light (१-३ दिवस व्यायाम)</option>
              <option value={1.55}>Moderate (३-५ दिवस)</option>
            </select>
          </div>
        </div>

        {/* Output Banner */}
        <div className="p-4 rounded-2xl bg-amber-50/80 border border-amber-200 flex items-center justify-between">
          <div>
            <span className="text-xs text-amber-900 font-semibold">Estimated Maintenance Calories:</span>
            <div className="text-2xl font-black text-amber-900 font-mono mt-0.5">{tdee} kcal / day</div>
          </div>
          <div className="text-right text-xs font-mono text-amber-800">
            <div>Target for Weight Loss: <b>{Math.max(1200, tdee - 400)} kcal</b></div>
            <div className="text-[11px] text-amber-700">Protein target: <b>~{Math.round(weight * 1.5)}g / day</b></div>
          </div>
        </div>
      </div>

      {/* Diet Plans Grid */}
      {loading ? (
        <div className="py-16 text-center text-xs text-slate-500 font-mono">Loading curated nutrition plans...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((p) => (
            <div
              key={p.id}
              onClick={() => setSelectedPlan(p)}
              className={`p-6 rounded-3xl border transition shadow-sm cursor-pointer space-y-4 ${
                selectedPlan?.id === p.id
                  ? 'bg-cyan-50/70 border-cyan-400 ring-2 ring-cyan-500/20'
                  : 'bg-white border-slate-200 hover:border-cyan-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-1 rounded-full bg-cyan-100 text-cyan-800 text-[10px] font-bold font-mono">
                  {p.target_calories}
                </span>
                <Sparkles className="w-4 h-4 text-cyan-600" />
              </div>

              <div>
                <h3 className="font-bold text-slate-900 text-base">{p.title}</h3>
                <p className="text-xs text-cyan-700 font-medium">{p.marathi_title}</p>
              </div>

              {/* Meals list */}
              <div className="space-y-2.5 text-xs text-slate-700 pt-2 border-t border-slate-100">
                <div>
                  <span className="font-bold text-slate-800 text-[11px]">🌅 Breakfast (नाश्ता):</span>
                  <p className="text-slate-600 mt-0.5 text-[11px] leading-relaxed">{p.breakfast}</p>
                </div>
                <div>
                  <span className="font-bold text-slate-800 text-[11px]">☀️ Lunch (दुपारचे जेवण):</span>
                  <p className="text-slate-600 mt-0.5 text-[11px] leading-relaxed">{p.lunch}</p>
                </div>
                <div>
                  <span className="font-bold text-slate-800 text-[11px]">🌙 Dinner (रात्रीचे जेवण):</span>
                  <p className="text-slate-600 mt-0.5 text-[11px] leading-relaxed">{p.dinner}</p>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-[11px] text-slate-600 leading-relaxed italic">
                💡 {p.tips}
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
