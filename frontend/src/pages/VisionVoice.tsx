import React, { useState } from 'react';
import { analyzeVisionImage, processVoiceQuery, uploadMedicalReportFile } from '../services/api';
import { Eye, Mic, MicOff, FileImage, Sparkles, Volume2, Upload, FileText, CheckCircle2, AlertTriangle, Activity } from 'lucide-react';

interface VisionVoiceProps {
  userId: number;
}

export const VisionVoice: React.FC<VisionVoiceProps> = ({ userId }) => {
  const [imageUrl, setImageUrl] = useState('');
  const [visionResult, setVisionResult] = useState<string | null>(null);
  const [extractedMetrics, setExtractedMetrics] = useState<any[]>([]);
  const [loadingVision, setLoadingVision] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [voiceText, setVoiceText] = useState('');
  const [voiceResult, setVoiceResult] = useState<string | null>(null);
  const [loadingVoice, setLoadingVoice] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const handleFileUpload = async (fileToUpload: File) => {
    setLoadingVision(true);
    setVisionResult(null);
    setExtractedMetrics([]);
    try {
      const res = await uploadMedicalReportFile(userId, fileToUpload);
      setVisionResult(res.analysis);
      if (res.metrics) setExtractedMetrics(res.metrics);
    } catch (err: any) {
      console.error(err);
      setVisionResult(`❌ Error processing report file: ${err.message || 'Server error'}`);
    } finally {
      setLoadingVision(false);
    }
  };

  const handleAnalyzeImage = async (e?: React.FormEvent, sampleUrl?: string) => {
    if (e) e.preventDefault();
    const urlToUse = sampleUrl || imageUrl;
    if (!urlToUse.trim()) return;
    setLoadingVision(true);
    setVisionResult(null);
    setExtractedMetrics([]);
    try {
      const res = await analyzeVisionImage(userId, urlToUse);
      setVisionResult(res.analysis);
    } catch (err: any) {
      console.error(err);
      setVisionResult(`❌ Error analyzing image: ${err.message || 'Server error'}`);
    } finally {
      setLoadingVision(false);
    }
  };

  const handleProcessVoice = async (e?: React.FormEvent, customText?: string) => {
    if (e) e.preventDefault();
    const textToUse = customText || voiceText;
    if (!textToUse.trim()) return;
    setLoadingVoice(true);
    setVoiceResult(null);
    try {
      const res = await processVoiceQuery(userId, textToUse);
      setVoiceResult(res.result);
    } catch (err: any) {
      console.error(err);
      setVoiceResult(`❌ Error processing voice query: ${err.message || 'Server error'}`);
    } finally {
      setLoadingVoice(false);
    }
  };

  const startVoiceRecording = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech Recognition is not supported in your browser. Try Chrome or Edge.');
      return;
    }
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    setIsListening(true);
    recognition.start();

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setVoiceText(transcript);
      setIsListening(false);
      handleProcessVoice(undefined, transcript);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };
  };

  const handleSpeakOutput = (text: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const cleanText = text.replace(/[*#_`]/g, '');
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const inputStyle: React.CSSProperties = {
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
      <div className="flex items-center justify-between glass-panel p-6 rounded-2xl" style={{ border: '1px solid rgba(14,165,233,0.1)' }}>
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Eye className="w-6 h-6" style={{ color: '#0EA5E9' }} /> Vision & Voice Multimodal AI
          </h2>
          <p className="text-xs mt-1" style={{ color: '#64748B' }}>Medical PDF lab report scanner, prescription image analyzer & hands-free voice query processor</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Prescription & Medical Image Vision */}
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <FileImage className="w-5 h-5" style={{ color: '#0EA5E9' }} /> Prescription & Lab Report Vision Analyzer
          </h3>

          {/* Drag & Drop File Upload Box */}
          <div className="p-5 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center text-center transition-all"
            style={{ borderColor: 'rgba(14,165,233,0.3)', background: 'rgba(15,23,42,0.6)' }}
          >
            <div className="w-12 h-12 rounded-2xl flex items-center justify-center mb-2" style={{ background: 'rgba(14,165,233,0.12)', color: '#0EA5E9' }}>
              <Upload className="w-6 h-6" />
            </div>
            <p className="text-xs font-bold text-white">Upload Lab Report PDF or Medical Image</p>
            <p className="text-[11px] mt-0.5" style={{ color: '#64748B' }}>Supports PDF, PNG, JPG, JPEG (CBC, Lipid Profile, Rx)</p>
            
            <label className="mt-3 px-4 py-2 rounded-xl text-xs font-extrabold btn-primary cursor-pointer">
              <span>Choose File</span>
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    const file = e.target.files[0];
                    setSelectedFile(file);
                    handleFileUpload(file);
                  }
                }}
              />
            </label>

            {selectedFile && (
              <div className="mt-2 text-xs font-semibold flex items-center gap-1.5" style={{ color: '#06D6A0' }}>
                <FileText className="w-4 h-4" /> Loaded: {selectedFile.name}
              </div>
            )}
          </div>

          {/* Sample Prescriptions Chips */}
          <div className="space-y-2 pt-1">
            <span className="text-xs font-semibold flex items-center gap-1" style={{ color: '#64748B' }}>
              <Sparkles className="w-3.5 h-3.5" style={{ color: '#0EA5E9' }} /> Or Try Preset Examples:
            </span>
            <div className="flex flex-wrap gap-2">
              {[
                { label: '📄 Doctor Prescription', url: 'https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=500' },
                { label: '🧪 CBC Blood Test Report', url: 'https://images.unsplash.com/photo-1579154204601-01588f351e67?w=500' },
                { label: '💊 Medicine Box', url: 'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500' },
              ].map((sample, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setImageUrl(sample.url);
                    handleAnalyzeImage(undefined, sample.url);
                  }}
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer"
                  style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(14,165,233,0.15)', color: '#38BDF8' }}
                  onMouseEnter={(e) => { (e.currentTarget).style.background = 'rgba(14,165,233,0.12)'; }}
                  onMouseLeave={(e) => { (e.currentTarget).style.background = 'rgba(15,23,42,0.7)'; }}
                >
                  {sample.label}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleAnalyzeImage} className="space-y-3 pt-1">
            <div>
              <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Image URL / Remote Path</label>
              <input
                type="text"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="https://example.com/prescription.jpg"
                style={inputStyle}
              />
            </div>
            <button
              type="submit"
              disabled={loadingVision || !imageUrl.trim()}
              className="w-full py-2.5 rounded-xl btn-primary font-semibold text-xs disabled:opacity-50 cursor-pointer"
            >
              {loadingVision ? 'Scanning & Parsing Medical Report...' : 'Analyze URL Image'}
            </button>
          </form>

          {/* Extracted Biomarker Cards */}
          {extractedMetrics.length > 0 && (
            <div className="space-y-2 pt-2">
              <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5" style={{ color: '#0EA5E9' }}>
                <Activity className="w-4 h-4" /> Extracted Telemetry Biomarkers (Auto-Synced to DB):
              </span>
              <div className="grid grid-cols-2 gap-2">
                {extractedMetrics.map((m, idx) => (
                  <div key={idx} className="p-3 rounded-xl" style={{ background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(14,165,233,0.15)' }}>
                    <p className="text-[11px] font-bold" style={{ color: '#94A3B8' }}>{m.metric_type}</p>
                    <p className="text-sm font-extrabold text-white mt-0.5">
                      {m.value}{m.value2 ? `/${m.value2}` : ''} <span className="text-[10px] font-normal" style={{ color: '#64748B' }}>{m.unit}</span>
                    </p>
                    <div className="mt-1 flex items-center gap-1 text-[10px] font-bold"
                      style={{ color: m.status.toLowerCase().includes('high') || m.status.toLowerCase().includes('hyper') ? '#EF4444' : (m.status.toLowerCase().includes('elevat') ? '#F59E0B' : '#06D6A0') }}
                    >
                      {m.status.toLowerCase().includes('high') || m.status.toLowerCase().includes('hyper') ? <AlertTriangle className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                      <span>{m.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {visionResult && (
            <div className="p-4 rounded-xl text-xs whitespace-pre-wrap leading-relaxed space-y-2" style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(14,165,233,0.12)', color: '#E2E8F0' }}>
              <div className="flex items-center justify-between font-bold text-[11px] uppercase tracking-wider mb-1" style={{ color: '#0EA5E9' }}>
                <span>Vision & PDF Report Analysis</span>
                <button onClick={() => handleSpeakOutput(visionResult)} className="flex items-center gap-1 text-[11px] font-bold cursor-pointer hover:underline" style={{ color: '#06D6A0' }}>
                  <Volume2 className="w-3.5 h-3.5" /> Listen Audio
                </button>
              </div>
              {visionResult}
            </div>
          )}
        </div>

        {/* Voice Query Processing */}
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Mic className="w-5 h-5" style={{ color: '#06D6A0' }} /> Voice Query & Speech AI Processor
          </h3>

          {/* Sample Prompts */}
          <div className="space-y-2">
            <span className="text-xs font-semibold flex items-center gap-1" style={{ color: '#64748B' }}>
              <Sparkles className="w-3.5 h-3.5" style={{ color: '#06D6A0' }} /> Quick Voice Prompts:
            </span>
            <div className="flex flex-wrap gap-2">
              {[
                "Log blood pressure 120 over 80",
                "What is 1mg price for Metformin 500mg?",
                "Explain Ashwagandha health benefits",
              ].map((promptText, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setVoiceText(promptText);
                    handleProcessVoice(undefined, promptText);
                  }}
                  className="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer"
                  style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(6,214,160,0.15)', color: '#06D6A0' }}
                  onMouseEnter={(e) => { (e.currentTarget).style.background = 'rgba(6,214,160,0.12)'; }}
                  onMouseLeave={(e) => { (e.currentTarget).style.background = 'rgba(15,23,42,0.7)'; }}
                >
                  "{promptText}"
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleProcessVoice} className="space-y-3 pt-2">
            <div>
              <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Transcribed Spoken Query</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={voiceText}
                  onChange={(e) => setVoiceText(e.target.value)}
                  placeholder="Click microphone to speak or type query..."
                  style={{ ...inputStyle, borderColor: isListening ? 'rgba(6,214,160,0.6)' : 'rgba(6,214,160,0.15)' }}
                  className="flex-1"
                />
                <button
                  type="button"
                  onClick={startVoiceRecording}
                  className="px-4 py-2.5 rounded-xl font-bold text-xs flex items-center justify-center transition-all cursor-pointer"
                  style={{
                    background: isListening ? 'rgba(239,68,68,0.2)' : 'rgba(6,214,160,0.15)',
                    border: `1px solid ${isListening ? '#EF4444' : '#06D6A0'}`,
                    color: isListening ? '#EF4444' : '#06D6A0',
                  }}
                  title={isListening ? 'Listening...' : 'Click to Speak'}
                >
                  {isListening ? <MicOff className="w-5 h-5 animate-pulse" /> : <Mic className="w-5 h-5" />}
                </button>
              </div>
            </div>
            <button
              type="submit"
              disabled={loadingVoice || !voiceText.trim()}
              className="w-full py-2.5 rounded-xl font-semibold text-xs text-white disabled:opacity-50 transition-all cursor-pointer"
              style={{ background: 'linear-gradient(135deg, #06D6A0, #14B8A6)', boxShadow: '0 4px 16px rgba(6,214,160,0.25)' }}
            >
              {loadingVoice ? 'Processing Voice Intent...' : 'Process Voice Query'}
            </button>
          </form>

          {voiceResult && (
            <div className="p-4 rounded-xl text-xs whitespace-pre-wrap leading-relaxed space-y-2" style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(6,214,160,0.12)', color: '#E2E8F0' }}>
              <div className="flex items-center justify-between font-bold text-[11px] uppercase tracking-wider mb-1" style={{ color: '#06D6A0' }}>
                <span>Voice AI Response</span>
                <button onClick={() => handleSpeakOutput(voiceResult)} className="flex items-center gap-1 text-[11px] font-bold cursor-pointer hover:underline" style={{ color: '#06D6A0' }}>
                  <Volume2 className="w-3.5 h-3.5" /> Read Aloud
                </button>
              </div>
              {voiceResult}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};


