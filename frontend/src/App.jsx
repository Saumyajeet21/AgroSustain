import { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom';
import { Leaf, Sprout, Stethoscope, BarChart3, MessageSquare, Sun, Moon, LogOut, Globe } from 'lucide-react';
import { supabase, signOut } from './supabase';
import { LanguageProvider, LANGUAGES, useLang } from './i18n';
import Landing       from './pages/Landing';
import CropPredictor from './pages/CropPredictor';
import PlantDoctor   from './pages/PlantDoctor';
import Economics     from './pages/Economics';
import Chatbot       from './pages/Chatbot';
import Auth          from './pages/Auth';
import './index.css';

/* ── Theme hook ──────────────────────────────────────────────────────── */
function useTheme() {
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem('agro-theme');
    return saved ? saved === 'dark' : true;
  });
  useEffect(() => {
    document.body.classList.toggle('light', !dark);
    localStorage.setItem('agro-theme', dark ? 'dark' : 'light');
  }, [dark]);
  return [dark, () => setDark(d => !d)];
}

/* ── Full-screen loader ──────────────────────────────────────────────── */
function AppLoader() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16 }}>
      <div style={{ width: 48, height: 48, borderRadius: 14, background: 'linear-gradient(135deg,var(--green-primary),var(--green-dark))', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 32px rgba(56,189,108,0.4)', animation: 'pulse-dot 1.4s ease-in-out infinite' }}>
        <Sprout size={24} color="#fff" />
      </div>
      <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Loading AgroSustain...</div>
    </div>
  );
}

/* ── Language selector dropdown ─────────────────────────────────────── */
function LangSelector() {
  const { lang, setLang } = useLang();
  const [open, setOpen]   = useState(false);
  const ref               = useRef(null);

  const current = LANGUAGES.find(l => l.code === lang) || LANGUAGES[0];

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button
        id="lang-selector"
        onClick={() => setOpen(o => !o)}
        style={{
          display: 'flex', alignItems: 'center', gap: 5,
          padding: '5px 10px', borderRadius: 8,
          background: open ? 'var(--bg-card-2)' : 'none',
          border: '1px solid ' + (open ? 'var(--border-bright)' : 'var(--border)'),
          cursor: 'pointer', color: 'var(--text-secondary)',
          fontSize: '0.78rem', fontWeight: 600,
          transition: 'all 0.2s ease',
        }}
        title="Change Language"
        onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--border-bright)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
        onMouseLeave={e => {
          if (!open) {
            e.currentTarget.style.borderColor = 'var(--border)';
            e.currentTarget.style.color = 'var(--text-secondary)';
          }
        }}
      >
        <Globe size={13} />
        <span>{current.flag}</span>
        <span>{current.short}</span>
      </button>

      {open && (
        <div style={{
          position: 'absolute', top: 'calc(100% + 8px)', right: 0, zIndex: 200,
          background: 'var(--bg-card)', border: '1px solid var(--border-bright)',
          borderRadius: 12, boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          minWidth: 160, overflow: 'hidden',
          animation: 'fade-up 0.18s ease both',
        }}>
          {LANGUAGES.map((l, i) => (
            <button
              key={l.code}
              onClick={() => { setLang(l.code); setOpen(false); }}
              style={{
                width: '100%', textAlign: 'left',
                padding: '9px 14px',
                display: 'flex', alignItems: 'center', gap: 9,
                background: lang === l.code ? 'rgba(56,189,108,0.1)' : 'none',
                border: 'none',
                borderBottom: i < LANGUAGES.length - 1 ? '1px solid var(--border)' : 'none',
                cursor: 'pointer',
                color: lang === l.code ? 'var(--green-primary)' : 'var(--text-secondary)',
                fontWeight: lang === l.code ? 700 : 400,
                fontSize: '0.84rem',
                transition: 'background 0.15s',
              }}
              onMouseEnter={e => { if (lang !== l.code) e.currentTarget.style.background = 'var(--bg-card-2)'; }}
              onMouseLeave={e => { if (lang !== l.code) e.currentTarget.style.background = 'none'; }}
              id={`lang-${l.code}`}
            >
              <span style={{ fontSize: '1.1rem' }}>{l.flag}</span>
              <span>{l.label}</span>
              {lang === l.code && <span style={{ marginLeft: 'auto', fontSize: '0.7rem', color: 'var(--green-primary)' }}>✓</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Navbar ──────────────────────────────────────────────────────────── */
function Navbar({ dark, toggleTheme, user, onLogout }) {
  const location   = useLocation();
  const isAuthPage = location.pathname === '/auth';
  const { t }      = useLang();

  const initials    = user?.user_metadata?.full_name
    ? user.user_metadata.full_name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
    : user?.email?.[0]?.toUpperCase() ?? '?';
  const displayName = user?.user_metadata?.full_name?.split(' ')[0] ?? user?.email?.split('@')[0] ?? '';

  return (
    <nav className="navbar">
      <NavLink to={user ? '/' : '/auth'} className="navbar-brand">
        <div className="brand-dot" />
        AgroSustain
      </NavLink>

      {!isAuthPage && user && (
        <ul className="navbar-links">
          {[
            { to: '/',          icon: <Leaf size={15} />,          label: t('home') },
            { to: '/predict',   icon: <Sprout size={15} />,        label: t('cropAdvisor') },
            { to: '/doctor',    icon: <Stethoscope size={15} />,   label: t('plantDoctor') },
            { to: '/economics', icon: <BarChart3 size={15} />,     label: t('economics') },
            { to: '/chat',      icon: <MessageSquare size={15} />, label: t('agroBot') },
          ].map(({ to, icon, label }) => (
            <li key={to}>
              <NavLink to={to} className={({ isActive }) => isActive ? 'active' : ''} end={to === '/'}>
                {icon} {label}
              </NavLink>
            </li>
          ))}
        </ul>
      )}

      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        {/* Language selector */}
        <LangSelector />

        {/* Theme toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <Moon size={13} />
          <button className="theme-toggle" onClick={toggleTheme} id="theme-toggle" title={dark ? 'Light Mode' : 'Dark Mode'} aria-label="Toggle theme">
            <div className="theme-toggle-thumb" />
          </button>
          <Sun size={13} />
        </div>

        {/* User pill */}
        {!isAuthPage && user && (
          <div className="user-pill" onClick={onLogout} title={t('signOut')} id="user-pill">
            <div className="user-avatar">{initials}</div>
            {displayName}
            <LogOut size={12} style={{ marginLeft: 2, opacity: 0.6 }} />
          </div>
        )}
      </div>
    </nav>
  );
}

/* ── Route guards ────────────────────────────────────────────────────── */
function RequireAuth({ user, loading, children }) {
  if (loading) return <AppLoader />;
  if (!user)   return <Navigate to="/auth" replace />;
  return children;
}
function PublicOnly({ user, loading, children }) {
  if (loading) return <AppLoader />;
  if (user)    return <Navigate to="/" replace />;
  return children;
}

/* ── App (inner — needs Router context for useLocation) ─────────────── */
function AppInner() {
  const [dark, toggleTheme] = useTheme();
  const [user, setUser]     = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setUser(data.session?.user ?? null);
      setLoading(false);
    });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      setLoading(false);
    });
    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => { await signOut(); setUser(null); };

  return (
    <>
      <div className="bg-orbs" />
      <Navbar dark={dark} toggleTheme={toggleTheme} user={user} onLogout={handleLogout} />
      <Routes>
        <Route path="/auth" element={<PublicOnly user={user} loading={loading}><Auth /></PublicOnly>} />
        <Route path="/"          element={<RequireAuth user={user} loading={loading}><Landing /></RequireAuth>} />
        <Route path="/predict"   element={<RequireAuth user={user} loading={loading}><CropPredictor /></RequireAuth>} />
        <Route path="/doctor"    element={<RequireAuth user={user} loading={loading}><PlantDoctor /></RequireAuth>} />
        <Route path="/economics" element={<RequireAuth user={user} loading={loading}><Economics /></RequireAuth>} />
        <Route path="/chat"      element={<RequireAuth user={user} loading={loading}><Chatbot /></RequireAuth>} />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <LanguageProvider>
        <AppInner />
      </LanguageProvider>
    </BrowserRouter>
  );
}
