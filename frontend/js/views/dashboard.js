/**
 * Dashboard View
 * Displays high-level safety KPIs, platform breakdowns, language distribution,
 * recent flagged items, and quick sync action.
 */

import { api } from '../api.js';

export async function renderDashboard(container) {
  container.innerHTML = `
    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-3 mb-4">
      <div>
        <h2 style="font-size: 1.6rem; font-weight: 700;">Safety Operations Dashboard</h2>
        <p style="color: var(--text-secondary); font-size: 0.9rem;" class="mb-0">Real-time multilingual AI threat detection and content monitoring across social channels.</p>
      </div>
      <div>
        <button id="btn-sync-feed" class="btn btn-primary text-nowrap">
          <i class="bi bi-arrow-repeat me-1"></i>
          Sync Social Stream
        </button>
      </div>
    </div>

    <!-- KPI Metric Cards -->
    <div class="grid-4" id="kpi-cards" style="margin-bottom: 28px;">
      <div class="card" style="border-left: 4px solid var(--primary);">
        <div style="color: var(--text-secondary); font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Total Analyzed</div>
        <div id="stat-total" style="font-size: 2.2rem; font-weight: 800; margin: 8px 0; font-family: 'Outfit';">...</div>
        <div style="font-size: 0.8rem; color: var(--success); display:flex; align-items:center; gap:4px;">
          <span>● Active Monitoring</span>
        </div>
      </div>

      <div class="card" style="border-left: 4px solid var(--danger);">
        <div style="color: var(--text-secondary); font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Toxic Flags</div>
        <div id="stat-toxic" style="font-size: 2.2rem; font-weight: 800; margin: 8px 0; font-family: 'Outfit'; color: var(--danger);">...</div>
        <div id="stat-toxic-rate" style="font-size: 0.8rem; color: var(--text-secondary);">... rate</div>
      </div>

      <div class="card" style="border-left: 4px solid var(--warning);">
        <div style="color: var(--text-secondary); font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Pending Human Review</div>
        <div id="stat-pending" style="font-size: 2.2rem; font-weight: 800; margin: 8px 0; font-family: 'Outfit'; color: var(--warning);">...</div>
        <div style="font-size: 0.8rem; color: var(--text-secondary);">Moderation Queue</div>
      </div>

      <div class="card" style="border-left: 4px solid var(--info);">
        <div style="color: var(--text-secondary); font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Platform Reports</div>
        <div id="stat-reports" style="font-size: 2.2rem; font-weight: 800; margin: 8px 0; font-family: 'Outfit'; color: var(--info);">...</div>
        <div id="stat-fp-rate" style="font-size: 0.8rem; color: var(--text-secondary);">... false positive rate</div>
      </div>
    </div>

    <!-- Middle Section: Languages & Categories -->
    <div class="grid-2" style="margin-bottom: 28px;">
      <!-- Language Distribution -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Multilingual Distribution</div>
            <div class="card-subtitle">Content breakdown by language & script</div>
          </div>
          <span class="badge badge-purple">8 Languages</span>
        </div>
        <div id="language-bars-container">Loading language distribution...</div>
      </div>

      <!-- Toxicity Categories -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title">Flagged Toxicity Categories</div>
            <div class="card-subtitle">Breakdown of harmful behavior classifications</div>
          </div>
          <span class="badge badge-danger">Harm Types</span>
        </div>
        <div id="category-bars-container">Loading categories...</div>
      </div>
    </div>

    <!-- Recent Flagged Content -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Recent Flagged Content</div>
          <div class="card-subtitle">Latest items requiring moderator attention</div>
        </div>
        <button id="btn-view-all-queue" class="btn btn-secondary btn-sm">View Full Queue</button>
      </div>

      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Author / Source</th>
              <th>Platform</th>
              <th>Language</th>
              <th>Original Content</th>
              <th>Categories</th>
              <th>Toxicity</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody id="recent-flagged-tbody">
            <tr><td colspan="8" style="text-align:center; padding: 24px;">Loading recent items...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `;

  // Fetch data
  try {
    const data = await api.getAnalyticsOverview();
    updateDashboardUI(data, container);
  } catch (err) {
    console.error("Dashboard error:", err);
  }

  // Handle Sync Stream Button
  const syncBtn = container.querySelector('#btn-sync-feed');
  if (syncBtn) {
    syncBtn.addEventListener('click', async () => {
      syncBtn.disabled = true;
      syncBtn.innerHTML = `Syncing...`;
      try {
        const res = await api.syncStream();
        window.showToast(`Fetched ${res.synced_count} new multilingual posts into queue!`, 'success');
        const fresh = await api.getAnalyticsOverview();
        updateDashboardUI(fresh, container);
      } catch (err) {
        window.showToast(`Sync error: ${err.message}`, 'danger');
      } finally {
        syncBtn.disabled = false;
        syncBtn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>
          Sync Social Stream
        `;
      }
    });
  }

  container.querySelector('#btn-view-all-queue')?.addEventListener('click', () => {
    window.navigateTo('moderation');
  });
}

function updateDashboardUI(data, container) {
  const k = data.kpis;
  container.querySelector('#stat-total').textContent = k.total_analyzed;
  container.querySelector('#stat-toxic').textContent = k.total_toxic;
  container.querySelector('#stat-toxic-rate').textContent = `${k.toxic_rate}% toxicity rate`;
  container.querySelector('#stat-pending').textContent = k.pending_review;
  container.querySelector('#stat-reports').textContent = k.total_reports;
  container.querySelector('#stat-fp-rate').textContent = `${k.false_positive_rate}% false positive rate`;

  // Render Language Bars
  const langCont = container.querySelector('#language-bars-container');
  if (langCont && data.language_stats) {
    langCont.innerHTML = data.language_stats.map(l => {
      const pct = Math.round((l.total / Math.max(1, k.total_analyzed)) * 100);
      return `
        <div class="category-bar-row">
          <div class="category-bar-header">
            <span class="category-bar-title" style="font-weight: 500; color: var(--text-primary);">${l.language}</span>
            <span class="category-bar-val" style="color: var(--text-secondary);">${l.total} items (${pct}%) · <span style="color:var(--danger)">${l.toxic} toxic</span></span>
          </div>
          <div class="category-bar-track">
            <div class="category-bar-fill" style="width: ${pct}%; background: var(--primary-gradient);"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Render Category Bars
  const catCont = container.querySelector('#category-bars-container');
  if (catCont && data.category_stats) {
    const maxCat = Math.max(...data.category_stats.map(c => c.count), 1);
    catCont.innerHTML = data.category_stats.map(c => {
      const pct = Math.round((c.count / maxCat) * 100);
      let color = 'var(--danger)';
      if (c.category.includes('Harassment')) color = '#f97316';
      if (c.category.includes('Insult')) color = '#eab308';
      if (c.category.includes('Profanity')) color = '#a855f7';
      if (c.category.includes('Threat')) color = '#ef4444';

      return `
        <div class="category-bar-row">
          <div class="category-bar-header">
            <span class="category-bar-title" style="font-weight: 500; color: var(--text-primary);">${c.category}</span>
            <span class="category-bar-val" style="font-weight: 600;">${c.count} flagged</span>
          </div>
          <div class="category-bar-track">
            <div class="category-bar-fill" style="width: ${pct}%; background: ${color};"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Render Recent Flagged Table
  const tbody = container.querySelector('#recent-flagged-tbody');
  if (tbody && data.recent_flagged) {
    if (data.recent_flagged.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 20px; color: var(--text-muted);">No flagged content currently in queue.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.recent_flagged.map(item => {
      const toxPct = Math.round(item.toxicity_score * 100);
      const cats = item.flagged_categories.filter(c => c !== 'Non-toxic/Safe').slice(0, 2);
      const catBadges = cats.map(c => `<span class="badge badge-danger" style="font-size:0.72rem; padding: 2px 6px;">${c}</span>`).join(' ');

      let statusBadge = `<span class="badge badge-warning">${item.moderation_status}</span>`;
      if (item.moderation_status === 'Reported') statusBadge = `<span class="badge badge-info">Reported</span>`;
      if (item.moderation_status === 'Flagged') statusBadge = `<span class="badge badge-danger">Flagged</span>`;

      return `
        <tr>
          <td>
            <div style="font-weight: 600; font-size: 0.88rem;">${item.author_name}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">${item.author_handle}</div>
          </td>
          <td>
            <span style="text-transform: capitalize; font-weight: 500;">${item.platform}</span>
          </td>
          <td>
            <span class="badge badge-purple">${item.detected_language_name}</span>
          </td>
          <td style="max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${item.original_text}">
            ${item.original_text}
          </td>
          <td>${catBadges || '<span style="color:var(--text-muted)">-</span>'}</td>
          <td>
            <span style="font-weight: 700; color: ${toxPct > 70 ? 'var(--danger)' : 'var(--warning)'};">${toxPct}%</span>
          </td>
          <td>${statusBadge}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="window.openItemReviewModal(${item.id})">Review</button>
          </td>
        </tr>
      `;
    }).join('');
  }
}
