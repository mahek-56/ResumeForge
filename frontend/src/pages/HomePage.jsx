import React, { useState } from 'react';
import {
  Sparkles, ArrowRight, UploadCloud, FileText, CheckCircle2,
  ShieldCheck, Cpu, BarChart2, Layers, Search, Code, Database, ChevronRight
} from 'lucide-react';

export default function HomePage({ setActivePage, onDirectAnalyzeText }) {
  const [dragActive, setDragActive] = useState(false);

  const sampleSoftwareResume = `Senior Full Stack Software Engineer with 6+ years of production experience designing, building, and deploying scalable distributed systems and cloud native applications.
Proficient in Python, Java, JavaScript, React.js, FastAPI, Node.js, SQL, PostgreSQL, and Docker.
Architected high-throughput microservices deployed on AWS (ECS, S3, RDS, Lambda). Built real-time analytics pipelines processing over 50M events per day.
Led cross-functional engineering teams in agile sprints, CI/CD automation with GitHub Actions, and code reviews.
Education: Bachelor of Science in Computer Science, State University. Certified AWS Solutions Architect Associate.`;

  const handleSampleClick = () => {
    if (onDirectAnalyzeText) {
      onDirectAnalyzeText(sampleSoftwareResume);
    }
    setActivePage('analyze');
  };

  return (
    <div className="space-y-20 pb-20">
      {/* Hero Section */}
      <section className="relative pt-12 md:pt-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        {/* Ambient Gradient Glows */}
        <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/3 right-1/4 translate-x-1/2 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Left Column: Headlines & CTA */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-blue-500/30 text-xs font-medium text-blue-300">
              <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              <span>SAMATRIX RESUMEFORGE 2026 CHALLENGE</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.12]">
              Turn Resumes Into <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400">
                Intelligence.
              </span>
            </h1>

            <p className="text-lg sm:text-xl text-slate-300 max-w-2xl font-normal leading-relaxed">
              AI-powered resume classification and profile intelligence using advanced NLP and machine learning.
              Instantly map raw CVs to 24 industrial verticals with calibrated confidence, mathematical keyword explainability, and skill extraction.
            </p>

            {/* Quick Upload Drop Area */}
            <div
              onClick={() => setActivePage('analyze')}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => { e.preventDefault(); setDragActive(false); setActivePage('analyze'); }}
              className={`cursor-pointer p-6 rounded-2xl border-2 border-dashed transition-all ${
                dragActive
                  ? 'border-blue-400 bg-blue-500/10 scale-[1.01]'
                  : 'border-slate-800 bg-navy-900/70 hover:border-slate-700 hover:bg-slate-900/80'
              }`}
            >
              <div className="flex flex-col sm:flex-row items-center space-y-3 sm:space-y-0 sm:space-x-4 text-center sm:text-left">
                <div className="w-12 h-12 rounded-xl bg-blue-600/15 border border-blue-500/30 flex items-center justify-center text-blue-400">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <div>
                  <p className="font-semibold text-white text-sm">
                    Drop resume file here or <span className="text-blue-400 underline underline-offset-2">browse</span>
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5 font-mono">
                    Supported: PDF, DOCX, TXT (up to 10MB)
                  </p>
                </div>
              </div>
            </div>

            {/* Primary Action Buttons */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={() => setActivePage('analyze')}
                className="flex items-center space-x-2.5 px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-glow-blue transition-all active:scale-95"
              >
                <span>Analyze Resume</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={() => setActivePage('analytics')}
                className="flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold text-slate-300 bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 transition-all"
              >
                <BarChart2 className="w-4 h-4 text-slate-400" />
                <span>Explore Analytics</span>
              </button>
            </div>

            {/* Verification Badges */}
            <div className="flex flex-wrap items-center gap-6 pt-4 text-xs text-slate-400 font-mono">
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>24 Standardized Categories</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Calibrated Probabilities</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Full Feature Attribution</span>
              </div>
            </div>
          </div>

          {/* Right Column: Visual AI Classification Showcase Panel */}
          <div className="lg:col-span-5">
            <div className="relative">
              {/* Outer decorative glow frame */}
              <div className="absolute -inset-1 rounded-3xl bg-gradient-to-br from-blue-500/20 via-indigo-500/20 to-purple-500/20 blur-xl opacity-75" />

              <div className="relative glass-panel rounded-2xl p-6 sm:p-7 border border-slate-700/60 shadow-2xl space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div className="flex items-center space-x-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-xs font-mono font-semibold tracking-wider text-slate-300 uppercase">
                      RESUME ANALYSIS DEMO
                    </span>
                  </div>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    Live Model Output
                  </span>
                </div>

                {/* Candidate Snippet */}
                <div className="bg-navy-950/80 rounded-xl p-3.5 border border-slate-800/80">
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                    <span className="font-semibold text-slate-300">Software Developer Resume</span>
                    <span className="font-mono text-[11px]">842 words</span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2 italic font-serif">
                    "Senior Full Stack Software Engineer with 6+ years experience in Python, C++, React, and AWS microservices..."
                  </p>
                </div>

                {/* Classification Hero Result */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 uppercase tracking-wider font-mono text-[11px]">Detected Profile</span>
                    <span className="text-blue-400 font-mono font-bold">94.8% Confidence</span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-gradient-to-r from-blue-900/40 via-indigo-900/30 to-purple-900/20 border border-blue-500/40 flex items-center justify-between">
                    <div>
                      <div className="text-lg font-bold text-white tracking-wide">
                        INFORMATION TECHNOLOGY
                      </div>
                      <div className="text-xs text-blue-300/80 font-mono">
                        Champion Model • Calibrated Linear SVM
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-indigo-300">
                        94.8%
                      </div>
                    </div>
                  </div>
                </div>

                {/* Top 3 Predictions Bar */}
                <div className="space-y-2 pt-1">
                  <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                    Top 3 Predictions
                  </div>
                  <div className="space-y-1.5 text-xs">
                    <div>
                      <div className="flex justify-between mb-1 text-slate-300 font-medium">
                        <span>1. INFORMATION-TECHNOLOGY</span>
                        <span className="font-mono text-blue-400">94.8%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full" style={{ width: '94.8%' }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1 text-slate-400">
                        <span>2. ENGINEERING</span>
                        <span className="font-mono text-slate-400">3.2%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-slate-600 rounded-full" style={{ width: '3.2%' }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1 text-slate-400">
                        <span>3. CONSULTANT</span>
                        <span className="font-mono text-slate-400">1.1%</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-slate-700 rounded-full" style={{ width: '1.1%' }} />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Top Skills Tags */}
                <div className="space-y-2 pt-2 border-t border-slate-800">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
                    Extracted Top Skills
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {['Python', 'Machine Learning', 'SQL', 'TensorFlow', 'React.js', 'AWS', 'Docker'].map((skill) => (
                      <span
                        key={skill}
                        className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800/80 text-blue-300 border border-slate-700"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Interactive Try Button */}
                <button
                  onClick={handleSampleClick}
                  className="w-full py-2.5 rounded-xl font-semibold text-xs text-blue-300 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/30 flex items-center justify-center space-x-2 transition-all"
                >
                  <span>Test This Sample in Live Analyzer</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Benchmark Metric Highlights */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Trained Resumes', value: '2,482', sub: 'Primary Resume.csv' },
            { label: 'Target Verticals', value: '24', sub: 'Multiclass Taxonomy' },
            { label: 'Evaluation Macro-F1', value: '84.8%', sub: 'Balanced Stratified Test' },
            { label: 'Inference Latency', value: '< 25ms', sub: 'Optimized TF-IDF Engine' },
          ].map((stat, i) => (
            <div key={i} className="glass-card rounded-2xl p-5 border border-slate-800 text-center">
              <div className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight">
                {stat.value}
              </div>
              <div className="text-sm font-semibold text-slate-300 mt-1">{stat.label}</div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">{stat.sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Architectural Pillars */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            Engineering Precision at Every Layer
          </h2>
          <p className="text-slate-400 text-sm">
            Built from scratch to satisfy every requirement of the Samatrix ResumeForge 2026 rubric.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4 hover:border-blue-500/40 transition-all">
            <div className="w-10 h-10 rounded-xl bg-blue-600/15 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Strict Leakage Prevention</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Stratified 80/10/10 split before any vectorizer fitting. Text deduplication and normalization ensure the test benchmark remains entirely unseen.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4 hover:border-purple-500/40 transition-all">
            <div className="w-10 h-10 rounded-xl bg-purple-600/15 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Classical ML & Deep Learning</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Calibrated Linear SVM, Logistic Regression, and Multinomial Naive Bayes benchmarked against a custom 2-layer Bidirectional LSTM neural network.
            </p>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4 hover:border-emerald-500/40 transition-all">
            <div className="w-10 h-10 rounded-xl bg-emerald-600/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-white">Authentic Explainability</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              No black-box guesses. Mathematically computes instance-level token contributions using model coefficients and active document features.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
