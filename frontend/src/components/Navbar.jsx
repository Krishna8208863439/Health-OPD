import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Activity, Heart, Droplets, LayoutDashboard, History, Award, 
  Building2, Pill, Bot, Ticket, Apple, AlertTriangle, Menu, X, ShieldAlert
} from 'lucide-react';

export default function Navbar({ onOpenSOS }) {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const mainLinks = [
    { name: 'Home', path: '/' },
    { name: 'Hospitals', path: '/hospitals', icon: Building2 },
    { name: 'Vitals & Score', path: '/vitals', icon: Activity },
    { name: 'Meds', path: '/meds', icon: Pill },
    { name: 'AI Chat', path: '/chat', icon: Bot },
    { name: 'OPD Queue', path: '/opd', icon: Ticket },
    { name: 'Diet', path: '/diet', icon: Apple },
    { name: 'Diabetes ML', path: '/predict/diabetes', icon: Droplets },
    { name: 'Heart ML', path: '/predict/heart', icon: Heart },
    { name: 'Analytics', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Records', path: '/history', icon: History },
  ];

  const isActive = (path) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-2">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2.5 group shrink-0">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-md shadow-cyan-500/20 group-hover:scale-105 transition">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-base tracking-tight text-slate-900 flex items-center gap-1">
              <span>HealthCare<span className="text-cyan-600">+</span></span>
              <span className="text-slate-400 font-normal">|</span>
              <span className="text-xs text-slate-600 font-mono">Predict AI</span>
            </div>
            <div className="text-[9px] text-slate-500 font-mono hidden sm:block">
              Unified Clinical Platform
            </div>
          </div>
        </Link>

        {/* Desktop Nav Items */}
        <nav className="hidden lg:flex items-center gap-1 overflow-x-auto">
          {mainLinks.map((link) => {
            const active = isActive(link.path);
            const Icon = link.icon;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1 shrink-0 ${
                  active
                    ? 'bg-cyan-50 text-cyan-700 border border-cyan-200 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
                }`}
              >
                {Icon && <Icon className={`w-3.5 h-3.5 ${active ? 'text-cyan-600' : 'text-slate-400'}`} />}
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* SOS Button & Mobile Menu Trigger */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={onOpenSOS}
            className="px-3 py-1.5 rounded-full bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold font-mono flex items-center gap-1.5 shadow-md shadow-rose-600/30 transition animate-pulse"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>SOS मदत</span>
          </button>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 rounded-lg bg-slate-100 border border-slate-200 text-slate-600 hover:text-slate-900"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-b border-slate-200 px-4 pt-2 pb-4 space-y-1 shadow-lg max-h-[80vh] overflow-y-auto">
          {mainLinks.map((link) => {
            const active = isActive(link.path);
            const Icon = link.icon;
            return (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition ${
                  active
                    ? 'bg-cyan-50 text-cyan-700 font-semibold'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                {Icon && <Icon className="w-4 h-4 text-cyan-600" />}
                <span>{link.name}</span>
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
}
