import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

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
              {/* Public Routes */}
              <Route path="/" element={<LandingPage onOpenSOS={() => setSosOpen(true)} />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />

              {/* Protected Clinical Routes (Accessible after Sign-In) */}
              <Route path="/hospitals" element={<ProtectedRoute><HospitalsPage /></ProtectedRoute>} />
              <Route path="/vitals" element={<ProtectedRoute><VitalsPage /></ProtectedRoute>} />
              <Route path="/meds" element={<ProtectedRoute><MedsPage /></ProtectedRoute>} />
              <Route path="/chat" element={<ProtectedRoute><ChatbotPage /></ProtectedRoute>} />
              <Route path="/opd" element={<ProtectedRoute><OPDPage /></ProtectedRoute>} />
              <Route path="/diet" element={<ProtectedRoute><DietPage /></ProtectedRoute>} />
              <Route path="/predict/diabetes" element={<ProtectedRoute><DiabetesPredictPage /></ProtectedRoute>} />
              <Route path="/predict/heart" element={<ProtectedRoute><HeartPredictPage /></ProtectedRoute>} />
              <Route path="/result/:id" element={<ProtectedRoute><ResultPage /></ProtectedRoute>} />
              <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
              <Route path="/history" element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
              <Route path="/models" element={<ProtectedRoute><ModelsPage /></ProtectedRoute>} />
              
              {/* Fallback */}
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
