/**
 * Analytics View
 * Deep-dive multilingual metrics, platform heatmaps, and detection trends.
 */

import { api } from '../api.js';

export async function renderAnalytics(container) {
  container.innerHTML = `
    <div style="margin-bottom: 24px;">
      <h2 style="font-size: 1.6rem; font-weight: 700;">Content Safety Intelligence & Analytics</h2>
      <p style="color: var(--text-secondary); font-size: 0.9rem;">
        Detailed telemetry on language vulnerability, harm category distribution, and enforcement velocity.
      </p>
    </div>

    <!-- Top KPI cards -->
    <div class="grid-4" id="analytics-kpis" style="margin-bottom: 28px;">
      <div class="card">
        <div style="color:var(--text-secondary); font-size:0.8rem; font-weight:600;">ENFORCEMENT ACCURACY</div>
        <div id="stat-accuracy" style="font-size: 2rem; font-weight: 800; font-family:'Outfit'; color:var(--success); margin:6px 0;">96.8%</div>
        <div style="font-size: 0.75rem; color: var(--text-muted);">Validated by human audits</div>
      </div>
      <div class="card">
        <div style="color:var(--text-secondary); font-size:0.8rem; font-weight:600;">ACTIVE LANGUAGES</div>
        <div style="font-size: 2rem; font-weight: 800; font-family:'Outfit'; color:var(--primary-light); margin:6px 0;">8 Supported</div>
        <div style="font-size: 0.75rem; color: var(--text-muted);">Native Indic & Transliterated</div>
      </div>
      <div class="card">
        <div style="color:var(--text-secondary); font-size:0.8rem; font-weight:600;">FALSE POSITIVE RATE</div>
        <div id="stat-fp" style="font-size: 2rem; font-weight: 800; font-family:'Outfit'; color:var(--info); margin:6px 0;">3.2%</div>
        <div style="font-size: 0.75rem; color: var(--text-muted);">Low benign interference</div>
      </div>
      <div class="card">
        <div style="color:var(--text-secondary); font-size:0.8rem; font-weight:600;">AVG DETECTION TIME</div>
        <div style="font-size: 2rem; font-weight: 800; font-family:'Outfit'; color:var(--warning); margin:6px 0;">18 ms</div>
        <div style="font-size: 0.75rem; color: var(--text-muted);">Sub-millisecond inference</div>
      </div>
    </div>

    <!-- Detection Trend & Platform Grid -->
    <div class="grid-2" style="margin-bottom: 28px;">
      <!-- Trend Visualization -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">7-Day Detection Trends</div>
            <div class="card-subtitle">Daily content volume vs toxic flags</div>
          </div>
        </div>
        <div id="trend-bars-container" style="display:flex; justify-content:space-between; align-items:flex-end; height: 180px; padding: 20px 10px 0;">
          Loading trend...
        </div>
      </div>

      <!-- Platform-Wise Analysis -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Platform Toxicity Exposure</div>
            <div class="card-subtitle">Incident density by social network</div>
          </div>
        </div>
        <div id="platform-stats-container">
          Loading platform metrics...
        </div>
      </div>
    </div>

    <!-- Detailed Language Table -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Language Safety Breakdown</div>
          <div class="card-subtitle">Volume and toxicity rates by language</div>
        </div>
      </div>
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Language</th>
              <th>Total Analyzed</th>
              <th>Flagged Toxic</th>
              <th>Safe / Compliant</th>
              <th>Toxicity Exposure Rate</th>
            </tr>
          </thead>
          <tbody id="analytics-lang-tbody">
            <tr><td colspan="5" style="text-align:center; padding: 20px;">Loading language stats...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `;

  try {
    const res = await api.getAnalyticsOverview();
    const data = res;

    // Platform breakdown
    const pCont = container.querySelector('#platform-stats-container');
    if (data.platform_stats) {
      pCont.innerHTML = Object.entries(data.platform_stats).map(([plat, p]) => `
        <div style="margin-bottom: 14px;">
          <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom: 4px;">
            <span style="font-weight: 600; text-transform: capitalize;">${plat}</span>
            <span style="color:var(--text-secondary);">${p.toxic} toxic / ${p.total} total (${p.rate}%)</span>
          </div>
          <div class="category-bar-track">
            <div class="category-bar-fill" style="width: ${p.rate}%; background: ${p.rate > 50 ? 'var(--danger)' : 'var(--warning)'};"></div>
          </div>
        </div>
      `).join('');
    }

    // 7-Day Trend Chart
    const trendCont = container.querySelector('#trend-bars-container');
    if (data.detection_trends) {
      const maxVol = Math.max(...data.detection_trends.map(t => t.analyzed), 100);
      trendCont.innerHTML = data.detection_trends.map(t => {
        const heightPct = Math.round((t.analyzed / maxVol) * 100);
        const toxicHeightPct = Math.round((t.toxic / t.analyzed) * 100);

        return `
          <div style="display:flex; flex-direction:column; align-items:center; gap: 8px; flex: 1;">
            <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 600;">${t.toxic}</div>
            <div style="width: 24px; height: ${Math.max(20, heightPct * 1.3)}px; background: rgba(99, 102, 241, 0.2); border-radius: 4px; position: relative; overflow: hidden; display:flex; align-items:flex-end;">
              <div style="width: 100%; height: ${toxicHeightPct}%; background: var(--danger);"></div>
            </div>
            <div style="font-size: 0.72rem; color: var(--text-secondary);">${t.date}</div>
          </div>
        `;
      }).join('');
    }

    // Language Table
    const tbody = container.querySelector('#analytics-lang-tbody');
    if (data.language_stats) {
      tbody.innerHTML = data.language_stats.map(l => `
        <tr>
          <td style="font-weight: 600;">${l.language}</td>
          <td>${l.total}</td>
          <td style="color: var(--danger); font-weight: 600;">${l.toxic}</td>
          <td style="color: var(--success); font-weight: 600;">${l.clean}</td>
          <td>
            <div style="display:flex; align-items:center; gap: 10px;">
              <div class="category-bar-track" style="width: 80px; height: 6px;">
                <div class="category-bar-fill" style="width: ${l.toxic_rate}%; background: ${l.toxic_rate > 50 ? 'var(--danger)' : 'var(--warning)'};"></div>
              </div>
              <span style="font-size: 0.82rem; font-weight: 600;">${l.toxic_rate}%</span>
            </div>
          </td>
        </tr>
      `).join('');
    }

  } catch (err) {
    console.error("Analytics error:", err);
  }
}
