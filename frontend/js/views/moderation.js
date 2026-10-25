/**
 * Moderation View
 * Interactive queue with filtering, detailed review modal, human override,
 * and audit action tracking.
 */

import { api } from '../api.js';

let currentFilter = {
  status: 'all',
  platform: 'all',
  language: 'all',
  search: '',
  page: 1
};

export async function renderModeration(container) {
  container.innerHTML = `
    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-3 mb-4">
      <div>
        <h2 style="font-size: 1.6rem; font-weight: 700;">Human-in-the-Loop Moderation Queue</h2>
        <p style="color: var(--text-secondary); font-size: 0.9rem;" class="mb-0">
          Review AI-flagged items, override machine classifications, and initiate compliance actions.
        </p>
      </div>
      <div>
        <button id="btn-view-audit" class="btn btn-secondary text-nowrap">
          <i class="bi bi-clock-history me-1"></i>
          Audit History
        </button>
      </div>
    </div>

    <!-- Filter & Search Bar -->
    <div class="card" style="margin-bottom: 24px; padding: 18px 24px;">
      <div style="display:flex; gap: 14px; flex-wrap: wrap; align-items:center;">
        <!-- Search Input -->
        <div style="flex: 2; min-width: 220px;">
          <input type="text" id="filter-search" class="form-input" placeholder="Search author, keyword, or text content..." style="width: 100%;" />
        </div>

        <!-- Status Filter -->
        <div style="flex: 1; min-width: 140px;">
          <select id="filter-status" class="form-select" style="width: 100%;">
            <option value="all">All Statuses</option>
            <option value="Under Review">Under Review</option>
            <option value="Flagged">Flagged</option>
            <option value="Reported">Reported</option>
            <option value="Resolved">Resolved</option>
            <option value="Safe">Safe</option>
            <option value="False Positive">False Positive</option>
          </select>
        </div>

        <!-- Platform Filter -->
        <div style="flex: 1; min-width: 140px;">
          <select id="filter-platform" class="form-select" style="width: 100%;">
            <option value="all">All Platforms</option>
            <option value="instagram">Instagram</option>
            <option value="youtube">YouTube</option>
            <option value="twitter">X (Twitter)</option>
            <option value="reddit">Reddit</option>
            <option value="facebook">Facebook</option>
            <option value="manual">Manual / Direct</option>
          </select>
        </div>

        <!-- Language Filter -->
        <div style="flex: 1; min-width: 140px;">
          <select id="filter-language" class="form-select" style="width: 100%;">
            <option value="all">All Languages</option>
            <option value="hi">Hindi</option>
            <option value="hinglish">Hinglish</option>
            <option value="en">English</option>
            <option value="kn">Kannada</option>
            <option value="ml">Malayalam</option>
            <option value="ta">Tamil</option>
            <option value="te">Telugu</option>
            <option value="mr">Marathi</option>
          </select>
        </div>

        <button id="btn-apply-filter" class="btn btn-primary" style="padding: 10px 18px;">
          Filter Queue
        </button>
      </div>
    </div>

    <!-- Queue Table Card -->
    <div class="card">
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Platform / Author</th>
              <th>Language</th>
              <th>Content Snippet</th>
              <th>Categories</th>
              <th>Score / Conf</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="queue-table-body">
            <tr><td colspan="8" style="text-align:center; padding: 30px;">Loading moderation queue...</td></tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--border-color);">
        <div id="pagination-info" style="font-size: 0.85rem; color: var(--text-secondary);">Showing ... items</div>
        <div style="display:flex; gap: 8px;">
          <button id="btn-prev-page" class="btn btn-secondary btn-sm">Previous</button>
          <button id="btn-next-page" class="btn btn-secondary btn-sm">Next</button>
        </div>
      </div>
    </div>

    <!-- Review Modal Container -->
    <div id="modal-review" class="modal-backdrop-custom">
      <div class="liquid-glass-modal" style="max-width: 720px;">
        <div class="modal-header-glass">
          <div class="d-flex align-items-center gap-2">
            <span class="card-title mb-0">Moderation Item Review</span>
            <span id="modal-item-id-badge" class="badge badge-purple">ID #0</span>
          </div>
          <button class="btn-close-modal" onclick="document.getElementById('modal-review').classList.remove('active')"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="modal-body-glass" id="modal-review-body">
          Loading item details...
        </div>
      </div>
    </div>

    <!-- Audit Log Modal -->
    <div id="modal-audit" class="modal-backdrop-custom">
      <div class="liquid-glass-modal" style="max-width: 760px;">
        <div class="modal-header-glass">
          <span class="card-title mb-0">Moderator Decision Audit Log</span>
          <button class="btn-close-modal" onclick="document.getElementById('modal-audit').classList.remove('active')"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="modal-body-glass" id="modal-audit-body" style="max-height: 60vh; overflow-y: auto;">
          Loading audit log...
        </div>
      </div>
    </div>
  `;

  // Attach search and filter listeners
  container.querySelector('#btn-apply-filter').addEventListener('click', () => {
    currentFilter.search = container.querySelector('#filter-search').value.trim();
    currentFilter.status = container.querySelector('#filter-status').value;
    currentFilter.platform = container.querySelector('#filter-platform').value;
    currentFilter.language = container.querySelector('#filter-language').value;
    currentFilter.page = 1;
    loadQueue(container);
  });

  container.querySelector('#btn-prev-page').addEventListener('click', () => {
    if (currentFilter.page > 1) {
      currentFilter.page--;
      loadQueue(container);
    }
  });

  container.querySelector('#btn-next-page').addEventListener('click', () => {
    currentFilter.page++;
    loadQueue(container);
  });

  // Audit modal trigger
  container.querySelector('#btn-view-audit').addEventListener('click', async () => {
    const modal = container.querySelector('#modal-audit');
    modal.classList.add('active');
    const body = container.querySelector('#modal-audit-body');
    body.innerHTML = `Loading decisions...`;
    try {
      const res = await api.getAuditLog();
      if (!res.audit_log || res.audit_log.length === 0) {
        body.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--text-muted);">No moderator actions recorded yet.</div>`;
        return;
      }

      body.innerHTML = res.audit_log.map(a => `
        <div style="background: var(--bg-input); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px 16px; margin-bottom: 10px;">
          <div style="display:flex; justify-content:space-between; margin-bottom: 4px;">
            <span style="font-weight: 600; font-size: 0.88rem;">${a.moderator_name}</span>
            <span style="font-size: 0.75rem; color: var(--text-muted);">${new Date(a.timestamp).toLocaleString()}</span>
          </div>
          <div style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 4px;">
            Action: <strong style="text-transform: uppercase; color: var(--primary-light);">${a.action_type}</strong> ·
            Item #${a.content_item_id} (${a.platform} - ${a.author_handle}) · Status changed from <em>${a.previous_status}</em> to <strong>${a.new_status}</strong>
          </div>
          ${a.notes ? `<div style="font-size: 0.8rem; color: var(--text-primary); font-style: italic;">Note: "${a.notes}"</div>` : ''}
        </div>
      `).join('');
    } catch (err) {
      body.innerHTML = `<div style="color:var(--danger)">Error: ${err.message}</div>`;
    }
  });

  // Expose global modal function
  window.openItemReviewModal = (id) => openReviewModal(id, container);

  // Initial load
  loadQueue(container);
}

async function loadQueue(container) {
  const tbody = container.querySelector('#queue-table-body');
  tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 20px;">Fetching moderation queue...</td></tr>`;

  try {
    const res = await api.getModerationQueue(currentFilter);
    const items = res.items;

    container.querySelector('#pagination-info').textContent =
      `Showing page ${res.page} of ${res.pages} (${res.total} total items)`;

    if (items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 30px; color: var(--text-muted);">No items match current filter criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map(item => {
      const toxPct = Math.round(item.toxicity_score * 100);
      const confPct = Math.round(item.confidence_score * 100);
      const cats = item.flagged_categories.filter(c => c !== 'Non-toxic/Safe').slice(0, 2);
      const catBadges = cats.map(c => `<span class="badge badge-danger" style="font-size:0.72rem; padding: 2px 6px;">${c}</span>`).join(' ');

      let statusBadge = `<span class="badge badge-warning">${item.moderation_status}</span>`;
      if (item.moderation_status === 'Reported') statusBadge = `<span class="badge badge-info">Reported</span>`;
      if (item.moderation_status === 'Flagged') statusBadge = `<span class="badge badge-danger">Flagged</span>`;
      if (item.moderation_status === 'Safe') statusBadge = `<span class="badge badge-success">Safe</span>`;
      if (item.moderation_status === 'False Positive') statusBadge = `<span class="badge badge-purple">False Positive</span>`;

      return `
        <tr>
          <td><span style="font-family: monospace; color: var(--text-muted);">#${item.id}</span></td>
          <td>
            <div style="font-weight: 600; font-size: 0.88rem;">${item.author_name}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">${item.platform} · ${item.author_handle}</div>
          </td>
          <td>
            <span class="badge badge-purple" style="font-size:0.75rem;">${item.detected_language_name}</span>
          </td>
          <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${item.original_text}">
            ${item.content_type === 'image' ? '<span class="badge badge-info" style="font-size:0.65rem; margin-right:4px;">IMG</span>' : ''}
            ${item.original_text}
          </td>
          <td>${catBadges || '<span style="color:var(--text-muted); font-size:0.75rem;">Safe</span>'}</td>
          <td>
            <span style="font-weight: 700; color: ${toxPct > 60 ? 'var(--danger)' : 'var(--warning)'};">${toxPct}%</span>
            <span style="font-size: 0.72rem; color: var(--text-muted);">(${confPct}% conf)</span>
          </td>
          <td>${statusBadge}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="window.openItemReviewModal(${item.id})">Review</button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 20px; color: var(--danger);">Failed to load queue: ${err.message}</td></tr>`;
  }
}

async function openReviewModal(itemId, container) {
  const modal = container.querySelector('#modal-review');
  const body = container.querySelector('#modal-review-body');
  container.querySelector('#modal-item-id-badge').textContent = `ID #${itemId}`;
  modal.classList.add('active');
  body.innerHTML = `Loading item #${itemId}...`;

  try {
    const data = await api.getItemDetails(itemId);
    const item = data.item;
    const toxPct = Math.round(item.toxicity_score * 100);

    body.innerHTML = `
      <!-- Author & Metadata header -->
      <div style="display:flex; justify-content:space-between; align-items:center; background: var(--bg-input); padding: 12px 16px; border-radius: var(--radius-md); margin-bottom: 16px;">
        <div style="display:flex; align-items:center; gap: 12px;">
          <img src="${item.author_avatar || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100'}" style="width: 40px; height: 40px; border-radius: 50%;" />
          <div>
            <div style="font-weight: 700;">${item.author_name} <span style="font-weight:400; color:var(--text-muted);">(${item.author_handle})</span></div>
            <div style="font-size: 0.75rem; color: var(--text-secondary);">Platform: <strong style="text-transform: capitalize;">${item.platform}</strong> · Detected: ${new Date(item.created_at).toLocaleString()}</div>
          </div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 0.75rem; color: var(--text-muted);">Language</div>
          <span class="badge badge-purple">${item.detected_language_name}</span>
        </div>
      </div>

      <!-- Content text -->
      <div style="margin-bottom: 16px;">
        <div style="font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">ORIGINAL CONTENT</div>
        <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px; font-size: 0.95rem; line-height: 1.5;">
          ${item.original_text}
        </div>
      </div>

      <!-- OCR Text display if available -->
      ${item.ocr_extracted_text ? `
        <div style="margin-bottom: 16px;">
          <div style="font-size: 0.8rem; font-weight: 600; color: var(--primary-light); margin-bottom: 6px;">OCR EXTRACTED TEXT FROM IMAGE</div>
          <div style="background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: var(--radius-md); padding: 12px; font-size: 0.9rem; font-style: italic;">
            ${item.ocr_extracted_text}
          </div>
        </div>
      ` : ''}

      <!-- Evaluation Grid -->
      <div class="grid-2" style="margin-bottom: 16px;">
        <div style="background: var(--bg-input); padding: 12px; border-radius: var(--radius-md);">
          <div style="font-size: 0.78rem; color: var(--text-secondary); font-weight: 600;">SEVERITY SCORE</div>
          <div style="font-size: 1.6rem; font-weight: 800; color: ${toxPct > 60 ? 'var(--danger)' : 'var(--warning)'}; margin: 4px 0;">
            ${toxPct}%
          </div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${Math.round(item.confidence_score * 100)}% AI Confidence</div>
        </div>

        <div style="background: var(--bg-input); padding: 12px; border-radius: var(--radius-md);">
          <div style="font-size: 0.78rem; color: var(--text-secondary); font-weight: 600;">CURRENT STATUS</div>
          <div style="font-size: 1.2rem; font-weight: 700; margin: 4px 0;">${item.moderation_status}</div>
          <div style="font-size: 0.75rem; color: var(--text-muted);">${item.moderator_override ? '⚠️ Modified by Moderator' : '🤖 Initial AI Classification'}</div>
        </div>
      </div>

      <!-- Explanation & Keywords -->
      <div style="background: rgba(99, 102, 241, 0.08); border-left: 3px solid var(--primary); padding: 12px; border-radius: 0 var(--radius-md) var(--radius-md) 0; margin-bottom: 16px;">
        <div style="font-size: 0.8rem; font-weight: 600; color: var(--primary-light); margin-bottom: 4px;">AI REASONING</div>
        <div style="font-size: 0.85rem; color: var(--text-primary); line-height: 1.4;">${item.explanation}</div>
      </div>

      <!-- Human Moderator Action Controls -->
      <div style="border-top: 1px solid var(--border-color); padding-top: 16px; margin-top: 16px;">
        <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-primary); margin-bottom: 10px;">HUMAN MODERATOR OVERRIDE & ACTION:</div>

        <div class="form-group" style="margin-bottom: 12px;">
          <input type="text" id="modal-override-notes" class="form-input" placeholder="Optional audit reasoning / moderator notes..." value="${item.moderator_notes || ''}" />
        </div>

        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <button class="btn btn-success btn-sm btn-modal-action" data-action="approve">
            ✓ Approve as Safe
          </button>
          <button class="btn btn-danger btn-sm btn-modal-action" data-action="flag">
            ⚑ Flag & Restrict
          </button>
          <button class="btn btn-primary btn-sm btn-modal-action" data-action="report">
            🚨 Submit Platform Report
          </button>
          <button class="btn btn-secondary btn-sm btn-modal-action" data-action="mark_false_positive">
            ✕ False Positive
          </button>
          <button class="btn btn-secondary btn-sm btn-modal-action" data-action="resolve">
            ✔ Resolve
          </button>
        </div>
      </div>
    `;

    // Attach Action Handler Buttons
    body.querySelectorAll('.btn-modal-action').forEach(btn => {
      btn.addEventListener('click', async () => {
        const action = btn.dataset.action;
        const notes = body.querySelector('#modal-override-notes').value.trim();
        btn.disabled = true;
        btn.innerHTML = `Applying...`;

        try {
          if (action === 'report') {
            const firstCat = item.flagged_categories.find(c => c !== 'Non-toxic/Safe') || 'Abusive Behavior';
            await api.submitReport(item.id, firstCat, notes);
            window.showToast(`Submitted official platform report ticket!`, 'success');
          } else {
            await api.performModerationAction(item.id, action, notes);
            window.showToast(`Updated moderation status!`, 'success');
          }
          modal.classList.remove('active');
          loadQueue(container);
        } catch (err) {
          window.showToast(`Action failed: ${err.message}`, 'danger');
          btn.disabled = false;
        }
      });
    });

  } catch (err) {
    body.innerHTML = `<div style="color:var(--danger)">Error loading details: ${err.message}</div>`;
  }
}
