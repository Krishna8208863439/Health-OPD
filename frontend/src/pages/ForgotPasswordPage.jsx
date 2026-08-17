import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Mail, Lock, KeyRound, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';
import { forgotPassword, resetPassword } from '../services/api';

export default function ForgotPasswordPage() {
  const [step, setStep] = useState(1); // 1: Email, 2: Reset Password, 3: Success
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setError(null);
    if (!email) {
      setError("Please enter your registered email address.");
      return;
    }

    try {
      setLoading(true);
      await forgotPassword(email);
      setStep(2);
    } catch (err) {
      const msg = err.response?.data?.message || err.message || "Failed to process request.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleResetSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (newPassword.length < 6) {
      setError("New password must be at least 6 characters in length.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);
      await resetPassword({ email, new_password: newPassword });
      setStep(3);
    } catch (err) {
      const msg = err.response?.data?.message || err.message || "Failed to reset password.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-[1700px] mx-auto px-4 sm:px-6 lg:px-10 py-12 flex items-center justify-center animate-fade-in">
      <div className="max-w-md w-full bg-white rounded-3xl border border-slate-200 shadow-xl p-8 sm:p-10 space-y-6">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 to-rose-600 flex items-center justify-center text-white mx-auto shadow-md shadow-amber-500/20">
            <KeyRound className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Password Recovery</h1>
          <p className="text-xs text-slate-500 font-mono">
            {step === 1 && "Enter your email to receive recovery instructions"}
            {step === 2 && "Enter your new account password"}
            {step === 3 && "Password updated successfully"}
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Step 1: Request Email */}
        {step === 1 && (
          <form onSubmit={handleRequestReset} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-700 font-semibold mb-1.5">Registered Email Address</label>
              <div className="relative">
                <input
                  type="email"
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-3 text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white"
                  required
                />
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-2xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/25 transition disabled:opacity-50"
            >
              <span>{loading ? 'Verifying Account...' : 'Continue to Reset Password'}</span>
            </button>
          </form>
        )}

        {/* Step 2: New Password Form */}
        {step === 2 && (
          <form onSubmit={handleResetSubmit} className="space-y-4 text-xs">
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px]">
              Verification verified for <b>{email}</b>. Please specify your new password below.
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1.5">New Password</label>
              <div className="relative">
                <input
                  type="password"
                  placeholder="Min 6 characters"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-3 text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white font-mono"
                  required
                />
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <div>
              <label className="block text-slate-700 font-semibold mb-1.5">Confirm New Password</label>
              <div className="relative">
                <input
                  type="password"
                  placeholder="Repeat new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-3 text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white font-mono"
                  required
                />
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-2xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/25 transition disabled:opacity-50"
            >
              <span>{loading ? 'Updating Password...' : 'Save New Password'}</span>
            </button>
          </form>
        )}

        {/* Step 3: Success */}
        {step === 3 && (
          <div className="text-center space-y-4 py-3">
            <div className="w-12 h-12 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle className="w-7 h-7" />
            </div>
            <h3 className="font-bold text-slate-900 text-base">Password Reset Completed!</h3>
            <p className="text-xs text-slate-600">
              Your credentials have been securely updated. You may now log in to the healthcare portal.
            </p>

            <Link
              to="/login"
              className="w-full py-3 rounded-2xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs block text-center shadow-md transition"
            >
              Sign In Now
            </Link>
          </div>
        )}

        {/* Back to Login Link */}
        <div className="text-center text-xs text-slate-600 border-t border-slate-100 pt-5">
          <Link to="/login" className="font-semibold text-cyan-600 hover:text-cyan-700 flex items-center justify-center gap-1.5">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Sign In</span>
          </Link>
        </div>

      </div>
    </div>
  );
}
