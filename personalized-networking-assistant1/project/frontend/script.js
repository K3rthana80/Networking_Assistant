/**
 * Personalized Networking Assistant — frontend logic.
 * Shared across every page: theming, nav, toasts, scroll reveals,
 * plus page-specific handlers guarded by element existence checks
 * so this one file can be safely included everywhere.
 */

const API_BASE = window.location.protocol === 'file:'
  ? 'http://127.0.0.1:8000'
  : `${window.location.protocol}//${window.location.hostname}:8000`;

// ---------------------------------------------------------------------
// Theme toggle (persisted in-memory for the session)
// ---------------------------------------------------------------------

function initTheme() {
  const root = document.documentElement;
  const saved = window.__nwaTheme || 'dark';
  root.setAttribute('data-theme', saved);

  document.querySelectorAll('.theme-toggle').forEach((btn) => {
    updateThemeIcon(btn, saved);
    btn.addEventListener('click', () => {
      const current = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      root.setAttribute('data-theme', current);
      window.__nwaTheme = current;
      document.querySelectorAll('.theme-toggle').forEach((b) => updateThemeIcon(b, current));
    });
  });
}

function updateThemeIcon(btn, theme) {
  btn.textContent = theme === 'light' ? '🌙' : '☀️';
  btn.setAttribute('aria-label', theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode');
}

// ---------------------------------------------------------------------
// Mobile nav toggle
// ---------------------------------------------------------------------

function initNav() {
  const toggleBtn = document.querySelector('.nav-toggle-btn');
  const links = document.querySelector('.nav-links');
  if (!toggleBtn || !links) return;
  toggleBtn.addEventListener('click', () => {
    links.classList.toggle('open');
    toggleBtn.textContent = links.classList.contains('open') ? '✕' : '☰';
  });
  links.querySelectorAll('a').forEach((a) =>
    a.addEventListener('click', () => {
      links.classList.remove('open');
      toggleBtn.textContent = '☰';
    })
  );
}

// ---------------------------------------------------------------------
// Toast notifications
// ---------------------------------------------------------------------

function ensureToastStack() {
  let stack = document.querySelector('.toast-stack');
  if (!stack) {
    stack = document.createElement('div');
    stack.className = 'toast-stack';
    document.body.appendChild(stack);
  }
  return stack;
}

function showToast(message, type = 'success') {
  const stack = ensureToastStack();
  const toast = document.createElement('div');
  toast.className = `toast${type === 'error' ? ' error' : ''}`;
  toast.textContent = message;
  stack.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// ---------------------------------------------------------------------
// Scroll reveal
// ---------------------------------------------------------------------

function initReveal() {
  const items = document.querySelectorAll('.reveal');
  if (!items.length) return;
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );
  items.forEach((item) => observer.observe(item));
}

// ---------------------------------------------------------------------
// Fetch helper
// ---------------------------------------------------------------------

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  let body = null;
  try {
    body = await response.json();
  } catch (err) {
    body = null;
  }
  if (!response.ok) {
    const message =
      (body && (body.message || body.detail)) ||
      `Request failed with status ${response.status}`;
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }
  return body;
}

// ---------------------------------------------------------------------
// Networking Assistant page
// ---------------------------------------------------------------------

function initNetworkingAssistant() {
  const form = document.querySelector('#assistant-form');
  if (!form) return;

  const loader = document.querySelector('#assistant-loader');
  const resultsWrap = document.querySelector('#assistant-results');
  const themeChips = document.querySelector('#theme-chips');
  const suggestionsList = document.querySelector('#suggestions-list');
  const generateBtn = document.querySelector('#generate-btn');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const description = document.querySelector('#event-description').value.trim();
    const interestsRaw = document.querySelector('#user-interests').value.trim();
    const interests = interestsRaw
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    if (!description || interests.length === 0) {
      showToast('Please add an event description and at least one interest.', 'error');
      return;
    }

    loader.classList.add('active');
    resultsWrap.style.display = 'none';
    generateBtn.disabled = true;

    try {
      const data = await apiRequest('/generate-conversation', {
        method: 'POST',
        body: JSON.stringify({ description, interests }),
      });

      themeChips.innerHTML = data.themes.map((t) => `<span class="chip">${escapeHtml(t)}</span>`).join('');
      suggestionsList.innerHTML = data.suggestions
        .map(
          (s, i) => `
        <div class="suggestion-card" data-suggestion="${escapeHtml(s)}">
          <span class="suggestion-quote">&ldquo;</span>
          <span class="suggestion-text">${escapeHtml(s)}</span>
          <span class="suggestion-feedback">
            <button class="icon-btn like-btn" title="Like" aria-label="Like this suggestion">&#128077;</button>
            <button class="icon-btn dislike-btn" title="Dislike" aria-label="Dislike this suggestion">&#128078;</button>
          </span>
        </div>`
        )
        .join('');

      resultsWrap.style.display = 'block';
      showToast('Conversation starters generated.');
      attachFeedbackHandlers();
    } catch (err) {
      showToast(err.message || 'Something went wrong. Please try again.', 'error');
    } finally {
      loader.classList.remove('active');
      generateBtn.disabled = false;
    }
  });
}

function attachFeedbackHandlers() {
  document.querySelectorAll('.like-btn').forEach((btn) => {
    btn.addEventListener('click', () => submitFeedback(btn, 'like'));
  });
  document.querySelectorAll('.dislike-btn').forEach((btn) => {
    btn.addEventListener('click', () => submitFeedback(btn, 'dislike'));
  });
}

async function submitFeedback(btn, action) {
  const card = btn.closest('.suggestion-card');
  const suggestion = card?.dataset.suggestion;
  if (!suggestion) return;

  try {
    await apiRequest('/feedback', {
      method: 'POST',
      body: JSON.stringify({ suggestion, action }),
    });
    const likeBtn = card.querySelector('.like-btn');
    const dislikeBtn = card.querySelector('.dislike-btn');
    likeBtn.classList.toggle('liked', action === 'like');
    dislikeBtn.classList.toggle('disliked', action === 'dislike');
    showToast(action === 'like' ? 'Marked as liked.' : 'Marked as disliked.');
  } catch (err) {
    showToast(err.message || 'Could not save feedback.', 'error');
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------
// Fact Checker page
// ---------------------------------------------------------------------

function initFactChecker() {
  const form = document.querySelector('#fact-form');
  if (!form) return;

  const loader = document.querySelector('#fact-loader');
  const resultWrap = document.querySelector('#fact-result');
  const verifyBtn = document.querySelector('#verify-btn');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const query = document.querySelector('#fact-query').value.trim();
    if (!query) {
      showToast('Enter a topic to verify.', 'error');
      return;
    }

    loader.classList.add('active');
    resultWrap.innerHTML = '';
    verifyBtn.disabled = true;

    try {
      const data = await apiRequest('/fact-check', {
        method: 'POST',
        body: JSON.stringify({ query }),
      });

      if (data.found) {
        resultWrap.innerHTML = `
          <div class="fact-card">
            <h3>${escapeHtml(data.title || query)}</h3>
            <p>${escapeHtml(data.summary)}</p>
            ${data.url ? `<a href="${data.url}" target="_blank" rel="noopener">Read more on Wikipedia →</a>` : ''}
          </div>`;
      } else {
        resultWrap.innerHTML = `
          <div class="fact-card not-found">
            <h3>No confirmed match</h3>
            <p>${escapeHtml(data.summary)}</p>
          </div>`;
      }
    } catch (err) {
      showToast(err.message || 'Fact check failed.', 'error');
    } finally {
      loader.classList.remove('active');
      verifyBtn.disabled = false;
    }
  });
}

// ---------------------------------------------------------------------
// History page
// ---------------------------------------------------------------------

function initHistoryPage() {
  const list = document.querySelector('#history-list');
  if (!list) return;

  const searchInput = document.querySelector('#history-search');
  let allEntries = [];

  function render(entries) {
    if (!entries.length) {
      list.innerHTML = `
        <div class="empty-state">
          <div class="glyph">🗂️</div>
          <p>No conversations yet. Generate some starters on the Networking Assistant page.</p>
        </div>`;
      return;
    }

    list.innerHTML = entries
      .map((entry) => {
        const date = new Date(entry.timestamp);
        const formatted = isNaN(date.getTime()) ? entry.timestamp : date.toLocaleString();
        return `
        <div class="history-card">
          <div class="history-card-head">
            <h3>${escapeHtml(entry.event)}</h3>
            <span class="history-date">${escapeHtml(formatted)}</span>
          </div>
          <div class="theme-chips">
            ${entry.themes.map((t) => `<span class="chip">${escapeHtml(t)}</span>`).join('')}
          </div>
          <ul>
            ${entry.suggestions.map((s) => `<li>${escapeHtml(s)}</li>`).join('')}
          </ul>
        </div>`;
      })
      .join('');
  }

  async function load() {
    list.innerHTML = `
      <div class="loader active">
        <span class="spinner"></span> Loading conversation history…
      </div>`;
    try {
      const data = await apiRequest('/history');
      allEntries = data.history || [];
      render(allEntries);
    } catch (err) {
      list.innerHTML = `<div class="empty-state"><p>Couldn't load history: ${escapeHtml(err.message)}</p></div>`;
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.trim().toLowerCase();
      if (!q) {
        render(allEntries);
        return;
      }
      const filtered = allEntries.filter((entry) => {
        const haystack = [entry.event, ...(entry.themes || []), ...(entry.suggestions || [])]
          .join(' ')
          .toLowerCase();
        return haystack.includes(q);
      });
      render(filtered);
    });
  }

  load();
}

// ---------------------------------------------------------------------
// Feedback page
// ---------------------------------------------------------------------

function initFeedbackPage() {
  const likedCol = document.querySelector('#liked-list');
  const dislikedCol = document.querySelector('#disliked-list');
  if (!likedCol || !dislikedCol) return;

  const filterSelect = document.querySelector('#feedback-filter');
  let allFeedback = [];

  function render() {
    const filterValue = filterSelect ? filterSelect.value : 'all';

    const liked = allFeedback.filter((f) => f.action === 'like');
    const disliked = allFeedback.filter((f) => f.action === 'dislike');

    likedCol.parentElement.style.display = filterValue === 'dislike' ? 'none' : 'block';
    dislikedCol.parentElement.style.display = filterValue === 'like' ? 'none' : 'block';

    likedCol.innerHTML = liked.length
      ? liked.map(renderFeedbackItem).join('')
      : '<p class="hint">No liked suggestions yet.</p>';

    dislikedCol.innerHTML = disliked.length
      ? disliked.map(renderFeedbackItem).join('')
      : '<p class="hint">No disliked suggestions yet.</p>';
  }

  function renderFeedbackItem(item) {
    const date = new Date(item.timestamp);
    const formatted = isNaN(date.getTime()) ? item.timestamp : date.toLocaleString();
    return `
      <div class="feedback-item">
        ${escapeHtml(item.suggestion)}
        <span class="fdate">${escapeHtml(formatted)}</span>
      </div>`;
  }

  async function load() {
    try {
      const data = await apiRequest('/feedback');
      allFeedback = data.feedback || [];
      render();
    } catch (err) {
      likedCol.innerHTML = `<p class="hint">Couldn't load feedback: ${escapeHtml(err.message)}</p>`;
    }
  }

  if (filterSelect) {
    filterSelect.addEventListener('change', render);
  }

  load();
}

// ---------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initNav();
  initReveal();
  initNetworkingAssistant();
  initFactChecker();
  initHistoryPage();
  initFeedbackPage();
});
