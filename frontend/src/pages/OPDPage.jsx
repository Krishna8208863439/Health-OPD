import React, { useState, useEffect } from 'react';
import { Ticket, PlusCircle, Clock, CheckCircle, AlertCircle, Building2 } from 'lucide-react';
import { getOPDTickets, createOPDTicket } from '../services/api';

export default function OPDPage() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [generatedTicket, setGeneratedTicket] = useState(null);

  const [form, setForm] = useState({
    patient_name: 'Krishna Devadkar',
    department: 'General Medicine',
    triage_level: 'ROUTINE',
    chief_complaint: 'Regular follow-up consultation'
  });

  const departments = [
    'General Medicine',
    'Cardiology (हृदयरोग विभाग)',
    'Diabetology & Endocrinology',
    'Orthopedics (अस्थिरोग विभाग)',
    'Pediatrics (बालरोग विभाग)',
    'ENT (कान-नाक-घसा विभाग)',
    'Dermatology (त्वचारोग विभाग)'
  ];

  const loadTickets = async () => {
    try {
      setLoading(true);
      const data = await getOPDTickets();
      setTickets(data.tickets || []);
    } catch (err) {
      console.error("Failed to load OPD tickets:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const res = await createOPDTicket(form);
      setGeneratedTicket(res.ticket);
      loadTickets();
    } catch (err) {
      console.error("Failed to create ticket:", err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-10 px-4 space-y-8 animate-fade-in">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center gap-2 text-cyan-700 text-xs font-mono font-semibold">
            <Ticket className="w-4 h-4 text-cyan-600" />
            <span>SMART HOSPITAL OPD & TRIAGE SYSTEM</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Digital OPD Queue & Tokens / ओपीडी टोकन प्रणाली
          </h1>
          <p className="text-slate-600 text-xs sm:text-sm">
            Generate digital OPD appointment tickets, track live consultation queue, and check triage status.
          </p>
        </div>
      </div>

      {/* Generated Token Banner Modal */}
      {generatedTicket && (
        <div className="p-6 rounded-3xl bg-emerald-50 border border-emerald-200 shadow-md flex flex-col md:flex-row items-center justify-between gap-6 animate-scale-up">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 rounded-2xl bg-emerald-600 text-white flex flex-col items-center justify-center font-mono">
              <span className="text-[10px] uppercase">Token</span>
              <span className="text-3xl font-black">#{generatedTicket.token_number}</span>
            </div>

            <div className="space-y-1">
              <div className="text-xs font-bold text-emerald-800 uppercase font-mono flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span>Ticket Generated Successfully!</span>
              </div>
              <h3 className="text-lg font-bold text-slate-900">{generatedTicket.department}</h3>
              <p className="text-xs text-slate-600 font-mono">
                Patient: <span className="font-bold text-slate-800">{generatedTicket.patient_name}</span> | Priority: <span className="font-bold text-amber-700">{generatedTicket.triage_level}</span>
              </p>
            </div>
          </div>

          <button
            onClick={() => setGeneratedTicket(null)}
            className="px-4 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-300 text-xs font-semibold text-slate-700"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Grid: Form + Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Booking Form */}
        <div className="lg:col-span-1 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <PlusCircle className="w-4 h-4 text-cyan-600" />
            <h3 className="font-bold text-slate-900 text-sm">Generate OPD Token</h3>
          </div>

          <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
            <div>
              <label className="block text-slate-700 font-semibold mb-1">Patient Name</label>
              <input
                type="text"
                value={form.patient_name}
                onChange={(e) => setForm({ ...form, patient_name: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-slate-900 focus:bg-white font-mono"
                required
              />
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">Department (विभाग)</label>
              <select
                value={form.department}
                onChange={(e) => setForm({ ...form, department: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-slate-900 focus:bg-white font-mono"
              >
                {departments.map((d, i) => (
                  <option key={i} value={d}>{d}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">Priority / Triage</label>
              <select
                value={form.triage_level}
                onChange={(e) => setForm({ ...form, triage_level: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-slate-900 focus:bg-white font-mono"
              >
                <option value="ROUTINE">Routine Consultation (नियमित तपासणी)</option>
                <option value="URGENT">Urgent Care (तातडीचे)</option>
                <option value="CRITICAL">Critical Emergency (अतिदक्षता)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1">Chief Complaint</label>
              <input
                type="text"
                value={form.chief_complaint}
                onChange={(e) => setForm({ ...form, chief_complaint: e.target.value })}
                placeholder="e.g. Mild chest tightness, fever"
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-slate-900 focus:bg-white"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold transition shadow-md shadow-cyan-600/20"
            >
              {submitting ? 'Generating Token...' : 'Get Instant OPD Ticket'}
            </button>
          </form>
        </div>

        {/* Live Queue Table */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 text-sm">Live Hospital OPD Desk Queue</h3>
            <span className="text-[11px] font-mono text-emerald-700 font-semibold flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Live Desk Active
            </span>
          </div>

          {loading ? (
            <div className="py-12 text-center text-xs text-slate-500 font-mono">Loading queue...</div>
          ) : tickets.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 font-mono">
              No active OPD tickets right now. Book a new ticket using the form.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-sans">
                <thead>
                  <tr className="text-slate-500 uppercase font-mono text-[10px] border-b border-slate-200">
                    <th className="py-2.5 px-3">Token #</th>
                    <th className="py-2.5 px-3">Patient</th>
                    <th className="py-2.5 px-3">Department</th>
                    <th className="py-2.5 px-3">Triage</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {tickets.map((t) => (
                    <tr key={t.id} className="hover:bg-slate-50 transition">
                      <td className="py-3 px-3 font-bold text-cyan-800">#{t.token_number}</td>
                      <td className="py-3 px-3 font-sans font-semibold text-slate-900">{t.patient_name}</td>
                      <td className="py-3 px-3 text-slate-700">{t.department}</td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                          t.triage_level === 'CRITICAL' 
                            ? 'bg-rose-100 text-rose-800' 
                            : (t.triage_level === 'URGENT' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700')
                        }`}>
                          {t.triage_level}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10px] font-semibold">
                          {t.status}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-400 text-[11px]">
                        {t.created_at.substring(11, 16)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
