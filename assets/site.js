(() => {
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];

  // Project filters
  const filters = $('#project-filters');
  if (filters) {
    const cards = $$('.filterable-project');
    const status = $('#project-filter-status');
    const applyFilter = (wanted, btn) => {
      $$('.filter', filters).forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
      let visible = 0;
      cards.forEach(card => {
        const tags = (card.dataset.tags || '').split(/\s+/).filter(Boolean);
        const show = wanted === 'all' || tags.includes(wanted);
        card.hidden = !show;
        if (show) visible++;
      });
      if (status) {
        const label = btn ? btn.textContent.trim() : 'All';
        status.textContent = `${visible} project${visible === 1 ? '' : 's'} shown for ${label}.`;
      }
    };
    filters.addEventListener('click', event => {
      const btn = event.target.closest('.filter');
      if (!btn || !filters.contains(btn)) return;
      applyFilter(btn.dataset.filter || 'all', btn);
    });
    const requested = new URLSearchParams(location.search).get('filter');
    const requestedBtn = requested ? $(`.filter[data-filter="${CSS.escape(requested)}"]`, filters) : null;
    const allBtn = $('.filter[data-filter="all"]', filters);
    applyFilter(requested && requestedBtn ? requested : 'all', requestedBtn || allBtn);
  }

  // Keyboard command palette. No cursor or scroll animation.
  const overlay = $('#command-palette');
  const input = $('#command-search');
  const results = $('#command-results');
  if (overlay && input && results) {
    const links = $$('.command-source a');
    const open = () => { overlay.classList.add('open'); input.value = ''; render(''); input.focus(); };
    const close = () => overlay.classList.remove('open');
    const render = query => {
      const q = query.trim().toLowerCase();
      results.innerHTML = '';
      links
        .filter(a => !q || a.textContent.toLowerCase().includes(q))
        .forEach(a => { const clone = a.cloneNode(true); clone.addEventListener('click', close); results.appendChild(clone); });
    };
    input.addEventListener('input', e => render(e.target.value));
    overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); open(); }
      if (e.key === 'Escape') close();
    });
  }

  // Optional live GitHub repository list. Falls back to static HTML when blocked or rate-limited.
  const live = $('#github-repos');
  if (live) {
    fetch('https://api.github.com/users/Cooper-Src/repos?per_page=100&sort=updated', { headers: { Accept: 'application/vnd.github+json' } })
      .then(r => r.ok ? r.json() : Promise.reject(new Error('GitHub request failed')))
      .then(repos => {
        const wanted = new Set(['src', 'src-registry', 'src-init', 'fsf', 'RustRadio']);
        const selected = repos.filter(r => wanted.has(r.name));
        if (!selected.length) return;
        live.innerHTML = selected.map(r => `<a class="repo-card" href="${r.html_url}" target="_blank" rel="noopener noreferrer"><strong>${escapeHtml(r.name)}</strong><small>${escapeHtml(r.language || 'Repository')} · Updated ${new Date(r.updated_at).toLocaleDateString()}</small></a>`).join('');
      })
      .catch(() => {});
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
  }
})();
