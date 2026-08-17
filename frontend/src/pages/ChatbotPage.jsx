import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Sparkles, AlertTriangle, ShieldCheck } from 'lucide-react';
import { sendChatMessage } from '../services/api';

export default function ChatbotPage() {
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: "Hello! I am your **HealthCare+ AI Assistant (आरोग्य सहाय्यक)**. Ask me any medical symptom question, disease information, medicine guidelines, or lifestyle recommendation in English or मराठी.",
      isEmergency: false
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const quickPrompts = [
    "What are early symptoms of Type 2 Diabetes?",
    "How to manage high blood pressure at home?",
    "What to do for severe chest pain?",
    "मधुमेह नियंत्रण आहार काय असावा?",
    "Nearest emergency hospital in Kolhapur"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (textToSend) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const userMsg = { sender: 'user', text: query };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendChatMessage(query);
      setMessages(prev => [
        ...prev,
        {
          sender: 'ai',
          text: res.reply,
          isEmergency: res.is_emergency
        }
      ]);
    } catch {
      setMessages(prev => [
        ...prev,
        {
          sender: 'ai',
          text: "I am having trouble connecting to the healthcare engine right now. Please try again or visit our Hospital Directory if urgent.",
          isEmergency: false
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-6 animate-fade-in">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2 text-cyan-700 text-xs font-mono font-semibold">
            <Bot className="w-4 h-4 text-cyan-600" />
            <span>CLINICAL TRIAGE & AI HEALTH CONSULTANT</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            AI Health Assistant / एआय आरोग्य सहाय्यक
          </h1>
          <p className="text-slate-600 text-xs sm:text-sm">
            Instant 24/7 symptom screening, medication precautions, and medical guidelines.
          </p>
        </div>
      </div>

      {/* Chat Container */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm flex flex-col h-[600px] overflow-hidden">
        
        {/* Messages Body */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.sender === 'ai' && (
                <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                  m.isEmergency ? 'bg-rose-100 text-rose-600' : 'bg-cyan-100 text-cyan-700'
                }`}>
                  {m.isEmergency ? <AlertTriangle className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>
              )}

              <div
                className={`max-w-lg p-4 rounded-2xl text-xs leading-relaxed ${
                  m.sender === 'user'
                    ? 'bg-cyan-600 text-white rounded-tr-none shadow-sm'
                    : m.isEmergency
                      ? 'bg-rose-50 border border-rose-200 text-rose-950 rounded-tl-none'
                      : 'bg-slate-100 text-slate-800 rounded-tl-none border border-slate-200'
                }`}
              >
                <div className="whitespace-pre-line font-sans">{m.text}</div>
              </div>

              {m.sender === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-slate-900 text-white flex items-center justify-center shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-xl bg-cyan-100 text-cyan-700 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-100 border border-slate-200 text-xs text-slate-500 font-mono flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-cyan-600 animate-pulse"></div>
                <span>Analyzing medical knowledge base...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestion Pills */}
        <div className="px-5 py-2.5 bg-slate-50 border-t border-slate-100 flex items-center gap-2 overflow-x-auto">
          <span className="text-[11px] text-slate-400 font-mono shrink-0 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-cyan-600" /> Suggestions:
          </span>
          {quickPrompts.map((q, i) => (
            <button
              key={i}
              onClick={() => handleSend(q)}
              className="px-2.5 py-1 rounded-full bg-white hover:bg-cyan-50 hover:text-cyan-700 border border-slate-200 text-[11px] text-slate-600 shrink-0 transition"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="p-4 bg-white border-t border-slate-200 flex items-center gap-3"
        >
          <input
            type="text"
            placeholder="Type your health inquiry (उदा. मला छातीत दुखत आहे किंवा रक्तदाब नियंत्रण)..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-xs text-slate-900 focus:outline-none focus:border-cyan-600 focus:bg-white"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-5 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-1.5 transition shadow-md shadow-cyan-600/20"
          >
            <span>Send</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>

      </div>

    </div>
  );
}
