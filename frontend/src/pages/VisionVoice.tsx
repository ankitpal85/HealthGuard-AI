import React, { useState } from 'react';
import { analyzeVisionImage, processVoiceQuery } from '../services/api';
import { Eye, Mic, MicOff, FileImage, Sparkles, Volume2 } from 'lucide-react';

interface VisionVoiceProps {
  userId: number;
}

export const VisionVoice: React.FC<VisionVoiceProps> = ({ userId }) => {
  const [imageUrl, setImageUrl] = useState('');
  const [visionResult, setVisionResult] = useState<string | null>(null);
  const [loadingVision, setLoadingVision] = useState(false);

  const [voiceText, setVoiceText] = useState('');
  const [voiceResult, setVoiceResult] = useState<string | null>(null);
  const [loadingVoice, setLoadingVoice] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const handleAnalyzeImage = async (e?: React.FormEvent, sampleUrl?: string) => {
    if (e) e.preventDefault();
    const urlToUse = sampleUrl || imageUrl;
    if (!urlToUse.trim()) return;
    setLoadingVision(true);
    setVisionResult(null);
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
      const utterance = new SpeechSynthesisUtterance(text);
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
    <div className="space-y-6">
      <div className="flex items-center justify-between glass-panel p-6 rounded-2xl" style={{ border: '1px solid rgba(14,165,233,0.1)' }}>
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <Eye className="w-6 h-6" style={{ color: '#0EA5E9' }} /> Vision & Voice Multimodal AI
          </h2>
          <p className="text-xs mt-1" style={{ color: '#64748B' }}>Medical prescription / lab report image analyzer & hands-free voice query processor</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Prescription & Medical Image Vision */}
        <div className="glass-panel glass-panel-hover p-6 space-y-4">
          <h3 className="font-bold text-white text-sm flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
            <FileImage className="w-5 h-5" style={{ color: '#0EA5E9' }} /> Prescription & Lab Report Vision Analyzer
          </h3>

          {/* Sample Prescriptions Chips */}
          <div className="space-y-2">
            <span className="text-xs font-semibold flex items-center gap-1" style={{ color: '#64748B' }}>
              <Sparkles className="w-3.5 h-3.5" style={{ color: '#0EA5E9' }} /> Try Preset Examples:
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

          <form onSubmit={handleAnalyzeImage} className="space-y-3 pt-2">
            <div>
              <label className="block text-xs font-semibold mb-1" style={{ color: '#94A3B8' }}>Image URL or Local Path</label>
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
              {loadingVision ? 'Extracting Medical Text...' : 'Analyze Prescription Image'}
            </button>
          </form>

          {visionResult && (
            <div className="p-4 rounded-xl text-xs whitespace-pre-wrap leading-relaxed space-y-2" style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(14,165,233,0.12)', color: '#E2E8F0' }}>
              <div className="flex items-center justify-between font-bold text-[11px] uppercase tracking-wider mb-1" style={{ color: '#0EA5E9' }}>
                <span>Vision AI Analysis Result</span>
                <button onClick={() => handleSpeakOutput(visionResult)} className="flex items-center gap-1 text-[11px] font-bold cursor-pointer hover:underline" style={{ color: '#06D6A0' }}>
                  <Volume2 className="w-3.5 h-3.5" /> Listen
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

