/**
 * App Router and Orchestrator
 * Single Page Application Router, Multi-Device Responsive Controller & Auth Orchestrator
 */

import { renderDashboard } from './views/dashboard.js';
import { renderAnalyze } from './views/analyze.js';
import { renderModeration } from './views/moderation.js';
import { renderReports } from './views/reports.js';
import { renderIntegrations } from './views/integrations.js';
import { renderAnalytics } from './views/analytics.js';
import { renderSettings } from './views/settings.js';
import { 
  initAuth, 
  getCurrentUser, 
  isAdmin, 
  openAuthModal, 
  closeAuthModal, 
  quickSwitchRole 
} from './auth.js';

// Route Map
const routes = {
  dashboard: { title: 'Safety Operations Dashboard', render: renderDashboard },
  analyze: { title: 'Multilingual Toxicity Analyzer', render: renderAnalyze },
  moderation: { title: 'Human-in-the-Loop Moderation Queue', render: renderModeration },
  reports: { title: 'Platform Compliance Reports', render: renderReports },
  integrations: { title: 'Social Media Integrations', render: renderIntegrations },
  analytics: { title: 'Analytics & Threat Trends', render: renderAnalytics },
  settings: { title: 'Settings & Model Sensitivity', render: renderSettings }
};

let currentPage = 'dashboard';

export function navigateTo(page, params = null) {
  if (!routes[page]) page = 'dashboard';
  currentPage = page;

  // Update URL hash
  window.location.hash = page;

  // Update sidebar navigation styling
  document.querySelectorAll('.nav-item').forEach(item => {
    if (item.dataset.page === page) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Update mobile bottom dock styling
  document.querySelectorAll('.dock-item').forEach(item => {
    if (item.dataset.page === page) {
      item.classList.add('active');
    } else if (item.id !== 'dock-auth') {
      item.classList.remove('active');
    }
  });

  // Update header title
  const titleElem = document.getElementById('header-title');
  if (titleElem) titleElem.textContent = routes[page].title;

  // Render view
  const contentArea = document.getElementById('view-content-area');
  contentArea.innerHTML = `
    <div class="text-center py-5">
      <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
        <span class="visually-hidden">Loading view...</span>
      </div>
      <div class="mt-3 text-secondary" style="font-size: 0.95rem;">Loading ${routes[page].title}...</div>
    </div>
  `;

  routes[page].render(contentArea, params);

  // Auto-close mobile sidebar drawer upon navigation
  closeMobileSidebar();

  // Scroll to top of content
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // If params were provided for analyze page
  if (page === 'analyze' && params && params.text) {
    setTimeout(() => {
      const txt = document.getElementById('input-content-text');
      const sel = document.getElementById('select-lang');
      if (txt) txt.value = params.text;
      if (sel && params.lang) sel.value = params.lang;
      const runBtn = document.getElementById('btn-run-analysis');
      if (runBtn) runBtn.click();
    }, 120);
  }
}

// Global Toast System (Liquid Glass Aesthetic)
window.showToast = function(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast`;

  let icon = 'ℹ️';
  let borderColor = 'var(--info)';
  if (type === 'success') { icon = '✓'; borderColor = 'var(--success)'; }
  if (type === 'danger') { icon = '⚠️'; borderColor = 'var(--danger)'; }
  if (type === 'warning') { icon = '⚡'; borderColor = 'var(--warning)'; }

  toast.style.borderLeft = `4px solid ${borderColor}`;
  toast.innerHTML = `
    <span style="font-weight:bold; font-size: 1.1rem;">${icon}</span>
    <span style="flex:1;">${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
};

window.navigateTo = navigateTo;

// Device Dimensions Live Detection (Android, iOS, Tab, Laptop, Desktop)
function setupDeviceDimensionsTracker() {
  const label = document.getElementById('device-dim-label');
  const pill = document.getElementById('device-dimension-pill');
  if (!label || !pill) return;

  function update() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    const ua = navigator.userAgent;
    const isIOS = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    const isAndroid = /Android/.test(ua);

    let deviceProfile = 'Desktop';
    let iconClass = 'bi-display';

    if (width <= 480) {
      deviceProfile = isIOS ? 'iPhone (iOS)' : (isAndroid ? 'Android Phone' : 'Mobile Phone');
      iconClass = 'bi-phone';
    } else if (width <= 768) {
      deviceProfile = isIOS ? 'iOS Phablet' : (isAndroid ? 'Android Phablet' : 'Compact Tab');
      iconClass = 'bi-phone';
    } else if (width <= 1024) {
      deviceProfile = isIOS ? 'iPad (iOS)' : (isAndroid ? 'Android Tablet' : 'Tablet');
      iconClass = 'bi-tablet';
    } else if (width <= 1440) {
      deviceProfile = 'Laptop';
      iconClass = 'bi-laptop';
    } else {
      deviceProfile = 'Desktop Monitor';
      iconClass = 'bi-display';
    }

    label.innerHTML = `${width}×${height} • ${deviceProfile}`;
    const iconElem = pill.querySelector('i');
    if (iconElem) {
      iconElem.className = `bi ${iconClass} me-1 text-info`;
    }
  }

  window.addEventListener('resize', update);
  window.addEventListener('orientationchange', update);
  update();
}

// Mobile Sidebar Drawer Management
function openMobileSidebar() {
  const sidebar = document.getElementById('app-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (sidebar) sidebar.classList.add('open');
  if (backdrop) backdrop.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeMobileSidebar() {
  const sidebar = document.getElementById('app-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (sidebar) sidebar.classList.remove('open');
  if (backdrop) backdrop.classList.remove('active');
  document.body.style.overflow = '';
}

function setupMobileNavigation() {
  const btnMobileMenu = document.getElementById('btn-mobile-menu');
  const btnCloseSidebar = document.getElementById('btn-close-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');

  if (btnMobileMenu) {
    btnMobileMenu.addEventListener('click', openMobileSidebar);
  }

  if (btnCloseSidebar) {
    btnCloseSidebar.addEventListener('click', closeMobileSidebar);
  }

  if (backdrop) {
    backdrop.addEventListener('click', closeMobileSidebar);
  }

  // Mobile Bottom Dock Items
  document.querySelectorAll('.dock-item').forEach(dockBtn => {
    dockBtn.addEventListener('click', (e) => {
      e.preventDefault();
      if (dockBtn.id === 'dock-auth') {
        openAuthModal();
      } else if (dockBtn.dataset.page) {
        navigateTo(dockBtn.dataset.page);
      }
    });
  });

  // Sidebar profile card click
  const profileCard = document.getElementById('sidebar-profile-card');
  if (profileCard) {
    profileCard.addEventListener('click', () => {
      openAuthModal();
      closeMobileSidebar();
    });
  }

  // Toggle Password Visibility in Modal
  const btnTogglePass = document.getElementById('btn-toggle-password');
  if (btnTogglePass) {
    btnTogglePass.addEventListener('click', () => {
      const passInput = document.getElementById('auth-input-password');
      if (passInput) {
        const isPass = passInput.type === 'password';
        passInput.type = isPass ? 'text' : 'password';
        btnTogglePass.innerHTML = isPass ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
      }
    });
  }
}

// Theme Toggle (Dark & Light Liquid Glass)
function setupThemeToggle() {
  const toggleBtn = document.getElementById('btn-theme-toggle');
  if (!toggleBtn) return;

  const currentTheme = localStorage.getItem('toxico_theme') || localStorage.getItem('safeguard_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', currentTheme);
  updateThemeIcon(toggleBtn, currentTheme);

  toggleBtn.addEventListener('click', () => {
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const newTheme = isDark ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('toxico_theme', newTheme);
    updateThemeIcon(toggleBtn, newTheme);
  });
}

function updateThemeIcon(btn, theme) {
  btn.innerHTML = theme === 'light'
    ? '<i class="bi bi-sun-fill text-warning"></i>'
    : '<i class="bi bi-moon-stars-fill text-info"></i>';
}

// App Initialization
document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Auth Subsystem
  initAuth();

  // 2. Initialize Theme Subsystem
  setupThemeToggle();

  // 3. Initialize Multi-Device Dimensions & Viewport Tracker
  setupDeviceDimensionsTracker();

  // 4. Initialize Mobile Navigation & Drawers
  setupMobileNavigation();

  // 5. Sidebar Navigation Click Handlers
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const page = item.dataset.page;
      navigateTo(page);
    });
  });

  // 6. Handle URL hash on initial load
  const initialHash = window.location.hash.replace('#', '');
  if (initialHash && routes[initialHash]) {
    navigateTo(initialHash);
  } else {
    navigateTo('dashboard');
  }

  // 7. Re-render view if auth changes
  window.addEventListener('toxico:auth-changed', (e) => {
    // If user switched role, refresh active view so any permission-dependent components update
    if (currentPage === 'settings' || currentPage === 'reports') {
      navigateTo(currentPage);
    }
  });
});
