import React, { useState, useEffect } from 'react';
import {
  BarChart3, PieChart, TrendingUp, AlertTriangle, Layers,
  RefreshCw, CheckCircle2, FileText, Cpu, Database
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip,
  CartesianGrid, Legend, Cell
} from 'recharts';
import { getAnalytics } from '../services/api';

const COLORS = [
  '#3B82F6', '#6366F1', '#8B5CF6', '#EC4899', '#F43F5E',
  '#10B981', '#06B6D4', '#F59E0B', '#14B8A6', '#64748B'
];

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await getAnalytics();
        setData(res);
      } catch (err) {
        setError('Failed to fetch analytics data from backend.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center space-y-4">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-400 mx-auto" />
        <p className="text-slate-400 font-mono text-sm">Loading Real Dataset & Model Analytics...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center space-y-4">
        <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
        <p className="text-slate-300 text-base">{error || 'No analytics data available.'}</p>
      </div>
    );
  }

  const { eda, model_comparison, error_summary, champion_metadata } = data;

  // Format category distribution for Recharts
  const categoryChartData = Object.entries(eda.category_counts || {})
    .map(([cat, count]) => ({
      category: cat.replace('-', ' '),
      shortCategory: cat.length > 12 ? cat.substring(0, 11) + '..' : cat,
      count
    }))
    .sort((a, b) => b.count - a.count);

  // Model comparison data
  const modelChartData = (model_comparison || []).map((m) => ({
    name: `${m.Model} (${m.Representation})`,
    shortName: m.Model.includes('SVM') ? 'Linear SVM (1,2)' : m.Model.includes('LSTM') ? 'BiLSTM' : m.Model.includes('Logistic') ? `LogReg ${m.Representation}` : `Naive Bayes`,
    Accuracy: (m.Accuracy * 100).toFixed(1),
    'Macro-F1': (m['Macro-F1'] * 100).toFixed(1),
    'Weighted-F1': (m['Weighted-F1'] * 100).toFixed(1),
  }));

  // Confused pairs data from error analysis
  const confusedPairs = (error_summary.top_confused_pairs || []).map((pair) => ({
    pair: `${pair.Category} → ${pair.Predicted_Category}`,
    count: pair.count
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Page Header */}
      <div className="border-b border-slate-800 pb-6">
        <div className="flex items-center space-x-2 text-xs font-mono text-blue-400 mb-1">
          <BarChart3 className="w-3.5 h-3.5" />
          <span>DATASET & MODEL BENCHMARK ANALYTICS</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Exploratory Data & Performance Dashboard
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Computed on the official 2,484 resume corpus using stratified evaluation and zero data leakage.
        </p>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          { label: 'Total Resumes', value: eda.total_resumes || 2484, sub: 'Corpus Size', icon: FileText, color: 'text-blue-400' },
          { label: 'Industries', value: eda.total_categories || 24, sub: 'Unique Classes', icon: Layers, color: 'text-indigo-400' },
          { label: 'Champion Model', value: 'SVM (1,2)', sub: 'Production Ready', icon: Cpu, color: 'text-emerald-400' },
          { label: 'Test Accuracy', value: `${(champion_metadata.accuracy * 100).toFixed(1)}%`, sub: 'Stratified Test', icon: CheckCircle2, color: 'text-purple-400' },
          { label: 'Macro-F1 Score', value: `${(champion_metadata.macro_f1 * 100).toFixed(1)}%`, sub: 'Balanced Metric', icon: TrendingUp, color: 'text-cyan-400' },
          { label: 'Median Word Count', value: eda.median_word_length || 757, sub: 'Words / Resume', icon: Database, color: 'text-amber-400' },
        ].map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="glass-card rounded-2xl p-4 border border-slate-800 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400 font-medium">{stat.label}</span>
                <Icon className={`w-4 h-4 ${stat.color}`} />
              </div>
              <div className="text-xl sm:text-2xl font-black text-white font-mono">{stat.value}</div>
              <div className="text-[11px] font-mono text-slate-400">{stat.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Chart 1: Category Distribution */}
      <div className="glass-panel rounded-2xl p-6 sm:p-7 border border-slate-800 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
          <div>
            <h2 className="font-bold text-white text-base">Class Distribution Across 24 Categories</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Highlighting majority categories (120 samples) down to minority niches (e.g. BPO with 22, Automobile with 36).
            </p>
          </div>
          <span className="text-xs font-mono text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-md border border-blue-500/20 self-start sm:self-auto">
            Total Resumes: {eda.total_resumes}
          </span>
        </div>

        <div className="h-80 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={categoryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis
                dataKey="shortCategory"
                stroke="#64748B"
                fontSize={10}
                interval={0}
                angle={-45}
                textAnchor="end"
              />
              <YAxis stroke="#64748B" fontSize={11} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                itemStyle={{ color: '#60A5FA' }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {categoryChartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Grid: Model Comparison & Error Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Model Comparison Bar Chart */}
        <div className="lg:col-span-7 glass-panel rounded-2xl p-6 sm:p-7 border border-slate-800 space-y-4 shadow-xl">
          <div className="border-b border-slate-800 pb-3">
            <h2 className="font-bold text-white text-base">Model Benchmark Comparison</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Comparing Accuracy, Macro-F1, and Weighted-F1 across TF-IDF baselines and PyTorch BiLSTM.
            </p>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={modelChartData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                <XAxis dataKey="shortName" stroke="#64748B" fontSize={10} angle={-20} textAnchor="end" />
                <YAxis stroke="#64748B" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0B0F19', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="Accuracy" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Macro-F1" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Weighted-F1" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Error Analysis & Confusion Breakdown */}
        <div className="lg:col-span-5 glass-panel rounded-2xl p-6 sm:p-7 border border-slate-800 space-y-4 shadow-xl">
          <div className="border-b border-slate-800 pb-3 flex justify-between items-center">
            <div>
              <h2 className="font-bold text-white text-base">Test Set Error Analysis</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Top confused category pairs on the 249-sample test set.
              </p>
            </div>
            <span className="text-xs font-mono text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
              Error Rate: {(error_summary.test_error_rate * 100).toFixed(1)}%
            </span>
          </div>

          <div className="space-y-3 pt-2">
            {confusedPairs.slice(0, 6).map((item, i) => (
              <div key={i} className="bg-navy-950/70 p-3 rounded-xl border border-slate-800/80 flex items-center justify-between text-xs">
                <span className="font-mono text-slate-300 font-medium">{item.pair}</span>
                <span className="px-2 py-0.5 rounded bg-rose-500/15 text-rose-400 font-mono font-bold">
                  {item.count} errors
                </span>
              </div>
            ))}
          </div>

          <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400 space-y-1 font-sans">
            <p className="font-semibold text-slate-300">Key Root Cause Observations:</p>
            <ul className="list-disc list-inside space-y-0.5 text-slate-400">
              <li>Cross-domain overlap: Banking vs Finance shared accounting terminology.</li>
              <li>Arts vs Designer profiles frequently share Photoshop & creative keywords.</li>
              <li>Very short resumes lack discriminatory technical tokens.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
