/* Durable paid-call controls. This view never changes limits or resets counters. */
var paidUsageRequest = 0;

function paidUsageSummary(data) {
  return data.usage.filter(function (r) { return r.day === data.day; }).reduce(function (s, r) {
    ['requests', 'charged_tokens', 'charged_usd', 'input_tokens', 'visible_output_tokens',
      'reasoning_tokens', 'uncertain_attempts'].forEach(function (k) { s[k] = (s[k] || 0) + Number(r[k]); });
    return s;
  }, {requests: 0, charged_tokens: 0, charged_usd: 0, input_tokens: 0,
    visible_output_tokens: 0, reasoning_tokens: 0, uncertain_attempts: 0});
}

function paidUsageAlerts(data, summary) {
  var alerts = [];
  if (!data.enabled) alerts.push('Paid calls are paused. Local replies and saved drafts remain available.');
  if (data.circuit_until && Date.parse(data.circuit_until) > Date.now()) {
    alerts.push('Provider failure protection is active until ' + new Date(data.circuit_until).toLocaleTimeString() + '.');
  }
  if (data.day > data.price_valid_until) alerts.push('Pricing has expired. Paid calls stay blocked until server prices are reviewed.');
  [['charged_usd', 'cost_usd', 'spending'], ['charged_tokens', 'tokens', 'tokens'],
    ['requests', 'requests', 'requests']].forEach(function (pair) {
    if (summary[pair[0]] >= data.limits[pair[1]] * 0.8) {
      alerts.push('Today\'s ' + pair[2] + ' allowance is at least 80% used. New attempts stop before exceeding it.');
    }
  });
  if (summary.uncertain_attempts) alerts.push('Unsettled or failed attempts retain their conservative reservations; they are included in the budget.');
  return alerts;
}

function renderPaidUsage(data) {
  var summary = paidUsageSummary(data);
  function money(n) { return '$' + Number(n).toFixed(4); }
  function number(n) { return Number(n).toLocaleString(); }
  function metric(label, value, detail) {
    return '<div class="kpi"><div class="kpi-label">' + esc(label) + '</div><div class="kpi-value">' + esc(value) +
      '</div><div class="kpi-note">' + esc(detail) + '</div></div>';
  }
  var alerts = paidUsageAlerts(data, summary).map(function (a) { return '<div class="banner warn" role="alert">' + esc(a) + '</div>'; }).join('');
  var rows = data.usage.map(function (r) {
    var purpose = {student: 'Student', curation_: 'Studio', curation_preview_: 'Student preview'}[r.purpose] || r.purpose;
    return '<tr>' + [r.day, purpose, r.model, number(r.requests), number(r.input_tokens),
      number(r.visible_output_tokens), number(r.reasoning_tokens), money(r.charged_usd),
      number(r.uncertain_attempts)].map(function (v) { return '<td>' + esc(v) + '</td>'; }).join('') + '</tr>';
  }).join('');
  var events = data.events.map(function (r) {
    return '<tr><td>' + esc(r.day) + '</td><td>' + esc(r.reason.replace(/_/g, ' ')) + '</td><td>' + number(r.count) + '</td></tr>';
  }).join('');
  document.getElementById('paid-report').innerHTML = alerts +
    '<section class="report-panel paid-control"><div><h3>Paid calls: ' + (data.enabled ? 'enabled' : 'paused') +
    '</h3><p class="panel-caption">Stop new student, Studio and preview calls immediately. Calls already sent can finish within their timeout.</p></div>' +
    '<button id="paid-toggle" class="' + (data.enabled ? 'danger' : 'secondary') + '"' +
    (!data.environment_enabled ? ' disabled' : '') + '>' + (data.enabled ? 'Pause paid calls' : 'Resume paid calls') + '</button></section>' +
    '<div class="usage-kpis">' + metric('Today: estimated spend', money(summary.charged_usd), 'Daily ceiling ' + money(data.limits.cost_usd)) +
    metric('Provider attempts', number(summary.requests), 'Daily ceiling ' + number(data.limits.requests) + ' · retries included') +
    metric('Budgeted tokens', number(summary.charged_tokens), 'Daily ceiling ' + number(data.limits.tokens) + ' · reservations included') +
    metric('Output including reasoning', number(summary.visible_output_tokens + summary.reasoning_tokens),
      number(summary.visible_output_tokens) + ' visible + ' + number(summary.reasoning_tokens) + ' reasoning') + '</div>' +
    '<section class="report-panel"><h3>Usage by model and workload · last 7 UTC days</h3><p class="report-note">Estimated app usage since this protection was enabled; this is not your Gemini balance or invoice. Unknown usage stays reserved. Older student logs remain in Usage overview.</p>' +
    '<div class="paid-table"><table><thead><tr><th>Date</th><th>Workload</th><th>Model</th><th>Attempts</th><th>Input</th><th>Visible output</th><th>Reasoning</th><th>Estimated USD</th><th>Uncertain</th></tr></thead><tbody>' +
    (rows || '<tr><td colspan="9">No paid attempts recorded yet.</td></tr>') + '</tbody></table></div></section>' +
    '<section class="report-panel"><h3>Protection events</h3><div class="paid-table"><table><thead><tr><th>Date</th><th>Event</th><th>Count</th></tr></thead><tbody>' +
    (events || '<tr><td colspan="3">No protection events recorded.</td></tr>') + '</tbody></table></div><p class="report-note">' +
    'IP allowance: ' + number(data.limits.ip_requests) + '/UTC day · Chat allowance: ' + number(data.limits.chat_questions) + '/24 hours · Shared provider concurrency: ' +
    number(data.limits.concurrency) + '. Prices require review after ' + esc(data.price_valid_until) + '.</p></section>';
  document.getElementById('paid-toggle').onclick = async function () {
    this.disabled = true;
    try {
      var response = await fetch(API + '/admin/api/llm-control', {
        method: 'POST', headers: headers(), body: JSON.stringify({enabled: !data.enabled})
      });
      if (!response.ok) throw new Error('The control could not be saved. Refresh to verify its status.');
      await loadPaidUsage();
    } catch (error) {
      document.getElementById('paid-status').textContent = error.message;
      // A lost response may still have changed the control. Refresh before
      // allowing another toggle based on an unverified old state.
    }
  };
}

async function loadPaidUsage() {
  var request = ++paidUsageRequest;
  var credential = token();
  var status = document.getElementById('paid-status');
  var report = document.getElementById('paid-report');
  status.textContent = 'Loading paid-call status…';
  report.setAttribute('aria-busy', 'true');
  var toggle = document.getElementById('paid-toggle');
  if (toggle) toggle.disabled = true;
  try {
    var response = await fetch(API + '/admin/api/llm-usage', {headers: headers()});
    if (!response.ok) throw new Error('Paid-call status is unavailable. Refresh to retry; spending controls remain enforced.');
    var data = await response.json();
    if (request !== paidUsageRequest || credential !== token()) return;
    renderPaidUsage(data);
    status.textContent = 'Updated ' + new Date().toLocaleTimeString() + ' · Daily allowances reset at midnight UTC';
  } catch (error) {
    if (request === paidUsageRequest && credential === token()) status.textContent = error.message;
  } finally {
    if (request === paidUsageRequest) report.removeAttribute('aria-busy');
  }
}
