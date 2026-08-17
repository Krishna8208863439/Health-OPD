import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Activity, User, Mail, Phone, Lock, UserPlus, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const { register, loading } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: ''
  });

  const [error, setError] = useState(null);
  const [agreed, setAgreed] = useState(true);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!form.full_name || !form.email || !form.password) {
      setError("Please fill out all required fields.");
      return;
    }

    if (form.password.length < 6) {
      setError("Password must be at least 6 characters in length.");
      return;
    }

    if (form.password !== form.confirm_password) {
      setError("Passwords do not match. Please verify.");
      return;
    }

    if (!agreed) {
      setError("Please accept the Healthcare Terms of Service.");
      return;
    }

    const res = await register({
      full_name: form.full_name,
      email: form.email,
      phone: form.phone,
      password: form.password
    });

    if (res.success) {
      navigate('/');
    } else {
      setError(res.error);
    }
  };

  return (
    <div className="w-full max-w-[1700px] mx-auto px-4 sm:px-6 lg:px-10 py-12 flex items-center justify-center animate-fade-in">
      <div className="max-w-lg w-full bg-white rounded-3xl border border-slate-200 shadow-xl p-8 sm:p-10 space-y-6">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center text-white mx-auto shadow-md shadow-cyan-600/20">
            <UserPlus className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Create Patient Account</h1>
          <p className="text-xs text-slate-500 font-mono">Register for full health tracking, ML predictions & OPD booking</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-700 font-semibold mb-1.5">Full Name (रुग्णाचे नाव) *</label>
            <div className="relative">
              <input
                type="text"
                name="full_name"
                placeholder="e.g. John Doe / Krishna Devadkar"
                value={form.full_name}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-3 text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white"
                required
              />
              <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <div>
              <label className="block text-slate-700 font-semibold mb-1.5">Email Address *</label>
              <div className="relative">
                <input
                  type="email"
                  name="email"
                  placeholder="name@example.com"
                  value={form.email}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-3 text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white"
                  required
                />
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1.5">Phone Number</label>
              <div className="relative">
                <input
                  type="tel"
                  name="phone"
                  placeholder="+91 98765 43210"
                  value={form.phone}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-3 text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white font-mono"
                />
                <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <div>
              <label className="block text-slate-700 font-semibold mb-1.5">Password *</label>
              <div className="relative">
                <input
                  type="password"
                  name="password"
                  placeholder="Min 6 chars"
                  value={form.password}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-3 text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white font-mono"
                  required
                />
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1.5">Confirm Password *</label>
              <div className="relative">
                <input
                  type="password"
                  name="confirm_password"
                  placeholder="Repeat password"
                  value={form.confirm_password}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-3 text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white font-mono"
                  required
                />
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 pt-1">
            <input
              type="checkbox"
              id="terms"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="rounded text-cyan-600 focus:ring-cyan-500 w-4 h-4"
            />
            <label htmlFor="terms" className="text-slate-600 text-xs select-none">
              I agree to the Healthcare Privacy Policy and Data Security Guidelines.
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-2xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/25 transition disabled:opacity-50"
          >
            <UserPlus className="w-4 h-4" />
            <span>{loading ? 'Creating Account...' : 'Complete Registration'}</span>
          </button>
        </form>

        {/* Footer Links */}
        <div className="text-center text-xs text-slate-600 border-t border-slate-100 pt-5">
          Already registered?{' '}
          <Link to="/login" className="font-bold text-cyan-600 hover:text-cyan-700 underline">
            Sign In Here
          </Link>
        </div>

      </div>
    </div>
  );
}
