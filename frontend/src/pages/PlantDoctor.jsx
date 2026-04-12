import { useState, useRef } from 'react';
import { Upload, Stethoscope, Loader, ImageIcon, CheckCircle, AlertTriangle, X } from 'lucide-react';
import { diagnosePlant } from '../api';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001';

export default function PlantDoctor() {
  const [file, setFile]         = useState(null);
  const [preview, setPreview]   = useState(null);
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState('');
  const [chat, setChat]         = useState([]);
  const fileRef = useRef();

  const handleFile = (f) => {
    if (!f || !f.type.startsWith('image/')) { setError('Please upload an image file'); return; }
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null); setError(''); setChat([]);
  };

  const handleDrop = (e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); };
  const handleDrag = (e) => { e.preventDefault(); };

  const diagnose = async () => {
    if (!file) { setError('Please upload a plant photo first'); return; }
    setLoading(true); setError('');
    try {
      const { data } = await diagnosePlant(file);
      setResult(data);
      // Build chat messages
      const msgs = [];
      if (data.diagnosis?.success) {
        msgs.push({
          role: 'assistant',
          type: data.diagnosis.is_healthy ? 'success' : 'warning',
          text: data.diagnosis.is_healthy
            ? `Your **${data.diagnosis.plant}** plant looks **healthy**! (${data.diagnosis.confidence}% confidence)`
            : `Detected **${data.diagnosis.condition}** on your **${data.diagnosis.plant}** plant. (${data.diagnosis.confidence}% confidence)`
        });
      }
      if (data.gemini_advice) {
        msgs.push({ role: 'assistant', type: 'advice', text: data.gemini_advice });
      }
      setChat(msgs);
    } catch (e) {
      const msg = e.response?.data?.detail || 'Diagnosis failed. Please try a clearer image.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => { setFile(null); setPreview(null); setResult(null); setError(''); setChat([]); };

  return (
    <div className="page-wrapper">
      <div className="animate-in" style={{ marginBottom: '2rem' }}>
        <h1 className="section-title">Plant <span>Doctor</span></h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Upload a photo of your crop. Our two-stage AI pipeline (YOLOv8 + ResNet50) detects & diagnoses, then Gemini prescribes treatment.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: '1.5rem', alignItems: 'start', maxWidth: result ? '100%' : 640, margin: result ? 0 : '0 auto' }}>
        {/* ── Upload Panel ─────────────────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Drop zone */}
          <div
            className="card animate-in delay-1"
            style={{
              padding: '2rem', cursor: 'pointer', transition: 'var(--transition)',
              borderStyle: preview ? 'solid' : 'dashed',
              borderColor: preview ? 'var(--border-bright)' : 'var(--border)',
              textAlign: 'center',
            }}
            onClick={() => fileRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDrag}
            id="drop-zone"
          >
            <input ref={fileRef} type="file" accept="image/*" hidden onChange={e => handleFile(e.target.files[0])} id="file-input" />
            {preview ? (
              <div style={{ position: 'relative' }}>
                <img src={preview} alt="Upload" style={{ maxHeight: 300, maxWidth: '100%', borderRadius: 12, objectFit: 'contain' }} />
                <button
                  className="btn btn-secondary"
                  onClick={e => { e.stopPropagation(); reset(); }}
                  style={{ position: 'absolute', top: 8, right: 8, padding: '4px 8px' }}
                  id="clear-image-btn"
                >
                  <X size={14} />
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem', padding: '2rem 0' }}>
                <div style={{ width: 56, height: 56, borderRadius: '50%', background: 'rgba(56,189,108,0.1)', border: '2px dashed var(--border-bright)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Upload size={22} color="var(--green-primary)" />
                </div>
                <div>
                  <div style={{ fontWeight: 600, marginBottom: 4 }}>Drop your plant photo here</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>or click to browse (JPG, PNG, WEBP)</div>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div style={{ padding: '10px 14px', borderRadius: 8, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5', fontSize: '0.85rem' }}>
              {error}
            </div>
          )}

          <button
            className="btn btn-primary"
            onClick={diagnose}
            disabled={loading || !file}
            style={{ width: '100%', justifyContent: 'center', fontSize: '0.95rem', padding: '12px' }}
            id="diagnose-btn"
          >
            {loading
              ? <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Analyzing Leaves...</>
              : <><Stethoscope size={16} /> Diagnose Plant</>}
          </button>

          {/* Pipeline steps */}
          <div className="card" style={{ padding: '1.25rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.75rem' }}>
              AI Pipeline
            </div>
            {[
              { n: 1, label: 'YOLOv8 detects leaf regions', done: !!result },
              { n: 2, label: 'OpenCV crops each leaf', done: !!result },
              { n: 3, label: 'ResNet50 classifies disease', done: !!result },
              { n: 4, label: 'Gemini generates treatment', done: !!result && !!result.gemini_advice },
            ].map(step => (
              <div key={step.n} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0' }}>
                <div style={{ width: 22, height: 22, borderRadius: '50%', background: step.done ? 'var(--green-primary)' : 'var(--bg-card-2)', border: step.done ? 'none' : '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  {step.done ? <CheckCircle size={12} color="#fff" /> : <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{step.n}</span>}
                </div>
                <span style={{ fontSize: '0.8rem', color: step.done ? 'var(--text-primary)' : 'var(--text-secondary)' }}>{step.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* ── Results Panel ─────────────────────────────────────── */}
        {result && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Annotated image */}
            {result.annotated_image_url && (
              <div className="card animate-in" style={{ padding: '1.25rem' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
                  Annotated by AI — {result.num_leaves_found} leaf region{result.num_leaves_found !== 1 ? 's' : ''} found
                </div>
                <img
                  src={`${API_BASE}${result.annotated_image_url}`}
                  alt="Annotated"
                  style={{ width: '100%', borderRadius: 10, objectFit: 'contain', maxHeight: 280 }}
                />
                {result.used_fallback && (
                  <div style={{ marginTop: 8, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    No distinct leaves detected — analyzed full image.
                  </div>
                )}
              </div>
            )}

            {/* Diagnosis */}
            {result.diagnosis?.success && (
              <div className={`card animate-in delay-1`} style={{ padding: '1.5rem', borderColor: result.diagnosis.is_healthy ? 'rgba(56,189,108,0.4)' : 'rgba(245,158,11,0.4)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '0.75rem' }}>
                  {result.diagnosis.is_healthy
                    ? <CheckCircle size={20} color="var(--green-primary)" />
                    : <AlertTriangle size={20} color="var(--accent-amber)" />}
                  <span style={{ fontWeight: 700, fontSize: '1rem' }}>
                    {result.diagnosis.is_healthy ? 'Healthy Plant' : result.diagnosis.condition}
                  </span>
                  <span className={`badge ${result.diagnosis.is_healthy ? 'badge-green' : 'badge-amber'}`} style={{ marginLeft: 'auto' }}>
                    {result.diagnosis.confidence}%
                  </span>
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  Plant identified as: <strong style={{ color: 'var(--text-primary)' }}>{result.diagnosis.plant}</strong>
                </div>

                <div className="progress-bar" style={{ marginTop: '0.75rem' }}>
                  <div className="progress-fill" style={{ width: `${result.diagnosis.confidence}%`, background: result.diagnosis.is_healthy ? undefined : 'linear-gradient(90deg, var(--accent-amber), #fde68a)' }} />
                </div>
              </div>
            )}

            {/* Gemini Chat */}
            <div className="card animate-in delay-2" style={{ padding: '1.5rem' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '1rem' }}>
                AI Treatment Advisor (Gemini)
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: 360, overflowY: 'auto' }}>
                {chat.map((msg, i) => (
                  <div key={i} style={{
                    padding: '12px 16px', borderRadius: 12,
                    background: msg.type === 'success' ? 'rgba(56,189,108,0.1)' : msg.type === 'warning' ? 'rgba(245,158,11,0.1)' : 'var(--bg-card-2)',
                    border: `1px solid ${msg.type === 'success' ? 'rgba(56,189,108,0.25)' : msg.type === 'warning' ? 'rgba(245,158,11,0.25)' : 'var(--border)'}`,
                    fontSize: '0.875rem', lineHeight: 1.65, color: 'var(--text-primary)',
                    whiteSpace: 'pre-wrap',
                  }}>
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.07em' }}>
                      {msg.type === 'advice' ? 'Gemini Prescription' : 'Diagnosis'}
                    </span>
                    {msg.text.replace(/\*\*(.*?)\*\*/g, '$1')}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
