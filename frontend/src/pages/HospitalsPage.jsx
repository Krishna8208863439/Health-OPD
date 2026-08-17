import React, { useState, useEffect } from 'react';
import { Building2, Search, Phone, MapPin, Bed, Activity, ExternalLink, Star } from 'lucide-react';
import { getHospitals } from '../services/api';

export default function HospitalsPage() {
  const [hospitals, setHospitals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cityFilter, setCityFilter] = useState('');
  const [search, setSearch] = useState('');

  const cities = ['Kolhapur', 'Pune', 'Mumbai', 'Delhi', 'Bengaluru', 'Hyderabad', 'Chennai'];

  const fetchHospitals = async () => {
    try {
      setLoading(true);
      const data = await getHospitals({ city: cityFilter, search });
      setHospitals(data.hospitals || []);
    } catch (err) {
      console.error("Failed to load hospitals:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHospitals();
  }, [cityFilter]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchHospitals();
  };

  return (
    <div className="max-w-6xl mx-auto py-10 px-4 space-y-8 animate-fade-in">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="flex items-center gap-2 text-cyan-700 text-xs font-mono font-semibold">
            <Building2 className="w-4 h-4 text-cyan-600" />
            <span>HOSPITAL DIRECTORY & EMERGENCY NETWORK</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Find Nearby Hospitals / जवळचे रुग्णालय शोधा
          </h1>
          <p className="text-slate-600 text-xs sm:text-sm">
            Live bed availability, 24/7 ICU status, emergency phone numbers, and location routes.
          </p>
        </div>
      </div>

      {/* Filter and Search */}
      <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Search */}
        <form onSubmit={handleSearch} className="relative w-full md:w-80">
          <input
            type="text"
            placeholder="Search by hospital name or specialty..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
        </form>

        {/* City Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          <button
            onClick={() => setCityFilter('')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
              cityFilter === ''
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Cities
          </button>
          {cities.map((city) => (
            <button
              key={city}
              onClick={() => setCityFilter(city)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition ${
                cityFilter === city
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {city}
            </button>
          ))}
        </div>

      </div>

      {/* Hospital Cards Grid */}
      {loading ? (
        <div className="py-16 text-center space-y-3">
          <div className="w-8 h-8 border-3 border-cyan-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-xs text-slate-500 font-mono">Loading hospital directory...</p>
        </div>
      ) : hospitals.length === 0 ? (
        <div className="p-12 text-center bg-white rounded-2xl border border-slate-200 space-y-2">
          <Building2 className="w-8 h-8 text-slate-400 mx-auto" />
          <h3 className="text-sm font-bold text-slate-800">No Hospitals Found</h3>
          <p className="text-xs text-slate-500">Try changing your search query or city filter.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {hospitals.map((h) => (
            <div
              key={h.id}
              className="p-5 rounded-2xl bg-white border border-slate-200/90 hover:border-cyan-400 hover:shadow-md transition space-y-4 flex flex-col justify-between"
            >
              <div className="space-y-2.5">
                {/* Type & 24/7 Status */}
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                    h.type === 'Government' 
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  }`}>
                    {h.type}
                  </span>

                  <div className="flex items-center gap-1.5">
                    {h.is_24hrs && (
                      <span className="px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 text-[9px] font-bold border border-rose-200 flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-600 animate-pulse"></span>
                        24/7 Emergency
                      </span>
                    )}
                    <span className="flex items-center text-amber-500 font-bold text-xs">
                      <Star className="w-3.5 h-3.5 fill-amber-400" /> {h.rating}
                    </span>
                  </div>
                </div>

                {/* Name & City */}
                <div>
                  <h3 className="font-bold text-slate-900 text-base leading-snug">{h.name}</h3>
                  <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                    <MapPin className="w-3 h-3 text-cyan-600 shrink-0" />
                    <span>{h.city} — {h.address}</span>
                  </p>
                </div>

                {/* Specialties */}
                <div className="flex flex-wrap gap-1 pt-1">
                  {h.specialty.map((spec, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-mono">
                      {spec}
                    </span>
                  ))}
                </div>

                {/* Beds & ICU Telemetry */}
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100">
                  <div className="p-2 rounded-xl bg-slate-50 border border-slate-100 text-center">
                    <div className="text-[10px] text-slate-500 font-mono">Total Beds</div>
                    <div className="text-sm font-bold text-slate-900 font-mono flex items-center justify-center gap-1">
                      <Bed className="w-3.5 h-3.5 text-cyan-600" /> {h.beds}
                    </div>
                  </div>

                  <div className="p-2 rounded-xl bg-slate-50 border border-slate-100 text-center">
                    <div className="text-[10px] text-slate-500 font-mono">Available ICU</div>
                    <div className="text-sm font-bold text-emerald-700 font-mono flex items-center justify-center gap-1">
                      <Activity className="w-3.5 h-3.5 text-emerald-600" /> {h.icu_available}
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 pt-2">
                <a
                  href={`tel:${h.phone}`}
                  className="flex-1 py-2.5 rounded-xl bg-cyan-50 hover:bg-cyan-600 hover:text-white text-cyan-800 font-semibold text-xs transition flex items-center justify-center gap-1.5 border border-cyan-200"
                >
                  <Phone className="w-3.5 h-3.5" />
                  <span>Call Hospital</span>
                </a>

                <a
                  href={`https://maps.google.com/?q=${encodeURIComponent(h.name + ' ' + h.address)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 transition"
                  title="Open in Maps"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
}
