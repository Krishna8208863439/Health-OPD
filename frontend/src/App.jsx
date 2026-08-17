import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import SOSModal from './components/SOSModal';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import HospitalsPage from './pages/HospitalsPage';
import VitalsPage from './pages/VitalsPage';
import MedsPage from './pages/MedsPage';
import ChatbotPage from './pages/ChatbotPage';
import OPDPage from './pages/OPDPage';
import DietPage from './pages/DietPage';
import DiabetesPredictPage from './pages/DiabetesPredictPage';
import HeartPredictPage from './pages/HeartPredictPage';
import ResultPage from './pages/ResultPage';
import DashboardPage from './pages/DashboardPage';
import HistoryPage from './pages/HistoryPage';
import ModelsPage from './pages/ModelsPage';

export default function App() {
  const [sosOpen, setSosOpen] = useState(false);

  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-cyan-500 selection:text-white font-sans">
          <Navbar onOpenSOS={() => setSosOpen(true)} />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<LandingPage onOpenSOS={() => setSosOpen(true)} />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/hospitals" element={<HospitalsPage />} />
              <Route path="/vitals" element={<VitalsPage />} />
              <Route path="/meds" element={<MedsPage />} />
              <Route path="/chat" element={<ChatbotPage />} />
              <Route path="/opd" element={<OPDPage />} />
              <Route path="/diet" element={<DietPage />} />
              <Route path="/predict/diabetes" element={<DiabetesPredictPage />} />
              <Route path="/predict/heart" element={<HeartPredictPage />} />
              <Route path="/result/:id" element={<ResultPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/history" element={<HistoryPage />} />
              <Route path="/models" element={<ModelsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
          
          {/* Global Emergency SOS Modal */}
          <SOSModal isOpen={sosOpen} onClose={() => setSosOpen(false)} />
        </div>
      </Router>
    </AuthProvider>
  );
}
