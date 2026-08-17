import React from 'react';
import { Activity } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 text-slate-600 font-sans text-xs w-full">
      <div className="w-full max-w-[1700px] mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center">
            <Activity className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-bold text-slate-900 text-sm">
            HealthPredict <span className="text-cyan-600">AI</span>
          </span>
        </div>
        
        <div className="text-center sm:text-right text-[11px] text-slate-400">
          © {new Date().getFullYear()} HealthPredict AI. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
