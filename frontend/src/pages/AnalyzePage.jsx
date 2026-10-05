import React, { useState, useRef } from 'react';
import {
  UploadCloud, FileText, CheckCircle2, AlertCircle, Sparkles,
  ArrowRight, RefreshCw, BarChart2, Layers, Briefcase, GraduationCap,
  Award, Shield, FileCheck, HelpCircle, Copy, Check
} from 'lucide-react';
import { predictResumeText, predictResumeFile } from '../services/api';

const PRESET_RESUMES = {
  'IT Developer': `Senior Full Stack Software Engineer with 7+ years of experience designing, developing, and deploying scalable distributed web applications.
Core Competencies: Python, Django, FastAPI, React.js, TypeScript, PostgreSQL, Redis, Docker, Kubernetes, AWS (ECS, Lambda, S3, RDS), CI/CD pipelines.
Experience:
- Architected microservices architecture serving 10M+ daily API requests with 99.99% uptime.
- Optimized SQL database queries reducing latency by 45%.
- Automated test suites with PyTest and GitHub Actions.
Education: Bachelor of Science in Computer Science, University of Technology. Certified AWS Solutions Architect.`,

  'Financial Analyst': `Senior Financial Analyst and Portfolio Manager with 8+ years experience in corporate finance, financial modeling, equity valuation, and risk assessment.
Key Skills: Financial analysis, financial reporting, budgeting, forecasting, DCF modeling, LBO, Bloomberg Terminal, Excel VBA, SQL, GAAP, SEC compliance.
Professional Experience:
- Managed $45M investment portfolio achieving 14.2% annualized return against benchmark.
- Conducted variance analysis, quarterly forecasting, and P&L budgeting across 4 corporate divisions.
- Prepared executive M&A financial models evaluating potential acquisitions.
Education: Master of Business Administration (MBA) in Finance. Chartered Financial Analyst (CFA) Charterholder.`,

  'Executive Chef': `Executive Chef with 12+ years of culinary leadership in fine dining and high-volume luxury hotel restaurants.
Specialties: Menu engineering, culinary technique, food cost control, kitchen brigade management, banquet catering, HACCP sanitation, inventory procurement, recipe formulation.
Experience:
- Directed back-of-house kitchen operations across 3 restaurant concepts generating $6.5M in annual food revenue.
- Reduced food waste by 18% while maintaining Michelin-guide standard culinary presentation.
- Trained and mentored culinary staff of 28 line cooks and sous chefs.
Education: Associate of Culinary Arts, Culinary Institute of America. ServSafe Food Manager Certification.`,

  'Corporate Attorney': `Senior Corporate Legal Counsel with 9+ years experience in contract negotiation, regulatory compliance, commercial litigation, and corporate governance.
Expertise: Corporate law, contract drafting, intellectual property, mergers & acquisitions, employment law, risk mitigation, antitrust regulations, arbitration.
Experience:
- Negotiated over 200 commercial enterprise vendor agreements and master service agreements (MSAs) valued at over $120M.
- Advised Board of Directors and senior executives on corporate compliance and litigation exposure.
- Managed external legal counsel and directed defense strategy in patent infringement litigation.
Education: Juris Doctor (J.D.), Law School. Admitted to the State Bar.`,

  'HR Recruiter': `Human Resources Manager and Talent Acquisition Specialist with 6+ years experience in full-lifecycle recruitment, onboarding, and employee relations.
Key Skills: Talent acquisition, technical recruitment, HRIS systems, Workday, compensation & benefits, employee engagement, performance management, labor law compliance.
Experience:
- Scaled technical engineering teams from 40 to 180 employees across 18 months with 92% retention rate.
- Designed structured behavioral interview frameworks, salary benchmarking, and employee onboarding roadmaps.
- Partnered with executive leadership to conduct annual performance appraisals and succession planning.
Education: Bachelor of Arts in Human Resource Management. SHRM Senior Certified Professional (SHRM-SCP).`
};

export default function AnalyzePage({ initialText = '' }) {
  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'file'
  const [resumeText, setResumeText] = useState(initialText || PRESET_RESUMES['IT Developer']);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleRunAnalysis = async () => {
    setError(null);
    setIsAnalyzing(true);
    setResult(null);

    const steps = [
      'Extracting resume text...',
      'Preprocessing and cleaning tokens...',
      'Running calibrated classifier...',
      'Computing keyword explainability...',
      'Extracting verified skills & metrics...'
    ];

    let stepIndex = 0;
    setAnalysisStep(steps[0]);
    const stepInterval = setInterval(() => {
      stepIndex++;
      if (stepIndex < steps.length) {
        setAnalysisStep(steps[stepIndex]);
      }
    }, 450);

    try {
      let data;
      if (activeTab === 'file') {
        if (!selectedFile) {
          throw new Error('Please select a PDF, DOCX, or TXT file to upload.');
        }
        data = await predictResumeFile(selectedFile);
      } else {
        if (!resumeText.trim() || resumeText.trim().length < 15) {
          throw new Error('Please enter at least 15 characters of resume content.');
        }
        data = await predictResumeText(resumeText);
      }

      clearInterval(stepInterval);
      setResult(data);
    } catch (err) {
      clearInterval(stepInterval);
      const msg = err.response?.data?.detail || err.message || 'Failed to complete resume analysis.';
      setError(msg);
    } finally {
      setIsAnalyzing(false);
      setAnalysisStep('');
    }
  };

  const handleCopyResult = () => {
    if (!result) return;
    const summary = `ResumeForge AI Classification\nCategory: ${result.prediction.category}\nConfidence: ${result.prediction.confidence_percentage}%\nTop Predictions: ${result.top_predictions.map(p => `${p.category} (${p.percentage}%)`).join(', ')}`;
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-2 text-xs font-mono text-blue-400 mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>REAL-TIME INFERENCE ENGINE</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Resume Intelligence Workspace
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Upload document or paste CV content for instantaneous classification, confidence scoring, and mathematical token attribution.
          </p>
        </div>

        {result && (
          <button
            onClick={handleCopyResult}
            className="self-start md:self-auto flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-slate-400" />}
            <span>{copied ? 'Copied Summary' : 'Copy Analysis'}</span>
          </button>
        )}
      </div>

      {/* Main Grid: Left Input Workspace vs Right Intelligence Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Input Panel */}
        <div className="lg:col-span-6 space-y-6">
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 shadow-xl space-y-5">
            {/* Input Mode Selector */}
            <div className="flex rounded-xl bg-navy-950 p-1 border border-slate-800 text-xs font-semibold">
              <button
                onClick={() => setActiveTab('text')}
                className={`flex-1 py-2 rounded-lg flex items-center justify-center space-x-2 transition-all ${
                  activeTab === 'text'
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <FileText className="w-4 h-4" />
                <span>Paste Resume Text</span>
              </button>
              <button
                onClick={() => setActiveTab('file')}
                className={`flex-1 py-2 rounded-lg flex items-center justify-center space-x-2 transition-all ${
                  activeTab === 'file'
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <UploadCloud className="w-4 h-4" />
                <span>Upload Document</span>
              </button>
            </div>

            {/* Mode 1: Paste Text */}
            {activeTab === 'text' && (
              <div className="space-y-3">
                {/* Presets Bar */}
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                    Quick Sample Presets:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {Object.keys(PRESET_RESUMES).map((name) => (
                      <button
                        key={name}
                        onClick={() => setResumeText(PRESET_RESUMES[name])}
                        className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700/80 transition-all"
                      >
                        {name}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="relative">
                  <textarea
                    rows={12}
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                    placeholder="Paste full resume text here (experience, skills, education, summary)..."
                    className="w-full rounded-xl bg-navy-950 border border-slate-800 p-4 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 font-sans leading-relaxed transition-all resize-y"
                  />
                  <div className="flex justify-between items-center text-[11px] font-mono text-slate-400 px-1 pt-1">
                    <span>{resumeText.split(/\s+/).filter(Boolean).length} words</span>
                    <span>{resumeText.length} characters</span>
                  </div>
                </div>
              </div>
            )}

            {/* Mode 2: File Upload */}
            {activeTab === 'file' && (
              <div className="space-y-4">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".pdf,.docx,.txt"
                  className="hidden"
                />

                <div
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
                  onDragLeave={() => setDragActive(false)}
                  onDrop={handleDrop}
                  className={`cursor-pointer p-8 rounded-2xl border-2 border-dashed text-center transition-all ${
                    dragActive
                      ? 'border-blue-400 bg-blue-500/10 scale-[1.01]'
                      : selectedFile
                      ? 'border-emerald-500/40 bg-emerald-500/5'
                      : 'border-slate-800 bg-navy-950/60 hover:border-slate-700 hover:bg-slate-900/50'
                  }`}
                >
                  <div className="flex flex-col items-center space-y-3">
                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${
                      selectedFile ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'bg-blue-600/15 text-blue-400 border border-blue-500/30'
                    }`}>
                      {selectedFile ? <FileCheck className="w-7 h-7" /> : <UploadCloud className="w-7 h-7" />}
                    </div>
                    {selectedFile ? (
                      <div>
                        <p className="font-semibold text-white text-sm">{selectedFile.name}</p>
                        <p className="text-xs text-slate-400 mt-0.5 font-mono">
                          {(selectedFile.size / 1024).toFixed(1)} KB • Click to change file
                        </p>
                      </div>
                    ) : (
                      <div>
                        <p className="font-semibold text-white text-sm">
                          Click to browse or drag & drop resume file
                        </p>
                        <p className="text-xs text-slate-400 mt-1 font-mono">
                          Supports PDF, DOCX, TXT (Maximum 10 MB)
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="flex items-start space-x-2.5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Action Button & Processing State */}
            <div className="pt-2">
              <button
                onClick={handleRunAnalysis}
                disabled={isAnalyzing}
                className={`w-full py-3.5 rounded-xl font-bold text-sm text-white flex items-center justify-center space-x-2 transition-all shadow-glow-blue ${
                  isAnalyzing
                    ? 'bg-blue-800 cursor-not-allowed opacity-90'
                    : 'bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-indigo-500 active:scale-98'
                }`}
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-white" />
                    <span>{analysisStep || 'Analyzing Resume...'}</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-blue-300" />
                    <span>Run Intelligent Classification</span>
                    <ArrowRight className="w-4 h-4 ml-1" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Prediction Results Dashboard */}
        <div className="lg:col-span-6 space-y-6">
          {!result && !isAnalyzing && (
            <div className="glass-panel rounded-2xl p-10 border border-slate-800 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-blue-600/10 border border-blue-500/20 text-blue-400 mx-auto flex items-center justify-center">
                <Briefcase className="w-8 h-8" />
              </div>
              <div className="max-w-sm mx-auto space-y-1">
                <h3 className="font-bold text-white text-base">Awaiting Resume Content</h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Submit text or a document on the left to trigger calibrated multiclass classification, feature attribution, and skills mapping.
                </p>
              </div>
            </div>
          )}

          {isAnalyzing && (
            <div className="glass-panel rounded-2xl p-10 border border-slate-800 text-center space-y-6 animate-pulse">
              <div className="w-16 h-16 rounded-2xl bg-blue-600/15 border border-blue-500/30 text-blue-400 mx-auto flex items-center justify-center">
                <RefreshCw className="w-8 h-8 animate-spin" />
              </div>
              <div className="space-y-2">
                <h3 className="font-bold text-white text-base">
                  {analysisStep || 'Analyzing Resume Content...'}
                </h3>
                <p className="text-xs text-slate-400 font-mono">
                  Preprocessing • TF-IDF Vectorization • Calibrated Decision Functions
                </p>
              </div>
              <div className="w-48 h-1.5 bg-slate-800 rounded-full mx-auto overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full animate-indeterminate" />
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-6 animate-fadeIn">
              {/* Primary Champion Prediction Card */}
              <div className="glass-card rounded-2xl p-6 sm:p-7 border border-blue-500/40 relative overflow-hidden space-y-5">
                <div className="absolute top-0 right-0 w-48 h-48 bg-blue-500/10 rounded-full blur-2xl pointer-events-none" />

                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="text-xs font-mono font-bold tracking-wider text-slate-300 uppercase">
                      PRIMARY CLASSIFICATION
                    </span>
                  </div>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    {result.model}
                  </span>
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <span className="text-xs text-slate-400 font-mono uppercase tracking-wider">
                      Detected Profile
                    </span>
                    <h2 className="text-2xl sm:text-3xl font-black text-white tracking-wide mt-0.5">
                      {result.prediction.category}
                    </h2>
                  </div>

                  {/* Confidence Gauge Badge */}
                  <div className="bg-navy-950/80 px-4 py-3 rounded-xl border border-slate-800 text-right">
                    <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">
                      Calibrated Confidence
                    </span>
                    <span className="text-2xl sm:text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 font-mono">
                      {result.prediction.confidence_percentage}%
                    </span>
                  </div>
                </div>

                {/* Top 3 Predictions Horizontal Probability Bars */}
                <div className="space-y-2 pt-2 border-t border-slate-800">
                  <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                    Top Category Probabilities
                  </span>
                  <div className="space-y-2 text-xs">
                    {result.top_predictions.map((pred, i) => (
                      <div key={pred.category}>
                        <div className="flex justify-between mb-1 font-medium text-slate-300">
                          <span>{i + 1}. {pred.category}</span>
                          <span className="font-mono text-blue-400 font-semibold">{pred.percentage}%</span>
                        </div>
                        <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                          <div
                            className={`h-full rounded-full transition-all duration-700 ${
                              i === 0
                                ? 'bg-gradient-to-r from-blue-500 to-indigo-500'
                                : i === 1
                                ? 'bg-slate-600'
                                : 'bg-slate-700'
                            }`}
                            style={{ width: `${Math.max(pred.percentage, 2)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Explainability Section: "Why did the model predict this?" */}
              <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <HelpCircle className="w-4 h-4 text-purple-400" />
                    <h3 className="font-bold text-white text-sm">
                      Why did the model predict this?
                    </h3>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">
                    Feature Attribution
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed bg-navy-950/70 p-3 rounded-xl border border-slate-800/80">
                  {result.explanation}
                </p>

                {/* Keyword Weights Bars */}
                <div className="space-y-2 pt-1">
                  <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                    Highest-Weighted Active N-Grams
                  </span>
                  <div className="space-y-2">
                    {result.keywords.map((kw, i) => (
                      <div key={i} className="text-xs">
                        <div className="flex justify-between text-slate-300 mb-1">
                          <span className="font-mono font-semibold text-blue-300">{kw.feature}</span>
                          <span className="font-mono text-slate-400 text-[11px]">
                            Weight: +{kw.weight}
                          </span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-500"
                            style={{ width: `${kw.relative_pct || 75}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Extracted Skills Intelligence */}
              {result.skills && result.skills.length > 0 && (
                <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-blue-400" />
                    <h3 className="font-bold text-white text-sm">
                      Extracted Technical & Professional Skills
                    </h3>
                  </div>

                  <div className="space-y-3">
                    {result.skills.map((group) => (
                      <div key={group.category} className="space-y-1.5">
                        <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                          {group.category}
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {group.skills.map((sk) => (
                            <span
                              key={sk}
                              className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800/90 text-blue-300 border border-slate-700/80"
                            >
                              {sk}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Structural Indicators (Education, Experience, Certifications) */}
              {result.metrics && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="glass-card rounded-xl p-3.5 border border-slate-800">
                    <div className="flex items-center space-x-2 text-slate-400 mb-1">
                      <GraduationCap className="w-4 h-4 text-indigo-400" />
                      <span className="text-xs font-semibold text-slate-300">Education</span>
                    </div>
                    <div className="text-xs text-slate-300 font-mono">
                      {result.metrics.education_signals.length > 0
                        ? result.metrics.education_signals.join(', ')
                        : 'Standard Degree'}
                    </div>
                  </div>

                  <div className="glass-card rounded-xl p-3.5 border border-slate-800">
                    <div className="flex items-center space-x-2 text-slate-400 mb-1">
                      <Briefcase className="w-4 h-4 text-emerald-400" />
                      <span className="text-xs font-semibold text-slate-300">Experience</span>
                    </div>
                    <div className="text-xs text-slate-300 font-mono">
                      {result.metrics.experience_signals.length > 0
                        ? result.metrics.experience_signals[0]
                        : 'Senior Profile'}
                    </div>
                  </div>

                  <div className="glass-card rounded-xl p-3.5 border border-slate-800">
                    <div className="flex items-center space-x-2 text-slate-400 mb-1">
                      <Award className="w-4 h-4 text-amber-400" />
                      <span className="text-xs font-semibold text-slate-300">Certifications</span>
                    </div>
                    <div className="text-xs text-slate-300 font-mono">
                      {result.metrics.has_certifications ? 'Detected' : 'None explicitly stated'}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
