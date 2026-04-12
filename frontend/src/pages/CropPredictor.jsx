import { useState } from 'react';
import { MapPin, Zap, Loader, ChevronRight, Leaf, Droplets, Thermometer, Wind, FlaskConical, CloudRain } from 'lucide-react';
import { predictCrop, calculateEconomics } from '../api';

const CROP_EMOJIS = {
  rice:'🌾', maize:'🌽', chickpea:'🫘', kidneybeans:'🫘', pigeonpeas:'🌿', mothbeans:'🌿',
  mungbean:'🌿', blackgram:'🌿', lentil:'🌿', pomegranate:'🍎', banana:'🍌', mango:'🥭',
  grapes:'🍇', watermelon:'🍉', muskmelon:'🍈', apple:'🍎', orange:'🍊', papaya:'🥭',
  coconut:'🥥', cotton:'🪡', jute:'🌿', coffee:'☕',
};

const defaultInputs = { N: '', P: '', K: '', temperature: '', humidity: '', ph: '', rainfall: '' };

const inputFields = [
  { key: 'N',           label: 'Nitrogen (N)',     unit: 'kg/ha', icon: <FlaskConical size={14} />,  placeholder: 'e.g. 90' },
  { key: 'P',           label: 'Phosphorus (P)',   unit: 'kg/ha', icon: <FlaskConical size={14} />,  placeholder: 'e.g. 42' },
  { key: 'K',           label: 'Potassium (K)',    unit: 'kg/ha', icon: <FlaskConical size={14} />,  placeholder: 'e.g. 43' },
  { key: 'temperature', label: 'Temperature',      unit: '°C',    icon: <Thermometer size={14} />,   placeholder: 'e.g. 25' },
  { key: 'humidity',    label: 'Humidity',         unit: '%',     icon: <Droplets size={14} />,      placeholder: 'e.g. 80' },
  { key: 'ph',          label: 'Soil pH',          unit: '0–14',  icon: <FlaskConical size={14} />,  placeholder: 'e.g. 6.5' },
  { key: 'rainfall',    label: 'Annual Rainfall',  unit: 'mm',    icon: <CloudRain size={14} />,     placeholder: 'e.g. 200' },
];

export default function CropPredictor() {
  const [inputs, setInputs]         = useState(defaultInputs);
  const [loadingGeo, setLoadingGeo] = useState(false);
  const [loadingPred, setLoadingPred] = useState(false);
  const [result, setResult]         = useState(null);
  const [econ, setEcon]             = useState(null);
  const [farmArea, setFarmArea]     = useState(1);
  const [error, setError]           = useState('');
  const [fetched, setFetched]       = useState(false);

  const handleInput = (key, val) => setInputs(p => ({ ...p, [key]: val }));

  /* ── Auto-fetch from GPS ─────────────────────────────────────── */
  const autoFetch = () => {
    if (!navigator.geolocation) { setError('Geolocation not supported'); return; }
    setLoadingGeo(true); setError('');
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        try {
          const { data } = await predictCrop({ lat: coords.latitude, lon: coords.longitude });
          setInputs({
            N: data.inputs_used.N, P: data.inputs_used.P, K: data.inputs_used.K,
            temperature: data.inputs_used.temperature, humidity: data.inputs_used.humidity,
            ph: data.inputs_used.ph, rainfall: data.inputs_used.rainfall,
          });
          setResult(data);
          setFetched(true);
          fetchEcon(data.crop, farmArea);
        } catch (e) { setError(e.response?.data?.detail || 'Auto-fetch failed'); }
        finally { setLoadingGeo(false); }
      },
      () => { setError('Location access denied'); setLoadingGeo(false); }
    );
  };

  /* ── Manual predict ──────────────────────────────────────────── */
  const predict = async () => {
    const allFilled = Object.values(inputs).every(v => v !== '');
    if (!allFilled) { setError('Please fill all fields or use Auto-Fetch'); return; }
    setLoadingPred(true); setError('');
    try {
      const payload = { lat: 28.6, lon: 77.2, ...Object.fromEntries(Object.entries(inputs).map(([k,v]) => [k, parseFloat(v)])) };
      const { data } = await predictCrop(payload);
      setResult(data);
      fetchEcon(data.crop, farmArea);
    } catch (e) { setError(e.response?.data?.detail || 'Prediction failed'); }
    finally { setLoadingPred(false); }
  };

  const fetchEcon = async (crop, area) => {
    try {
      const { data } = await calculateEconomics(crop, parseFloat(area));
      setEcon(data);
    } catch { /* silent */ }
  };

  const loading = loadingGeo || loadingPred;

  return (
    <div className="page-wrapper">
      <div className="animate-in" style={{ marginBottom: '2rem' }}>
        <h1 className="section-title">Crop <span>Advisor</span></h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Auto-fetch live weather & soil data, or enter values manually to get an AI crop recommendation.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* ── Input Panel ─────────────────────────────────────── */}
        <div className="card animate-in delay-1" style={{ padding: '1.75rem' }}>
          {/* Auto-fetch button */}
          <button
            className="btn btn-primary"
            onClick={autoFetch}
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', marginBottom: '1.5rem', fontSize: '0.95rem', padding: '12px' }}
            id="auto-fetch-btn"
          >
            {loadingGeo ? <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Fetching Location...</> : <><MapPin size={16} /> Auto-Fetch from GPS</>}
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.25rem' }}>
            <div className="divider" style={{ flex: 1, margin: 0 }} />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>or enter manually</span>
            <div className="divider" style={{ flex: 1, margin: 0 }} />
          </div>

          <div className="grid-2" style={{ gap: '1rem', marginBottom: '1.25rem' }}>
            {inputFields.map(field => (
              <div key={field.key} className="form-group">
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  {field.icon} {field.label}
                  <span style={{ color: 'var(--text-muted)', fontWeight: 400, marginLeft: 'auto' }}>{field.unit}</span>
                </label>
                <input
                  id={`input-${field.key}`}
                  type="number"
                  className="form-input"
                  placeholder={field.placeholder}
                  value={inputs[field.key]}
                  onChange={e => handleInput(field.key, e.target.value)}
                />
              </div>
            ))}
          </div>

          {error && (
            <div style={{ padding: '10px 14px', borderRadius: 8, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5', fontSize: '0.85rem', marginBottom: '1rem' }}>
              {error}
            </div>
          )}

          <button
            className="btn btn-primary"
            onClick={predict}
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', fontSize: '0.95rem', padding: '12px' }}
            id="predict-btn"
          >
            {loadingPred ? <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Analyzing...</> : <><Zap size={16} /> Get AI Recommendation</>}
          </button>
        </div>

        {/* ── Result Panel ─────────────────────────────────────── */}
        {result && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Main crop result */}
            <div className="card animate-in" style={{ padding: '2rem', textAlign: 'center' }}>
              <div style={{ fontSize: '5rem', marginBottom: '0.5rem' }}>
                {CROP_EMOJIS[result.crop] || '🌱'}
              </div>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 6 }}>
                Best Crop for Your Land
              </div>
              <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: '2rem', fontWeight: 900, textTransform: 'capitalize', marginBottom: '0.5rem', color: 'var(--green-primary)' }}>
                {result.crop}
              </h2>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginBottom: '1.25rem' }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Confidence</span>
                <span className="badge badge-green" style={{ fontSize: '0.85rem' }}>{result.confidence}%</span>
              </div>

              {/* Confidence bar */}
              <div className="progress-bar" style={{ marginBottom: '1.25rem' }}>
                <div className="progress-fill" style={{ width: `${result.confidence}%` }} />
              </div>

              {/* Top 3 */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', textAlign: 'left' }}>
                  Other Options
                </div>
                {result.top3?.slice(1).map((c, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px', background: 'var(--bg-card-2)', borderRadius: 8 }}>
                    <span>{CROP_EMOJIS[c.crop] || '🌱'}</span>
                    <span style={{ flex: 1, textTransform: 'capitalize', fontSize: '0.875rem' }}>{c.crop}</span>
                    <span className="badge badge-blue">{c.confidence}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Live conditions used */}
            {result.location && (
              <div className="card" style={{ padding: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: '0.75rem' }}>
                  <MapPin size={14} color="var(--green-primary)" />
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Live data from: {result.location}
                  </span>
                </div>
                <div className="grid-3" style={{ gap: '0.6rem' }}>
                  {[
                    { label: 'Temp', value: `${result.inputs_used?.temperature}°C`, icon: '🌡️' },
                    { label: 'Humidity', value: `${result.inputs_used?.humidity}%`, icon: '💧' },
                    { label: 'pH', value: result.inputs_used?.ph, icon: '🧪' },
                  ].map((m, i) => (
                    <div key={i} style={{ textAlign: 'center', padding: '0.6rem', background: 'var(--bg-card-2)', borderRadius: 8 }}>
                      <div style={{ fontSize: '1.2rem' }}>{m.icon}</div>
                      <div style={{ fontSize: '0.8rem', fontWeight: 700 }}>{m.value}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{m.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Farm area + quick econ */}
            <div className="card" style={{ padding: '1.25rem' }}>
              <div className="form-group" style={{ marginBottom: '0.75rem' }}>
                <label className="form-label">Farm Area (hectares)</label>
                <input
                  id="farm-area-input"
                  type="number" min="0.1" step="0.1"
                  className="form-input"
                  value={farmArea}
                  onChange={e => { setFarmArea(e.target.value); if (result) fetchEcon(result.crop, e.target.value); }}
                />
              </div>
              {econ && (
                <div className="grid-2" style={{ gap: '0.6rem' }}>
                  {[
                    { label: 'Yield', value: `${econ.total_yield_tons} tons`, color: 'var(--green-primary)' },
                    { label: 'Revenue', value: `₹${econ.total_revenue_inr.toLocaleString()}`, color: 'var(--accent-amber)' },
                    { label: 'Investment', value: `₹${econ.total_investment_inr.toLocaleString()}`, color: 'var(--accent-red)' },
                    { label: 'ROI', value: `${econ.roi_pct}%`, color: 'var(--accent-blue)' },
                  ].map((m, i) => (
                    <div key={i} style={{ padding: '0.75rem', background: 'var(--bg-card-2)', borderRadius: 8 }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: 2 }}>{m.label}</div>
                      <div style={{ fontWeight: 700, color: m.color, fontSize: '0.95rem' }}>{m.value}</div>
                    </div>
                  ))}
                </div>
              )}
              <button
                className="btn btn-secondary"
                onClick={() => window.location.href = '/economics'}
                style={{ width: '100%', justifyContent: 'center', marginTop: '0.75rem', fontSize: '0.85rem' }}
              >
                Full Economic Analysis <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
