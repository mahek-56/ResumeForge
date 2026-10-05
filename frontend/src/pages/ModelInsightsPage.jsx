import React, { useState, useEffect } from 'react';
import {
  Layers, Search, CheckCircle2, Cpu, BarChart2,
  RefreshCw, AlertCircle, ArrowUpRight, Filter
} from 'lucide-react';
import { getMetrics, getAnalytics } from '../services/api';

export default function ModelInsightsPage() {
  const [metrics, setMetrics] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('INFORMATION-TECHNOLOGY');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const loadAll = async () => {
      try {
        setLoading(true);
        const [metRes, anaRes] = await Promise.all([getMetrics(), getAnalytics()]);
        setMetrics(metRes);
        setAnalytics(anaRes);
      } catch (err) {
        setError('Failed to load model insights.');
      } finally {
        setLoading(false);
      }
    };
    loadAll();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center space-y-4">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-400 mx-auto" />
        <p className="text-slate-400 font-mono text-sm">Loading Model Intelligence & Feature Weights...</p>
      </div>
    );
  }

  if (error || !metrics || !analytics) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center space-y-4">
        <AlertCircle className="w-8 h-8 text-rose-400 mx-auto" />
        <p className="text-slate-300">{error || 'Unable to load model insights.'}</p>
      </div>
    );
  }

  const { classification_report, feature_importance } = metrics;
  const { model_comparison, champion_metadata } = analytics;

  // Filter categories for the class-wise table
  const allCategories = champion_metadata.categories || Object.keys(feature_importance || {});
  const filteredCategories = allCategories.filter((cat) =>
    cat.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Features for the currently selected category
  const activeFeatures = feature_importance[selectedCategory] || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Header */}
      <div className="border-b border-slate-800 pb-6">
        <div className="flex items-center space-x-2 text-xs font-mono text-blue-400 mb-1">
          <Layers className="w-3.5 h-3.5" />
          <span>MODEL INTELLIGENCE & EXPLAINABILITY</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Model Comparison & Feature Architecture
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Complete evaluation across classical and deep neural architectures with transparent mathematical feature weights.
        </p>
      </div>

      {/* Champion Model Overview Card */}
      <div className="glass-card rounded-2xl p-6 sm:p-7 border border-blue-500/40 relative overflow-hidden space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                PRODUCTION SERVING CHAMPION
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-white tracking-wide mt-1">
              {champion_metadata.model_name || 'Linear SVM (Calibrated)'}
            </h2>
            <p className="text-xs text-blue-300 font-mono mt-0.5">
              Representation: {champion_metadata.representation} • Vocabulary: {champion_metadata.vocabulary_size.toLocaleString()} tokens
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-navy-950/80 px-4 py-2.5 rounded-xl border border-slate-800 text-center">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Accuracy</span>
              <span className="text-xl font-bold text-white font-mono">{(champion_metadata.accuracy * 100).toFixed(1)}%</span>
            </div>
            <div className="bg-navy-950/80 px-4 py-2.5 rounded-xl border border-slate-800 text-center">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Macro-F1</span>
              <span className="text-xl font-bold text-blue-400 font-mono">{(champion_metadata.macro_f1 * 100).toFixed(1)}%</span>
            </div>
            <div className="bg-navy-950/80 px-4 py-2.5 rounded-xl border border-slate-800 text-center">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block">Weighted-F1</span>
              <span className="text-xl font-bold text-purple-400 font-mono">{(champion_metadata.weighted_f1 * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-300">
          <div className="bg-navy-950/60 p-3.5 rounded-xl border border-slate-800/80">
            <span className="font-semibold text-white block mb-1">Probability Calibration:</span>
            Platt sigmoid scaling via 3-fold cross-validation maps raw hyperplanes to true probability simplex.
          </div>
          <div className="bg-navy-950/60 p-3.5 rounded-xl border border-slate-800/80">
            <span className="font-semibold text-white block mb-1">Sub-Millisecond Inference:</span>
            Sparse matrix dot-products execute in under 5ms, ideal for production workloads.
          </div>
          <div className="bg-navy-950/60 p-3.5 rounded-xl border border-slate-800/80">
            <span className="font-semibold text-white block mb-1">Deep Learning Benchmark:</span>
            PyTorch 2-layer BiLSTM achieved 77.11% test accuracy and 0.7112 Macro-F1 across 24 classes.
          </div>
        </div>
      </div>

      {/* Model Comparison Table */}
      <div className="glass-panel rounded-2xl p-6 sm:p-7 border border-slate-800 space-y-4 shadow-xl">
        <div className="border-b border-slate-800 pb-3">
          <h2 className="font-bold text-white text-base">Full Architectural Comparison (model_comparison.csv)</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Real test set results evaluated on the 249-sample held-out stratified test set.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-sans">
            <thead className="bg-navy-950 text-slate-400 font-mono uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Model Architecture</th>
                <th className="py-3 px-4">Representation</th>
                <th className="py-3 px-4">Accuracy</th>
                <th className="py-3 px-4">Precision</th>
                <th className="py-3 px-4">Recall</th>
                <th className="py-3 px-4">Macro-F1</th>
                <th className="py-3 px-4">Weighted-F1</th>
                <th className="py-3 px-4">Training Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {(model_comparison || []).map((row, i) => {
                const isChampion = row.Model.includes('Linear SVM') && row.Representation.includes('1,2');
                const isBiLSTM = row.Model.includes('LSTM');
                return (
                  <tr
                    key={i}
                    className={`hover:bg-slate-800/30 transition-colors ${
                      isChampion ? 'bg-blue-600/10 text-white font-semibold' : 'text-slate-300'
                    }`}
                  >
                    <td className="py-3 px-4 font-sans font-medium flex items-center space-x-2">
                      <span>{row.Model}</span>
                      {isChampion && (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                          Champion
                        </span>
                      )}
                      {isBiLSTM && (
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                          Deep Learning
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-400">{row.Representation}</td>
                    <td className="py-3 px-4 text-blue-400 font-bold">{(row.Accuracy * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4">{(row.Precision * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4">{(row.Recall * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4 text-purple-400 font-bold">{(row['Macro-F1'] * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4 text-emerald-400 font-bold">{(row['Weighted-F1'] * 100).toFixed(1)}%</td>
                    <td className="py-3 px-4 text-slate-400">{row.Training_Time}s</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Two Column Section: Category Feature Explorer + Per-Class Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left: Interactive Category Feature Explorer */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-6 sm:p-7 border border-slate-800 space-y-5 shadow-xl">
          <div className="border-b border-slate-800 pb-3 space-y-1">
            <h2 className="font-bold text-white text-base">Top Predictive N-Grams Explorer</h2>
            <p className="text-xs text-slate-400">
              Select any of the 24 categories to view the exact positive weights extracted from the trained champion model.
            </p>
          </div>

          <div>
            <label className="text-xs font-mono text-slate-400 uppercase tracking-wider block mb-1.5">
              Select Target Category:
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full bg-navy-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-blue-500 font-sans"
            >
              {allCategories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Features List */}
          <div className="space-y-2 pt-2">
            <div className="flex justify-between text-xs font-mono text-slate-400 uppercase border-b border-slate-800 pb-1.5">
              <span>Predictive Term</span>
              <span>Model Weight</span>
            </div>
            <div className="space-y-1.5 max-h-96 overflow-y-auto pr-1">
              {activeFeatures.slice(0, 18).map((f, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-2 rounded-lg bg-navy-950/60 border border-slate-800/80 text-xs hover:border-slate-700 transition-all"
                >
                  <span className="font-mono text-blue-300 font-medium">{f.feature}</span>
                  <span className="font-mono text-slate-300 font-semibold bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
                    +{f.weight}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Per-Class Performance Table */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 sm:p-7 border border-slate-800 space-y-5 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h2 className="font-bold text-white text-base">Class-Wise Test Performance</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Precision, Recall, and F1-score for all 24 categories on held-out test data.
              </p>
            </div>
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-navy-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="overflow-x-auto max-h-[440px] overflow-y-auto">
            <table className="w-full text-left text-xs font-sans">
              <thead className="bg-navy-950 text-slate-400 font-mono uppercase tracking-wider sticky top-0 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Precision</th>
                  <th className="py-2.5 px-3">Recall</th>
                  <th className="py-2.5 px-3">F1-Score</th>
                  <th className="py-2.5 px-3">Support</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {filteredCategories.map((cat) => {
                  const catMetrics = classification_report[cat] || { precision: 0, recall: 0, 'f1-score': 0, support: 0 };
                  const f1 = (catMetrics['f1-score'] * 100).toFixed(1);
                  return (
                    <tr
                      key={cat}
                      onClick={() => setSelectedCategory(cat)}
                      className={`cursor-pointer hover:bg-slate-800/40 transition-colors ${
                        selectedCategory === cat ? 'bg-blue-600/15 text-blue-300 font-semibold' : 'text-slate-300'
                      }`}
                    >
                      <td className="py-2.5 px-3 font-sans font-medium">{cat}</td>
                      <td className="py-2.5 px-3">{(catMetrics.precision * 100).toFixed(1)}%</td>
                      <td className="py-2.5 px-3">{(catMetrics.recall * 100).toFixed(1)}%</td>
                      <td className="py-2.5 px-3 text-purple-400 font-bold">{f1}%</td>
                      <td className="py-2.5 px-3 text-slate-400">{catMetrics.support}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
