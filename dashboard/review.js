/* Readable explanations of AI advice and deterministic publication checks. */
(function (root, factory) {
  var review = factory();
  if (typeof module === 'object' && module.exports) module.exports = review;
  else root.KnowledgeReview = review;
}(typeof window === 'undefined' ? this : window, function () {
  'use strict';
  var labels = {
    new_information: 'New information', complementary: 'Adds useful detail',
    duplicate: 'Already covered', potential_conflict: 'A policy decision is needed',
    direct_conflict: 'Conflicting guidance', supersedes: 'Possible policy replacement',
    needs_clarification: 'More approved information is needed'
  };
  var checks = {
    schema_source: ['Source and authority', 'Required source information is complete.', 'Complete the source, authority and scope fields.'],
    candidate_index: ['Private test copy', 'A private knowledge copy was prepared.', 'The test service could not prepare its copy. A maintainer needs to investigate.'],
    conflict_review: ['Policy comparison', 'Related guidance was checked; any flags still need staff review.', 'The comparison could not finish. Check its recorded error before retrying.'],
    positive_retrieval: ['Can students find this new answer?', 'The sample questions found the draft and its answer evidence.', 'One or more sample questions could not find the intended answer.'],
    department_isolation: ['Correct department scope', 'Department-specific knowledge stayed in scope.', 'The draft appeared outside its declared scope. Verify the selected department.'],
    unknown_department: ['Students without a department', 'The applicability of this guidance remained clear.', 'The scope was unclear without a department. A maintainer needs to inspect the test.'],
    regression: ['Protect existing student answers', 'Previously passing questions still found their required source evidence.', 'A previously passing question lost required source evidence in the private test.']
  };
  function e(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }
  function quote(value) { return e(value).replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>'); }
  function source(value) { return String(value || '').replace(/\.md$/, '').replace(/[-_]/g, ' '); }
  function conversation(lost) {
    return '<div class="review-conversation">' + (lost.history || []).map(function (message) {
      return '<div class="review-turn"><span>' + (message.role === 'user' ? 'Student' : 'Previous bot reply') + '</span><p>' + e(message.content) + '</p></div>';
    }).join('') + '<div class="review-turn current"><span>Student’s follow-up</span><p>' + e(lost.question || ('Test ' + lost.id)) + '</p></div></div>';
  }
  function ai(data) {
    if (!data || !data.report) return '<section class="review-ai missing"><div class="review-section-head"><span class="review-label">AI WRITING & POLICY REVIEW</span><span class="review-chip neutral">Not used for this revision</span></div><h4>No AI feedback was recorded</h4><p>This revision was saved through the manual editor. The search checks below do not constitute an AI policy review.</p></section>';
    var report = data.report;
    var decision = report.requires_decision || report.blocked || report.classification === 'duplicate';
    return '<section class="review-ai"><div class="review-section-head"><span class="review-label">AI WRITING & POLICY REVIEW</span><span class="review-chip ' + (decision ? 'attention' : 'good') + '">AI review completed</span></div>' +
      '<h4>What the AI found</h4><div class="review-model">Reviewed by ' + e(data.model) + ' · ' + e(labels[report.classification] || report.classification) + '</div><p class="review-ai-summary">' + e(report.summary) + '</p>' +
      '<div class="review-coverage">' + (typeof report.one_focused_topic === 'boolean' ? '<span>Topic check · AI says: <strong>' + (report.one_focused_topic ? 'one focused topic' : 'split the topics') + '</strong></span>' : '') +
      (typeof report.question_supported === 'boolean' ? '<span>Question check · AI says: <strong>' + (report.question_supported ? 'guidance covers the supplied question or topic' : 'approved details are missing') + '</strong></span>' : '') + '</div>' +
      (report.clarifications && report.clarifications.length ? '<div class="review-next"><strong>What to add before continuing</strong><ul>' + report.clarifications.map(function (item) { return '<li>' + e(item) + '</li>'; }).join('') + '</ul></div>' : '') +
      (report.findings || []).map(function (finding) {
        return '<article class="review-claim"><div class="review-model">AI finding · ' + e(labels[finding.category] || finding.category) + '</div><p>' + e(finding.explanation) + '</p><div class="studio-claims"><div><span>Your proposed claim</span><blockquote>' + quote(finding.proposed_claim) + '</blockquote></div><div><span>Existing policy claim</span><blockquote>' + quote(finding.existing_claim) + '</blockquote><small>' + e(source(finding.source_doc)) + ' › ' + e(finding.section) + '</small></div></div><p class="review-caption">Staff must verify whether the original policy needs correcting or this is an authorized, clearly scoped exception.</p>' + (finding.entry_id ? '<button type="button" class="studio-update secondary" data-entry="' + e(finding.entry_id) + '">Open existing entry as an update</button>' : '') + '</article>';
      }).join('') +
      (!(report.findings || []).length ? '<p class="review-caption">The AI did not identify a relevant duplicate or conflict in the passages it reviewed. This does not guarantee that every policy was checked.</p>' : '') +
      '<details class="review-disclosure"><summary>See the AI’s suggested title and test questions</summary><p><strong>' + e((report.draft || {}).document_title) + '</strong></p><ol><li>' + e((report.draft || {}).representative_question) + '</li><li>' + e((report.draft || {}).paraphrase_question) + '</li></ol><p>The factual guidance was preserved verbatim. These suggestions organize and test it.</p></details>' +
      '<p class="review-caption">AI advice is separate from retrieval testing and human approval. It cannot authorize publication.</p></section>';
  }
  function regressionIssue(result, item, run) {
    var details = result.details || {}, lost = details.lost_cases || [];
    return '<section class="review-problem"><div class="review-section-head"><span class="review-label">SEARCH TEST · PUBLICATION PAUSED</span><span class="review-chip danger">Needs technical review</span></div><h3>' + (lost.length ? lost.length + ' existing answer' + (lost.length === 1 ? '' : 's') + ' could no longer be found' : 'An existing answer could no longer be found') +
      '</h3><p>The AI may consider this guidance useful, but adding it changed the search results in the private test. Required evidence for an existing answer was no longer included. The original source still exists.</p>' +
      lost.map(function (test) {
        return '<article class="review-impact"><h4>The affected conversation</h4>' + conversation(test) +
          '<div class="review-expectation"><span>What this student should receive</span><p>' + e(test.expected_answer || 'The complete source evidence required by this test.') + '</p>' +
          (test.source_doc || test.source_section ? '<small>Expected source: ' + e(source(test.source_doc)) + (test.source_section ? ' › ' + e(test.source_section) : '') + '</small>' : '') + '</div>' +
          '<div class="review-before-after"><div><span>Current knowledge</span><strong>Required evidence found</strong></div><div class="changed"><span>With this draft added</span><strong>Required evidence missing</strong></div></div>' +
          (test.before_sources ? '<details class="review-disclosure"><summary>Inspect the recorded source passages</summary><h5>Previously retrieved evidence</h5>' + test.before_sources.map(function (s) { return '<blockquote>' + quote(s.text) + '</blockquote>'; }).join('') + '<h5>Top passages in the private test</h5>' + (test.after_sources || []).map(function (s) { return '<p><strong>' + e(source(s.source_doc)) + ' › ' + e(s.section) + '</strong></p><blockquote>' + quote(s.text) + '</blockquote>'; }).join('') + '</details>' :
            '<p class="review-caption">The failed test is recorded. A maintainer needs to investigate the exact search cause.</p><details class="review-disclosure"><summary>About this earlier result</summary><p>This earlier run did not store passage rankings. The conversation and expected answer come from the evaluation set; an exact ranking cause has not been established.</p></details>') + '</article>';
      }).join('') +
      '<div class="review-next"><h4>What should you do next?</h4><p><strong>You do not need to diagnose search rankings.</strong> Keep this entry private and copy the issue report for the project maintainer. They should reproduce the affected question and inspect the retrieval change.</p><p>If the guidance itself is broad or unclear, review its wording and scope. Preserve the approved facts and the original test question; changing tests to make them pass would hide the problem.</p>' +
      '<div class="actions"><button type="button" class="copy-review-issue" data-revision="' + e(item.id) + '">Copy issue for maintainer</button>' + (item.source_kind === 'admin_authored' ? '<button type="button" class="guided-correction secondary" data-revision="' + e(item.id) + '">Review guidance with AI</button>' : '') + '<span class="status" role="status"></span></div></div><p class="review-caption">Nothing from this draft was published. Existing student knowledge remains active.</p></section>';
  }
  function retrievalIssue(result, item) {
    var cases = (result.details || {}).cases || [];
    return '<section class="review-problem"><span class="review-label">SEARCH TEST · PUBLICATION PAUSED</span><h3>A sample question could not find the new answer</h3><p>This is a retrieval test result, separate from the AI’s policy assessment.</p>' + cases.filter(function (test) { return !test.passed; }).map(function (test) {
      return '<article class="review-impact"><span class="review-label">Question tested</span><h4>' + e(test.question) + '</h4><p>' + (test.candidate_hit === false ? 'The draft was absent from the selected search results.' : test.evidence_hit === false ? 'The selected results did not contain the required answer phrase.' : 'The retrieved result did not meet the similarity threshold.') + '</p><p>Required answer phrase: <q>' + e(test.expected_evidence || item.expected_evidence) + '</q></p></article>';
    }).join('') + '<div class="review-next"><h4>What should you do next?</h4><p>Check that the approved guidance actually answers the displayed question and that the topic and department are specific. Keep realistic questions and facts unchanged. If a clearly relevant answer still cannot be found, copy this issue for the maintainer.</p><div class="actions"><button class="copy-review-issue" data-revision="' + e(item.id) + '">Copy issue for maintainer</button>' + (item.source_kind === 'admin_authored' ? '<button class="guided-correction secondary" data-revision="' + e(item.id) + '">Review guidance with AI</button>' : '') + '<span class="status" role="status"></span></div></div></section>';
  }
  function diagnostic(item, run) {
    return 'Knowledge Studio issue\nEntry: ' + (item.document_title || item.question) + '\nRevision: ' + item.id + '\nRun: ' + (run ? run.id : 'none') + '\nStatus: ' + (run ? run.status : 'not tested') + '\nCanonical guidance: ' + item.answer + '\n\nRecorded test results:\n' + JSON.stringify(run ? run.results : [], null, 2) + '\n\nAI feedback (advisory):\n' + JSON.stringify(item.assistance || null, null, 2) + '\n\nKeep the approved facts and evaluation questions unchanged. Reproduce the retrieval problem before proposing a correction.';
  }
  function render(run, item) {
    var results = run ? run.results || [] : [], map = {};
    results.forEach(function (result) { map[result.step] = result; });
    var failed = results.filter(function (result) { return result.status !== 'passed'; });
    var regression = map.regression && map.regression.status === 'failed';
    var positive = map.positive_retrieval && map.positive_retrieval.status === 'failed';
    var progress = !run || ['pending', 'running'].indexOf(run.status) >= 0;
    var title = !run ? 'Next: test this draft privately' : progress ? 'Checking search and student-answer safety…' : run.status === 'passed' ? 'Search checks passed. Your policy decision is next.' : 'Publication is paused. Students have not received this draft.';
    var summary = !run ? 'Start the checks below. We will test realistic questions and protect existing answers before asking you to approve publication.' : progress ? 'These are automated search tests, not an LLM judgment. You can leave and return; completed results will appear here.' : run.status === 'passed' ? 'Review the AI feedback and any comparison flags below, then record a named decision. Passing search tests does not establish that a policy is correct.' : 'The specific issue and next action are below. You can keep the draft while the problem is resolved.';
    var issue = regression ? regressionIssue(map.regression, item, run) : positive ? retrievalIssue(map.positive_retrieval, item) :
      failed.length && run.status === 'failed' ? '<section class="review-problem"><h3>' + e((checks[failed[0].step] || ['Automatic check'])[0]) + ' needs attention</h3><p>' + e((checks[failed[0].step] || ['', '', 'A maintainer needs to inspect the recorded error.'])[2]) + '</p><p>' + e(((failed[0].details || {}).errors || []).join(' ')) + '</p></section>' : '';
    var ruleFlags = ((map.conflict_review || {}).details || {}).flags || [];
    var related = ((map.conflict_review || {}).details || {}).related || [];
    var quickAI = item.assistance && item.assistance.report;
    return '<section class="review-overview ' + (run && run.status === 'failed' ? 'paused' : '') + '"><div class="review-section-head"><span class="review-label">DRAFT DECISION</span><span class="review-chip neutral">Private · not published</span></div><h3>' + title + '</h3><p>' + summary + '</p>' +
      (quickAI ? '<div class="review-ai-quick"><span>AI feedback · ' + e(item.assistance.model) + '</span><strong>' + e(labels[quickAI.classification] || quickAI.classification) + '</strong><p>' + e(quickAI.summary.length > 180 ? quickAI.summary.slice(0,180).replace(/\s+\S*$/, '') + '… (full feedback below)' : quickAI.summary) + '</p></div>' : '') +
      '<div class="review-stages"><div><span>1 · AI review</span><strong>' + (item.assistance ? 'Feedback recorded below' : 'Not used') + '</strong></div><div><span>2 · Search tests</span><strong>' + (run && run.status === 'failed' ? 'Paused — see issue below' : run && run.status === 'passed' ? 'Passed' : 'Pending') + '</strong></div><div><span>3 · Staff decision</span><strong>' + (run && (run.reviews || []).length ? 'Recorded' : 'Required before publishing') + '</strong></div></div></section>' + issue + ai(item.assistance) +
      '<section class="review-tests"><div class="review-section-head"><span class="review-label">AUTOMATED SEARCH TESTS · NO LLM JUDGMENT</span><span class="review-chip neutral">' + results.filter(function (r) { return r.status === 'passed'; }).length + ' / 7 passed</span></div><details class="review-disclosure"><summary>Inspect all seven checks and sample questions</summary>' + Object.keys(checks).map(function (step) {
        var result = map[step], status = result ? result.status : 'pending', check = checks[step];
        return '<div class="review-check"><span class="review-chip ' + (status === 'passed' ? 'good' : status === 'pending' ? 'neutral' : 'danger') + '">' + e(status === 'passed' ? 'Passed' : status === 'pending' ? 'Pending' : 'Paused') + '</span><div><strong>' + check[0] + '</strong><p>' + (!result ? 'Waiting for this check.' : status === 'passed' ? check[1] : check[2]) + '</p></div></div>';
      }).join('') + (((map.positive_retrieval || {}).details || {}).cases || []).map(function (test) { return '<p class="review-caption">' + e(test.passed ? 'Found: ' : 'Not found: ') + e(test.question) + '</p>'; }).join('') + '</details></section>' +
      (ruleFlags.length ? '<section class="review-tests"><details class="review-disclosure"><summary>' + ruleFlags.length + ' automated comparison flags for staff to inspect</summary><p class="review-caption">These are broad similarity, number and wording checks. They are not additional AI findings or confirmed contradictions.</p>' + ruleFlags.map(function (flag) {
        var candidate = related.find(function (c) { return c.id === flag.candidate_id; }) || {};
        return '<details class="review-disclosure"><summary>' + e(flag.reason.replace(/_/g, ' ')) + ' · ' + e(source(candidate.source_doc)) + ' › ' + e(candidate.section) + '</summary><p>' + e(flag.explanation || '') + '</p><blockquote>' + quote(candidate.text) + '</blockquote></details>';
      }).join('') + '</details></section>' : '') +
      (run ? '<details class="review-disclosure review-audit"><summary>Technical record for maintainers</summary><p>Run: ' + e(run.id) + '<br>Fingerprint: ' + e(run.fingerprint) + '</p></details>' : '');
  }
  return {render:render, ai:ai, diagnostic:diagnostic};
}));
