import React, { useState } from 'react';
import { analyzeSymptoms, runRiskAssessment, generateHealthReport, downloadDoctorPdfReport } from '../services/api';
import { TrendingUp, Stethoscope, AlertTriangle, FileText, Download, Sparkles } from 'lucide-react';

interface AnalyticsProps {
  userId: number;
}

export const Analytics: React.FC<AnalyticsProps> = ({ userId }) => {
  const [symptoms, setSymptoms] = useState('');
  const [symptomResult, setSymptomResult] = useState<string | null>(null);
  const [loadingSymptoms, setLoadingSymptoms] = useState(false);

  const [condition, setCondition] = useState('Diabetes Type 2');
  const [riskResult, setRiskResult] = useState<string | null>(null);
  const [loadingRisk, setLoadingRisk] = useState(false);

  const [reportResult, setReportResult] = useState<string | null>(null);
  const [loadingReport, setLoadingReport] = useState(false);

  const handleAnalyzeSymptoms = async (e?: React.FormEvent, customSyms?: string) => {
    if (e) e.preventDefault();
    const symsToUse = customSyms || symptoms;
    if (!symsToUse.trim()) return;
    setLoadingSymptoms(true);
    setSymptomResult(null);
    try {
      const symList = symsToUse.split(',').map((s) => s.trim());
      const res = await analyzeSymptoms(userId, symList);
      setSymptomResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingSymptoms(false);
    }
  };

  const handleRunRisk = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingRisk(true);
    setRiskResult(null);
    try {
      const res = await runRiskAssessment(userId, condition);
      setRiskResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingRisk(false);
    }
  };

  const handleGenerateReport = async () => {
    setLoadingReport(true);
    setReportResult(null);
    try {
      const res = await generateHealthReport(userId);
      setReportResult(res.report);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingReport(false);
    }
  };

  const handleDownloadReportFile = () => {
    if (!reportResult) return;
    const blob = new Blob([reportResult], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `HealthGuard_Clinical_Report_Patient_${userId}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const inputStyle = {
    background: 'rgba(15,23,42,0.8)',
    border: '1px solid rgba(14,165,233,0.15)',
    color: '#F8FAFC',
    borderRadius: '12px',
    padding: '10px 14px',
    fontSize: '14px',
    width: '100%',
    outline: 'none',
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-wrap items-center justify-between glass-panel p-6 rounded-2xl gap-4" style={{ border: '1px solid rgba(14,165,233,0.1)' }}>
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <TrendingUp className="w-6 h-6" style={{ color: '#0EA5E9' }} /> Clinical Analytics & Risk Predictors
          </h2>
          <p className="text-xs mt-1" style={{ color: '#64748B' }}>Run AI symptom checker, predictive disease risk models, and generate comprehensive medical reports</p>
        </div>

        <button
          onClick={() => downloadDoctorPdfReport(userId)}
          className="px-5 py-2.5 rounded-xl font-extrabold text-xs text-white transition-all shadow-lg flex items-center gap-2 cursor-pointer"
          style={{ background: 'linear-gradient(135deg, #06D6A0, #0EA5E9)', boxShadow: '0 6px 20px rgba(6,214,160,0.25)' }}
        >
          <Download className="w-4 h-4" />
          <span>Download Doctor Report (PDF)</span>
        </button>
      </div>


      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Symptom Checker Tool */}
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Stethoscope className="w-5 h-5" style={{ color: '#0EA5E9' }} /> AI Symptom Triage & Analysis
          </h3>

          {/* Sample Symptom Chips */}
          <div className="space-y-1.5">
            <span className="text-xs font-semibold flex items-center gap-1" style={{ color: '#64748B' }}>
              <Sparkles className="w-3.5 h-3.5" style={{ color: '#0EA5E9' }} /> Common Symptom Sets:
            </span>
            <div className="flex flex-wrap gap-2">
              {[
                "headache, mild fever, fatigue",
                "frequent thirst, blurred vision, fatigue",
                "chest tightness, shortness of breath",
              ].map((symStr, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => { setSymptoms(symStr); handleAnalyzeSymptoms(undefined, symStr); }}
                  className="px-2.5 py-1 rounded-lg text-xs font-semibold cursor-pointer transition-all"
                  style={{ background: 'rgba(14,165,233,0.08)', border: '1px solid rgba(14,165,233,0.2)', color: '#38BDF8' }}
                >
                  "{symStr}"
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleAnalyzeSymptoms} className="space-y-3 pt-1">
            <div>
              <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Enter Symptoms (comma separated)</label>
              <input
                type="text"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="e.g. headache, mild fever, fatigue"
                style={inputStyle}
              />
            </div>
            <button
              type="submit"
              disabled={loadingSymptoms || !symptoms.trim()}
              className="w-full py-2.5 rounded-xl btn-primary font-semibold text-xs disabled:opacity-50 cursor-pointer"
            >
              {loadingSymptoms ? 'Analyzing Symptoms...' : 'Analyze Symptoms'}
            </button>
          </form>

          {symptomResult && (
            <div className="p-4 rounded-xl text-xs whitespace-pre-wrap leading-relaxed"
              style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(14,165,233,0.12)', color: '#E2E8F0' }}>
              {symptomResult}
            </div>
          )}
        </div>

        {/* Predictive Risk Model */}
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <AlertTriangle className="w-5 h-5" style={{ color: '#F59E0B' }} /> Disease Risk Assessment
          </h3>
          <form onSubmit={handleRunRisk} className="space-y-3">
            <div>
              <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Target Medical Condition</label>
              <select
                value={condition}
                onChange={(e) => setCondition(e.target.value)}
                style={inputStyle}
              >
                <option>Diabetes Type 2</option>
                <option>Hypertension & Cardiovascular Risk</option>
                <option>Kidney Health & Filtration</option>
                <option>Metabolic Syndrome</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={loadingRisk}
              className="w-full py-2.5 rounded-xl font-semibold text-xs disabled:opacity-50 text-white cursor-pointer"
              style={{ background: 'linear-gradient(135deg, #F59E0B, #0EA5E9)', boxShadow: '0 4px 16px rgba(245,158,11,0.2)' }}
            >
              {loadingRisk ? 'Calculating Risk Scores...' : 'Run Risk Assessment'}
            </button>
          </form>

          {riskResult && (
            <div className="p-4 rounded-xl text-xs whitespace-pre-wrap leading-relaxed"
              style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(245,158,11,0.15)', color: '#E2E8F0' }}>
              {riskResult}
            </div>
          )}
        </div>
      </div>

      {/* Automated Report Generator */}
      <div className="glass-panel p-6 rounded-2xl space-y-4" style={{ border: '1px solid rgba(6,214,160,0.1)' }}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              <FileText className="w-5 h-5" style={{ color: '#06D6A0' }} /> Automated Clinical Summary Generator
            </h3>
            <p className="text-xs mt-1" style={{ color: '#64748B' }}>Generates a comprehensive clinical summary report for doctor consultations</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleGenerateReport}
              disabled={loadingReport}
              className="px-4 py-2.5 rounded-xl text-white font-semibold text-xs flex items-center gap-2 disabled:opacity-50 transition-all cursor-pointer"
              style={{ background: 'linear-gradient(135deg, #06D6A0, #14B8A6)', boxShadow: '0 4px 16px rgba(6,214,160,0.25)' }}
            >
              <Download className="w-4 h-4" /> {loadingReport ? 'Generating...' : 'Generate Full Report'}
            </button>
            {reportResult && (
              <button
                onClick={handleDownloadReportFile}
                className="px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer"
                style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(6,214,160,0.3)', color: '#06D6A0' }}
              >
                💾 Save .md File
              </button>
            )}
          </div>
        </div>

        {reportResult && (
          <div className="p-4 rounded-xl text-xs whitespace-pre-wrap leading-relaxed"
            style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(6,214,160,0.12)', color: '#E2E8F0' }}>
            {reportResult}
          </div>
        )}
      </div>
    </div>
  );
};

