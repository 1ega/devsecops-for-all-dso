/* Horizontal roadmap with a persistent detail panel on the right. */
(function () {
  'use strict';
  const D = window.ROADMAP;
  const $ = (selector, root = document) => root.querySelector(selector);
  const map = $('#roadmap');
  const scroller = $('#roadmap-scroll');
  const inspector = $('#inspector');
  const jump = $('#jump');
  const search = $('#search');
  const searchResults = $('#search-results');
  const scrim = $('#scrim');
  const stageById = Object.fromEntries(D.stages.map(stage => [stage.id, stage]));
  const areaById = Object.fromEntries(D.areas.map(area => [area.id, area]));
  const areaOfStage = Object.fromEntries(D.areas.flatMap(area => area.stages.map(id => [id, area])));
  const tools = D.stages.flatMap(stage => stage.tools.map(tool => ({ ...tool, stage })));
  const toolById = Object.fromEntries(tools.map(tool => [tool.id, tool]));
  const controlById = Object.fromEntries((D.controls || []).map(control => [control.id, control]));
  const STORE = 'dso-adopted';
  let adopted;
  try { adopted = new Set(JSON.parse(localStorage.getItem(STORE) || '[]')); }
  catch (e) { adopted = new Set(); }
  let selected = { kind: null, id: null };

  const esc = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const count = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;
  const motion = () => matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
  const save = () => { try { localStorage.setItem(STORE, JSON.stringify([...adopted])); } catch (e) {} };
  function progress() {
    $('#progress-done').textContent = tools.filter(tool => adopted.has(tool.id)).length;
    $('#progress-total').textContent = tools.length;
  }
  function renderJump() {
    jump.innerHTML = `<span>Jump to</span>${D.areas.map((area, i) => `<button type="button" data-jump="${area.id}"><b>${String(i + 1).padStart(2, '0')}</b> ${esc(area.title)}</button>`).join('')}`;
  }
  function renderMap() {
    const x = scroller.scrollLeft;
    map.innerHTML = D.areas.map((area, index) => `<section class="map-area" id="area-${area.id}" aria-labelledby="area-title-${area.id}"><button type="button" class="map-area__head${selected.kind === 'area' && selected.id === area.id ? ' is-selected' : ''}" data-area="${area.id}"><span class="map-area__number">${String(index + 1).padStart(2, '0')}</span><span><strong id="area-title-${area.id}">${esc(area.title)}</strong><small>${esc(area.short)}</small></span></button><div class="branches">${area.stages.map((stageId, i) => {
      const stage = stageById[stageId];
      return `<div class="branch"><button type="button" class="topic-node${selected.kind === 'topic' && selected.id === stage.id ? ' is-selected' : ''}" data-topic="${stage.id}"><span class="topic-node__index">${String(i + 1).padStart(2, '0')}</span><span><strong>${esc(stage.title)}</strong><small>${stage.tools.length ? count(stage.tools.length, 'tool') : count((stage.resources || []).length, 'guide')}</small></span><span class="node-arrow" aria-hidden="true">↗</span></button>${stage.tools.length ? `<div class="tool-nodes" aria-label="Tools for ${esc(stage.title)}">${stage.tools.map(tool => `<button type="button" class="tool-node${tool.pick === 'start' ? ' is-start' : ''}${adopted.has(tool.id) ? ' is-done' : ''}${selected.kind === 'tool' && selected.id === tool.id ? ' is-selected' : ''}" data-tool="${tool.id}">${esc(tool.name)}${tool.pick === 'start' ? '<span aria-label="Suggested first tool">★</span>' : ''}${adopted.has(tool.id) ? '<span aria-label="Adopted">✓</span>' : ''}</button>`).join('')}</div>` : ''}</div>`;
    }).join('')}</div></section>`).join('');
    scroller.scrollLeft = x;
    progress();
  }
  function codeBlock(value) {
    return `<div class="code"><button type="button" class="copy" aria-label="Copy command">Copy</button><pre><code>${esc(value.trim())}</code></pre></div>`;
  }
  function instructions(items) {
    return (items || []).map(item => `<div class="instruction">${item.label ? `<h4>${esc(item.label)}</h4>` : ''}${codeBlock(item.code)}</div>`).join('');
  }
  function welcome() {
    return `<div class="inspector__header"><p class="eyebrow">NODE DETAILS</p><h2>Pick a node on the map</h2><p>Choose an area, a topic, or a tool. Its information will appear here while the roadmap stays in view.</p></div><div class="info-card"><strong>Reading the map</strong><p>Follow the line from left to right. Start with the company baseline and owners. Green ★ nodes suggest a first tool for each topic; use its acceptance checks before marking it adopted.</p></div><div class="info-card"><button type="button" class="panel-row" data-topic="baseline">Open the company baseline <span>→</span></button><p>Topic guides cover identity, backups, alert delivery and response alongside scanner tools.</p></div>`;
  }
  function areaInfo(area) {
    const total = area.stages.reduce((n, id) => n + stageById[id].tools.length, 0);
    return `<div class="inspector__header"><button type="button" class="inspector__close" data-close aria-label="Close details">×</button><p class="eyebrow">SECURITY AREA</p><h2>${esc(area.title)}</h2><p>${esc(area.short)}</p></div><div class="info-card"><strong>${count(area.stages.length, 'topic')} · ${count(total, 'tool')}</strong><p>Choose a topic here or on the map to see what it covers.</p></div><div class="info-card"><h3>Topics in this area</h3>${area.stages.map(id => `<button type="button" class="panel-row" data-topic="${id}">${esc(stageById[id].title)} <span>→</span></button>`).join('')}</div>`;
  }
  function topicInfo(stage) {
    const area = areaOfStage[stage.id];
    const resources = stage.resources || [];
    const controls = (stage.controlIds || []).map(id => controlById[id]);
    return `<div class="inspector__header"><button type="button" class="inspector__close" data-close aria-label="Close details">×</button><p class="eyebrow">${esc(area.title.toUpperCase())} / TOPIC</p><h2>${esc(stage.title)}</h2><p>${esc(stage.goal)}</p></div>
      ${stage.tools.length ? `<div class="info-card"><h3>Tools · ${stage.tools.length}</h3>${stage.tools.map(tool => `<button type="button" class="panel-row" data-tool="${tool.id}">${esc(tool.name)}${tool.pick === 'start' ? '<span class="panel-row__hint">Start here</span>' : '<span>→</span>'}</button>`).join('')}</div>` : ''}
      ${resources.length ? `<div class="info-card"><h3>Repository guides and starters</h3>${resources.map(resource => `<a class="panel-row" href="${esc(D.fileBase + resource.path)}" target="_blank" rel="noopener">${esc(resource.label)} <span>↗</span></a>`).join('')}</div>` : ''}
      ${stage.acceptance && stage.acceptance.length ? `<div class="info-card"><h3>How to verify adoption</h3><ul>${stage.acceptance.map(item => `<li>${esc(item)}</li>`).join('')}</ul></div>` : ''}
      ${controls.length ? `<div class="info-card"><h3>Company baseline controls</h3><ul>${controls.map(control => `<li><strong>${esc(control.id)}:</strong> ${esc(control.title)}<br><small>Owner: ${esc(control.owner_role)}</small></li>`).join('')}</ul></div>` : ''}
      ${stage.concepts && stage.concepts.length ? `<div class="info-card"><h3>Concepts to know</h3><div class="chips">${stage.concepts.map(c => `<span>${esc(c)}</span>`).join('')}</div></div>` : ''}
      ${stage.builtins && stage.builtins.length ? `<div class="info-card"><h3>Built into your platform</h3>${stage.builtins.map(x => `<p><strong>${esc(x.platform)}:</strong> ${x.text}</p>`).join('')}</div>` : ''}`;
  }
  function toolInfo(tool) {
    const stage = tool.stage;
    const area = areaOfStage[stage.id];
    const ci = tool.ciExamples || [];
    return `<div class="inspector__header"><button type="button" class="inspector__close" data-close aria-label="Close details">×</button><p class="eyebrow">${esc(area.title.toUpperCase())} / ${esc(stage.title.toUpperCase())}</p><h2>${esc(tool.name)}</h2><p>${esc(tool.role)}</p></div>
      <div class="inspector__actions"><button type="button" class="adopt" data-adopt="${tool.id}" aria-pressed="${adopted.has(tool.id)}">${adopted.has(tool.id) ? '✓ Adopted' : 'Mark as adopted'}</button><a class="primary-link" href="${D.manualBase}${tool.id}.md" target="_blank" rel="noopener">Full manual ↗</a>${tool.repoPath ? `<a href="${D.repoBase}${tool.repoPath}" target="_blank" rel="noopener">Repository files ↗</a>` : ''}</div>
      <div class="info-card"><h3>Why use it</h3>${tool.why}<p class="fine">${esc(tool.validation)}</p>${tool.versionInfo ? `<p class="fine">${tool.versionInfo}</p>` : ''}</div>
      ${(tool.install && tool.install.length) || tool.installNotes ? `<div class="info-card"><h3>Install and prepare</h3>${tool.installNotes || ''}${instructions(tool.install)}</div>` : ''}
      ${(tool.run && tool.run.length) || tool.runNotes ? `<div class="info-card"><h3>Run it</h3>${tool.runNotes || ''}${instructions(tool.run)}</div>` : ''}
      ${ci.length ? `<div class="info-card"><h3>Automate</h3>${tool.ciNotes || ''}${instructions(ci)}</div>` : ''}
      ${tool.results ? `<div class="info-card"><h3>Read the results</h3>${tool.results}</div>` : ''}
      ${(tool.notes || []).map(note => `<div class="info-card"><h3>${esc(note.title)}</h3>${note.html}</div>`).join('')}
      <div class="info-card info-card--small"><span>License: ${esc(tool.license)}</span>${tool.docs ? `<a href="${esc(tool.docs)}" target="_blank" rel="noopener">Official docs ↗</a>` : ''}${tool.repo ? `<a href="https://github.com/${esc(tool.repo)}" target="_blank" rel="noopener">GitHub project ↗</a>` : ''}</div>`;
  }
  function renderInspector() {
    if (selected.kind === 'tool' && toolById[selected.id]) inspector.innerHTML = toolInfo(toolById[selected.id]);
    else if (selected.kind === 'topic' && stageById[selected.id]) inspector.innerHTML = topicInfo(stageById[selected.id]);
    else if (selected.kind === 'area' && areaById[selected.id]) inspector.innerHTML = areaInfo(areaById[selected.id]);
    else inspector.innerHTML = welcome();
    inspector.scrollTop = 0;
    document.body.classList.toggle('has-detail', !!selected.kind);
    scrim.hidden = !selected.kind;
  }
  function scrollArea(id) {
    const area = document.getElementById(`area-${id}`);
    if (area) scroller.scrollTo({ left: Math.max(0, area.offsetLeft - map.offsetLeft - 24), behavior: motion() });
  }
  function select(kind, id, options = {}) {
    const valid = kind === 'tool' ? toolById[id] : kind === 'topic' ? stageById[id] : areaById[id];
    if (!valid) return;
    selected = { kind, id };
    search.value = '';
    searchResults.hidden = true;
    renderMap();
    renderInspector();
    const areaId = kind === 'tool' ? areaOfStage[toolById[id].stage.id].id : kind === 'topic' ? areaOfStage[id].id : id;
    if (options.scrollMap) scrollArea(areaId);
    if (options.updateHash !== false) history.replaceState(null, '', kind === 'tool' ? `#tool=${id}` : kind === 'topic' ? `#area=${areaId}&stage=${id}` : `#area=${id}`);
  }
  function clearSelection() {
    selected = { kind: null, id: null };
    renderMap(); renderInspector();
    history.replaceState(null, '', location.pathname);
  }
  function runSearch() {
    const q = search.value.trim().toLowerCase();
    if (!q) { searchResults.hidden = true; searchResults.innerHTML = ''; return; }
    const foundTools = tools.filter(tool => `${tool.name} ${tool.role} ${tool.keywords || ''} ${tool.stage.title} ${areaOfStage[tool.stage.id].title}`.toLowerCase().includes(q)).slice(0, 10);
    const foundTopics = D.stages.filter(stage => `${stage.title} ${stage.goal} ${stage.keywords || ''} ${(stage.controlIds || []).join(' ')}`.toLowerCase().includes(q)).slice(0, 4);
    searchResults.hidden = false;
    searchResults.innerHTML = `<p>Search results</p>${foundTopics.map(stage => `<button type="button" data-topic="${stage.id}"><b>Topic</b> ${esc(stage.title)}</button>`).join('')}${foundTools.map(tool => `<button type="button" data-tool="${tool.id}"><b>Tool</b> ${esc(tool.name)} <small>${esc(tool.stage.title)}</small></button>`).join('')}${!foundTools.length && !foundTopics.length ? '<span class="search-results__empty">No match. Try “Grype” or “cloud”.</span>' : ''}`;
  }
  document.addEventListener('click', event => {
    const copy = event.target.closest('.copy');
    if (copy) {
      const value = $('code', copy.parentElement).textContent;
      (navigator.clipboard ? navigator.clipboard.writeText(value) : Promise.reject()).then(() => { copy.textContent = 'Copied'; setTimeout(() => { copy.textContent = 'Copy'; }, 1400); }, () => { copy.textContent = 'Select text'; });
      return;
    }
    const adopt = event.target.closest('[data-adopt]');
    if (adopt) {
      const id = adopt.dataset.adopt;
      adopted.has(id) ? adopted.delete(id) : adopted.add(id);
      save();
      const y = inspector.scrollTop;
      renderMap(); renderInspector(); inspector.scrollTop = y;
      return;
    }
    if (event.target.closest('[data-close]')) return clearSelection();
    const tool = event.target.closest('[data-tool]');
    if (tool) return select('tool', tool.dataset.tool, { scrollMap: !!tool.closest('#search-results') });
    const topic = event.target.closest('[data-topic]');
    if (topic) return select('topic', topic.dataset.topic, { scrollMap: !!topic.closest('#search-results') });
    const area = event.target.closest('[data-area]');
    if (area) return select('area', area.dataset.area);
    const target = event.target.closest('[data-jump]');
    if (target) return select('area', target.dataset.jump, { scrollMap: true });
  });
  scrim.addEventListener('click', clearSelection);
  search.addEventListener('input', runSearch);
  search.addEventListener('keydown', event => { if (event.key === 'Escape') { search.value = ''; runSearch(); } });
  $('#theme-toggle').addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('dso-theme-v2', next); } catch (e) {}
  });
  function fromHash() {
    const params = new URLSearchParams(location.hash.slice(1));
    const tool = params.get('tool'), stage = params.get('stage'), area = params.get('area');
    if (toolById[tool]) select('tool', tool, { updateHash: false, scrollMap: true });
    else if (stageById[stage]) select('topic', stage, { updateHash: false, scrollMap: true });
    else if (areaById[area]) select('area', area, { updateHash: false, scrollMap: true });
    else { selected = { kind: null, id: null }; renderMap(); renderInspector(); }
  }
  renderJump();
  fromHash();
  window.addEventListener('hashchange', fromHash);
  window.addEventListener('popstate', fromHash);
})();
