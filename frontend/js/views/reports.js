/**
 * Reports View
 * Formal compliance and platform escalation reports with export capabilities.
 */

import { api } from '../api.js';

export async function renderReports(container) {
  container.innerHTML = `
    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-3 mb-4">
      <div>
        <h2 style="font-size: 1.6rem; font-weight: 700;">Platform Compliance & Abuse Reports</h2>
        <p style="color: var(--text-secondary); font-size: 0.9rem;" class="mb-0">
          Official moderation tickets submitted to social platform safety desks with legal evidence bundles.
        </p>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <a href="${api.getExportUrl('csv')}" download="moderation_reports.csv" class="btn btn-secondary">
          <i class="bi bi-filetype-csv me-1"></i>
          Export CSV
        </a>
        <a href="${api.getExportUrl('json')}" download="moderation_reports.json" class="btn btn-secondary">
          <i class="bi bi-filetype-json me-1"></i>
          Export JSON
        </a>
      </div>
    </div>

    <!-- Reports Table Card -->
    <div class="card">
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Ticket ID</th>
              <th>Platform</th>
              <th>Violation Type</th>
              <th>Severity</th>
              <th>Offending Author</th>
              <th>Language</th>
              <th>Status</th>
              <th>Filed At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="reports-table-body">
            <tr><td colspan="9" style="text-align:center; padding: 24px;">Loading platform reports...</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Evidence Modal -->
    <div id="modal-evidence" class="modal-backdrop-custom">
      <div class="liquid-glass-modal" style="max-width: 600px;">
        <div class="modal-header-glass">
          <div class="d-flex align-items-center gap-2">
            <span class="card-title mb-0">Report Evidence Bundle</span>
            <span id="evidence-ticket-badge" class="badge badge-purple">TKT</span>
          </div>
          <button class="btn-close-modal" onclick="document.getElementById('modal-evidence').classList.remove('active')"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="modal-body-glass" id="modal-evidence-body">
          Loading evidence...
        </div>
      </div>
    </div>
  `;

  try {
    const res = await api.getReports();
    const reports = res.reports;
    const tbody = container.querySelector('#reports-table-body');

    if (!reports || reports.length === 0) {
      tbody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 30px; color: var(--text-muted);">No reports filed yet. Use the Moderation Queue to submit platform reports.</td></tr>`;
      return;
    }

    tbody.innerHTML = reports.map(r => {
      let statusBadge = `<span class="badge badge-info">${r.platform_report_status}</span>`;
      if (r.platform_report_status === 'Content Removed') statusBadge = `<span class="badge badge-success">Content Removed</span>`;
      if (r.platform_report_status === 'Submitted') statusBadge = `<span class="badge badge-warning">Submitted</span>`;

      return `
        <tr>
          <td><span style="font-family: monospace; font-weight: 700; color: var(--primary-light);">${r.report_ticket_id}</span></td>
          <td><span style="text-transform: capitalize; font-weight: 600;">${r.platform}</span></td>
          <td><span class="badge badge-danger" style="font-size:0.75rem;">${r.violation_category}</span></td>
          <td><span class="badge badge-${r.severity === 'Critical' ? 'danger' : 'warning'}">${r.severity}</span></td>
          <td>${r.author_handle || '@unknown'}</td>
          <td><span class="badge badge-purple">${r.detected_language_name}</span></td>
          <td>${statusBadge}</td>
          <td style="font-size: 0.78rem; color: var(--text-muted);">${new Date(r.filed_at).toLocaleDateString()}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick='window.viewReportEvidence(${JSON.stringify(r).replace(/'/g, "&#39;")})'>Evidence</button>
          </td>
        </tr>
      `;
    }).join('');

    window.viewReportEvidence = (rep) => {
      const modal = container.querySelector('#modal-evidence');
      container.querySelector('#evidence-ticket-badge').textContent = rep.report_ticket_id;
      const body = container.querySelector('#modal-evidence-body');

      const ev = typeof rep.evidence_payload === 'string' ? JSON.parse(rep.evidence_payload) : rep.evidence_payload;

      body.innerHTML = `
        <div style="background: var(--bg-input); padding: 12px; border-radius: var(--radius-md); margin-bottom: 14px;">
          <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Platform Dispatch Target</div>
          <div style="font-size: 1.1rem; font-weight: 700; text-transform: capitalize;">${rep.platform} Trust & Safety API</div>
        </div>

        <div style="margin-bottom: 14px;">
          <div style="font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px;">INCIDENT EVIDENCE SNIPPET</div>
          <div style="background: var(--bg-card-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px; font-size: 0.92rem;">
            "${rep.original_text}"
          </div>
        </div>

        <div style="background: rgba(99, 102, 241, 0.08); border-left: 3px solid var(--primary); padding: 10px 14px; border-radius: 0 var(--radius-md) var(--radius-md) 0; margin-bottom: 14px;">
          <div style="font-size: 0.78rem; font-weight: 600; color: var(--primary-light);">VIOLATION SUMMARY</div>
          <div style="font-size: 0.85rem; color: var(--text-primary); margin-top: 4px;">
            Violation Category: <strong>${rep.violation_category}</strong> (Severity: ${rep.severity})
          </div>
          ${ev && ev.custom_notes ? `<div style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 4px;">Moderator Notes: "${ev.custom_notes}"</div>` : ''}
        </div>

        <div style="font-size: 0.75rem; color: var(--text-muted); display:flex; justify-content:space-between;">
          <span>Filed by: ${rep.filed_by}</span>
          <span>Status: ${rep.platform_report_status}</span>
        </div>
      `;

      modal.classList.add('active');
    };

  } catch (err) {
    console.error("Reports error:", err);
  }
}
