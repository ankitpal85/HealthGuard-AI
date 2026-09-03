import React, { useEffect, useState, useRef } from 'react';
import { fetchChatHistory, sendChatMessage, clearChatHistory, getBaseApiUrl, saveLocalChatHistory, getStoredAuthSession } from '../services/api';
import { Send, User, Trash2, Sparkles, Stethoscope, Brain, Loader2, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';

interface ChatbotProps {
  userId: number;
}

const SUGGESTED_QUESTIONS = [
  "Check 1mg price for Dolo 650",
  "Find a Cardiologist in Mumbai on Practo",
  "What are the benefits of Ashwagandha?",
  "Check AQI for Delhi respiratory health",
  "What are today's medications?",
  "Explain symptoms of diabetes",
];

export const Chatbot: React.FC<ChatbotProps> = ({ userId }) => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speakingIdx, setSpeakingIdx] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    const session = getStoredAuthSession();
    fetchChatHistory(userId, session?.email)
      .then((res) => {
        if (res.length === 0) {
          setMessages([
            {
              role: 'assistant',
              content: "👋 **Hello! I'm HealthGuard AI**, your personal health monitoring assistant.\n\nAsk me anything about your medications, symptoms, wellness, or AYUSH remedies!",
            },
          ]);
        } else {
          setMessages(res);
        }
        scrollToBottom();
      })
      .catch((err) => console.error(err));
  }, [userId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const session = getStoredAuthSession();
    const userEmail = session?.email;

    const userMsg = { role: 'user', content: text, created_at: new Date().toISOString() };
    setMessages((prev) => {
      const updated = [...prev, userMsg];
      saveLocalChatHistory(userId, updated, userEmail);
      return updated;
    });
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const baseUrl = getBaseApiUrl();
      const response = await fetch(`${baseUrl}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message: text }),
      });

      if (!response.ok) {
        throw new Error(`Chat API responded with status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('ReadableStream not supported');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let assistantText = '';

      setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (dataStr.trim() === '[DONE]') break;
            assistantText += dataStr;

            setMessages((prev) => {
              const newMsgs = [...prev];
              newMsgs[newMsgs.length - 1] = { role: 'assistant', content: assistantText };
              saveLocalChatHistory(userId, newMsgs, userEmail);
              return newMsgs;
            });
          }
        }
      }
    } catch (err) {
      console.warn('Chat streaming unavailable, using intelligent clinical engine fallback:', err);
      const res = await sendChatMessage(userId, text, userEmail);
      setMessages((prev) => {
        const newMsgs = [...prev];
        if (newMsgs.length > 0 && newMsgs[newMsgs.length - 1].role === 'assistant' && !newMsgs[newMsgs.length - 1].content) {
          newMsgs[newMsgs.length - 1] = res;
          saveLocalChatHistory(userId, newMsgs, userEmail);
          return newMsgs;
        }
        const updated = [...prev, res];
        saveLocalChatHistory(userId, updated, userEmail);
        return updated;
      });
    } finally {
      setLoading(false);
    }
  };

  const startVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech Recognition is not supported in your browser. Please try Google Chrome or Microsoft Edge.');
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
      setInput(transcript);
      setIsListening(false);
      handleSend(transcript);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };
  };

  const handleSpeakMessage = (text: string, idx: number) => {
    if (!('speechSynthesis' in window)) return;

    if (speakingIdx === idx) {
      window.speechSynthesis.cancel();
      setSpeakingIdx(null);
      return;
    }

    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*#_`]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.onend = () => setSpeakingIdx(null);
    utterance.onerror = () => setSpeakingIdx(null);

    setSpeakingIdx(idx);
    window.speechSynthesis.speak(utterance);
  };

  const handleClear = async () => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    const session = getStoredAuthSession();
    await clearChatHistory(userId, session?.email);
    const initialMsg: any[] = [
      {
        role: 'assistant',
        content: "👋 Chat history cleared. How can I help you today?",
      },
    ];
    setMessages(initialMsg);
    saveLocalChatHistory(userId, initialMsg, session?.email);
  };

  const [continuousVoice, setContinuousVoice] = useState(false);

  return (
    <div className="flex flex-col h-[calc(100vh-7.5rem)] space-y-4 animate-in fade-in duration-300">
      {/* Top Header Card */}
      <div className="flex flex-wrap items-center justify-between glass-panel p-4 px-6 rounded-2xl gap-3"
        style={{ border: '1px solid rgba(14,165,233,0.15)' }}>
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded-2xl flex items-center justify-center text-white shadow-lg"
            style={{ background: 'linear-gradient(135deg, #0EA5E9, #06B6D4)', boxShadow: '0 6px 20px rgba(14,165,233,0.25)' }}>
            <Stethoscope className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-extrabold text-white text-sm tracking-tight flex items-center gap-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              HealthGuard AI Conversational Engine
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-60" style={{ background: '#06D6A0' }} />
                <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: '#06D6A0' }} />
              </span>
            </h2>
            <p className="text-xs font-medium" style={{ color: '#64748B' }}>Hands-free Voice STT/TTS • LangGraph Pipeline • Multi-Provider Model</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => {
              const nextVal = !continuousVoice;
              setContinuousVoice(nextVal);
              if (nextVal && !isListening) startVoiceInput();
            }}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all shadow-sm cursor-pointer"
            style={{
              border: `1px solid ${continuousVoice ? '#06D6A0' : 'rgba(148,163,184,0.2)'}`,
              background: continuousVoice ? 'rgba(6,214,160,0.15)' : 'rgba(15,23,42,0.6)',
              color: continuousVoice ? '#06D6A0' : '#94A3B8',
            }}
          >
            {continuousVoice ? <Mic className="w-3.5 h-3.5 animate-pulse" /> : <MicOff className="w-3.5 h-3.5" />}
            <span>{continuousVoice ? 'Continuous Voice: ON' : 'Continuous Voice: OFF'}</span>
          </button>

          <button
            onClick={handleClear}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all shadow-sm cursor-pointer"
            style={{ border: '1px solid rgba(239,68,68,0.2)', background: 'rgba(239,68,68,0.08)', color: '#EF4444' }}
          >
            <Trash2 className="w-3.5 h-3.5" /> Clear Session
          </button>
        </div>
      </div>


      {/* Suggested Questions Slider */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
        <span className="text-xs font-bold flex items-center gap-1 shrink-0 uppercase tracking-wider px-1" style={{ color: '#64748B' }}>
          <Sparkles className="w-3.5 h-3.5" style={{ color: '#F59E0B' }} /> Prompts:
        </span>
        {SUGGESTED_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            className="shrink-0 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer prompt-chip"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Message Container */}
      <div className="flex-1 glass-panel p-6 rounded-3xl overflow-y-auto space-y-5" style={{ border: '1px solid rgba(14,165,233,0.08)' }}>
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-3.5 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div
              className="w-9 h-9 rounded-2xl flex items-center justify-center shrink-0 shadow-md"
              style={m.role === 'user'
                ? { background: 'linear-gradient(135deg, #0EA5E9, #06B6D4)', color: '#ffffff' }
                : { background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(14,165,233,0.2)', color: '#0EA5E9' }
              }
            >
              {m.role === 'user' ? <User className="w-4 h-4" /> : <Brain className="w-4 h-4" />}
            </div>

            <div className="relative group max-w-[78%]">
              <div
                className="p-4 px-5 rounded-2xl text-xs sm:text-sm leading-relaxed whitespace-pre-wrap shadow-md font-medium"
                style={m.role === 'user'
                  ? { background: 'linear-gradient(135deg, #0EA5E9, #0284C7)', color: '#ffffff', borderBottomRightRadius: '6px', boxShadow: '0 4px 16px rgba(14,165,233,0.25)' }
                  : { background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderBottomLeftRadius: '6px' }
                }
              >
                {m.content}
              </div>

              {m.role === 'assistant' && m.content && (
                <button
                  type="button"
                  onClick={() => handleSpeakMessage(m.content, idx)}
                  className="mt-1 flex items-center gap-1 text-[11px] font-bold transition-all cursor-pointer hover:underline opacity-80 hover:opacity-100"
                  style={{ color: speakingIdx === idx ? '#EF4444' : '#06D6A0' }}
                  title={speakingIdx === idx ? 'Stop Speaking' : 'Read Aloud'}
                >
                  {speakingIdx === idx ? (
                    <>
                      <VolumeX className="w-3.5 h-3.5 animate-pulse" /> Stop Voice
                    </>
                  ) : (
                    <>
                      <Volume2 className="w-3.5 h-3.5" /> Listen Audio
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 text-xs font-semibold italic pl-2 text-sky-500">
            <div className="w-7 h-7 rounded-xl flex items-center justify-center animate-pulse" style={{ background: 'rgba(14,165,233,0.15)' }}>
              <Loader2 className="w-4 h-4 animate-spin" style={{ color: '#0EA5E9' }} />
            </div>
            <span>HealthGuard AI is analyzing & generating answer...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2 glass-panel p-2.5 px-3 rounded-2xl shadow-2xl"
        style={{ border: isListening ? '1px solid #06D6A0' : '1px solid var(--border-color)' }}
      >
        <button
          type="button"
          onClick={startVoiceInput}
          className="w-10 h-10 rounded-xl flex items-center justify-center transition-all cursor-pointer shrink-0"
          style={{
            background: isListening ? 'rgba(239,68,68,0.2)' : 'rgba(6,214,160,0.12)',
            border: `1px solid ${isListening ? '#EF4444' : 'rgba(6,214,160,0.3)'}`,
            color: isListening ? '#EF4444' : '#06D6A0',
          }}
          title={isListening ? 'Listening... Speak now!' : 'Hands-Free Voice Input (Click to Speak)'}
        >
          {isListening ? <MicOff className="w-4 h-4 animate-pulse" /> : <Mic className="w-4 h-4" />}
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={isListening ? '🎤 Listening... Speak your health query...' : 'Ask anything about symptoms, 1mg medicine prices, or AYUSH herbs...'}
          className="flex-1 bg-transparent border-none text-sm px-2 focus:outline-none font-medium text-slate-900 dark:text-slate-100"
        />

        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-primary px-5 py-2.5 rounded-xl text-xs font-extrabold flex items-center gap-2 disabled:opacity-40 cursor-pointer shrink-0"
        >
          <span>Send</span>
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
};

