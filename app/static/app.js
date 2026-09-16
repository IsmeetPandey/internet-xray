const form = document.querySelector('#analyze-form');
const urlInput = document.querySelector('#url');
const button = form.querySelector('button');
const state = document.querySelector('#state');
const results = document.querySelector('#results');

const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ms = (value) => value == null ? '—' : `${Math.round(value)} ms`;
const bytes = (value) => {
  if (!value) return '0 B';
  const units = ['B','KB','MB','GB'];
  let n = value, i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i += 1; }
  return `${n.toFixed(n >= 10 || i === 0 ? 0 : 1)} ${units[i]}`;
};

function showState(message, error = false) {
  state.classList.remove('hidden');
  state.textContent = message;
  state.style.borderColor = error ? '#5a2a2a' : '';
}

function render(data) {
  results.classList.remove('hidden');
  state.classList.add('hidden');

  document.querySelector('#metrics').innerHTML = [
    ['Requests', data.request_count],
    ['Third-party requests', data.third_party_request_count],
    ['Known data', bytes(data.known_response_bytes)],
    ['Navigation status', data.navigation_status ?? '—']
  ].map(([label, value]) => `<div class="metric"><div class="label">${esc(label)}</div><div class="value">${esc(value)}</div></div>`).join('');

  document.querySelector('#final-url').textContent = data.final_url;
  const timing = data.timing || {};
  const timingRows = [
    ['DNS', timing.dns_ms], ['TCP', timing.tcp_ms], ['TLS', timing.tls_ms],
    ['TTFB', timing.ttfb_ms], ['Load', timing.load_event_ms]
  ];
  document.querySelector('#timing').innerHTML = timingRows.map(([name, value]) =>
    `<div class="timing-item"><div class="name">${name}</div><div class="num">${ms(value)}</div></div>`).join('');

  const resources = Object.entries(data.resource_counts || {}).sort((a,b) => b[1]-a[1]);
  const maxResource = resources[0]?.[1] || 1;
  document.querySelector('#resources').innerHTML = resources.length ? resources.map(([name,count]) =>
    `<div class="bar-row"><span>${esc(name)}</span><div class="track"><div class="fill" style="width:${(count/maxResource)*100}%"></div></div><strong>${count}</strong></div>`).join('') : '<div class="muted">No response records.</div>';

  const hosts = Object.entries(data.host_counts || {}).sort((a,b) => b[1]-a[1]).slice(0, 12);
  document.querySelector('#hosts').innerHTML = hosts.length ? hosts.map(([host,count]) =>
    `<div class="host"><span>${esc(host)}</span><span class="count">${count}</span></div>`).join('') : '<div class="muted">No hosts recorded.</div>';

  const requests = [...(data.requests || [])].sort((a,b) => (b.duration_ms ?? 0) - (a.duration_ms ?? 0)).slice(0, 100);
  document.querySelector('#request-count-label').textContent = `${requests.length} shown`;
  document.querySelector('#requests').innerHTML = requests.map((r) => {
    const statusClass = r.status >= 200 && r.status < 400 ? 'status-ok' : 'status-bad';
    return `<tr><td class="mono">${esc(r.host)}</td><td>${esc(r.resource_type)}</td><td class="${statusClass}">${esc(r.status ?? '—')}</td><td>${ms(r.duration_ms)}</td><td>${r.is_third_party ? 'YES' : 'NO'}</td></tr>`;
  }).join('');
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const url = urlInput.value.trim();
  if (!url) return;
  button.disabled = true;
  results.classList.add('hidden');
  showState('Running a real browser trace… this can take a few seconds.');
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({url})
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || 'Analysis failed.');
    render(payload);
  } catch (error) {
    showState(error.message || 'Something went wrong.', true);
  } finally {
    button.disabled = false;
  }
});
