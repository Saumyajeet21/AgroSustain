import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Eye, EyeOff, ArrowRight, Sprout } from 'lucide-react';
import { signIn, signUp } from '../supabase';
import { useLang } from '../i18n';

/* ─────────────────────────────────────────────────────────────────────────
   Animated background: morphing gradient blobs + drifting dots
───────────────────────────────────────────────────────────────────────── */
const DOTS = Array.from({ length: 22 }, (_, i) => ({
  id: i,
  size:    Math.random() * 5 + 2,
  left:    Math.random() * 100,
  delay:   Math.random() * 10,
  dur:     Math.random() * 8 + 8,
  opacity: Math.random() * 0.45 + 0.1,
}));

function AnimatedBackground() {
  return (
    <>
      {/* Morphing blobs */}
      <div style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', overflow: 'hidden' }}>
        <div className="auth-blob auth-blob-1" />
        <div className="auth-blob auth-blob-2" />
        <div className="auth-blob auth-blob-3" />

        {/* Rising dots */}
        {DOTS.map(d => (
          <div
            key={d.id}
            className="particle"
            style={{
              width: d.size, height: d.size,
              left: `${d.left}%`, bottom: -20,
              opacity: d.opacity,
              animationDuration: `${d.dur}s`,
              animationDelay: `${d.delay}s`,
            }}
          />
        ))}
      </div>
    </>
  );
}

/* ─────────────────────────────────────────────────────────────────────────
   Glowing ring that animates around the card
───────────────────────────────────────────────────────────────────────── */
function GlowRing() {
  return (
    <div
      style={{
        position: 'absolute',
        inset: -2,
        borderRadius: 'calc(var(--radius-xl) + 2px)',
        background: 'linear-gradient(135deg, rgba(56,189,108,0.5), rgba(59,130,246,0.2), rgba(56,189,108,0.1), rgba(139,92,246,0.2), rgba(56,189,108,0.5))',
        backgroundSize: '300% 300%',
        animation: 'ring-spin 4s linear infinite',
        zIndex: -1,
        filter: 'blur(3px)',
      }}
    />
  );
}

/* ─────────────────────────────────────────────────────────────────────────
   Input with animated focus glow
───────────────────────────────────────────────────────────────────────── */
function AuthInput({ id, icon, label, type = 'text', value, onChange, placeholder, rightIcon, onRightClick, delay = 0 }) {
  const [focused, setFocused] = useState(false);
  return (
    <div
      className="form-group animate-in"
      style={{ animationDelay: `${delay}s` }}
    >
      <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
        <span style={{ color: focused ? 'var(--green-primary)' : 'var(--text-secondary)', transition: 'color 0.2s' }}>
          {icon}
        </span>
        {label}
      </label>
      <div style={{ position: 'relative' }}>
        <input
          id={id}
          type={type}
          className="form-input"
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          style={{
            paddingRight: rightIcon ? '2.5rem' : '1rem',
            width: '100%',
            transform: focused ? 'scale(1.01)' : 'scale(1)',
            transition: 'transform 0.2s ease, border-color 0.2s, box-shadow 0.2s',
          }}
          autoComplete="off"
        />
        {rightIcon && (
          <button
            type="button"
            onClick={onRightClick}
            style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 2, display: 'flex', transition: 'color 0.2s' }}
            onMouseEnter={e => e.currentTarget.style.color = 'var(--green-primary)'}
            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
          >
            {rightIcon}
          </button>
        )}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────
   Main Auth page
───────────────────────────────────────────────────────────────────────── */
export default function Auth() {
  const [tab, setTab]           = useState('login');
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const [success, setSuccess]   = useState('');
  const [showPass, setShowPass] = useState(false);
  const navigate                = useNavigate();
  const { t }                   = useLang();

  const [loginEmail, setLoginEmail] = useState('');
  const [loginPass,  setLoginPass]  = useState('');
  const [signupName,  setSignupName]  = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPass,  setSignupPass]  = useState('');
  const [signupConf,  setSignupConf]  = useState('');

  const switchTab = (t) => { setTab(t); setError(''); setSuccess(''); };

  /* ── Login ──────────────────────────────────────────────────────────── */
  const handleLogin = async (e) => {
    e.preventDefault();
    if (!loginEmail || !loginPass) { setError(t('fillAll')); return; }
    setLoading(true); setError('');
    const { error: err } = await signIn(loginEmail, loginPass);
    if (err) { setError(err.message); setLoading(false); }
    else     { setSuccess(t('welcome')); setTimeout(() => navigate('/'), 900); }
  };

  /* ── Sign up ────────────────────────────────────────────────────────── */
  const handleSignup = async (e) => {
    e.preventDefault();
    if (!signupName || !signupEmail || !signupPass || !signupConf) { setError(t('fillAll')); return; }
    if (signupPass !== signupConf) { setError(t('passNoMatch')); return; }
    if (signupPass.length < 6)    { setError(t('passShort')); return; }
    setLoading(true); setError('');
    const { error: err } = await signUp(signupEmail, signupPass, signupName);
    if (err) { setError(err.message); setLoading(false); }
    else {
      setSuccess(t('acctCreated'));
      setLoading(false);
      setTimeout(() => switchTab('login'), 2000);
    }
  };

  /* ── Password strength ──────────────────────────────────────────────── */
  const strength = (() => {
    const p = signupPass;
    if (!p) return 0;
    let s = 0;
    if (p.length >= 6) s++;
    if (p.length >= 10) s++;
    if (/[A-Z]/.test(p)) s++;
    if (/[0-9]/.test(p)) s++;
    if (/[^a-zA-Z0-9]/.test(p)) s++;
    return s;
  })();
  const strengthLabel = ['', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'][strength];
  const strengthColor = ['', '#ef4444', '#f59e0b', '#eab308', '#38bd6c', '#22c55e'][strength];

  return (
    <>
      {/* Inject animation keyframes */}
      <style>{`
        @keyframes blob-morph-1 {
          0%,100% { border-radius: 60% 40% 70% 30% / 50% 60% 40% 50%; transform: translateY(0) scale(1); }
          33%      { border-radius: 40% 60% 30% 70% / 60% 40% 60% 40%; transform: translateY(-30px) scale(1.05); }
          66%      { border-radius: 70% 30% 50% 50% / 40% 70% 30% 60%; transform: translateY(20px) scale(0.97); }
        }
        @keyframes blob-morph-2 {
          0%,100% { border-radius: 40% 60% 50% 50% / 60% 40% 60% 40%; transform: translateY(0) scale(1); }
          33%      { border-radius: 70% 30% 60% 40% / 40% 60% 40% 60%; transform: translateY(25px) scale(1.08); }
          66%      { border-radius: 30% 70% 40% 60% / 60% 30% 70% 40%; transform: translateY(-20px) scale(0.95); }
        }
        @keyframes blob-morph-3 {
          0%,100% { border-radius: 50% 50% 40% 60% / 40% 60% 50% 50%; transform: scale(1); }
          50%      { border-radius: 30% 70% 60% 40% / 60% 30% 50% 50%; transform: scale(1.1) rotate(10deg); }
        }
        @keyframes ring-spin {
          0%   { background-position: 0% 50%; }
          50%  { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes logo-breathe {
          0%,100% { box-shadow: 0 8px 32px rgba(56,189,108,0.4), 0 0 0 0 rgba(56,189,108,0.2); }
          50%      { box-shadow: 0 12px 48px rgba(56,189,108,0.6), 0 0 0 12px rgba(56,189,108,0.06); }
        }

        .auth-blob { position: absolute; filter: blur(72px); opacity: 0.55; }
        .auth-blob-1 {
          width: 480px; height: 480px;
          top: -120px; left: -120px;
          background: radial-gradient(circle, rgba(56,189,108,0.35) 0%, transparent 70%);
          animation: blob-morph-1 12s ease-in-out infinite;
        }
        .auth-blob-2 {
          width: 400px; height: 400px;
          bottom: -100px; right: -100px;
          background: radial-gradient(circle, rgba(59,130,246,0.25) 0%, transparent 70%);
          animation: blob-morph-2 15s ease-in-out infinite;
        }
        .auth-blob-3 {
          width: 300px; height: 300px;
          top: 40%; left: 55%;
          background: radial-gradient(circle, rgba(139,92,246,0.18) 0%, transparent 70%);
          animation: blob-morph-3 10s ease-in-out infinite;
        }

        .auth-logo-icon {
          animation: logo-breathe 3s ease-in-out infinite;
        }

        .auth-tab.active {
          background: var(--bg-card);
          color: var(--green-primary);
          box-shadow: 0 2px 16px rgba(0,0,0,0.25), 0 0 0 1px rgba(56,189,108,0.2);
        }

        .auth-submit-btn {
          position: relative; overflow: hidden;
        }
        .auth-submit-btn::after {
          content: '';
          position: absolute; inset: 0;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
          transform: translateX(-100%);
          transition: transform 0.4s ease;
        }
        .auth-submit-btn:hover::after { transform: translateX(100%); }

        .tab-content { animation: fade-up 0.3s ease both; }
      `}</style>

      <AnimatedBackground />

      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem', position: 'relative', zIndex: 1 }}>

        {/* Glow ring wrapper */}
        <div style={{ position: 'relative', width: '100%', maxWidth: 440 }}>
          <GlowRing />

          {/* Card */}
          <div className="auth-card scale-in" style={{ position: 'relative', zIndex: 1 }}>

            {/* Logo */}
            <div style={{ textAlign: 'center', marginBottom: '1.75rem' }} className="animate-in">
              <div
                className="auth-logo-icon"
                style={{
                  display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                  width: 64, height: 64, borderRadius: 20,
                  background: 'linear-gradient(135deg, var(--green-primary), var(--green-dark))',
                  marginBottom: '1rem',
                }}
              >
                <Sprout size={30} color="#fff" />
              </div>
              <h1 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '1.7rem', fontWeight: 900, marginBottom: 6, letterSpacing: '-0.02em' }}>
                Agro<span style={{ color: 'var(--green-primary)' }}>Sustain</span>
              </h1>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                {tab === 'login' ? t('dashboardSub') : t('growSub')}
              </p>
            </div>

            {/* Tab switcher */}
            <div className="auth-tab-bar animate-in delay-1">
              <button className={`auth-tab${tab === 'login' ? ' active' : ''}`} onClick={() => switchTab('login')} id="login-tab">{t('signInLabel')}</button>
              <button className={`auth-tab${tab === 'signup' ? ' active' : ''}`} onClick={() => switchTab('signup')} id="signup-tab">{t('signUpLabel')}</button>
            </div>

            {/* ── LOGIN FORM ─────────────────────────────────────────── */}
            {tab === 'login' && (
              <form key="login" onSubmit={handleLogin} className="tab-content" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <AuthInput id="login-email" icon={<Mail size={13} />} label={t('emailAddr')}
                  type="email" value={loginEmail} onChange={e => setLoginEmail(e.target.value)}
                  placeholder="you@example.com" delay={0.05} />
                <AuthInput id="login-password" icon={<Lock size={13} />} label={t('password')}
                  type={showPass ? 'text' : 'password'} value={loginPass} onChange={e => setLoginPass(e.target.value)}
                  placeholder="••••••••" delay={0.1}
                  rightIcon={showPass ? <EyeOff size={14} /> : <Eye size={14} />}
                  onRightClick={() => setShowPass(p => !p)} />

                {error   && <div className="animate-in" style={{ padding: '10px 14px', borderRadius: 8, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5', fontSize: '0.84rem' }}>{error}</div>}
                {success && <div className="animate-in" style={{ padding: '10px 14px', borderRadius: 8, background: 'rgba(56,189,108,0.1)', border: '1px solid rgba(56,189,108,0.3)', color: 'var(--green-light)', fontSize: '0.84rem' }}>{success}</div>}

                <button
                  type="submit"
                  className="btn btn-primary auth-submit-btn animate-in"
                  style={{ width: '100%', justifyContent: 'center', padding: '14px', fontSize: '0.95rem', marginTop: '0.25rem', animationDelay: '0.15s', borderRadius: 12 }}
                  disabled={loading}
                  id="login-submit"
                >
                  {loading ? <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> {t('signingIn')}</> : <>{t('signInLabel')} <ArrowRight size={16} /></>}
                </button>
              </form>
            )}

            {/* ── SIGNUP FORM ────────────────────────────────────────── */}
            {tab === 'signup' && (
              <form key="signup" onSubmit={handleSignup} className="tab-content" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <AuthInput id="signup-name" icon={<User size={13} />} label={t('fullName')}
                  value={signupName} onChange={e => setSignupName(e.target.value)}
                  placeholder="Your full name" delay={0.05} />
                <AuthInput id="signup-email" icon={<Mail size={13} />} label={t('emailAddr')}
                  type="email" value={signupEmail} onChange={e => setSignupEmail(e.target.value)}
                  placeholder="you@example.com" delay={0.1} />
                <AuthInput id="signup-password" icon={<Lock size={13} />} label={t('password')}
                  type={showPass ? 'text' : 'password'} value={signupPass} onChange={e => setSignupPass(e.target.value)}
                  placeholder="Min. 6 characters" delay={0.15}
                  rightIcon={showPass ? <EyeOff size={14} /> : <Eye size={14} />}
                  onRightClick={() => setShowPass(p => !p)} />

                {/* Password strength */}
                {signupPass && (
                  <div className="animate-in" style={{ marginTop: -6 }}>
                    <div style={{ display: 'flex', gap: 4, marginBottom: 4 }}>
                      {[1,2,3,4,5].map(n => (
                        <div key={n} style={{ flex: 1, height: 3, borderRadius: 2, background: n <= strength ? strengthColor : 'var(--bg-card-2)', transition: 'background 0.3s ease' }} />
                      ))}
                    </div>
                    <span style={{ fontSize: '0.72rem', color: strengthColor, fontWeight: 600 }}>{strengthLabel}</span>
                  </div>
                )}

                <AuthInput id="signup-confirm" icon={<Lock size={13} />} label={t('confirmPass')}
                  type={showPass ? 'text' : 'password'} value={signupConf} onChange={e => setSignupConf(e.target.value)}
                  placeholder="Re-enter password" delay={0.2} />

                {error   && <div className="animate-in" style={{ padding: '10px 14px', borderRadius: 8, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5', fontSize: '0.84rem' }}>{error}</div>}
                {success && <div className="animate-in" style={{ padding: '10px 14px', borderRadius: 8, background: 'rgba(56,189,108,0.1)', border: '1px solid rgba(56,189,108,0.3)', color: 'var(--green-light)', fontSize: '0.84rem' }}>{success}</div>}

                <button
                  type="submit"
                  className="btn btn-primary auth-submit-btn animate-in"
                  style={{ width: '100%', justifyContent: 'center', padding: '14px', fontSize: '0.95rem', marginTop: '0.25rem', animationDelay: '0.25s', borderRadius: 12 }}
                  disabled={loading}
                  id="signup-submit"
                >
                  {loading ? <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> {t('creating')}</> : <>{t('createAcct')} <ArrowRight size={16} /></>}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
