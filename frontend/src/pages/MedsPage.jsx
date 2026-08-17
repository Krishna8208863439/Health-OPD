import React, { useState, useEffect } from 'react';
import { Pill, PlusCircle, CheckCircle2, Circle, Clock, Trash2, AlertCircle } from 'lucide-react';
import { getMedicines, addMedicine, updateMedicine, deleteMedicine } from '../services/api';

export default function MedsPage() {
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newMed, setNewMed] = useState({
    name: '',
    dosage: '500 mg',
    timing: 'Morning & Night',
    meal_instruction: 'After Meal',
    stock_count: 30
  });

  const loadMeds = async () => {
    try {
      setLoading(true);
      const data = await getMedicines();
      setMedicines(data.medicines || []);
    } catch (err) {
      console.error("Failed to load medicines:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMeds();
  }, []);

  const handleToggle = async (id, currentStatus) => {
    try {
      await updateMedicine({ id, taken_today: !currentStatus });
      setMedicines(prev => prev.map(m => m.id === id ? { ...m, taken_today: !currentStatus } : m));
    } catch (err) {
      console.error("Failed to update medicine status:", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Remove this medicine reminder?")) return;
    try {
      await deleteMedicine(id);
      setMedicines(prev => prev.filter(m => m.id !== id));
    } catch (err) {
      console.error("Failed to delete medicine:", err);
    }
  };

  const handleAddSubmit = async (e) => {
    e.preventDefault();
    if (!newMed.name) return;
    try {
      await addMedicine(newMed);
      setShowAddModal(false);
      setNewMed({ name: '', dosage: '500 mg', timing: 'Morning & Night', meal_instruction: 'After Meal', stock_count: 30 });
      loadMeds();
    } catch (err) {
      console.error("Failed to add medicine:", err);
    }
  };

  const completedCount = medicines.filter(m => m.taken_today).length;

  return (
    <div className="max-w-5xl mx-auto py-10 px-4 space-y-8 animate-fade-in">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center gap-2 text-cyan-700 text-xs font-mono font-semibold">
            <Pill className="w-4 h-4 text-cyan-600" />
            <span>DAILY PHARMACY & PRESCRIPTION REMINDERS</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Medication Manager / औषधे व्यवस्थापन
          </h1>
          <p className="text-slate-600 text-xs sm:text-sm">
            Track daily dosages, meal instructions, refill stock alerts, and mark doses as taken.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs flex items-center gap-2 shadow-md shadow-cyan-600/20 transition self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Add New Prescription</span>
        </button>
      </div>

      {/* Adherence Progress Card */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-cyan-600 to-blue-700 text-white shadow-lg space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs uppercase font-mono text-cyan-200">Today's Adherence Schedule</div>
            <div className="text-2xl font-black">{completedCount} of {medicines.length} Doses Taken</div>
          </div>
          <div className="text-right font-mono text-xs text-cyan-100">
            {medicines.length > 0 ? `${Math.round((completedCount / medicines.length) * 100)}% Complete` : '0%'}
          </div>
        </div>

        <div className="w-full h-3 rounded-full bg-white/20 overflow-hidden">
          <div
            className="h-full bg-white rounded-full transition-all duration-500"
            style={{ width: medicines.length > 0 ? `${(completedCount / medicines.length) * 100}%` : '0%' }}
          ></div>
        </div>
      </div>

      {/* Medicines List */}
      {loading ? (
        <div className="py-16 text-center text-xs text-slate-500 font-mono">Loading active prescriptions...</div>
      ) : medicines.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 space-y-3">
          <Pill className="w-8 h-8 text-slate-400 mx-auto" />
          <h3 className="text-sm font-bold text-slate-800">No Medications Scheduled</h3>
          <p className="text-xs text-slate-500">Click "Add New Prescription" to set up your medicine alerts.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {medicines.map((med) => (
            <div
              key={med.id}
              className={`p-5 rounded-2xl border transition shadow-sm flex items-center justify-between gap-4 ${
                med.taken_today
                  ? 'bg-emerald-50/60 border-emerald-200'
                  : 'bg-white border-slate-200 hover:border-cyan-300'
              }`}
            >
              <div className="flex items-start gap-3.5">
                <button
                  onClick={() => handleToggle(med.id, med.taken_today)}
                  className="mt-0.5 transition hover:scale-110"
                  title="Toggle Taken Status"
                >
                  {med.taken_today ? (
                    <CheckCircle2 className="w-6 h-6 text-emerald-600 fill-emerald-100" />
                  ) : (
                    <Circle className="w-6 h-6 text-slate-300 hover:text-cyan-600" />
                  )}
                </button>

                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h4 className={`font-bold text-sm ${med.taken_today ? 'text-slate-500 line-through' : 'text-slate-900'}`}>
                      {med.name}
                    </h4>
                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px] font-semibold border border-slate-200">
                      {med.dosage}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500 font-mono">
                    <span className="flex items-center gap-1 text-cyan-800 font-medium">
                      <Clock className="w-3 h-3" /> {med.timing}
                    </span>
                    <span>•</span>
                    <span className="text-slate-600">{med.meal_instruction}</span>
                  </div>

                  <div className="text-[11px] text-slate-400 font-mono pt-0.5">
                    Stock Remaining: <span className="font-bold text-slate-700">{med.stock_count} pills</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleDelete(med.id)}
                className="p-2 rounded-lg text-slate-300 hover:text-rose-600 hover:bg-rose-50 transition"
                title="Delete Medicine"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-5 shadow-2xl border border-slate-200">
            <h3 className="font-bold text-slate-900 text-base">Add Medication Reminder</h3>
            
            <form onSubmit={handleAddSubmit} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Medicine Name (औषधाचे नाव) *</label>
                <input
                  type="text"
                  placeholder="e.g. Paracetamol / Metformin"
                  value={newMed.name}
                  onChange={(e) => setNewMed({ ...newMed, name: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-slate-900 focus:bg-white"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Dosage (मात्रा)</label>
                  <input
                    type="text"
                    placeholder="e.g. 500 mg"
                    value={newMed.dosage}
                    onChange={(e) => setNewMed({ ...newMed, dosage: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-slate-900 focus:bg-white"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Stock Count</label>
                  <input
                    type="number"
                    value={newMed.stock_count}
                    onChange={(e) => setNewMed({ ...newMed, stock_count: e.target.value })}
                    className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-slate-900 focus:bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Frequency / Timing</label>
                <select
                  value={newMed.timing}
                  onChange={(e) => setNewMed({ ...newMed, timing: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-slate-900 focus:bg-white font-mono"
                >
                  <option value="Morning">Morning (सकाळी)</option>
                  <option value="Afternoon">Afternoon (दुपारी)</option>
                  <option value="Night">Night (रात्री)</option>
                  <option value="Morning & Night">Morning & Night (सकाळी आणि रात्री)</option>
                  <option value="Three Times a Day">Three Times a Day (दिवसातून ३ वेळा)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Meal Instruction</label>
                <select
                  value={newMed.meal_instruction}
                  onChange={(e) => setNewMed({ ...newMed, meal_instruction: e.target.value })}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-slate-900 focus:bg-white font-mono"
                >
                  <option value="After Meal">After Meal (जेवणानंतर)</option>
                  <option value="Before Meal">Before Meal (जेवणापूर्वी)</option>
                  <option value="With Meal">With Meal (जेवणासोबत)</option>
                </select>
              </div>

              <div className="flex items-center gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold"
                >
                  Add Medicine
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
