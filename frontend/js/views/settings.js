/**
 * Settings View
 * Sensitivity thresholds, active language toggles, and model inventory.
 * Features Role-Based permission controls for Administrator vs Standard User.
 */

import { api } from '../api.js';
import { isAdmin, quickSwitchRole } from '../auth.js';

export async function renderSettings(container) {
  const isAdm = isAdmin();

  container.innerHTML = `
    <!-- Settings Header with Role Status Banner -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3 mb-4">
      <div>
        <h2 style="font-size: 1.6rem; font-weight: 700;">Platform Settings & Model Configuration</h2>
        <p style="color: var(--text-secondary); font-size: 0.9rem;" class="mb-0">
          Fine-tune AI detection thresholds, manage multilingual modules, and view machine learning model health.
        </p>
      </div>
      <div>
        ${isAdm 
          ? `<span class="badge badge-purple p-2 px-3"><i class="bi bi-shield-check me-1"></i> Admin Privileges Active</span>`
          : `<button id="btn-settings-elevate" class="btn btn-sm btn-glass-role"><i class="bi bi-shield-lock-fill me-1"></i> Elevate to Admin</button>`
        }
      </div>
    </div>

    <!-- Role Notice Banner -->
    <div class="card mb-4" style="background: ${isAdm ? 'rgba(99, 102, 241, 0.12)' : 'rgba(245, 158, 11, 0.12)'}; border-color: ${isAdm ? 'rgba(99, 102, 241, 0.35)' : 'rgba(245, 158, 11, 0.35)'};">
      <div class="d-flex align-items-center gap-3">
        <div style="font-size: 1.6rem;">${isAdm ? '👑' : '🛡️'}</div>
        <div class="flex-grow-1">
          <div style="font-weight: 700; color: var(--text-bright);">
            ${isAdm ? 'Administrator Access: Full Control Enabled' : 'Standard User Access: Read-Only Mode'}
          </div>
          <div style="font-size: 0.85rem; color: var(--text-secondary);">
            ${isAdm 
              ? 'You have permission to modify AI sensitivity thresholds, update pipeline configurations, and manage live models.' 
              : 'Logged in as Standard User. Switch to Administrator to save threshold changes and modify platform parameters.'}
          </div>
        </div>
        ${!isAdm ? `<button id="btn-switch-admin-banner" class="btn btn-sm btn-primary">Switch to Admin</button>` : ''}
      </div>
    </div>

    <div class="grid-2">
      <!-- Sensitivity Thresholds -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title"><i class="bi bi-sliders me-1 text-primary"></i> Toxicity Sensitivity Thresholds</div>
            <div class="card-subtitle">Control automated escalation and queue boundaries</div>
          </div>
        </div>

        <form id="form-thresholds">
          <div class="form-group">
            <div style="display:flex; justify-content:space-between; margin-bottom: 4px;">
              <label class="form-label">Safe Threshold (Auto-Allow)</label>
              <span id="val-safe" style="font-weight: 700; font-size: 0.88rem; color: var(--success);">25%</span>
            </div>
            <input type="range" id="slider-safe" min="5" max="40" value="25" step="1" style="width: 100%;" ${!isAdm ? 'disabled' : ''} />
            <span style="font-size: 0.74rem; color: var(--text-muted);">Scores below this are immediately approved as Safe.</span>
          </div>

          <div class="form-group">
            <div style="display:flex; justify-content:space-between; margin-bottom: 4px;">
              <label class="form-label">Review Threshold (Queue Flag)</label>
              <span id="val-review" style="font-weight: 700; font-size: 0.88rem; color: var(--warning);">60%</span>
            </div>
            <input type="range" id="slider-review" min="40" max="75" value="60" step="1" style="width: 100%;" ${!isAdm ? 'disabled' : ''} />
            <span style="font-size: 0.74rem; color: var(--text-muted);">Scores above this enter human moderation queue.</span>
          </div>

          <div class="form-group">
            <div style="display:flex; justify-content:space-between; margin-bottom: 4px;">
              <label class="form-label">Escalate Threshold (Immediate Report)</label>
              <span id="val-flag" style="font-weight: 700; font-size: 0.88rem; color: var(--danger);">85%</span>
            </div>
            <input type="range" id="slider-flag" min="70" max="95" value="85" step="1" style="width: 100%;" ${!isAdm ? 'disabled' : ''} />
            <span style="font-size: 0.74rem; color: var(--text-muted);">Severe scores automatically prepare platform reports.</span>
          </div>

          <div style="margin-top: 24px;">
            <button type="submit" class="btn btn-primary w-100" ${!isAdm ? 'disabled title="Admin role required to save"' : ''}>
              <i class="bi bi-check2-circle me-1"></i> Save Sensitivity Thresholds
            </button>
          </div>
        </form>
      </div>

      <!-- Supported Multilingual Engines -->
      <div class="card">
        <div class="card-header">
          <div>
            <div class="card-title"><i class="bi bi-translate me-1 text-info"></i> Supported Multilingual Engines</div>
            <div class="card-subtitle">Native scripts and code-mixed detection coverage</div>
          </div>
        </div>

        <div style="display:flex; flex-direction:column; gap: 12px;" id="languages-toggles-list">
          <div style="display:flex; justify-content:space-between; align-items:center; background: var(--bg-card-subtle); padding: 12px 16px; border-radius: var(--radius-md); border: 1px solid var(--glass-border);">
            <div>
              <div style="font-weight:700; font-size: 0.92rem; color: var(--text-bright);">Hindi (हिन्दी)</div>
              <div style="font-size: 0.76rem; color: var(--text-muted);">Devanagari script · Specialized Classifier</div>
            </div>
            <span class="badge badge-success"><i class="bi bi-check-circle-fill me-1"></i>Active</span>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; background: var(--bg-card-subtle); padding: 12px 16px; border-radius: var(--radius-md); border: 1px solid var(--glass-border);">
            <div>
              <div style="font-weight:700; font-size: 0.92rem; color: var(--text-bright);">Hinglish (Transliterated Hindi)</div>
              <div style="font-size: 0.76rem; color: var(--text-muted);">Latin script · Indo-HateSpeech Model</div>
            </div>
            <span class="badge badge-success"><i class="bi bi-check-circle-fill me-1"></i>Active</span>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; background: var(--bg-card-subtle); padding: 12px 16px; border-radius: var(--radius-md); border: 1px solid var(--glass-border);">
            <div>
              <div style="font-weight:700; font-size: 0.92rem; color: var(--text-bright);">Kannada (ಕನ್ನಡ)</div>
              <div style="font-size: 0.76rem; color: var(--text-muted);">Kannada script · Dedicated Model</div>
            </div>
            <span class="badge badge-success"><i class="bi bi-check-circle-fill me-1"></i>Active</span>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; background: var(--bg-card-subtle); padding: 12px 16px; border-radius: var(--radius-md); border: 1px solid var(--glass-border);">
            <div>
              <div style="font-weight:700; font-size: 0.92rem; color: var(--text-bright);">Malayalam (മലയാളം)</div>
              <div style="font-size: 0.76rem; color: var(--text-muted);">Malayalam script · Dedicated Model</div>
            </div>
            <span class="badge badge-success"><i class="bi bi-check-circle-fill me-1"></i>Active</span>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; background: var(--bg-card-subtle); padding: 12px 16px; border-radius: var(--radius-md); border: 1px solid var(--glass-border);">
            <div>
              <div style="font-weight:700; font-size: 0.92rem; color: var(--text-bright);">Tamil (தமிழ்) & Telugu (తెలుగు)</div>
              <div style="font-size: 0.76rem; color: var(--text-muted);">Dravidian Language High-Accuracy Classifiers</div>
            </div>
            <span class="badge badge-success"><i class="bi bi-check-circle-fill me-1"></i>Active</span>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; background: var(--bg-card-subtle); padding: 12px 16px; border-radius: var(--radius-md); border: 1px solid var(--glass-border);">
            <div>
              <div style="font-weight:700; font-size: 0.92rem; color: var(--text-bright);">English (Global Safety)</div>
              <div style="font-size: 0.76rem; color: var(--text-muted);">Jigsaw Multi-Category Toxicity Classifier</div>
            </div>
            <span class="badge badge-success"><i class="bi bi-check-circle-fill me-1"></i>Active</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Machine Learning Models Inventory -->
    <div class="card" style="margin-top: 24px;">
      <div class="card-header">
        <div>
          <div class="card-title"><i class="bi bi-cpu me-1 text-primary"></i> Deployed ML Model Inventory</div>
          <div class="card-subtitle">Active classification pipelines running in production runtime</div>
        </div>
        <span class="badge badge-success">7 Models Active</span>
      </div>

      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Model Identifier</th>
              <th>Target Language</th>
              <th>Pipeline Architecture</th>
              <th>Status</th>
              <th>Runtime Engine</th>
            </tr>
          </thead>
          <tbody id="models-inventory-tbody">
            <tr><td colspan="5" style="text-align:center; padding: 20px;">Loading model metadata...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  `;

  // Attach elevate / switch role buttons
  const btnElevate = container.querySelector('#btn-settings-elevate');
  if (btnElevate) {
    btnElevate.addEventListener('click', () => quickSwitchRole('Admin'));
  }

  const btnBannerSwitch = container.querySelector('#btn-switch-admin-banner');
  if (btnBannerSwitch) {
    btnBannerSwitch.addEventListener('click', () => quickSwitchRole('Admin'));
  }

  // Attach slider real-time value updates
  const sSafe = container.querySelector('#slider-safe');
  const sReview = container.querySelector('#slider-review');
  const sFlag = container.querySelector('#slider-flag');

  sSafe.addEventListener('input', () => container.querySelector('#val-safe').textContent = `${sSafe.value}%`);
  sReview.addEventListener('input', () => container.querySelector('#val-review').textContent = `${sReview.value}%`);
  sFlag.addEventListener('input', () => container.querySelector('#val-flag').textContent = `${sFlag.value}%`);

  container.querySelector('#form-thresholds').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!isAdmin()) {
      window.showToast("Admin privileges required to save sensitivity settings.", "warning");
      return;
    }
    try {
      await api.updateSettings({
        safe_threshold: parseFloat(sSafe.value) / 100,
        review_threshold: parseFloat(sReview.value) / 100,
        flag_threshold: parseFloat(sFlag.value) / 100
      });
      window.showToast("Threshold settings saved successfully!", "success");
    } catch (err) {
      window.showToast("Save error: " + err.message, "danger");
    }
  });

  // Load models inventory
  try {
    const res = await api.getSettings();
    const models = res.loaded_models;
    const tbody = container.querySelector('#models-inventory-tbody');

    if (models && models.length > 0) {
      tbody.innerHTML = models.map(m => `
        <tr>
          <td style="font-weight: 700; color: var(--text-bright);">${m.name}</td>
          <td><span class="badge badge-purple">${m.language_code.toUpperCase()}</span></td>
          <td style="color: var(--text-secondary); font-size: 0.84rem;">TF-IDF Char/Word N-Gram + LogisticRegression</td>
          <td><span class="badge badge-success"><i class="bi bi-circle-fill me-1" style="font-size: 0.5rem;"></i>${m.status}</span></td>
          <td style="font-size: 0.82rem; color: var(--text-muted);">Local Memory / Scikit-Learn 1.9</td>
        </tr>
      `).join('');
    }
  } catch (err) {
    console.error("Settings error:", err);
  }
}
