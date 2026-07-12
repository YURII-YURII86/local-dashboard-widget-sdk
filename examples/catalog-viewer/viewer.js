(function () {
  'use strict';

  const data = window.LDW_CATALOG || { widgets: [], presets: [], summary: { widgets: 0, presets: 0, renderers: [] } };
  const cards = [
    ...data.widgets.map((item) => ({ kind: 'widget', ...item, id: item.contract.id, title: item.contract.title, status: item.contract.status, renderer: item.contract.renderer.kind })),
    ...data.presets.map((item) => ({ kind: 'preset', ...item, id: item.contract.id, title: item.contract.title, status: 'preset', renderer: item.contract.renderer })),
  ];

  const els = {
    stats: document.querySelector('#catalog-stats'),
    grid: document.querySelector('#catalog-grid'),
    search: document.querySelector('#search'),
    renderer: document.querySelector('#renderer-filter'),
    status: document.querySelector('#status-filter'),
    detailKind: document.querySelector('#detail-kind'),
    detailTitle: document.querySelector('#detail-title'),
    detailMeta: document.querySelector('#detail-meta'),
    detailJson: document.querySelector('#detail-json code'),
  };

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
  }

  function renderStats() {
    els.stats.innerHTML = [
      `<span class="stat"><strong>${data.summary.widgets}</strong>widgets</span>`,
      `<span class="stat"><strong>${data.summary.presets}</strong>presets</span>`,
      `<span class="stat"><strong>${data.summary.renderers.length}</strong>renderers</span>`,
    ].join('');
  }

  function renderRendererOptions() {
    for (const renderer of data.summary.renderers) {
      const option = document.createElement('option');
      option.value = renderer;
      option.textContent = renderer;
      els.renderer.appendChild(option);
    }
  }

  function matches(card) {
    const q = els.search.value.trim().toLowerCase();
    const renderer = els.renderer.value;
    const status = els.status.value;
    const haystack = `${card.id} ${card.title} ${card.status} ${card.renderer} ${JSON.stringify(card.contract.tags || [])}`.toLowerCase();
    return (!q || haystack.includes(q)) && (renderer === 'all' || card.renderer === renderer) && (status === 'all' || card.status === status);
  }

  function renderCards() {
    const visible = cards.filter(matches);
    if (!visible.length) {
      els.grid.innerHTML = '<div class="empty">No contracts match the current filters.</div>';
      return;
    }
    els.grid.innerHTML = visible.map((card, index) => `
      <article class="card" tabindex="0" data-index="${index}" data-id="${escapeHtml(card.id)}">
        <p class="eyebrow">${escapeHtml(card.kind)} · ${escapeHtml(card.renderer)}</p>
        <h3>${escapeHtml(card.title)}</h3>
        <p>${escapeHtml(card.path)}</p>
        <div class="badge-row">
          <span class="badge ${escapeHtml(card.status)}">${escapeHtml(card.status)}</span>
          <span class="badge">${escapeHtml(card.id)}</span>
        </div>
      </article>`).join('');
    for (const node of els.grid.querySelectorAll('.card')) {
      const card = visible[Number(node.dataset.index)];
      node.addEventListener('click', () => selectCard(card, node));
      node.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          selectCard(card, node);
        }
      });
    }
    selectCard(visible[0], els.grid.querySelector('.card'));
  }

  function selectCard(card, node) {
    for (const item of els.grid.querySelectorAll('.card')) item.classList.remove('is-selected');
    if (node) node.classList.add('is-selected');
    els.detailKind.textContent = `${card.kind} · ${card.renderer} · ${card.status}`;
    els.detailTitle.textContent = card.title;
    els.detailMeta.textContent = `${card.id} · ${card.path}`;
    els.detailJson.textContent = JSON.stringify(card.contract, null, 2);
  }

  function bind() {
    for (const el of [els.search, els.renderer, els.status]) el.addEventListener('input', renderCards);
  }

  renderStats();
  renderRendererOptions();
  bind();
  renderCards();
  window.LDW_CATALOG_VIEWER = { cards, renderCards, selectCard };
})();
