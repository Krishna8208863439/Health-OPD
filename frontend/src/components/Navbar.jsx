import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Activity, Heart, Droplets, LayoutDashboard, History, Award, 
  Building2, Pill, Bot, Ticket, Apple, Menu, X, ShieldAlert, LogOut, LogIn, UserPlus, User
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ onOpenSOS }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Protected clinical navigation links visible AFTER sign in
  const authenticatedLinks = [
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

  // Public links visible before sign in
  const publicLinks = [
    { name: 'Home', path: '/' },
  ];

  const visibleLinks = user ? authenticatedLinks : publicLinks;

  const isActive = (path) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname.startsWith(path);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm w-full">
      <div className="w-full max-w-[1700px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-3">
        
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
            <div className="text-[10px] text-slate-500 font-mono hidden 2xl:block">
              Unified Clinical Healthcare Platform
            </div>
          </div>
        </Link>

        {/* Desktop Nav Items - Visible depending on Auth status */}
        <nav className="hidden xl:flex items-center gap-1">
          {visibleLinks.map((link) => {
            const active = isActive(link.path);
            const Icon = link.icon;
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`px-2.5 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5 shrink-0 ${
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

        {/* Right Action: Auth / User Profile + SOS Button & Mobile Menu */}
        <div className="flex items-center gap-2.5 shrink-0">
          
          {/* Emergency SOS Button */}
          <button
            onClick={onOpenSOS}
            className="px-3 py-1.5 rounded-full bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold font-mono flex items-center gap-1 shadow-md shadow-rose-600/20 transition hover:scale-105 shrink-0"
          >
            <ShieldAlert className="w-3.5 h-3.5 animate-pulse" />
            <span>SOS</span>
          </button>

          {/* User Auth Section */}
          {user ? (
            <div className="flex items-center gap-2 pl-1 border-l border-slate-200">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                <div className="w-6 h-6 rounded-full bg-cyan-600 text-white font-bold flex items-center justify-center text-[11px]">
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                </div>
                <span className="font-semibold text-slate-800 max-w-[130px] truncate hidden sm:inline">
                  {user.full_name}
                </span>
              </div>

              <button
                onClick={handleLogout}
                className="px-3 py-1.5 rounded-xl text-slate-600 hover:text-rose-600 hover:bg-rose-50 border border-slate-200 hover:border-rose-200 font-semibold text-xs transition flex items-center gap-1"
                title="Sign Out"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden md:inline">Log Out</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2 pl-1 border-l border-slate-200">
              <Link
                to="/login"
                className="px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-xs transition flex items-center gap-1.5"
              >
                <LogIn className="w-3.5 h-3.5 text-cyan-600" />
                <span>Sign In</span>
              </Link>
              <Link
                to="/register"
                className="px-3.5 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-md shadow-cyan-600/20"
              >
                <UserPlus className="w-3.5 h-3.5" />
                <span>Create Account</span>
              </Link>
            </div>
          )}

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="xl:hidden p-2 rounded-xl bg-slate-100 border border-slate-200 text-slate-600 hover:text-slate-900 transition"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="xl:hidden bg-white border-b border-slate-200 px-4 pt-3 pb-5 space-y-2 shadow-xl max-h-[85vh] overflow-y-auto">
          
          {/* User Status in Mobile Menu */}
          {user ? (
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-cyan-600 text-white font-bold flex items-center justify-center text-sm">
                  {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                </div>
                <div>
                  <div className="font-bold text-xs text-slate-900">{user.full_name}</div>
                  <div className="text-[10px] text-slate-500 font-mono">{user.email}</div>
                </div>
              </div>

              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleLogout();
                }}
                className="px-3 py-1.5 rounded-xl bg-rose-50 text-rose-700 hover:bg-rose-100 font-bold text-xs flex items-center gap-1 border border-rose-200"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Log Out</span>
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-2 pt-1 pb-2">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-xs flex items-center justify-center gap-1.5"
              >
                <LogIn className="w-4 h-4 text-cyan-600" />
                <span>Sign In</span>
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-xs flex items-center justify-center gap-1.5"
              >
                <UserPlus className="w-4 h-4" />
                <span>Create Account</span>
              </Link>
            </div>
          )}

          <div className="border-t border-slate-100 pt-2 space-y-1">
            {visibleLinks.map((link) => {
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
        </div>
      )}
    </header>
  );
}
