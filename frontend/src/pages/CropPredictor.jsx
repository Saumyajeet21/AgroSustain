import { useState, useRef, useEffect } from 'react';
import { MapPin, Zap, ChevronRight, Droplets, Thermometer, FlaskConical, CloudRain, Search, X } from 'lucide-react';
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

// ── Geocode a city name → {lat, lon, display_name} via OpenStreetMap Nominatim ──
async function geocodeCity(query) {
  const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=5&countrycodes=in`;
  const res  = await fetch(url, { headers: { 'Accept-Language': 'en' } });
  const data = await res.json();
  return data.map(r => ({
    lat:          parseFloat(r.lat),
    lon:          parseFloat(r.lon),
    display_name: r.display_name,
    short_name:   r.display_name.split(',').slice(0,2).join(', '),
  }));
}

export default function CropPredictor() {
  const [inputs, setInputs]           = useState(defaultInputs);
  const [loadingGeo, setLoadingGeo]   = useState(false);
  const [loadingPred, setLoadingPred] = useState(false);
  const [result, setResult]           = useState(null);
  const [econ, setEcon]               = useState(null);
  const [farmArea, setFarmArea]       = useState(1);
  const [error, setError]             = useState('');

  // Location search
  const [locationQuery, setLocationQuery]   = useState('');
  const [suggestions, setSuggestions]       = useState([]);
  const [loadingSuggest, setLoadingSuggest] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const debounceRef = useRef(null);
  const suggestRef  = useRef(null);

  const handleInput = (key, val) => setInputs(p => ({ ...p, [key]: val }));

  // ── Close suggestions on outside click ────────────────────────
  useEffect(() => {
    const handler = (e) => {
      if (suggestRef.current && !suggestRef.current.contains(e.target))
        setSuggestions([]);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // ── Debounced city search ──────────────────────────────────────
  const handleLocationInput = (val) => {
    setLocationQuery(val);
    setSelectedLocation(null);
    clearTimeout(debounceRef.current);
    if (val.trim().length < 2) { setSuggestions([]); return; }
    debounceRef.current = setTimeout(async () => {
      setLoadingSuggest(true);
      try {
        const results = await geocodeCity(val);
        setSuggestions(results);
      } catch { setSuggestions([]); }
      finally { setLoadingSuggest(false); }
    }, 400);
  };

  // ── Fetch weather+soil for given lat/lon ──────────────────────
  const fetchForCoords = async (lat, lon, label) => {
    setLoadingGeo(true); setError(''); setSuggestions([]);
    try {
      const { data } = await predictCrop({ lat, lon });
      setInputs({
        N: data.inputs_used.N, P: data.inputs_used.P, K: data.inputs_used.K,
        temperature: data.inputs_used.temperature, humidity: data.inputs_used.humidity,
        ph: data.inputs_used.ph, rainfall: data.inputs_used.rainfall,
      });
      setResult(data);
      fetchEcon(data.crop, farmArea);
    } catch (e) { setError(e.response?.data?.detail || 'Failed to fetch data for this location'); }
    finally { setLoadingGeo(false); }
  };

  // ── Pick a suggestion ─────────────────────────────────────────
  const pickSuggestion = (s) => {
    setLocationQuery(s.short_name);
    setSelectedLocation(s);
    setSuggestions([]);
    fetchForCoords(s.lat, s.lon, s.short_name);
  };

  // ── GPS auto-fetch ────────────────────────────────────────────
  const autoFetch = () => {
    if (!navigator.geolocation) { setError('Geolocation not supported by this browser'); return; }
    setLoadingGeo(true); setError(''); setLocationQuery(''); setSelectedLocation(null);
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => fetchForCoords(coords.latitude, coords.longitude, 'Your GPS'),
      () => { setError('Location access denied. Please allow location or type a city name.'); setLoadingGeo(false); }
    );
  };

  // ── Manual predict ────────────────────────────────────────────
  const predict = async () => {
    const allFilled = Object.values(inputs).every(v => v !== '');
    if (!allFilled) { setError('Please fill all fields, use GPS, or search a city'); return; }
    setLoadingPred(true); setError('');
    try {
      const lat = selectedLocation?.lat ?? 28.6;
      const lon = selectedLocation?.lon ?? 77.2;
      const payload = { lat, lon, ...Object.fromEntries(Object.entries(inputs).map(([k,v]) => [k, parseFloat(v)])) };
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
          Search any location in India, use your GPS, or enter values manually to get an AI crop recommendation.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* ── Input Panel ──────────────────────────────────────── */}
        <div className="card animate-in delay-1" style={{ padding: '1.75rem' }}>

          {/* ── LOCATION SEARCH BOX ───────────────────────────── */}
          <div ref={suggestRef} style={{ position: 'relative', marginBottom: '0.75rem' }}>
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 6 }}>
              <MapPin size={14} color="var(--green-primary)" /> Search Location
              <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: '0.75rem', marginLeft: 4 }}>
                (city, district, state)
              </span>
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="location-search"
                type="text"
                className="form-input"
                placeholder="e.g. Pune, Nashik, Vidarbha..."
                value={locationQuery}
                onChange={e => handleLocationInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && suggestions.length) pickSuggestion(suggestions[0]); }}
                style={{ paddingLeft: '2.5rem', paddingRight: locationQuery ? '2.5rem' : '1rem' }}
              />
              <Search size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', pointerEvents: 'none' }} />
              {loadingSuggest && (
                <span className="spinner" style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', width: 14, height: 14, borderWidth: 2 }} />
              )}
              {locationQuery && !loadingSuggest && (
                <button
                  style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 2 }}
                  onClick={() => { setLocationQuery(''); setSuggestions([]); setSelectedLocation(null); }}
                >
                  <X size={14} />
                </button>
              )}
            </div>

            {/* Dropdown suggestions */}
            {suggestions.length > 0 && (
              <div style={{
                position: 'absolute', top: 'calc(100% + 6px)', left: 0, right: 0, zIndex: 100,
                background: 'var(--bg-card)', border: '1px solid var(--border-bright)',
                borderRadius: 10, boxShadow: '0 8px 32px rgba(0,0,0,0.4)', overflow: 'hidden',
              }}>
                {suggestions.map((s, i) => (
                  <button
                    key={i}
                    onClick={() => pickSuggestion(s)}
                    style={{
                      width: '100%', textAlign: 'left', padding: '10px 14px',
                      background: 'none', border: 'none', cursor: 'pointer',
                      borderBottom: i < suggestions.length - 1 ? '1px solid var(--border)' : 'none',
                      transition: 'background 0.15s',
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-card-2)'}
                    onMouseLeave={e => e.currentTarget.style.background = 'none'}
                    id={`suggestion-${i}`}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <MapPin size={13} color="var(--green-primary)" style={{ flexShrink: 0 }} />
                      <div>
                        <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                          {s.short_name}
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 1 }}>
                          {s.display_name}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Selected location badge */}
          {selectedLocation && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', background: 'rgba(56,189,108,0.1)', border: '1px solid rgba(56,189,108,0.25)', borderRadius: 8, marginBottom: '0.75rem' }}>
              <MapPin size={13} color="var(--green-primary)" />
              <span style={{ fontSize: '0.8rem', color: 'var(--green-primary)', fontWeight: 600 }}>
                Fetching data for: {selectedLocation.short_name}
              </span>
            </div>
          )}

          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '0.75rem' }}>
            <div className="divider" style={{ flex: 1, margin: 0 }} />
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>or use your current location</span>
            <div className="divider" style={{ flex: 1, margin: 0 }} />
          </div>

          {/* GPS Button */}
          <button
            className="btn btn-secondary"
            onClick={autoFetch}
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', marginBottom: '1.25rem', fontSize: '0.9rem', padding: '10px' }}
            id="auto-fetch-btn"
          >
            {loadingGeo
              ? <><span className="spinner" style={{ width: 15, height: 15, borderWidth: 2 }} /> Fetching...</>
              : <><MapPin size={15} /> Auto-Fetch from GPS</>}
          </button>

          {/* Divider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1.25rem' }}>
            <div className="divider" style={{ flex: 1, margin: 0 }} />
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>or edit values manually</span>
            <div className="divider" style={{ flex: 1, margin: 0 }} />
          </div>

          {/* Input fields */}
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
            {loadingPred
              ? <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Analyzing...</>
              : <><Zap size={16} /> Get AI Recommendation</>}
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
              <div className="progress-bar" style={{ marginBottom: '1.25rem' }}>
                <div className="progress-fill" style={{ width: `${result.confidence}%` }} />
              </div>
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

            {/* Location data used */}
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
                    { label: 'Yield',      value: `${econ.total_yield_tons} tons`,              color: 'var(--green-primary)' },
                    { label: 'Revenue',    value: `₹${econ.total_revenue_inr.toLocaleString()}`, color: 'var(--accent-amber)' },
                    { label: 'Investment', value: `₹${econ.total_investment_inr.toLocaleString()}`, color: 'var(--accent-red)' },
                    { label: 'ROI',        value: `${econ.roi_pct}%`,                           color: 'var(--accent-blue)' },
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
