import React, { useEffect, useState, useRef } from 'react';
import { fetchChatHistory, sendChatMessage, clearChatHistory } from '../services/api';
import { Send, User, Trash2, Sparkles, Stethoscope, Brain, Loader2 } from 'lucide-react';

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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    fetchChatHistory(userId)
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

    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, message: text }),
      });

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
              return newMsgs;
            });
          }
        }
      }
    } catch (err) {
      console.error(err);
      const res = await sendChatMessage(userId, text);
      setMessages((prev) => {
        const newMsgs = [...prev];
        if (newMsgs.length > 0 && newMsgs[newMsgs.length - 1].role === 'assistant' && !newMsgs[newMsgs.length - 1].content) {
          newMsgs[newMsgs.length - 1] = res;
          return newMsgs;
        }
        return [...prev, res];
      });
    } finally {
      setLoading(false);
    }
  };


  const handleClear = async () => {
    await clearChatHistory(userId);
    setMessages([
      {
        role: 'assistant',
        content: "👋 Chat history cleared. How can I help you today?",
      },
    ]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-7.5rem)] space-y-4 animate-in fade-in duration-300">
      {/* Top Header Card */}
      <div className="flex items-center justify-between glass-panel p-4 px-6 rounded-2xl"
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
            <p className="text-xs font-medium" style={{ color: '#64748B' }}>LangGraph Stateful Pipeline • Multi-Provider Model</p>
          </div>
        </div>

        <button
          onClick={handleClear}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all shadow-sm"
          style={{ border: '1px solid rgba(239,68,68,0.2)', background: 'rgba(239,68,68,0.08)', color: '#EF4444' }}
        >
          <Trash2 className="w-3.5 h-3.5" /> Clear Session
        </button>
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
            className="shrink-0 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all"
            style={{ background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(14,165,233,0.1)', color: '#94A3B8' }}
            onMouseEnter={(e) => { (e.currentTarget).style.borderColor = 'rgba(14,165,233,0.35)'; (e.currentTarget).style.background = 'rgba(14,165,233,0.08)'; (e.currentTarget).style.color = '#38BDF8'; }}
            onMouseLeave={(e) => { (e.currentTarget).style.borderColor = 'rgba(14,165,233,0.1)'; (e.currentTarget).style.background = 'rgba(15,23,42,0.7)'; (e.currentTarget).style.color = '#94A3B8'; }}
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

            <div
              className="max-w-[78%] p-4 px-5 rounded-2xl text-xs sm:text-sm leading-relaxed whitespace-pre-wrap shadow-md"
              style={m.role === 'user'
                ? { background: 'linear-gradient(135deg, #0EA5E9, #0284C7)', color: '#ffffff', borderBottomRightRadius: '6px', boxShadow: '0 4px 16px rgba(14,165,233,0.2)' }
                : { background: 'rgba(15,23,42,0.8)', border: '1px solid rgba(14,165,233,0.08)', color: '#E2E8F0', borderBottomLeftRadius: '6px' }
              }
            >
              {m.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3 text-xs font-semibold italic pl-2" style={{ color: '#64748B' }}>
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
        className="flex items-center gap-3 glass-panel p-3 rounded-2xl shadow-2xl"
        style={{ border: '1px solid rgba(14,165,233,0.15)' }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about symptoms, 1mg medicine prices, or AYUSH herbs..."
          className="flex-1 bg-transparent border-none text-sm px-4 focus:outline-none font-medium"
          style={{ color: '#F8FAFC' }}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-primary px-5 py-3 rounded-xl text-xs font-extrabold flex items-center gap-2 disabled:opacity-40"
        >
          <span>Send</span>
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
};
