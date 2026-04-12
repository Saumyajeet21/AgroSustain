import { Link } from 'react-router-dom';
import { Sprout, Stethoscope, BarChart3, Zap, Globe, Brain, ChevronRight, Leaf } from 'lucide-react';

const features = [
  {
    icon: <Sprout size={22} />,
    color: '#38bd6c',
    bg: 'rgba(56,189,108,0.12)',
    title: 'Smart Crop Advisor',
    desc: 'AI-powered crop recommendations based on live weather, soil pH, and NPK data — fetched automatically from your GPS location.',
    link: '/predict',
    label: 'Get Recommendation',
  },
  {
    icon: <Stethoscope size={22} />,
    color: '#3b82f6',
    bg: 'rgba(59,130,246,0.12)',
    title: 'Plant Doctor',
    desc: 'Upload a photo of your crop. Our YOLOv8 + ResNet50 pipeline detects leaves, diagnoses diseases, and Gemini AI delivers a treatment plan.',
    link: '/doctor',
    label: 'Diagnose Now',
  },
  {
    icon: <BarChart3 size={22} />,
    color: '#f59e0b',
    bg: 'rgba(245,158,11,0.12)',
    title: 'Economic Dashboard',
    desc: 'Calculate projected yield, total investment, expected revenue, and ROI for any crop on your farm size.',
    link: '/economics',
    label: 'Calculate ROI',
  },
];

const techPills = [
  'XGBoost', 'ResNet50', 'YOLOv8', 'Google Gemini',
  'OpenWeatherMap', 'ISRIC SoilGrids', 'FastAPI', 'React',
];

const stats = [
  { value: '22+', label: 'Crops Supported', icon: '🌾' },
  { value: '38', label: 'Disease Classes', icon: '🔬' },
  { value: '98.9%', label: 'Crop Model Accuracy', icon: '🎯' },
  { value: '100%', label: 'Hardware-Free', icon: '📡' },
];

export default function Landing() {
  return (
    <div className="page-wrapper">
      {/* ── Hero ─────────────────────────────────────────────────── */}
      <section style={{ textAlign: 'center', padding: '5rem 1rem 3rem', maxWidth: 760, margin: '0 auto' }}>
        <div className="animate-in" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px', borderRadius: 999, background: 'rgba(56,189,108,0.1)', border: '1px solid rgba(56,189,108,0.25)', marginBottom: '1.5rem' }}>
          <Leaf size={14} color="var(--green-primary)" />
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--green-primary)', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
            AI-Driven Agriculture
          </span>
        </div>

        <h1 className="animate-in delay-1" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: 'clamp(2.2rem, 5vw, 3.5rem)', fontWeight: 900, lineHeight: 1.12, marginBottom: '1.2rem' }}>
          Farm Smarter with{' '}
          <span style={{ color: 'var(--green-primary)', position: 'relative' }}>
            AgroSustain
          </span>
        </h1>

        <p className="animate-in delay-2" style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: '2rem' }}>
          A hardware-free agricultural intelligence platform that fetches live climate and soil data from your GPS location,
          recommends the optimal crop, diagnoses plant diseases from photos, and projects your farm economics — all powered by AI.
        </p>

        <div className="animate-in delay-3" style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/predict" className="btn btn-primary" style={{ fontSize: '1rem', padding: '12px 28px' }}>
            <Zap size={18} /> Start Growing
          </Link>
          <Link to="/doctor" className="btn btn-secondary" style={{ fontSize: '1rem', padding: '12px 28px' }}>
            <Stethoscope size={18} /> Plant Doctor
          </Link>
        </div>
      </section>

      {/* ── Stats ────────────────────────────────────────────────── */}
      <section className="animate-in delay-4" style={{ marginBottom: '3.5rem' }}>
        <div className="grid-4">
          {stats.map((s, i) => (
            <div key={i} className="card stat-card" style={{ textAlign: 'center', alignItems: 'center' }}>
              <div style={{ fontSize: '2rem' }}>{s.icon}</div>
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Feature Cards ─────────────────────────────────────────── */}
      <section style={{ marginBottom: '3.5rem' }}>
        <h2 className="section-title" style={{ textAlign: 'center' }}>
          Everything your farm <span>needs</span>
        </h2>
        <div className="grid-3">
          {features.map((f, i) => (
            <div key={i} className="card" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', gap: '1rem', animationDelay: `${i * 0.1}s` }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: f.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', color: f.color }}>
                {f.icon}
              </div>
              <div>
                <h3 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '1.05rem', fontWeight: 700, marginBottom: 6 }}>{f.title}</h3>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.65 }}>{f.desc}</p>
              </div>
              <Link to={f.link} className="btn btn-secondary" style={{ marginTop: 'auto', fontSize: '0.85rem' }}>
                {f.label} <ChevronRight size={14} />
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works ──────────────────────────────────────────── */}
      <section className="card" style={{ padding: '2.5rem', marginBottom: '3.5rem' }}>
        <h2 className="section-title" style={{ textAlign: 'center' }}>
          How It <span>Works</span>
        </h2>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start', flexWrap: 'wrap', justifyContent: 'center' }}>
          {[
            { n: '01', icon: <Globe size={20} />, title: 'Share Location', desc: 'One click auto-fetches live temperature, humidity, rainfall & soil pH from satellites.' },
            { n: '02', icon: <Brain size={20} />, title: 'AI Analyzes', desc: 'XGBoost processes your environment data to find the optimal crop for your conditions.' },
            { n: '03', icon: <Sprout size={20} />, title: 'Get Insights', desc: 'Receive crop recommendation, disease diagnosis, and full financial projections instantly.' },
          ].map((step, i) => (
            <div key={i} style={{ flex: '1 1 200px', textAlign: 'center', padding: '1rem' }}>
              <div style={{ width: 52, height: 52, borderRadius: '50%', background: 'var(--green-glow)', border: '2px solid var(--border-bright)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem', color: 'var(--green-primary)' }}>
                {step.icon}
              </div>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.1em', marginBottom: 6 }}>STEP {step.n}</div>
              <h4 style={{ fontWeight: 700, marginBottom: 6 }}>{step.title}</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Tech Stack ────────────────────────────────────────────── */}
      <section style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '1rem' }}>
          Powered By
        </p>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center' }}>
          {techPills.map(t => (
            <span key={t} className="badge badge-green" style={{ fontSize: '0.78rem', padding: '6px 14px' }}>{t}</span>
          ))}
        </div>
      </section>
    </div>
  );
}
