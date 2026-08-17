import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, registerUser, forgotPassword, resetPassword, getCurrentUser } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('healthcare_user');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return null;
      }
    }
    return null; // Logged out by default until sign in
  });

  const [token, setToken] = useState(() => localStorage.getItem('healthcare_token') || null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      localStorage.setItem('healthcare_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('healthcare_user');
    }
  }, [user]);

  useEffect(() => {
    if (token) {
      localStorage.setItem('healthcare_token', token);
    } else {
      localStorage.removeItem('healthcare_token');
    }
  }, [token]);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const res = await loginUser({ email, password });
      setUser(res.user);
      setToken(res.token);
      return { success: true, user: res.user };
    } catch (err) {
      const msg = err.response?.data?.message || err.message || "Failed to log in.";
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const res = await registerUser(userData);
      setUser(res.user);
      setToken(res.token);
      return { success: true, user: res.user };
    } catch (err) {
      const msg = err.response?.data?.message || err.message || "Failed to register.";
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('healthcare_user');
    localStorage.removeItem('healthcare_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
