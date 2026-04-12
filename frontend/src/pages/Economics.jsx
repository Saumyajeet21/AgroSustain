import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { TrendingUp, Tractor } from 'lucide-react';
import { calculateEconomics } from '../api';

const CROPS = [
  'rice','maize','chickpea','kidneybeans','pigeonpeas','mothbeans','mungbean',
  'blackgram','lentil','pomegranate','banana','mango','grapes','watermelon',
  'muskmelon','apple','orange','papaya','coconut','cotton','jute','coffee'
];

const CROP_EMOJIS = {
  rice:'🌾', maize:'🌽', chickpea:'🫘', kidneybeans:'🫘', pigeonpeas:'🌿', mothbeans:'🌿',
  mungbean:'🌿', blackgram:'🌿', lentil:'🌿', pomegranate:'🍎', banana:'🍌', mango:'🥭',
  grapes:'🍇', watermelon:'🍉', muskmelon:'🍈', apple:'🍎', orange:'🍊', papaya:'🥭',
  coconut:'🥥', cotton:'🪡', jute:'🌿', coffee:'☕',
};

const PIE_COLORS = ['#38bd6c', '#ef4444', '#3b82f6'];

const fmt = (n) => n >= 100000 ? `₹${(n/100000).toFixed(1)}L` : `₹${n.toLocaleString()}`;

export default function Economics() {
  const [crop, setCrop]       = useState('rice');
  const [area, setArea]       = useState(1);
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const calculate = async () => {
    setLoading(true); setError('');
    try {
      const { data: d } = await calculateEconomics(crop, parseFloat(area));
      setData(d);
    } catch (e) {
      setError(e.response?.data?.detail || 'Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const barData = data ? [
    { name: 'Investment', amount: data.total_investment_inr, fill: '#ef4444' },
    { name: 'Revenue',    amount: data.total_revenue_inr,    fill: '#38bd6c' },
    { name: 'Profit',     amount: data.net_profit_inr,       fill: '#3b82f6' },
  ] : [];

  const pieData = data ? [
    { name: 'Profit',     value: Math.max(0, data.net_profit_inr) },
    { name: 'Investment', value: data.total_investment_inr },
    { name: 'Market',     value: data.total_revenue_inr - data.total_investment_inr - Math.max(0, data.net_profit_inr) },
  ] : [];

  return (
    <div className="page-wrapper">
      <div className="animate-in" style={{ marginBottom: '2rem' }}>
        <h1 className="section-title">Economic <span>Dashboard</span></h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Calculate projected yield, investment, revenue, and ROI for any crop on your farm size.
        </p>
      </div>

      {/* ── Controls ────────────────────────────────────────────── */}
      <div className="card animate-in delay-1" style={{ padding: '1.75rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '1rem', alignItems: 'end' }}>
          <div className="form-group">
            <label className="form-label">Select Crop</label>
            <select
              id="crop-select"
              className="form-input"
              value={crop}
              onChange={e => setCrop(e.target.value)}
              style={{ cursor: 'pointer' }}
            >
              {CROPS.map(c => (
                <option key={c} value={c}>{CROP_EMOJIS[c]} {c.charAt(0).toUpperCase() + c.slice(1)}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Farm Area (hectares)</label>
            <input
              id="econ-area-input"
              type="number" min="0.1" step="0.1"
              className="form-input"
              value={area}
              onChange={e => setArea(e.target.value)}
              placeholder="e.g. 2.5"
            />
          </div>
          <button
            className="btn btn-primary"
            onClick={calculate}
            disabled={loading}
            style={{ padding: '10px 24px', whiteSpace: 'nowrap' }}
            id="calculate-btn"
          >
            {loading
              ? <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Calculating...</>
              : <><TrendingUp size={16} /> Calculate</>}
          </button>
        </div>
        {error && (
          <div style={{ marginTop: '0.75rem', padding: '10px 14px', borderRadius: 8, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5', fontSize: '0.85rem' }}>
            {error}
          </div>
        )}
      </div>

      {/* ── Results ─────────────────────────────────────────────── */}
      {data && (
        <>
          {/* Stat cards */}
          <div className="grid-4 animate-in" style={{ marginBottom: '1.5rem' }}>
            {[
              { label: 'Total Yield',  value: `${data.total_yield_tons} tons`, icon: '🌾', color: 'var(--green-primary)', bg: 'rgba(56,189,108,0.12)' },
              { label: 'Investment',   value: fmt(data.total_investment_inr),  icon: '💰', color: 'var(--accent-red)',   bg: 'rgba(239,68,68,0.12)' },
              { label: 'Revenue',      value: fmt(data.total_revenue_inr),     icon: '📈', color: 'var(--accent-amber)', bg: 'rgba(245,158,11,0.12)' },
              { label: 'Net Profit',   value: fmt(data.net_profit_inr),        icon: '🏆', color: 'var(--accent-blue)',  bg: 'rgba(59,130,246,0.12)' },
            ].map((s, i) => (
              <div key={i} className="card stat-card">
                <div className="stat-icon" style={{ background: s.bg, color: s.color, fontSize: '1.3rem' }}>{s.icon}</div>
                <div className="stat-value" style={{ color: s.color, fontSize: '1.5rem' }}>{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>

          {/* ROI + Margin badges */}
          <div style={{ display: 'flex', gap: 10, marginBottom: '1.5rem', flexWrap: 'wrap' }}>
            <div className="badge badge-green" style={{ fontSize: '0.875rem', padding: '8px 16px' }}>
              ROI: {data.roi_pct}%
            </div>
            <div className="badge badge-blue" style={{ fontSize: '0.875rem', padding: '8px 16px' }}>
              Profit Margin: {data.profit_margin_pct}%
            </div>
            <div className="badge badge-amber" style={{ fontSize: '0.875rem', padding: '8px 16px' }}>
              {data.yield_per_ha} tons/ha yield rate
            </div>
            <div className="badge badge-green" style={{ fontSize: '0.875rem', padding: '8px 16px' }}>
              ₹{data.price_per_ton_inr.toLocaleString()}/ton market price
            </div>
          </div>

          {/* Charts */}
          <div className="grid-2 animate-in delay-2" style={{ marginBottom: '1.5rem' }}>
            {/* Bar chart */}
            <div className="card" style={{ padding: '1.5rem' }}>
              <div style={{ fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                <TrendingUp size={16} color="var(--green-primary)" /> Financial Breakdown
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={barData} barCategoryGap="30%">
                  <XAxis dataKey="name" tick={{ fill: 'var(--text-secondary)', fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => v >= 100000 ? `${(v/100000).toFixed(0)}L` : v} />
                  <Tooltip
                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 10, color: 'var(--text-primary)' }}
                    formatter={v => [`₹${v.toLocaleString()}`, '']}
                    cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                  />
                  <Bar dataKey="amount" radius={[6, 6, 0, 0]}>
                    {barData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Pie chart */}
            <div className="card" style={{ padding: '1.5rem' }}>
              <div style={{ fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Tractor size={16} color="var(--green-primary)" /> Revenue Allocation
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={pieData.filter(d => d.value > 0)}
                    cx="50%" cy="50%" innerRadius={55} outerRadius={85}
                    paddingAngle={4} dataKey="value"
                  >
                    {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                  </Pie>
                  <Legend
                    formatter={(val) => <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{val}</span>}
                  />
                  <Tooltip
                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 10, color: 'var(--text-primary)' }}
                    formatter={v => [`₹${v.toLocaleString()}`, '']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Details table */}
          <div className="card animate-in delay-3" style={{ padding: '1.5rem' }}>
            <div style={{ fontWeight: 700, marginBottom: '1rem' }}>Full Breakdown — {data.crop.charAt(0).toUpperCase() + data.crop.slice(1)} on {data.farm_area_ha} hectare{data.farm_area_ha !== 1 ? 's' : ''}</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              {[
                ['Yield per Hectare', `${data.yield_per_ha} tons/ha`],
                ['Total Yield', `${data.total_yield_tons} tons`],
                ['Market Price', `₹${data.price_per_ton_inr.toLocaleString()}/ton`],
                ['Investment per Hectare', `₹${data.invest_per_ha_inr.toLocaleString()}/ha`],
                ['Total Investment', `₹${data.total_investment_inr.toLocaleString()}`],
                ['Gross Revenue', `₹${data.total_revenue_inr.toLocaleString()}`],
                ['Net Profit', `₹${data.net_profit_inr.toLocaleString()}`],
                ['Return on Investment', `${data.roi_pct}%`],
                ['Profit Margin', `${data.profit_margin_pct}%`],
              ].map(([label, value], i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: i < 8 ? '1px solid var(--border)' : 'none' }}>
                  <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{label}</span>
                  <span style={{ fontSize: '0.875rem', fontWeight: 600, color: label.includes('Profit') || label.includes('ROI') ? 'var(--green-primary)' : 'var(--text-primary)' }}>{value}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {!data && !loading && (
        <div className="card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>📊</div>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>Select a crop and farm size</div>
          <div style={{ fontSize: '0.875rem' }}>Click Calculate to see yield, investment, and profit projections</div>
        </div>
      )}
    </div>
  );
}
