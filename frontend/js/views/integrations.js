/**
 * Social Integrations View
 * Manage social media accounts (Instagram, YouTube, X, Reddit, Facebook),
 * OAuth connections, Demo/Mock mode streams, and multilingual test samples.
 */

import { api } from '../api.js';

export async function renderIntegrations(container) {
  container.innerHTML = `
    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-3 mb-4">
      <div>
        <h2 style="font-size: 1.6rem; font-weight: 700;">Social Media Platform Integrations</h2>
        <p style="color: var(--text-secondary); font-size: 0.9rem;" class="mb-0">
          Connect official platform APIs or run realistic Demo/Mock feeds to monitor comments and posts.
        </p>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <button id="btn-sync-all" class="btn btn-primary text-nowrap">
          <i class="bi bi-arrow-repeat me-1"></i>
          Sync Live Feeds
        </button>
        <button id="btn-open-connect" class="btn btn-secondary text-nowrap">
          <i class="bi bi-plus-circle me-1"></i>
          Connect Account
        </button>
      </div>
    </div>

    <!-- Demo Mode Notice Banner -->
    <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid var(--success-border); border-radius: var(--radius-md); padding: 14px 20px; margin-bottom: 24px; display:flex; align-items:center; justify-content:space-between;">
      <div style="display:flex; align-items:center; gap: 12px;">
        <span class="mode-badge"><span class="dot"></span> Active Demo Integration Mode</span>
        <span style="font-size: 0.88rem; color: var(--text-secondary);">
          Social platform simulation is active. Multilingual data feeds and mock OAuth streams are fully operational without requiring external platform approval.
        </span>
      </div>
    </div>

    <!-- Connected Accounts Grid -->
    <div class="grid-3" id="accounts-grid" style="margin-bottom: 32px;">
      <div style="grid-column: 1 / -1; text-align: center; padding: 20px;">Loading connected accounts...</div>
    </div>

    <!-- Multilingual Demo Sample Explorer -->
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Multilingual Demonstration Repository</div>
          <div class="card-subtitle">Test authentic multilingual comments curated from the training datasets</div>
        </div>
        <span class="badge badge-purple">11 Authentic Samples</span>
      </div>

      <div id="demo-samples-container" style="display:flex; flex-direction:column; gap: 10px;">
        Loading demo samples...
      </div>
    </div>

    <!-- Connect Account Modal -->
    <div id="modal-connect" class="modal-backdrop-custom">
      <div class="liquid-glass-modal" style="max-width: 500px;">
        <div class="modal-header-glass">
          <span class="card-title mb-0">Connect Social Media Account</span>
          <button class="btn-close-modal" onclick="document.getElementById('modal-connect').classList.remove('active')"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="modal-body-glass">
          <form id="form-connect-account">
            <div class="form-group">
              <label class="form-label">Platform</label>
              <select id="conn-platform" class="form-select">
                <option value="instagram">Instagram</option>
                <option value="youtube">YouTube</option>
                <option value="twitter">X (Twitter)</option>
                <option value="reddit">Reddit</option>
                <option value="facebook">Facebook</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Account / Page Name</label>
              <input type="text" id="conn-name" class="form-input" placeholder="e.g. Creator Studio India" required />
            </div>
            <div class="form-group">
              <label class="form-label">User Handle</label>
              <input type="text" id="conn-handle" class="form-input" placeholder="e.g. @creator_studio_in" required />
            </div>
            <div class="form-group" style="display:flex; align-items:center; gap: 10px; margin-top: 14px;">
              <input type="checkbox" id="conn-is-demo" checked style="width: 18px; height: 18px;" />
              <label for="conn-is-demo" style="font-size: 0.88rem; font-weight: 500;">Enable Demo Mode (Simulate API stream & permissions)</label>
            </div>
            <div style="margin-top: 20px; display:flex; justify-content:flex-end; gap: 10px;">
              <button type="button" class="btn btn-secondary" onclick="document.getElementById('modal-connect').classList.remove('active')">Cancel</button>
              <button type="submit" class="btn btn-primary">Connect Account</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `;

  // Fetch accounts and samples
  await loadAccounts(container);
  await loadSamples(container);

  // Sync All
  container.querySelector('#btn-sync-all').addEventListener('click', async () => {
    const btn = container.querySelector('#btn-sync-all');
    btn.disabled = true;
    btn.innerHTML = `Fetching stream...`;
    try {
      const res = await api.syncStream();
      window.showToast(`Fetched and evaluated ${res.synced_count} items from active social streams!`, 'success');
      await loadAccounts(container);
    } catch (err) {
      window.showToast(`Sync failed: ${err.message}`, 'danger');
    } finally {
      btn.disabled = false;
      btn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>
        Sync Live Feeds
      `;
    }
  });

  // Open Connect Modal
  container.querySelector('#btn-open-connect').addEventListener('click', () => {
    container.querySelector('#modal-connect').classList.add('active');
  });

  // Handle Form Submit
  container.querySelector('#form-connect-account').addEventListener('submit', async (e) => {
    e.preventDefault();
    const platform = container.querySelector('#conn-platform').value;
    const account_name = container.querySelector('#conn-name').value;
    const handle = container.querySelector('#conn-handle').value;
    const is_demo = container.querySelector('#conn-is-demo').checked;

    try {
      await api.connectAccount({ platform, account_name, handle, is_demo });
      window.showToast(`Connected ${handle} successfully!`, 'success');
      container.querySelector('#modal-connect').classList.remove('active');
      await loadAccounts(container);
    } catch (err) {
      window.showToast(`Connect failed: ${err.message}`, 'danger');
    }
  });
}

async function loadAccounts(container) {
  const grid = container.querySelector('#accounts-grid');
  try {
    const res = await api.getConnectedAccounts();
    const accounts = res.accounts;

    if (!accounts || accounts.length === 0) {
      grid.innerHTML = `<div style="grid-column: 1 / -1; text-align:center; padding: 30px; color:var(--text-muted);">No accounts connected. Click "Connect New Account" above.</div>`;
      return;
    }

    grid.innerHTML = accounts.map(acc => {
      const isConn = acc.status === 'Connected';
      return `
        <div class="card" style="position: relative; overflow: hidden;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 14px;">
            <div style="display:flex; align-items:center; gap: 12px;">
              <img src="${acc.avatar_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100'}" style="width: 44px; height: 44px; border-radius: 50%; object-fit: cover;" />
              <div>
                <div style="font-weight: 700; font-size: 0.95rem;">${acc.account_name}</div>
                <div style="font-size: 0.8rem; color: var(--text-muted);">${acc.handle}</div>
              </div>
            </div>
            <span class="badge ${isConn ? 'badge-success' : 'badge-danger'}">${acc.status}</span>
          </div>

          <div style="display:flex; justify-content:space-between; font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 12px; background: var(--bg-input); padding: 8px 12px; border-radius: var(--radius-sm);">
            <span>Platform: <strong style="color:var(--text-primary); text-transform:capitalize;">${acc.platform}</strong></span>
            <span>Mode: <strong style="color:var(--primary-light);">${acc.is_demo ? 'Demo Mock' : 'Live OAuth'}</strong></span>
          </div>

          <div style="display:flex; justify-content:space-between; font-size: 0.82rem; margin-bottom: 16px;">
            <div>
              <span style="color: var(--text-muted);">Monitored:</span>
              <strong style="color: var(--text-primary);">${acc.posts_monitored_count}</strong>
            </div>
            <div>
              <span style="color: var(--text-muted);">Flagged Toxic:</span>
              <strong style="color: var(--danger);">${acc.toxic_detected_count}</strong>
            </div>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; border-top: 1px solid var(--border-color); padding-top: 12px;">
            <span style="font-size: 0.72rem; color: var(--text-muted);">Sync: ${acc.last_sync_at ? new Date(acc.last_sync_at).toLocaleTimeString() : 'Never'}</span>
            <button class="btn btn-secondary btn-sm" onclick="window.disconnectAccountAction(${acc.id})" style="color: var(--danger);">Disconnect</button>
          </div>
        </div>
      `;
    }).join('');

    window.disconnectAccountAction = async (id) => {
      if (confirm("Disconnect this social account?")) {
        try {
          await api.disconnectAccount(id);
          window.showToast("Account disconnected.", "info");
          await loadAccounts(container);
        } catch (err) {
          window.showToast("Disconnect failed: " + err.message, "danger");
        }
      }
    };

  } catch (err) {
    grid.innerHTML = `<div style="color:var(--danger)">Failed to load accounts: ${err.message}</div>`;
  }
}

async function loadSamples(container) {
  const sampCont = container.querySelector('#demo-samples-container');
  try {
    const res = await api.getDemoSamples();
    const samples = res.samples;

    sampCont.innerHTML = samples.map(s => {
      const isToxic = s.type.includes('Abusive') || s.type.includes('Threat') || s.type.includes('Slur') || s.type.includes('Vulgar') || s.type.includes('Harassment');
      return `
        <div style="background: var(--bg-input); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px 16px; display:flex; justify-content:space-between; align-items:center; gap: 16px;">
          <div style="flex: 1;">
            <div style="display:flex; gap: 8px; align-items:center; margin-bottom: 4px;">
              <span class="badge badge-purple" style="font-size:0.75rem;">${s.language}</span>
              <span class="badge ${isToxic ? 'badge-danger' : 'badge-success'}" style="font-size:0.72rem;">${s.type}</span>
              <span style="font-size: 0.75rem; color: var(--text-muted); text-transform:capitalize;">${s.platform} · ${s.author}</span>
            </div>
            <div style="font-size: 0.92rem; font-weight: 500; color: var(--text-primary); margin-bottom: 2px;">
              "${s.text}"
            </div>
            <div style="font-size: 0.75rem; color: var(--text-muted); font-style: italic;">${s.desc}</div>
          </div>
          <div>
            <button class="btn btn-secondary btn-sm" onclick='window.testSampleInAnalyzer("${encodeURIComponent(s.text)}", "${s.language.toLowerCase()}")'>
              Test in Analyzer
            </button>
          </div>
        </div>
      `;
    }).join('');

    window.testSampleInAnalyzer = (textEnc, lang) => {
      const text = decodeURIComponent(textEnc);
      window.navigateTo('analyze', { text, lang });
    };

  } catch (err) {
    sampCont.innerHTML = `<div style="color:var(--danger)">Failed to load samples: ${err.message}</div>`;
  }
}
