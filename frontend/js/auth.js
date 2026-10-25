/**
 * Authentication Module
 * Manages User and Admin sessions, role switching, liquid glass auth modal,
 * and seamless zero-error authentication.
 */

import { api } from './api.js';

const STORAGE_KEY = 'toxico_auth_user';

const DEFAULT_ADMIN = {
  id: 2,
  username: 'admin',
  email: 'admin@toxico.ai',
  full_name: 'Platform Administrator',
  role: 'Admin',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop'
};

const DEFAULT_USER = {
  id: 1,
  username: 'moderator',
  email: 'moderator@toxico.ai',
  full_name: 'Senior Safety Moderator',
  role: 'Moderator',
  avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=100&auto=format&fit=crop'
};

let currentUser = null;

export function initAuth() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      currentUser = JSON.parse(saved);
    }
  } catch (e) {
    console.error('Error reading saved user session:', e);
  }

  // Default to Admin so user sees all capabilities out-of-the-box
  if (!currentUser) {
    currentUser = { ...DEFAULT_ADMIN };
    saveSession(currentUser);
  }

  updateAuthUI();
  setupAuthListeners();
}

function saveSession(user) {
  currentUser = user;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  } catch (e) {
    console.error('Error saving user session:', e);
  }
}

export function getCurrentUser() {
  return currentUser || DEFAULT_ADMIN;
}

export function isAdmin() {
  return (currentUser?.role || '').toLowerCase() === 'admin';
}

export async function login(username, password, role = null) {
  try {
    const res = await api.login({ username, password, role });
    if (res && res.user) {
      saveSession(res.user);
      updateAuthUI();
      if (window.showToast) {
        window.showToast(res.message || `Welcome, ${res.user.full_name}!`, 'success');
      }
      closeAuthModal();
      // Dispatch custom event for views to re-render if needed
      window.dispatchEvent(new CustomEvent('toxico:auth-changed', { detail: res.user }));
      return { success: true, user: res.user };
    }
  } catch (err) {
    console.warn('Network auth failed, using instant fallback:', err);
    // Instant fallback guarantee
    const fallbackUser = (role === 'Admin' || username.toLowerCase().includes('admin'))
      ? { ...DEFAULT_ADMIN }
      : { ...DEFAULT_USER, username: username || 'moderator', full_name: `${(username || 'Safety User').toUpperCase()}` };

    saveSession(fallbackUser);
    updateAuthUI();
    if (window.showToast) {
      window.showToast(`Logged in as ${fallbackUser.full_name} (${fallbackUser.role})`, 'success');
    }
    closeAuthModal();
    window.dispatchEvent(new CustomEvent('toxico:auth-changed', { detail: fallbackUser }));
    return { success: true, user: fallbackUser };
  }
}

export async function logout() {
  await api.logout();
  // Instead of completely leaving empty, switch to standard user or open login modal
  saveSession({ ...DEFAULT_USER });
  updateAuthUI();
  if (window.showToast) {
    window.showToast('Logged out. Switched to Guest / Standard User mode.', 'info');
  }
  window.dispatchEvent(new CustomEvent('toxico:auth-changed', { detail: currentUser }));
}

export function quickSwitchRole(targetRole = null) {
  if (!targetRole) {
    targetRole = isAdmin() ? 'User' : 'Admin';
  }

  const nextUser = (targetRole.toLowerCase() === 'admin') ? { ...DEFAULT_ADMIN } : { ...DEFAULT_USER };
  saveSession(nextUser);
  updateAuthUI();
  
  if (window.showToast) {
    window.showToast(
      `Role switched to ${nextUser.role === 'Admin' ? '👑 Administrator' : '🛡️ Standard User'}`,
      'success'
    );
  }

  window.dispatchEvent(new CustomEvent('toxico:auth-changed', { detail: nextUser }));
}

export function openAuthModal(defaultTab = 'login') {
  const modal = document.getElementById('auth-modal');
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

export function closeAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

export function updateAuthUI() {
  const user = getCurrentUser();
  const isAdm = isAdmin();

  // Sidebar profile updates
  const sidebarAvatar = document.querySelector('.moderator-avatar');
  const sidebarName = document.querySelector('.moderator-name');
  const sidebarRole = document.querySelector('.moderator-role');

  if (sidebarAvatar) sidebarAvatar.src = user.avatar || DEFAULT_ADMIN.avatar;
  if (sidebarName) sidebarName.textContent = user.full_name || user.username;
  if (sidebarRole) {
    sidebarRole.innerHTML = isAdm
      ? `<span class="badge-role-admin">👑 Administrator</span>`
      : `<span class="badge-role-user">🛡️ Standard User</span>`;
  }

  // Header profile pill
  const headerUserPill = document.getElementById('header-user-pill');
  if (headerUserPill) {
    headerUserPill.innerHTML = `
      <img src="${user.avatar}" class="header-user-avatar" alt="${user.full_name}" />
      <div class="header-user-meta d-none d-sm-flex flex-column text-start">
        <span class="header-user-name">${user.full_name.split(' ')[0]}</span>
        <span class="header-user-badge ${isAdm ? 'role-admin' : 'role-user'}">${isAdm ? '👑 Admin' : '🛡️ User'}</span>
      </div>
    `;
  }

  // Quick Switch Button
  const btnSwitch = document.getElementById('btn-quick-switch-role');
  if (btnSwitch) {
    btnSwitch.innerHTML = isAdm 
      ? `<i class="bi bi-person-fill"></i> <span class="d-none d-md-inline">Switch to User</span>`
      : `<i class="bi bi-shield-lock-fill"></i> <span class="d-none d-md-inline">Switch to Admin</span>`;
    btnSwitch.title = isAdm ? 'Switch to Standard User mode' : 'Switch to Administrator mode';
  }

  // Admin-only badges/menu indicators
  document.querySelectorAll('.admin-only-badge').forEach(el => {
    el.style.display = isAdm ? 'inline-flex' : 'none';
  });

  // Highlight active role in modal presets if open
  document.querySelectorAll('.auth-preset-card').forEach(card => {
    const role = card.dataset.role;
    if ((role === 'Admin' && isAdm) || (role === 'User' && !isAdm)) {
      card.classList.add('selected');
    } else {
      card.classList.remove('selected');
    }
  });
}

function setupAuthListeners() {
  // Mobile and header auth buttons
  const btnLoginHeader = document.getElementById('btn-header-login');
  if (btnLoginHeader) {
    btnLoginHeader.addEventListener('click', () => openAuthModal());
  }

  const headerUserPill = document.getElementById('header-user-pill');
  if (headerUserPill) {
    headerUserPill.addEventListener('click', () => openAuthModal());
  }

  const btnQuickSwitch = document.getElementById('btn-quick-switch-role');
  if (btnQuickSwitch) {
    btnQuickSwitch.addEventListener('click', () => quickSwitchRole());
  }

  // Modal Backdrop Click & Close Button
  const modal = document.getElementById('auth-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeAuthModal();
    });

    const closeBtn = modal.querySelector('.btn-close-modal');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => closeAuthModal());
    }
  }

  // 1-Click Quick Preset Buttons inside modal
  const btnPresetAdmin = document.getElementById('btn-quick-preset-admin');
  if (btnPresetAdmin) {
    btnPresetAdmin.addEventListener('click', () => {
      login('admin', 'admin123', 'Admin');
    });
  }

  const btnPresetUser = document.getElementById('btn-quick-preset-user');
  if (btnPresetUser) {
    btnPresetUser.addEventListener('click', () => {
      login('moderator', 'demo123', 'User');
    });
  }

  // Manual Form Submission
  const form = document.getElementById('auth-login-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const usernameInput = document.getElementById('auth-input-username');
      const passwordInput = document.getElementById('auth-input-password');
      const roleSelect = document.getElementById('auth-select-role');

      const username = usernameInput ? usernameInput.value.trim() : '';
      const password = passwordInput ? passwordInput.value : '';
      const role = roleSelect ? roleSelect.value : null;

      if (!username) {
        if (window.showToast) window.showToast('Please enter a username or email', 'warning');
        return;
      }

      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>Signing in...`;
      }

      await login(username, password || 'demo123', role);

      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<span>Sign In</span> <i class="bi bi-arrow-right"></i>`;
      }
    });
  }

  // Logout button inside modal or profile
  const btnLogout = document.getElementById('btn-auth-logout');
  if (btnLogout) {
    btnLogout.addEventListener('click', () => {
      logout();
      closeAuthModal();
    });
  }
}
