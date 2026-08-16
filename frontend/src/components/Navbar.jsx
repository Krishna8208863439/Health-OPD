import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, Heart, Droplets, LayoutDashboard, History, Award, Menu, X, ShieldCheck } from 'lucide-react';
import { checkHealth } from '../services/api';

export default function Navbar() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    async function verifyBackend() {
      try {
        const res = await checkHealth();
        setBackendOnline(res.status === 'ok');
      } catch {
        setBackendOnline(false);
      }
    }
    verifyBackend();
    const interval = setInterval(verifyBackend, 15000);
    return () => clearInterval(interval);
  }, []);

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Diabetes Risk', path: '/predict/diabetes', icon: Droplets },
    { name: 'Heart Disease Risk', path: '/predict/heart', icon: Heart },
    { name: 'Patient History', path: '/history', icon: History },
    { name: 'Model Metrics', path: '/models', icon: Award },
  ];

  const isActive = (path) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-50 bg-slate-950/90 backdrop-blur-xl border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-lg tracking-tight text-white flex items-center gap-1.5">
              <span>HealthPredict</span>
              <span className="text-cyan-400">AI</span>
            </div>
            <div className="text-[10px] text-slate-400 font-mono flex items-center gap-1">
              <span className="text-cyan-400">ML Clinical Support</span>
              <span className="text-slate-600">•</span>
              <span className="px-1.5 py-0.2 rounded bg-slate-800 text-[9px] text-slate-300">DEMO MODE</span>
            </div>
          </div>
        </Link>

        {/* Desktop Nav Items */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const active = isActive(link.path);
            const Icon = link.icon;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition flex items-center gap-2 ${
                  active
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/25 shadow-sm shadow-cyan-500/10'
                    : 'text-slate-300 hover:text-white hover:bg-slate-900/60'
                }`}
              >
                {Icon && <Icon className={`w-3.5 h-3.5 ${active ? 'text-cyan-400' : 'text-slate-400'}`} />}
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Status Indicator & Mobile Menu Button */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs font-mono">
            <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`}></span>
            <span className={backendOnline ? 'text-emerald-400' : 'text-rose-400'}>
              {backendOnline ? 'ML Backend Active' : 'Offline'}
            </span>
          </div>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-slate-950 border-b border-slate-800 px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const active = isActive(link.path);
            const Icon = link.icon;
            return (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition ${
                  active
                    ? 'bg-cyan-500/15 text-cyan-400 font-semibold'
                    : 'text-slate-300 hover:bg-slate-900'
                }`}
              >
                {Icon && <Icon className="w-4 h-4" />}
                <span>{link.name}</span>
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
}
