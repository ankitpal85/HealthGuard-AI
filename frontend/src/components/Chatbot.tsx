import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Sparkles, Loader2, RefreshCw, Stethoscope, Brain } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    const userMsg: Message = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok || !res.body) throw new Error('Stream failed');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let assistantContent = '';
      setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const payload = line.slice(6);
            if (payload === '[DONE]') break;
            try {
              const data = JSON.parse(payload);
              if (data.token) {
                assistantContent += data.token;
                setMessages((prev) => {
                  const copy = [...prev];
                  copy[copy.length - 1] = { role: 'assistant', content: assistantContent };
                  return copy;
                });
              }
            } catch { /* skip malformed */ }
          }
        }
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '⚠️ Connection error. Please ensure the backend is running on port 8000.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const suggestions = [
    'Analyze my current vitals',
    'Suggest Ayurvedic remedies for stress',
    'Review my medication schedule',
    'What foods help lower blood pressure?',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-80px)]">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-5">
        {messages.length === 0 ? (
          /* Empty State — Clinical Welcome */
          <div className="flex flex-col items-center justify-center h-full text-center max-w-lg mx-auto">
            <div className="w-20 h-20 rounded-3xl flex items-center justify-center mb-6"
              style={{ background: 'linear-gradient(135deg, rgba(14,165,233,0.15), rgba(6,214,160,0.1))', border: '1px solid rgba(14,165,233,0.2)' }}>
              <Stethoscope className="w-10 h-10" style={{ color: '#0EA5E9' }} />
            </div>
            <h3 className="text-xl font-extrabold text-white mb-2" style={{ fontFamily: 'Plus Jakarta Sans, sans-serif' }}>
              Clinical AI Assistant
            </h3>
            <p className="text-sm font-medium mb-8" style={{ color: '#64748B' }}>
              Powered by advanced LLM + clinical tools. Ask about vitals, medications, nutrition, or Ayurvedic remedies.
            </p>

            <div className="grid grid-cols-2 gap-3 w-full">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => setInput(s)}
                  className="p-3.5 rounded-xl text-left text-[12px] font-semibold transition-all duration-200 group"
                  style={{
                    background: 'rgba(15,23,42,0.5)',
                    border: '1px solid rgba(14,165,233,0.1)',
                    color: '#94A3B8',
                  }}
                  onMouseEnter={(e) => {
                    (e.target as HTMLElement).style.borderColor = 'rgba(14,165,233,0.3)';
                    (e.target as HTMLElement).style.background = 'rgba(14,165,233,0.06)';
                    (e.target as HTMLElement).style.color = '#38BDF8';
                  }}
                  onMouseLeave={(e) => {
                    (e.target as HTMLElement).style.borderColor = 'rgba(14,165,233,0.1)';
                    (e.target as HTMLElement).style.background = 'rgba(15,23,42,0.5)';
                    (e.target as HTMLElement).style.color = '#94A3B8';
                  }}
                >
                  <Sparkles className="w-3.5 h-3.5 mb-1.5 inline-block mr-1" style={{ color: '#0EA5E9' }} />
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Messages */
          messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
                  style={{ background: 'rgba(14,165,233,0.12)', border: '1px solid rgba(14,165,233,0.2)' }}>
                  <Brain className="w-4.5 h-4.5" style={{ color: '#0EA5E9' }} />
                </div>
              )}
              <div className={`max-w-[70%] px-5 py-3.5 rounded-2xl text-[13px] font-medium leading-relaxed whitespace-pre-wrap`}
                style={msg.role === 'user'
                  ? { background: 'linear-gradient(135deg, #0EA5E9, #0284C7)', color: '#ffffff', borderBottomRightRadius: '6px' }
                  : { background: 'rgba(15,23,42,0.7)', border: '1px solid rgba(14,165,233,0.1)', color: '#E2E8F0', borderBottomLeftRadius: '6px' }
                }>
                {msg.content || (
                  <span className="flex items-center gap-2" style={{ color: '#64748B' }}>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" style={{ color: '#0EA5E9' }} />
                    Analyzing clinical data...
                  </span>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
                  style={{ background: 'linear-gradient(135deg, #0EA5E9, #06D6A0)' }}>
                  <User className="w-4.5 h-4.5 text-white" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="px-8 py-5" style={{ borderTop: '1px solid rgba(14,165,233,0.06)' }}>
        <div className="flex items-end gap-3 p-3 rounded-2xl"
          style={{ background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(14,165,233,0.12)' }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Describe symptoms, ask about medications, or request a health analysis..."
            rows={1}
            className="flex-1 bg-transparent text-[13px] font-medium resize-none focus:outline-none py-2 px-2 placeholder-[#64748B] text-white"
            style={{ maxHeight: '120px' }}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-all duration-200 btn-primary disabled:opacity-30 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <RefreshCw className="w-4 h-4 text-white animate-spin" />
            ) : (
              <Send className="w-4 h-4 text-white" />
            )}
          </button>
        </div>
        <p className="text-[10px] font-semibold mt-2 text-center" style={{ color: '#475569' }}>
          HealthGuard AI provides clinical decision support — not medical advice. Always consult a licensed physician.
        </p>
      </div>
    </div>
  );
};
