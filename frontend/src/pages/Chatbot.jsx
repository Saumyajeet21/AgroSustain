import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sprout, RefreshCw } from 'lucide-react';
import { sendChatMessage } from '../api';

const SESSION_ID = `agro_${Date.now()}`;

const SUGGESTED = [
  "What's the best crop to grow in black soil?",
  "How do I treat tomato late blight?",
  "When should I apply urea fertilizer?",
  "What causes yellow leaves in rice?",
  "How to improve soil pH naturally?",
  "What pests attack wheat crops?",
];

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '12px 16px', background: 'var(--bg-card-2)', borderRadius: '16px 16px 16px 4px', width: 'fit-content', border: '1px solid var(--border)' }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--green-primary)', opacity: 0.7, animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite` }} />
      ))}
      <style>{`@keyframes bounce { 0%,80%,100%{transform:translateY(0)} 40%{transform:translateY(-6px)} }`}</style>
    </div>
  );
}

function ChatMessage({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div style={{ display: 'flex', flexDirection: isUser ? 'row-reverse' : 'row', gap: 10, alignItems: 'flex-end' }}>
      {/* Avatar */}
      <div style={{ width: 32, height: 32, borderRadius: '50%', flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: isUser ? 'rgba(59,130,246,0.2)' : 'rgba(56,189,108,0.15)', border: `1px solid ${isUser ? 'rgba(59,130,246,0.3)' : 'rgba(56,189,108,0.3)'}` }}>
        {isUser ? <User size={14} color="var(--accent-blue)" /> : <Bot size={14} color="var(--green-primary)" />}
      </div>
      {/* Bubble */}
      <div style={{
        maxWidth: '78%', padding: '12px 16px',
        borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
        background: isUser ? 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(59,130,246,0.1))' : 'var(--bg-card-2)',
        border: `1px solid ${isUser ? 'rgba(59,130,246,0.25)' : 'var(--border)'}`,
        fontSize: '0.875rem', lineHeight: 1.65, color: 'var(--text-primary)',
        whiteSpace: 'pre-wrap',
        animation: 'fade-up 0.3s ease',
      }}>
        {msg.text}
        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 6, textAlign: isUser ? 'left' : 'right' }}>
          {new Date(msg.ts).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: "Namaste! I'm **AgroBot**, your AI agricultural advisor 🌱\n\nAsk me anything about crops, soil, plant diseases, fertilizers, or farming techniques. I'm here to help you grow smarter!", ts: Date.now() }
  ]);
  const [input, setInput]   = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]); // Gemini format history
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text) => {
    const msg = text || input.trim();
    if (!msg || loading) return;
    setInput('');

    // Add user message
    const userMsg = { role: 'user', text: msg, ts: Date.now() };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const { data } = await sendChatMessage(msg, SESSION_ID, history);

      // Update Gemini history for multi-turn
      const newHistory = [
        ...history,
        { role: 'user',  parts: [{ text: msg }] },
        { role: 'model', parts: [{ text: data.reply }] },
      ];
      setHistory(newHistory);

      setMessages(prev => [...prev, { role: 'assistant', text: data.reply, ts: Date.now() }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: "Sorry, I'm having trouble connecting to the server. Please check that the backend is running.",
        ts: Date.now(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setMessages([{ role: 'assistant', text: "Namaste! I'm **AgroBot**, your AI agricultural advisor 🌱\n\nAsk me anything about crops, soil, plant diseases, fertilizers, or farming techniques.", ts: Date.now() }]);
    setHistory([]);
  };

  return (
    <div className="page-wrapper" style={{ maxWidth: 860, margin: '0 auto' }}>
      <div className="animate-in" style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 className="section-title" style={{ marginBottom: '0.25rem' }}>
            Agro<span>Bot</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Your AI-powered agricultural advisor — ask anything about farming
          </p>
        </div>
        <button className="btn btn-secondary" onClick={reset} style={{ gap: 6, fontSize: '0.8rem' }} id="reset-chat-btn">
          <RefreshCw size={13} /> New Chat
        </button>
      </div>

      {/* Chat window */}
      <div className="card animate-in delay-1" style={{ display: 'flex', flexDirection: 'column', height: 520 }}>
        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {messages.map((msg, i) => <ChatMessage key={i} msg={msg} />)}
          {loading && (
            <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(56,189,108,0.15)', border: '1px solid rgba(56,189,108,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={14} color="var(--green-primary)" />
              </div>
              <TypingIndicator />
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input bar */}
        <div style={{ padding: '1rem 1.25rem', borderTop: '1px solid var(--border)', display: 'flex', gap: 10 }}>
          <input
            id="chat-input"
            type="text"
            className="form-input"
            style={{ flex: 1 }}
            placeholder="Ask about crops, diseases, soil, fertilizers..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
            disabled={loading}
          />
          <button
            id="chat-send-btn"
            className="btn btn-primary"
            onClick={() => send()}
            disabled={loading || !input.trim()}
            style={{ padding: '10px 18px' }}
          >
            {loading ? <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> : <Send size={16} />}
          </button>
        </div>
      </div>

      {/* Suggested questions */}
      <div className="animate-in delay-2" style={{ marginTop: '1.25rem' }}>
        <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.6rem' }}>
          Suggested Questions
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {SUGGESTED.map((q, i) => (
            <button
              key={i}
              className="btn btn-secondary"
              style={{ fontSize: '0.78rem', padding: '6px 14px', borderRadius: 999 }}
              onClick={() => send(q)}
              disabled={loading}
            >
              <Sprout size={12} /> {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
