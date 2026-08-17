import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Activity, Heart, Droplets, LayoutDashboard, History, Award, 
  Building2, Pill, Bot, Ticket, Apple, Menu, X, ShieldAlert
} from 'lucide-react';

export default function Navbar({ onOpenSOS }) {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Hospitals', path: '/hospitals', icon: Building2 },
    { name: 'Vitals & Score', path: '/vitals', icon: Activity },
    { name: 'Medications', path: '/meds', icon: Pill },
    { name: 'AI Assistant', path: '/chat', icon: Bot },
    { name: 'OPD Queue', path: '/opd', icon: Ticket },
    { name: 'Diet Plans', path: '/diet', icon: Apple },
    { name: 'Diabetes AI', path: '/predict/diabetes', icon: Droplets },
    { name: 'Heart AI', path: '/predict/heart', icon: Heart },
    { name: 'Analytics', path: '/dashboard', icon: LayoutDashboard },
    { name: 'History', path: '/history', icon: History },
  ];

  const isActive = (path) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm w-full">
      <div className="w-full max-w-[1700px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-3 group shrink-0">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-md shadow-cyan-500/20 group-hover:scale-105 transition">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-base tracking-tight text-slate-900 flex items-center gap-1.5">
              <span>HealthCare<span className="text-cyan-600">+</span></span>
              <span className="text-slate-300 font-light">|</span>
              <span className="text-xs text-slate-700 font-medium font-mono">Predict AI</span>
            </div>
            <div className="text-[10px] text-slate-500 font-mono hidden xl:block">
              Unified Clinical Healthcare Platform
            </div>
          </div>
        </Link>

        {/* Desktop Nav Items */}
        <nav className="hidden xl:flex items-center gap-1">
          {navLinks.map((link) => {
            const active = isActive(link.path);
            const Icon = link.icon;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 shrink-0 ${
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

        {/* Right Action: SOS Button & Mobile Menu */}
        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={onOpenSOS}
            className="px-3.5 py-1.5 rounded-full bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold font-mono flex items-center gap-1.5 shadow-md shadow-rose-600/20 transition hover:scale-105"
          >
            <ShieldAlert className="w-3.5 h-3.5 animate-pulse" />
            <span>Emergency SOS</span>
          </button>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="xl:hidden p-2 rounded-xl bg-slate-100 border border-slate-200 text-slate-600 hover:text-slate-900 transition"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile / Tablet Drawer Menu */}
      {mobileMenuOpen && (
        <div className="xl:hidden bg-white border-b border-slate-200 px-4 pt-3 pb-5 space-y-1 shadow-xl max-h-[85vh] overflow-y-auto">
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
                    ? 'bg-cyan-50 text-cyan-700 font-semibold border border-cyan-200'
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
