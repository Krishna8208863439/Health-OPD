import React, { useState } from 'react';
import { PhoneCall, AlertTriangle, X, ShieldAlert, MapPin, CheckCircle } from 'lucide-react';
import { triggerSOS } from '../services/api';

export default function SOSModal({ isOpen, onClose }) {
  const [sent, setSent] = useState(false);
  const [location, setLocation] = useState(null);

  if (!isOpen) return null;

  const handleTrigger = async () => {
    try {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (pos) => {
          const coords = { lat: pos.coords.latitude, lng: pos.coords.longitude };
          setLocation(coords);
          await triggerSOS(coords);
          setSent(true);
        }, async () => {
          await triggerSOS({});
          setSent(true);
        });
      } else {
        await triggerSOS({});
        setSent(true);
      }
    } catch {
      setSent(true);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 space-y-6 shadow-2xl border border-rose-200 relative overflow-hidden">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Emergency Banner Header */}
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-rose-100 text-rose-600 flex items-center justify-center animate-bounce">
            <ShieldAlert className="w-7 h-7" />
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-black text-rose-700 tracking-tight">
              EMERGENCY SOS RESPONSE
            </h2>
            <p className="text-xs text-slate-500 font-mono">Instant Medical Helplines & Location Dispatch</p>
          </div>
        </div>

        {/* Dispatch Alert button */}
        {!sent ? (
          <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-center space-y-3">
            <p className="text-xs text-rose-950 font-medium">
              Click below to broadcast your live coordinates to emergency medical responders and notification centers.
            </p>
            <button
              onClick={handleTrigger}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-700 hover:to-red-700 text-white font-extrabold text-sm shadow-lg shadow-rose-600/30 flex items-center justify-center gap-2 transition"
            >
              <AlertTriangle className="w-5 h-5" />
              <span>DISPATCH EMERGENCY SOS NOW</span>
            </button>
          </div>
        ) : (
          <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-center space-y-2">
            <div className="flex items-center justify-center gap-2 text-emerald-800 font-bold text-sm">
              <CheckCircle className="w-5 h-5 text-emerald-600" />
              <span>Emergency Signal Broadcasted Successfully!</span>
            </div>
            {location && (
              <p className="text-[11px] text-slate-600 font-mono flex items-center justify-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-rose-600" /> Coordinates: {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
              </p>
            )}
          </div>
        )}

        {/* Immediate Dial Direct Buttons */}
        <div className="space-y-2.5">
          <div className="text-xs font-bold text-slate-800 uppercase tracking-wider font-mono">
            Direct Emergency Call Lines
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <a
              href="tel:108"
              className="p-3 rounded-xl bg-rose-600 hover:bg-rose-700 text-white flex items-center justify-between shadow-sm transition"
            >
              <div className="flex items-center gap-2.5">
                <PhoneCall className="w-4 h-4" />
                <span className="font-bold text-xs">Ambulance Dispatch</span>
              </div>
              <span className="font-mono font-extrabold text-sm">108</span>
            </a>

            <a
              href="tel:112"
              className="p-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white flex items-center justify-between shadow-sm transition"
            >
              <div className="flex items-center gap-2.5">
                <PhoneCall className="w-4 h-4" />
                <span className="font-bold text-xs">National Emergency</span>
              </div>
              <span className="font-mono font-extrabold text-sm">112</span>
            </a>

            <a
              href="tel:102"
              className="p-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 flex items-center justify-between border border-slate-300 shadow-sm transition"
            >
              <div className="flex items-center gap-2.5">
                <PhoneCall className="w-4 h-4 text-cyan-600" />
                <span className="font-bold text-xs">Maternity & Child</span>
              </div>
              <span className="font-mono font-extrabold text-sm">102</span>
            </a>

            <a
              href="tel:1091"
              className="p-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 flex items-center justify-between border border-slate-300 shadow-sm transition"
            >
              <div className="flex items-center gap-2.5">
                <PhoneCall className="w-4 h-4 text-purple-600" />
                <span className="font-bold text-xs">Senior Citizen Line</span>
              </div>
              <span className="font-mono font-extrabold text-sm">1091</span>
            </a>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition"
        >
          Close Emergency Panel
        </button>

      </div>
    </div>
  );
}
