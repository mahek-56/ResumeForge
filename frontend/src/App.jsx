import React, { useState } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';
import AnalyticsPage from './pages/AnalyticsPage';
import ModelInsightsPage from './pages/ModelInsightsPage';
import HowItWorksPage from './pages/HowItWorksPage';
import { Sparkles, Heart, GitBranch, ExternalLink } from 'lucide-react';

export default function App() {
  const [activePage, setActivePage] = useState('home');
  const [passedResumeText, setPassedResumeText] = useState('');

  const handleDirectAnalyzeText = (text) => {
    setPassedResumeText(text);
    setActivePage('analyze');
  };

  return (
    <div className="min-h-screen flex flex-col bg-navy-950 text-slate-100 font-sans selection:bg-blue-600/30 selection:text-blue-200">
      {/* Navbar */}
      <Navbar activePage={activePage} setActivePage={setActivePage} />

      {/* Main Page Body */}
      <main className="flex-1">
        {activePage === 'home' && (
          <HomePage
            setActivePage={setActivePage}
            onDirectAnalyzeText={handleDirectAnalyzeText}
          />
        )}
        {activePage === 'analyze' && (
          <AnalyzePage initialText={passedResumeText} />
        )}
        {activePage === 'analytics' && <AnalyticsPage />}
        {activePage === 'insights' && <ModelInsightsPage />}
        {activePage === 'pipeline' && (
          <HowItWorksPage setActivePage={setActivePage} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-navy-950/90 py-8 px-4 sm:px-6 lg:px-8 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span className="font-extrabold text-white tracking-tight">RESUMEFORGE AI</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              SAMATRIX 2026
            </span>
          </div>

          <div className="flex items-center space-x-6 text-slate-400 font-medium">
            <button onClick={() => setActivePage('home')} className="hover:text-slate-200 transition-colors">Home</button>
            <button onClick={() => setActivePage('analyze')} className="hover:text-slate-200 transition-colors">Analyze</button>
            <button onClick={() => setActivePage('analytics')} className="hover:text-slate-200 transition-colors">Analytics</button>
            <button onClick={() => setActivePage('insights')} className="hover:text-slate-200 transition-colors">Insights</button>
            <button onClick={() => setActivePage('pipeline')} className="hover:text-slate-200 transition-colors">How It Works</button>
          </div>

          <div className="font-mono text-[11px] text-slate-500">
            End-to-End NLP & ML Application
          </div>
        </div>
      </footer>
    </div>
  );
}
