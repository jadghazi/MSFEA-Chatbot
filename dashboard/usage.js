/* Reporting uses persisted logs. The process-local /usage counters have a different window. */
var usageRequest = 0;
var activityObserver;

function loadUsage() {
  var request = ++usageRequest;
  var report = document.getElementById('usage-report');
  var status = document.getElementById('usage-status');
  var days = document.getElementById('usage-range').value;
  report.setAttribute('aria-busy', 'true');
  status.textContent = 'Updating report…';
  document.getElementById('usage-period').textContent = 'Loading selected period…';
  return fetch(API + '/admin/api/analytics?days=' + days, {headers: headers()})
    .then(function (r) {
      if (!r.ok) throw new Error(r.status === 401 ? 'Your access code is no longer valid. Sign in again.' : 'Usage data could not be loaded. Try refreshing.');
      return r.json();
    }).then(function (data) {
      if (request !== usageRequest) return;
      renderUsage(data);
      status.textContent = '';
    }).catch(function (error) {
      if (request !== usageRequest) return;
      report.innerHTML = '';
      document.getElementById('usage-period').textContent = 'Selected period unavailable · Refresh to try again';
      status.innerHTML = '<div class="banner err">' + esc(error.message) + ' <button class="secondary" id="usage-retry">Retry</button></div>';
      document.getElementById('usage-retry').onclick = loadUsage;
    }).finally(function () {
      if (request === usageRequest) report.removeAttribute('aria-busy');
    });
}

function usageNumber(n) { return n == null ? '—' : Number(n).toLocaleString(); }
function usagePercent(n, d) { return d ? (100 * n / d).toFixed(1).replace(/\.0$/, '') + '%' : '—'; }
function usageDate(date) { return new Date(date).toLocaleDateString(undefined, {month:'short',day:'numeric',timeZone:'UTC'}); }

function activityChart(rows, width) {
  var colors = ['#862633', '#c5a477', '#6c7485'];
  var keys = ['answered', 'refused', 'temporary_errors'];
  var peak = Math.max.apply(null, rows.map(function (r) { return r.total; }).concat([1]));
  var top = Math.ceil(peak / 4) * 4;
  width = Math.max(260, width || 640);
  var left = 32, plot = width - 40, height = 140;
  var step = plot / rows.length;
  var svg = '<svg class="activity-chart" viewBox="0 0 ' + width + ' 190" role="img" aria-label="Daily logged questions, split into answered, refused and temporary failures. Exact values are in the daily data table below.">';
  for (var i = 0; i <= 4; i++) {
    var y = 12 + height - i * height / 4;
    svg += '<line class="gridline" x1="' + left + '" x2="' + (width - 8) + '" y1="' + y + '" y2="' + y + '"/><text x="24" y="' + (y+3) + '" text-anchor="end">' + usageNumber(top*i/4) + '</text>';
  }
  rows.forEach(function (r, i) {
    var y = 152;
    var label = usageDate(r.date) + ': ' + r.total + ' questions; ' + r.answered + ' answered, ' + r.refused + ' refused, ' + r.temporary_errors + ' failures';
    svg += '<g><title>' + esc(label) + '</title>';
    keys.forEach(function (key, j) {
      var h = r[key] / top * height;
      y -= h;
      if (h) svg += '<rect x="' + (left+i*step+step*.18) + '" y="' + y + '" width="' + step*.64 + '" height="' + h + '" fill="' + colors[j] + '"/>';
    });
    svg += '</g>';
    if (i === 0 || i === rows.length-1 || i === Math.floor(rows.length/2)) {
      svg += '<text x="' + (left+i*step+step/2) + '" y="176" text-anchor="' + (i===0?'start':i===rows.length-1?'end':'middle') + '">' + esc(usageDate(r.date)) + '</text>';
    }
  });
  return svg + '</svg>';
}

function renderUsage(data) {
  var s = data.summary;
  var completed = s.answered + s.refused;
  var rated = s.thumbs_up + s.thumbs_down;
  var report = document.getElementById('usage-report');
  document.getElementById('usage-period').textContent = usageDate(data.start) + ' – ' + usageDate(data.end) + ' · UTC · Today is partial · Saved interactions';
  function kpi(label, value, note, action) {
    return '<article class="kpi' + (action ? ' action' : '') + '"><div class="kpi-label">' + label + '</div><strong class="kpi-value">' + value + '</strong><div class="kpi-note">' + note + '</div></article>';
  }
  function bar(label, n, denominator, color) {
    return '<div class="outcome" style="--series:' + color + '"><div class="outcome-line"><span>' + esc(label) + '</span><strong>' + usageNumber(n) + '<small>' + usagePercent(n, denominator) + '</small></strong></div><div class="bar-track"><div class="bar-fill" style="width:' + (denominator ? 100*n/denominator : 0) + '%"></div></div></div>';
  }
  var gaps = data.unanswered.length ? data.unanswered.map(function (r) {
    return '<div class="list-row"><div class="label">' + esc(r.question) + '<small>Earliest in period · ' + esc(usageDate(r.oldest)) + '</small></div><span class="count">' + usageNumber(r.count) + '<small>' + (r.count===1?'question':'questions') + '</small></span></div>';
  }).join('') : '<div class="usage-empty">No unresolved refusals from this period.</div>';
  var sources = data.sources.length ? data.sources.map(function (r) {
    var parts = r.source.split(' > ');
    return '<div class="list-row"><div class="label"><span class="source-label">' + esc(parts[0]) + '</span>' + (parts.length>1?'<small>' + esc(parts.slice(1).join(' › ')) + '</small>':'') + '<div class="bar-track source-bar"><div class="bar-fill" style="width:' + (100*r.count/data.sources[0].count) + '%"></div></div></div><span class="count">' + usageNumber(r.count) + '</span></div>';
  }).join('') : '<div class="usage-empty">Cited sources will appear after answers are logged.</div>';
  var reasons = data.negative_reasons.length ? data.negative_reasons.map(function (r) {
    return '<div class="list-row"><span class="label">' + esc(r.reason) + '</span><span class="count">' + usageNumber(r.count) + '</span></div>';
  }).join('') : '<p class="report-note">No negative answer ratings in this period.</p>';
  var dailyTable = '<details class="data-table"><summary>View daily counts</summary><div class="table-scroll"><table><caption class="hidden">Daily logged questions, UTC</caption><thead><tr><th scope="col">Date (UTC)</th><th scope="col">Total</th><th scope="col">Answered</th><th scope="col">Refused</th><th scope="col">Failures</th></tr></thead><tbody>' + data.daily.map(function (r) {
    return '<tr><th scope="row">' + esc(r.date) + '</th><td>' + r.total + '</td><td>' + r.answered + '</td><td>' + r.refused + '</td><td>' + r.temporary_errors + '</td></tr>';
  }).join('') + '</tbody></table></div></details>';
  function seconds(ms) { return ms == null ? '—' : (ms/1000).toFixed(2) + ' s'; }
  report.innerHTML =
    '<div class="usage-kpis">' +
    kpi('Questions logged', usageNumber(s.total), 'Interactions in the selected period') +
    kpi('Answer rate', usagePercent(s.answered, completed), usageNumber(s.answered) + ' answered / ' + usageNumber(completed) + ' without service errors') +
    kpi('Needs review', usageNumber(s.pending), 'Unresolved from this period<br><button class="text-action" data-go="attention">Open attention queue ↗</button>', true) +
    kpi('Rated helpful', usagePercent(s.thumbs_up, rated), usageNumber(s.thumbs_up) + ' helpful / ' + usageNumber(rated) + ' answer ratings') + '</div>' +
    '<div class="usage-grid"><section class="report-panel"><div class="panel-heading"><h3>Question activity</h3><span class="eyebrow">Daily volume</span></div><p class="panel-caption">When students turn to the assistant</p>' +
    '<div class="legend"><span style="--series:#862633">Answered</span><span style="--series:#c5a477">Refused</span><span style="--series:#6c7485">Temporary failure</span></div>' +
    (s.total ? '<div id="activity-plot"></div>' : '<div class="usage-empty">No interactions logged in this period. Try a longer date range.</div>') + dailyTable + '</section>' +
    '<section class="report-panel"><h3>What happened to each question?</h3><p class="panel-caption">Outcomes out of all ' + usageNumber(s.total) + ' logged questions</p>' +
    bar('Answered', s.answered, s.total, '#862633') + bar('Refused · human guidance needed', s.refused, s.total, '#c5a477') + bar('Temporary failure', s.temporary_errors, s.total, '#6c7485') +
    '<p class="report-note">A refusal can be the correct safe response. An answer does not prove accuracy or that a staff email was avoided.</p></section></div>' +
    '<div class="usage-grid equal"><section class="report-panel"><div class="panel-heading"><h3>Unanswered questions to review</h3><button class="text-action" data-go="attention">View queue ↗</button></div><p class="panel-caption">Top 5 unresolved refusals · exact question matches</p><div>' + gaps + '</div><p class="report-note">Review source coverage before adding knowledge. The attention queue includes all dates and negative ratings too.</p></section>' +
    '<section class="report-panel"><h3>Most-cited sources</h3><p class="panel-caption">Top 5 document sections · answers citing each source</p><div>' + sources + '</div><p class="report-note">An answer may cite multiple sections. Citation frequency is not a measure of correctness.</p></section></div>' +
    '<div class="usage-grid equal"><section class="report-panel"><div class="panel-heading"><h3>Student feedback</h3><button class="text-action" data-go="experience">Experience feedback ↗</button></div><p class="panel-caption">Answer ratings for questions logged in this period</p><div class="feedback-summary"><div><strong>' + usageNumber(s.thumbs_up) + '</strong><span>Helpful</span></div><div><strong>' + usageNumber(s.thumbs_down) + '</strong><span>Not helpful</span></div><div><strong>' + usagePercent(rated,s.total) + '</strong><span>Questions rated</span></div></div>' + reasons + '<p class="report-note">Optional ratings represent respondents, not every student. Whole-experience feedback is collected separately.</p></section>' +
    '<section class="report-panel"><h3>Service & source checks</h3><p class="panel-caption">Signals to investigate, separate from answer quality</p>' +
    bar('Temporary failure rate', s.temporary_errors, s.total, '#6c7485') + bar('Answers with a citation', s.answers_with_citations, s.answered, '#862633') +
    '<p class="report-note">Counts cover saved interactions; rejected requests and logging failures are not included. Citation presence does not establish that a source supports an answer.</p></section></div>' +
    '<details class="report-panel diagnostics"><summary>Generation & token details <span>Latency, provider usage and measurement coverage</span></summary><div class="diagnostic-body"><div class="diagnostic-metrics">' +
    '<div><span>Average generation</span><strong>' + seconds(s.avg_llm_latency_ms) + '</strong></div><div><span>95th percentile generation</span><strong>' + seconds(s.p95_llm_latency_ms) + '</strong></div><div><span>Input tokens</span><strong>' + usageNumber(s.llm_input_tokens) + '</strong></div><div><span>Output tokens</span><strong>' + usageNumber(s.llm_output_tokens) + '</strong></div></div><p class="report-note">Latency recorded for ' + usageNumber(s.latency_samples) + ' interactions; both token counts recorded for ' + usageNumber(s.token_samples) + '. Generation time excludes retrieval and network time to the student. Token totals include recorded provider values only; unavailable measurements show —.</p></div></details>';
  report.querySelectorAll('[data-go]').forEach(function (button) {
    button.onclick = function () { selectTab(button.dataset.go); };
  });
  if (activityObserver) activityObserver.disconnect();
  var plot = document.getElementById('activity-plot');
  if (plot) {
    var lastWidth;
    activityObserver = new ResizeObserver(function () {
      var width = Math.round(plot.clientWidth);
      if (width && width !== lastWidth) {
        lastWidth = width;
        plot.innerHTML = activityChart(data.daily, width);
      }
    });
    activityObserver.observe(plot);
  }
}

document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('usage-range').addEventListener('change', loadUsage);
});
