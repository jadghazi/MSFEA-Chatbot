/* One guided composer for knowledge intake and unanswered-question review. */
(function () {
  "use strict";
  var host, hooks, current = null, timer = null, feedback = null, entry = null;
  var draft = null, requestKey = null, lastIntake = null, busy = false;
  var workspaceId = null;
  var proposal = null, suggestionTimer = null, acceptedSuggestion = null;
  var labels = {
    new_information: "New information", complementary: "Adds useful detail",
    duplicate: "Already covered", potential_conflict: "Needs your judgment",
    direct_conflict: "Conflicting guidance", supersedes: "Possible policy update",
    needs_clarification: "A few details are missing"
  };
  var errors = {
    quota: "The staff-review model has reached its Gemini limit. Your guidance is still here. Try again later or use the manual source editor.",
    daily_budget: "Today's staff-review allowance has been used. Your guidance is still here; you can use the manual editor or return tomorrow.",
    provider_unavailable: "The review model is unavailable. Your guidance is saved here; retry later or use the manual editor.",
    invalid_review: "The AI response could not be verified. This is a review-service failure, not a finding that your guidance is incorrect. Nothing was saved as knowledge. Retry later or use the manual editor.",
    stale_index: "The knowledge base changed during review. Run a fresh review against the latest guidance.",
    stale_review: "The review rules changed. Your guidance is preserved; start a fresh comparison.",
    interrupted: "The review was interrupted. Your guidance is still available. Start a new review when you are ready.",
    review_unavailable: "This review could not finish. Nothing was published. Try again or use the manual editor."
  };
  function e(value) { return hooks.escape(value); }
  function humanLabel(value) { return String(value).replace(/[-_]/g, ' ').replace(/\b\w/g, function (letter) { return letter.toUpperCase(); }); }

  function el(selector) { return host.querySelector(selector); }
  function unique() {
    return window.crypto && window.crypto.randomUUID ? window.crypto.randomUUID() :
      "review-" + Date.now() + "-" + Math.random().toString(36).slice(2);
  }
  function icon(name) {
    var paths = {
      spark: '<path d="m12 3 2.2 6.8L21 12l-6.8 2.2L12 21l-2.2-6.8L3 12l6.8-2.2z"/>',
      source: '<path d="M14 3H5v18h14V8l-5-5v5h5M8 12h8m-8 4h5"/>',
      shield: '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3z"/><path d="m8 12 3 3 5-6"/>',
      arrow: '<path d="M4 12h16m-6-6 6 6-6 6"/>'
    };
    return '<svg viewBox="0 0 24 24" aria-hidden="true">' + paths[name] + '</svg>';
  }
  function options(items, selected) {
    return items.map(function (item) {
      var value = item.code || item, label = item.label || item;
      return '<option value="' + e(value) + '"' + (value === selected ? ' selected' : '') +
        '>' + e(label) + '</option>';
    }).join("");
  }
  function intake() {
    return {
      guidance: el("#studio-guidance").value.trim(),
      question: el("#studio-topic").value.trim(),
      department: el("#studio-department").value,
      programs: Array.prototype.map.call(host.querySelectorAll('.studio-program-choice input:checked'), function (input) { return input.value; }),
      linked_feedback_ids: feedback ? [feedback.id] : [],
      entry_id: entry ? entry.id : null,
      suggestion_id: acceptedSuggestion
    };
  }
  function sameIntake(left, right) {
    if (!left || !right) return false;
    // PostgreSQL JSONB does not preserve object key order.
    return ["guidance", "question", "department", "entry_id"].every(function (key) {
      return left[key] === right[key];
    }) && JSON.stringify(left.programs) === JSON.stringify(right.programs) &&
      JSON.stringify(left.linked_feedback_ids) === JSON.stringify(right.linked_feedback_ids);
  }
  function remember() {
    try {
      sessionStorage.setItem("msfea_studio_intake", JSON.stringify({
        intake: intake(), feedback: feedback, entry: entry, current: current,
        requestKey: requestKey, lastIntake: lastIntake
        , workspaceId: workspaceId, proposal: proposal
      }));
    } catch (_) { /* Storage may be disabled; the composer still works. */ }
  }
  function setBusy(value) {
    busy = value;
    el(".studio-review").disabled = value;
    el(".studio-review").innerHTML = icon("spark") + (value ? "Review in progress…" : "Prepare & review draft");
    el(".studio-reset").disabled = value;
    host.setAttribute("aria-busy", value ? "true" : "false");
  }
  function message(text, error) {
    var node = el(".studio-status");
    node.className = "studio-status" + (error ? " error" : "");
    node.textContent = text;
  }
  function replaceWorking(text, action) {
    if (!intake().guidance) { action(); return; }
    var node = el('.studio-status');
    if (host.classList.contains('has-candidate')) {
      clearTimeout(timer);
      var existing = el('.studio-switch-confirm');
      if (existing) existing.remove();
      node = document.createElement('section');
      node.className = 'review-next studio-switch-confirm';
      node.setAttribute('role', 'status');
      el('.studio-results').appendChild(node);
    }
    else node.className = 'studio-status';
    node.innerHTML = '<p>' + e(text) + '</p><div class="actions"><button type="button" class="studio-replace">Replace working guidance</button><button type="button" class="studio-keep secondary">Keep editing</button></div>';
    node.querySelector('.studio-replace').addEventListener('click', action);
    node.querySelector('.studio-keep').addEventListener('click', function () {
      if (workspaceId) { node.remove(); pollWorkspace(); }
      else message('Your working guidance has been kept.');
    });
    hooks.showStudio(); node.querySelector('.studio-replace').focus();
  }
  function request(path, body) {
    return fetch(hooks.api + path, {
      method: body ? "POST" : "GET", headers: hooks.headers(),
      body: body ? JSON.stringify(body) : undefined
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) {
          var detail = typeof data.detail === "string" ? data.detail :
            (Array.isArray(data.detail) ? data.detail.map(function (x) { return x.msg; }).join(". ") : "The request could not finish.");
          throw new Error(detail);
        }
        return data;
      });
    });
  }
  function rail(step) {
    host.querySelectorAll(".studio-progress li").forEach(function (node, index) {
      node.classList.toggle("complete", index < step);
      node.classList.toggle("active", index === step);
      if (index === step) node.setAttribute("aria-current", "step");
      else node.removeAttribute("aria-current");
    });
  }
  function emptyReview() {
    el(".studio-results").innerHTML =
      '<div class="studio-placeholder"><span class="studio-orbit">' + icon("source") + '</span>' +
      '<span class="eyebrow">AI writing & policy review</span><h3>Turn approved guidance into a reviewed draft.</h3><p>When you select Prepare & review draft, the AI checks for missing details and overlapping policies, suggests a title, and prepares realistic student questions.</p>' +
      '<div class="review-next"><strong>You will see</strong><p>The AI’s explanation, exact policy comparisons, and a clear next step. After saving, separate search tests check whether this draft can be published safely.</p></div>' +
      '<div class="studio-promise">' + icon("shield") + '<span>Staff approve the facts.<br>Private checks protect student answers.</span></div></div>';
  }
  function reviewSteps(data) {
    var names = {interpreting:'Understand your entry', retrieving:'Find related policies', comparing:'Initial claim comparison', preparing:'Prepare student search wording', verifying:'Independent final verification'};
    var recorded = {};
    (data.steps || []).forEach(function (step) { recorded[step.stage] = step.summary; });
    return '<ol class="studio-ai-timeline">' + Object.keys(names).map(function (key) {
      var done = !!recorded[key] || (key === 'retrieving' && data.evidence && data.evidence.length);
      var active = data.stage === key && data.status === 'running';
      return '<li class="' + (done ? 'done' : active ? 'working' : 'waiting') + '"><span class="studio-step-dot">' + (done ? '✓' : active ? '…' : '·') + '</span><div><strong>' + names[key] + '</strong><p>' + e(recorded[key] || (active ? 'In progress' : key === 'retrieving' && done ? data.evidence.length + ' source passages checked' : data.status === 'completed' ? 'Not needed for this review' : 'Waiting')) + '</p></div></li>';
    }).join('') + '</ol>';
  }
  function progress(stage, model, data) {
    var names = {queued:'Your private review is queued', interpreting:'Understanding the guidance', retrieving:'Finding related policies', comparing:'Comparing the actual claims', preparing:'Preparing focused student questions', verifying:'Checking the preparation independently'};
    rail(1);
    el(".studio-results").innerHTML =
      '<div class="studio-working" role="status"><span class="studio-orbit working">' + icon("spark") + '</span>' +
      '<span class="eyebrow">AI preparation · ' + e(model || 'staff review model') + '</span>' +
      '<h3>' + e(names[stage] || 'Preparing your review') + '</h3><p>Facts, search preparation and verification are separate steps. You’ll see the feedback from each.</p>' +
      reviewSteps(data || {stage:stage, status:'running'}) + '<small>Private work only. You can leave this page and return.</small></div>';
  }
  function poll() {
    clearTimeout(timer);
    if (!current || !hooks.signedIn()) return;
    request("/admin/api/studio/reviews/" + encodeURIComponent(current)).then(function (data) {
      if (!hooks.signedIn()) return;
      if (data.outdated) { data.status = 'failed'; data.error_code = 'stale_review'; }
      if (data.status === "completed") {
        if (data.accepted_revision_id) { workspaceId = data.accepted_revision_id; remember(); pollWorkspace(); return; }
        setBusy(false); renderReport(data); remember(); return;
      }
      if (data.status === "failed") {
        setBusy(false); remember(); rail(0);
        message(errors[data.error_code] || errors.review_unavailable, true);
        el('.studio-results').innerHTML = '<section class="studio-report"><div class="review-section-head"><span class="review-label">AI WRITING & POLICY REVIEW</span><span class="review-chip attention">Review did not finish</span></div><h3>There is no AI assessment yet</h3><div class="review-model">Review model: ' + e(data.model) + '</div><p class="review-ai-summary">' + e(errors[data.error_code] || errors.review_unavailable) + '</p><div class="review-next"><h4>Your next step</h4><p>Keep the approved guidance you entered. Retry when the review service is available, or use the existing manual review route. This failure does not mean your policy is wrong, and it cannot authorize publication.</p></div><p class="review-caption">No knowledge was published. Your input and the failed review remain available for inspection.</p><details class="review-disclosure"><summary>Review reference for the maintainer</summary><p>' + e(data.id) + ' · ' + e(data.error_code) + '</p></details></section>'; return;
      }
      progress(data.stage, data.model, data);
      timer = setTimeout(poll, 2500);
    }).catch(function (error) {
      setBusy(false);
      message(error.message + " Your input is preserved. Use Resume review to check again.", true);
      el(".studio-results").innerHTML = '<button type="button" class="studio-resume secondary">Resume review</button>';
      el(".studio-resume").addEventListener("click", function () { setBusy(true); poll(); });
    });
  }
  function start() {
    clearTimeout(suggestionTimer);
    proposal = null;
    var data = intake();
    if (!data.guidance || data.guidance.length < 20) return message("Add the complete approved guidance for one topic (at least 20 characters).", true);
    if (!data.department || !data.programs[0]) return message("Choose the department and program this guidance applies to.", true);
    // Replaying a lost response reuses its request ID. A deliberate new review
    // after completion or failure gets a fresh ID.
    if (!requestKey || !sameIntake(lastIntake, data)) requestKey = unique();
    lastIntake = data;
    setBusy(true); message(""); progress("queued"); remember();
    request("/admin/api/studio/reviews", {intake: data, request_key: requestKey}).then(function (result) {
      current = result.id; requestKey = null; remember(); poll();
    }).catch(function (error) {
      setBusy(false); rail(0); message(error.message, true); emptyReview();
    });
  }
  function renderReport(data) {
    var report = data.report;
    var searchQuestions = report.prepared_retrieval_questions || report.draft.retrieval_questions || [];
    draft = report.draft;
    var duplicate = report.classification === "duplicate" && !entry;
    var officialConflict = KnowledgeReview.externalPolicyConflict(report.findings, entry && entry.id);
    var blocked = report.blocked || duplicate || officialConflict;
    rail(1); message("");
    el(".studio-results").innerHTML =
      '<section class="studio-report"><div class="studio-report-top"><span class="eyebrow">AI review complete</span><span class="studio-private">' +
      icon("shield") + ' Private draft</span></div>' +
      '<div class="studio-verdict"><span class="studio-tag ' + e(report.classification) + '">' + e(labels[report.classification]) +
      '</span><h3>' + e(draft.document_title) + '</h3></div>' +
      '<div class="review-next"><h4>' + (blocked ? 'Resolve this before continuing' : 'Ready for private testing') + '</h4><p>' + (report.blocked ? 'Add the approved answers to the specific questions below, then review again. The assistant will use the complete revised guidance.' : duplicate ? 'This rule already exists. Read the quoted source below before adding a second copy. If you meant to change a published Studio entry, choose Update that entry.' : officialConflict ? 'The quoted existing rule would remain active alongside your proposed rule. Correct your guidance, or explicitly define an approved exception and its scope. An official document change must be reviewed at its source before this entry can replace it.' : report.requires_decision ? 'Review the exact differences. You’ll make a named policy decision after the private search tests and answer previews.' : 'Confirm the source below. The system will handle search tests, preserve existing answers, and prepare actual student previews here.') + '</p>' +
      (blocked ? '<button type="button" class="studio-refine secondary">Update guidance & review again</button>' : '') + '</div>' +
      KnowledgeReview.ai(data) +
      (report.dismissed_findings && report.dismissed_findings.length ? '<div class="studio-verified-note"><strong>Independent check removed unrelated matches</strong><p>' + report.dismissed_findings.map(function (finding) { return e(finding.explanation); }).join(' ') + '</p></div>' : '') +
      '<details class="studio-evidence"><summary>How the AI prepared this entry</summary>' + reviewSteps(data) + '</details>' +
      (duplicate ? '<div class="studio-clear">This guidance is already covered. Use the existing source; creating a second copy usually adds no retrieval value. If the student could not find it, inspect the original retrieval evidence.</div>' : '') +
      '<details class="studio-evidence"><summary>Inspect the comparison sources (' + e(data.evidence.length) + ')</summary>' +
        data.evidence.map(function (source) { return '<details><summary>' + e(source.source_doc + " · " + source.section) +
          '</summary><p>' + e(source.text) + '</p></details>'; }).join("") + '</details>' +
      (!blocked ? '<section class="studio-draft-preview"><div class="studio-section-title"><h4>Prepared knowledge entry</h4><span>Canonical content</span></div>' +
        '<div class="studio-prepared-question">' + e(draft.question) + '</div><div class="studio-canonical">' + e(draft.answer) +
        '</div><p class="studio-source-note">Your approved guidance is preserved verbatim. The title and questions help organize and test it.</p></section>' +
      '<section class="studio-tests"><div class="studio-section-title"><h4>How students might ask</h4><span>Prepared by AI · tested privately next</span></div>' +
        '<ol><li>' + e(draft.representative_question) + '</li><li>' + e(draft.paraphrase_question) +
        '</li></ol><div class="studio-verify">Expected evidence <q>' + e(draft.expected_evidence) + '</q></div></section>' +
      (searchQuestions.length ? '<details class="studio-evidence"><summary>Search preparation, separate from the approved facts</summary><p>These independently verified questions test how students find this entry. We test the approved content first; search wording is added to its embedding only if a measured failure needs one bounded correction. Longer entries retain their section embeddings.</p><ul>' + searchQuestions.map(function (question) { return '<li>' + e(question) + '</li>'; }).join('') + '</ul></details>' : '') +
      '<section class="studio-approval"><h4>Confirm the source</h4>' +
        '<div class="studio-metadata"><label>Contributor name or role<input id="studio-author" autocomplete="name" maxlength="120" placeholder="Your name or staff role"></label>' +
        '<label>Responsible office / policy owner<input id="studio-authority" maxlength="200" placeholder="e.g. MSFEA CDC"></label>' +
        '<label>Effective date <small>optional</small><input id="studio-effective" type="date"></label>' +
        '<label>Supporting reference <small>optional</small><input id="studio-reference" maxlength="1000" placeholder="Approved memo, meeting or URL"></label>' +
        '<label class="wide">Reason for adding or updating<textarea id="studio-reason" maxlength="2000" placeholder="What gap does this guidance address?"></textarea></label></div>' +
        '<label class="studio-confirm"><input id="studio-confirm" type="checkbox"><span>I verified the factual guidance, its authority and scope' +
          (report.requires_decision ? ', and read the flagged claims. I understand these still require a recorded decision during validation' : '') +
          '.</span></label><div class="studio-save-row"><button type="button" class="studio-save"' + (blocked ? ' disabled' : '') +
          '>Continue to checks & previews ' + icon("arrow") + '</button><small>Stay here. The next steps run automatically.</small></div>' +
        (blocked ? '<p class="review-caption">Complete the action above before preparing a publishable draft.</p>' : '') +
        '<div class="studio-save-status" role="status" aria-live="polite"></div></section>' : '') +
      '<details class="studio-audit"><summary>Review provenance</summary><p>Model: ' + e(data.model) + ' · ' + e(data.prompt_version) +
        '<br>Review: ' + e(data.id) + '<br>Knowledge generation: ' + e(data.kb_generation) + '</p></details></section>';
    if (el("#studio-reason")) el("#studio-reason").value = feedback ? "Address the reviewed student question: " + feedback.question :
      entry ? "Update existing CDC guidance after staff review." : "Add approved CDC guidance to answer a documented knowledge gap.";
    if (el('.studio-refine')) el('.studio-refine').addEventListener('click', function () { el('#studio-guidance').focus(); message('Update the approved guidance, then choose Prepare & review draft.'); });
    if (entry && el('#studio-author')) {
      el('#studio-author').value = entry.created_by || '';
      el('#studio-authority').value = entry.authority_label || '';
      el('#studio-reference').value = entry.supporting_reference || '';
      el('#studio-effective').value = entry.effective_date || '';
    }
    host.querySelectorAll(".studio-update").forEach(function (button) {
      button.addEventListener("click", function () {
        var item = hooks.entries().find(function (value) { return value.id === Number(button.dataset.entry); });
        if (!item) return message("This source is no longer active. Refresh the dashboard.", true);
        entry = item; current = null; requestKey = null; draft = null;
        el(".studio-origin").innerHTML = 'Updating <strong>' + e(item.document_title || item.question) + '</strong>. The current version stays active until its replacement is approved.';
        el(".studio-origin").classList.remove("hidden");
        message("Review again to compare this update explicitly with its previous version.");
        emptyReview(); rail(0); remember();
        el(".studio-review").focus();
      });
    });
    if (el(".studio-save")) el(".studio-save").addEventListener("click", function () { save(data); });
    if (data.accepted_revision_id && el(".studio-save")) {
      el(".studio-save").disabled = true;
      el(".studio-save-status").textContent = "This review has a saved draft. Resuming its workspace…";
    }
    if (!sameIntake(intake(), data.intake) && el(".studio-save")) {
      el(".studio-save").disabled = true;
      message("The guidance or scope changed while this review was running. Review the updated input again.", true);
    }
    if (data.intake.suggestion_id) {
      var note = document.createElement('p'); note.className = 'studio-verified-note';
      note.textContent = 'You selected an AI-assisted answer revision. This is its fresh review; earlier checks do not authorize this version.';
      el('.studio-verdict').insertAdjacentElement('afterend', note);
    }
    attachSuggestion({key:'review:'+data.id,review_id:data.id,intake:data.intake,report:data.report});
  }
  function attachSuggestion(context) {
    var node=document.createElement('section'); node.className='studio-suggestion';
    node.setAttribute('aria-label','Optional AI answer revision');
    var before=el('.studio-approval') || el('.studio-workspace-actions') || el('.studio-audit');
    if (before) before.parentNode.insertBefore(node,before);
    else el('.studio-report').appendChild(node);
    function introduction(status) {
      node.innerHTML='<div class="studio-suggestion-head"><div><span class="eyebrow">Optional writing assistance</span><h4>Want help improving this answer?</h4></div></div><p class="studio-suggestion-why">The AI uses KB facts and this review’s feedback to suggest a clearer answer, including corrections to conflicting claims. Changes to rules, numbers and links are explained with their sources. Your answer stays unchanged until you choose.</p><button class="studio-suggestion-generate secondary">Suggest an improved answer</button><p class="studio-source-note">Review the changes, edit or discard the suggestion, then submit it for fresh review. A suggestion does not approve a policy change.</p><div class="studio-suggestion-status" role="status">'+e(status || '')+'</div>';
      node.querySelector('.studio-suggestion-generate').addEventListener('click', function () {
        if (!context.revision_id && !sameIntake(intake(),context.intake)) {
          node.querySelector('.studio-suggestion-status').textContent='Your guidance or scope changed. Run a fresh review before asking for a matching suggestion.'; return;
        }
        clearTimeout(timer);
        proposal={key:context.key,requestKey:unique(),id:null,edited:null};
        requestSuggestion();
      });
    }
    function working(job) {
      node.innerHTML='<span class="eyebrow">Optional AI revision · '+e(job && job.model || 'staff model')+'</span><div class="studio-suggestion-working" role="status"><strong>'+e(job && job.stage==='verifying' ? 'Checking the revised answer against its sources' : 'Preparing a source-backed revision')+'</strong><p>Your original answer is preserved. Nothing is being published.</p><ol><li>Read your guidance and the recorded feedback</li><li>Draft focused wording from the available facts</li><li>Independently verify the suggested claims</li><li>Show changes for your choice</li></ol></div>';
    }
    function requestSuggestion() {
      working(); remember();
      var body={request_key:proposal.requestKey};
      if (context.revision_id) body.revision_id=context.revision_id;
      else body.review_id=context.review_id;
      request('/admin/api/studio/suggestions',body).then(function (result) {
        if (!proposal || proposal.key!==context.key) return;
        proposal.id=result.id; remember(); pollSuggestion();
      }).catch(function (error) { introduction(error.message+' Your original answer is unchanged.'); });
    }
    function pollSuggestion() {
      clearTimeout(suggestionTimer);
      if (!proposal || proposal.key!==context.key || !hooks.signedIn()) return;
      request('/admin/api/studio/suggestions/'+proposal.id).then(function (job) {
        if (!proposal || proposal.key!==context.key || !node.isConnected) return;
        if (job.outdated) {
          proposal=null; remember(); introduction('The writing assistant was updated. Request a new suggestion to use its current checks. Your original answer is unchanged.'); return;
        }
        if (job.status==='failed') {
          var text={unsupported_suggestion:'The AI could not produce a fully supported answer with every changed claim explained. You can try another suggestion or edit your guidance and review it again.',suggestion_unavailable:'The suggestion service could not finish.',outdated_review:'The writing assistant was updated. Request a new suggestion to use its current checks.',stale_index:'The knowledge base changed. Run a fresh review before requesting another suggestion.'};
          proposal=null; remember(); introduction((text[job.error_code] || errors[job.error_code] || 'The suggestion could not finish.')+(job.report && job.report.rejection_reason ? ' Check feedback: '+job.report.rejection_reason : '')+' Your original answer is unchanged.'); return;
        }
        if (job.status!=='completed') { working(job); suggestionTimer=setTimeout(pollSuggestion,2500); return; }
        node.innerHTML=StudioSuggestion.card(job,proposal.edited);
        var editor=node.querySelector('.studio-suggestion-text');
        editor.value=proposal.edited == null ? job.report.suggested_answer : proposal.edited;
        if (proposal.edited != null) node.querySelector('.studio-suggestion-editor').classList.remove('hidden');
        editor.addEventListener('input', function () {
          proposal.edited=editor.value; remember();
          node.querySelector('.studio-tracked-answer').innerHTML=StudioSuggestion.diff(job.intake.guidance,editor.value);
          node.querySelector('.studio-suggested-answer').textContent=editor.value;
          node.querySelector('.studio-suggestion-verification').textContent='You edited this suggestion. The previous AI check applies to the offered wording; your version will receive a fresh review.';
        });
        node.querySelector('.studio-suggestion-edit').addEventListener('click', function () {
          node.querySelector('.studio-suggestion-editor').classList.remove('hidden'); editor.focus();
        });
        node.querySelector('.studio-suggestion-discard').addEventListener('click', function () {
          proposal=null; remember(); introduction('Suggestion discarded. Your original answer has been kept.');
        });
        node.querySelector('.studio-suggestion-use').addEventListener('click', function () {
          var value=editor.value.trim();
          if (value.length<20) { node.querySelector('.studio-suggestion-status').textContent='Keep at least 20 characters of factual guidance before reviewing.'; return; }
          if (!context.revision_id && !sameIntake(intake(),context.intake)) {
            node.querySelector('.studio-suggestion-status').textContent='Your original input changed. Keep your edits and run a fresh review instead of replacing them.'; return;
          }
          if (context.state) editWorking(context.state);
          el('#studio-guidance').value=value;
          el('#studio-topic').value=job.intake.question;
          acceptedSuggestion=job.id; workspaceId=null; current=null; requestKey=null;
          host.classList.remove('has-candidate');
          remember(); updateCount(); start();
          el('.studio-progress').scrollIntoView({block:'start',behavior:'smooth'});
        });
        remember();
      }).catch(function (error) {
        node.innerHTML='<h4>Your suggestion is saved</h4><p>'+e(error.message)+'</p><button class="studio-suggestion-resume secondary">Resume suggestion</button>';
        node.querySelector('.studio-suggestion-resume').addEventListener('click',pollSuggestion);
      });
    }
    if (proposal && proposal.key===context.key) {
      if (proposal.id) { working(); pollSuggestion(); } else requestSuggestion();
    } else introduction();
  }
  function save(data) {
    var status = el(".studio-save-status"), button = el(".studio-save");
    if (!sameIntake(intake(), data.intake)) {
      status.textContent = "The guidance or scope changed. Review it again before saving."; return;
    }
    if (!el("#studio-confirm").checked) { status.textContent = "Confirm that you reviewed the facts, authority and scope."; return; }
    var author = el("#studio-author").value.trim(), authority = el("#studio-authority").value.trim(), reason = el("#studio-reason").value.trim();
    if (author.length < 2 || !authority || !reason) { status.textContent = "Add the contributor, responsible office and reason before saving."; return; }
    var payload = Object.assign({}, draft, {
      author_name: author, source_kind: "admin_authored", authority_label: authority,
      effective_date: el("#studio-effective").value || null,
      supporting_reference: el("#studio-reference").value.trim(), change_reason: reason,
      department: data.intake.department, programs: data.intake.programs,
      linked_feedback_ids: data.intake.linked_feedback_ids, evidence_refs: []
    });
    button.disabled = true; status.textContent = "Saving your reviewed draft…";
    request("/admin/api/studio/drafts", {review_id: data.id, draft: payload}).then(function (saved) {
      workspaceId = saved.revision_id; remember();
      status.textContent = "Draft saved. Preparing private retrieval and regression checks…"; rail(2);
      return request("/admin/api/revisions/validate", {revision_id: saved.revision_id}).catch(function (error) {
        // Saving succeeded; do not offer to save again or imply that it failed.
        return {validation_error: error.message};
      });
    }).then(function (validation) {
      hooks.onSaved(''); setBusy(false); remember(); pollWorkspace();
    }).catch(function (error) { button.disabled = false; status.textContent = error.message; });
  }
  function reset(preserveFeedback) {
    clearTimeout(suggestionTimer); proposal=null; acceptedSuggestion=null;
    workspaceId = null; host.classList.remove('has-candidate');
    clearTimeout(timer); current = null; requestKey = null; draft = null; entry = null;
    if (!preserveFeedback) feedback = null;
    el("#studio-guidance").value = ""; el("#studio-topic").value = "";
    el("#studio-topic").readOnly = false;
    el("#studio-department").value = ""; setPrograms([]);
    el(".studio-origin").classList.add("hidden"); message(""); rail(0); emptyReview(); setBusy(false);
    try { sessionStorage.removeItem("msfea_studio_intake"); } catch (_) {}
    try { sessionStorage.removeItem("msfea_studio_approval"); } catch (_) {}
    updateCount();
  }
  function editWorking(state) {
    clearTimeout(suggestionTimer); proposal=null; acceptedSuggestion=null;
    clearTimeout(timer); workspaceId = null; current = null; draft = null;
    host.classList.remove('has-candidate');
    entry = Object.assign({}, state.revision, {id:state.revision.entry_id, working_draft:true});
    el('#studio-guidance').value = state.revision.answer;
    el('#studio-topic').value = feedback ? feedback.question : state.revision.question;
    el('#studio-topic').readOnly = !!feedback;
    el('#studio-department').value = state.revision.department || '';
    setPrograms(state.revision.programs);
    emptyReview(); rail(0); setBusy(false); remember(); updateCount();
    message('Your saved revision stays private. Review the revised guidance to create its successor.');
    el('#studio-guidance').focus();
  }
  function pollWorkspace() {
    clearTimeout(timer);
    if (!workspaceId || !hooks.signedIn()) return;
    var target = workspaceId;
    request('/admin/api/studio/workspaces/' + target).then(function (state) {
      if (workspaceId !== target || !hooks.signedIn()) return;
      var repaired = state.jobs.find(function (job) { return job.kind === 'repair' && ['completed','failed'].indexOf(job.status) >= 0 && job.result.successor_revision_id; });
      if (repaired) { workspaceId = repaired.result.successor_revision_id; remember(); pollWorkspace(); return; }
      renderWorkspace(state);
      var working = state.revision.state === 'publishing' || (state.run && ['pending','running'].indexOf(state.run.status) >= 0) || state.jobs.some(function (job) { return ['queued','running'].indexOf(job.status) >= 0; });
      if (working) timer = setTimeout(pollWorkspace, 2500);
    }).catch(function (error) {
      setBusy(false); host.classList.remove('has-candidate');
      message(error.message + ' Your saved draft is preserved. Resume to check its status.', true);
      el('.studio-results').innerHTML = '<section class="studio-report"><h3>Reconnect to your draft</h3><p>The connection was interrupted. Your saved work has not been lost.</p><button class="studio-resume">Resume workspace</button></section>';
      el('.studio-resume').addEventListener('click', pollWorkspace);
    });
  }
  function renderWorkspace(state) {
    var entering = !host.classList.contains('has-candidate');
    var revision = state.revision, run = state.run, jobs = state.jobs;
    var preview = jobs.find(function (job) { return job.kind === 'preview'; });
    var repair = jobs.find(function (job) { return job.kind === 'repair'; });
    var testing = run && ['pending','running'].indexOf(run.status) >= 0;
    var passed = run && run.status === 'passed' && !state.stale;
    var ready = passed && preview && preview.status === 'completed' && preview.result.passed;
    var active = revision.active, publishing = revision.state === 'publishing';
    var results = run ? run.results : [];
    var names = {schema_source:'Source & scope', candidate_index:'Private knowledge index', conflict_review:'Policy comparison', positive_retrieval:'New questions find this entry', department_isolation:'Department boundaries', unknown_department:'Unknown-department behavior', regression:'Existing questions preserved'};
    var officialConflict = state.assistance && state.assistance.report.findings.some(function (finding) { return ['direct_conflict','supersedes'].indexOf(finding.category) >= 0 && finding.entry_id !== revision.entry_id; });
    var conflict = results.find(function (result) { return result.step === 'conflict_review'; });
    var flags = conflict && conflict.details.flags || [];
    host.classList.add('has-candidate'); setBusy(false); rail(active ? 4 : ready ? 3 : 2);
    if (revision.linked_feedback_ids.length && state.assistance) {
      el('.studio-origin').classList.remove('hidden');
      el('.studio-origin').innerHTML = '<span class="studio-origin-label">Linked student question</span><strong>' + e(state.assistance.intake.question) + '</strong><span>' + (active ? 'Resolved by this published entry.' : 'The question stays in Needs attention until this entry is published.') + '</span>';
    } else el('.studio-origin').classList.add('hidden');
    el('.studio-results').innerHTML = '<section class="studio-report studio-continuous"><div class="studio-report-top"><span class="eyebrow">' + (active ? 'Published knowledge' : 'Private workspace · KB-' + revision.entry_id + ' · Version ' + revision.revision_number) + '</span><span class="studio-private">' + icon('shield') + (active ? 'Live for students' : 'Students cannot see this yet') + '</span></div>' +
      '<div class="studio-verdict"><span class="studio-tag">' + (active ? 'Published' : publishing ? 'Publishing…' : ready ? 'Ready for your approval' : testing ? 'Private checks running' : passed ? 'Preparing student previews' : 'Publication paused') + '</span><h3>' + e(revision.document_title) + '</h3></div>' +
      '<div class="studio-workflow-summary"><div><span>Approved source</span><strong>' + e(revision.authority_label) + '</strong></div><div><span>Applies to</span><strong>' + e(revision.department === 'all' ? 'All departments' : revision.department.toUpperCase()) + '</strong></div><div><span>Prepared by</span><strong>' + e(state.assistance ? state.assistance.model : 'Staff') + '</strong></div></div>' +
      '<details class="studio-evidence"><summary>Read the approved guidance and AI feedback</summary><div class="studio-canonical">' + e(revision.answer) + '</div>' + (state.assistance ? KnowledgeReview.ai(state.assistance, false) + reviewSteps(state.assistance) : '') + '</details>' +
      (active ? '<div class="studio-published"><span>✓</span><div><h4>Your knowledge is published</h4><p>Students can now retrieve this entry alongside the official documents.' + (revision.linked_feedback_ids.length ? ' The linked unanswered question has been resolved.' : '') + ' The source, author, version and approval are recorded.</p><button class="studio-new secondary">Prepare another entry</button></div></div>' : '') +
      (!active && state.review_outdated ? '<div class="review-next"><h4>Refresh this earlier AI review</h4><p>The recorded result used earlier review rules. Choose Edit approved guidance, then Prepare & review draft to use the current assistant. Keep the approved facts unchanged unless they need a real correction.</p></div>' : '') +
      '<section class="studio-checks-section"><div class="studio-section-title"><h4>Protecting student answers</h4><span>' + results.filter(function (result) { return result.status === 'passed'; }).length + ' / 7 checks passed</span></div><div class="studio-check-grid">' + Object.keys(names).map(function (key) {
        var result = results.find(function (value) { return value.step === key; });
        var needsDecision = key === 'conflict_review' && flags.length && !active;
        return '<div class="studio-check-tile ' + (needsDecision ? 'failed' : result ? result.status : 'pending') + '"><span>' + (needsDecision ? '!' : result && result.status === 'passed' ? '✓' : result && result.status === 'failed' ? '!' : '·') + '</span><strong>' + names[key] + '</strong><small>' + (needsDecision ? 'Staff decision needed' : result ? result.status === 'passed' ? 'Passed' : 'Needs attention' : 'Waiting') + '</small></div>';
      }).join('') + '</div><p class="studio-source-note">These are measured retrieval tests against a private index. The AI cannot waive a failure.</p></section>' +
      (!active && !passed && !testing ? '<section class="review-next"><h4>' + (state.stale ? 'Knowledge changed during this review' : repair && ['queued','running'].indexOf(repair.status) >= 0 ? 'The assistant is refining search preparation' : 'This entry is still private') + '</h4><p>' + (state.stale ? 'Recheck against the current knowledge before approving.' : repair && ['queued','running'].indexOf(repair.status) >= 0 ? 'One bounded correction uses the failed search evidence. Your approved facts and original test questions stay unchanged. All checks will run again.' : 'The check below needs attention. You can revise the guidance or rerun the complete checks. Nothing was published.') + '</p>' +
        results.filter(function (result) { return result.status === 'failed'; }).map(function (result) {
          var cases = result.details.lost_cases || (result.details.cases || []).filter(function (test) { return !test.passed; });
          return '<details class="studio-evidence" open><summary>' + e(names[result.step]) + '</summary>' + cases.map(function (test) { return (test.history || []).map(function (turn) { return '<p><strong>' + (turn.role === 'user' ? 'Earlier student question: ' : 'Earlier assistant reply: ') + '</strong>' + e(turn.content) + '</p>'; }).join('') + '<p><strong>Question tested:</strong> ' + e(test.question) + '</p><p><strong>What the answer should include:</strong> ' + e(test.expected_answer || test.expected_evidence || (Array.isArray(test.evidence) ? test.evidence.join('; ') : test.evidence) || revision.expected_evidence) + '</p>'; }).join('') + '<details><summary>Recorded test evidence</summary><pre>' + e(JSON.stringify(result.details, null, 2)) + '</pre></details></details>';
        }).join('') + (repair && repair.status === 'completed' ? '<p>' + e(repair.result.summary) + '</p>' : repair && repair.status === 'failed' ? '<p>The search correction could not finish (' + e(repair.error_code) + '). This is a service condition, not a policy judgment.</p>' : '') + '</section>' : '') +
      (!active && passed ? '<section class="studio-preview-section"><div class="studio-section-title"><h4>What students will see</h4><span>Actual answer model · ' + e(preview && preview.result.model || 'preparing') + '</span></div><p class="studio-help">These answers use the existing student RAG flow against this private candidate. Check the facts, citations and any links before approving.</p>' +
        (preview && preview.status === 'completed' ? (preview.result.previews || []).map(function (item) {
          return '<article class="studio-student-preview"><div class="studio-student-question"><span>Student</span><p>' + e(item.question) + '</p></div><div class="studio-student-answer"><span>CDC Assistant · private preview</span><div>' + StudioPreview.render(item.text) + '</div><ul>' + item.citations.map(function (citation) { return '<li>' + e(citation) + '</li>'; }).join('') + '</ul><small>' + e(item.disclaimer) + '</small></div></article>';
        }).join('') + (!preview.result.passed ? '<div class="review-next"><h4>A preview did not answer successfully</h4><p>The original student flow refused or could not cite its evidence. Edit the guidance or run the checks again. Approval stays paused.</p></div>' : '') : preview && preview.status === 'failed' ? '<div class="review-next"><h4>Preview service unavailable</h4><p>' + e(errors[preview.error_code] || 'The preview could not finish. Your saved facts and checks are preserved.') + '</p><button class="studio-preview-retry secondary">Retry answer previews</button></div>' : '<div class="studio-preview-loading">Preparing actual student answers…<div class="studio-loading-track"><span></span></div></div>') + '</section>' : '') +
      (!active && ready ? '<section class="studio-final-approval"><div class="studio-section-title"><h4>Approve & publish</h4><span>Human decision required</span></div><p>The AI prepared and tested the entry. You approve the policy and the student-facing result.</p>' +
        (flags.length ? '<div class="review-next"><h4>A policy decision is needed</h4><p>Review the exact differences below. Only an approved scoped exception or an update to this entry can be authorized.</p></div>' + (state.assistance ? KnowledgeReview.ai(state.assistance, false) : '') + flags.filter(function (flag) { return flag.reason.indexOf('ai_') !== 0; }).map(function (flag) { var source = conflict.details.related.find(function (item) { return item.id === flag.candidate_id; }); return '<details class="studio-evidence"><summary>Additional source check: ' + e(humanLabel(flag.reason)) + '</summary><p>A rule-based check also flagged this passage. Verify whether it governs the same claim and scope before recording a decision.</p><p><strong>Your approved guidance</strong></p><blockquote>' + e(revision.answer) + '</blockquote><p><strong>Existing source · ' + e(source ? source.source_doc + ' · ' + source.section : flag.candidate_id) + '</strong></p><blockquote>' + e(source ? source.text : 'See the recorded comparison evidence.') + '</blockquote></details>'; }).join('') : '') +
        '<label for="studio-reviewer">Reviewer name or staff role<input id="studio-reviewer" maxlength="120"></label><label for="studio-decision">Your decision<select id="studio-decision">' + (!flags.length ? '<option value="confirm_no_conflict">The facts and previews are correct</option>' : '<option value="">Choose a decision…</option><option value="valid_scoped_exception">Approved exception for the stated scope</option>' + (revision.predecessor_revision_id ? '<option value="replace_outdated">Replace this entry’s outdated version</option>' : '')) + '</select></label><label for="studio-decision-reason">Approval note<textarea id="studio-decision-reason" maxlength="2000" placeholder="What did you verify, and why is this approved?"></textarea></label><label class="studio-confirm"><input id="studio-publish-confirm" type="checkbox"><span>I verified the approved facts, scope and student previews. I authorize publication.</span></label><button class="studio-publish"' + (officialConflict || publishing ? ' disabled' : '') + '>Approve & publish ' + icon('arrow') + '</button><div class="studio-publish-status" role="status" aria-live="polite"></div></section>' : '') +
      (!active && !publishing ? '<div class="studio-workspace-actions"><button class="studio-edit-guidance secondary">Edit approved guidance</button>' + (!state.review_outdated && !testing && !jobs.some(function (job) { return ['queued','running'].indexOf(job.status) >= 0; }) ? '<button class="studio-recheck secondary">Run fresh checks</button>' : '') + '</div>' : '') +
      '<details class="studio-audit"><summary>Version and test audit</summary><p>Revision ' + revision.id + ' · ' + e(run ? run.id : 'Not tested') + '</p><pre>' + e(JSON.stringify({run:run, jobs:jobs, retrieval_questions:revision.retrieval_questions}, null, 2)) + '</pre></details></section>';
    if (entering) el('.studio-progress').scrollIntoView({block:'start', behavior:'smooth'});
    if (repair && repair.status === 'failed' && !repair.result.successor_revision_id && ['quota','provider_unavailable','interrupted','service_unavailable'].indexOf(repair.error_code) >= 0 && !state.stale) {
      var retry = document.createElement('button'); retry.className = 'studio-repair-retry secondary';
      retry.textContent = 'Retry interrupted search correction';
      retry.addEventListener('click', function () {
        retry.disabled = true;
        request('/admin/api/studio/repair/retry', {revision_id:revision.id}).then(pollWorkspace).catch(function (error) { retry.disabled = false; el('.studio-workspace-actions').appendChild(document.createTextNode(error.message)); });
      });
      el('.studio-workspace-actions').appendChild(retry);
    }
    if (el('.studio-edit-guidance')) el('.studio-edit-guidance').addEventListener('click', function () { editWorking(state); });
    if (el('.studio-recheck')) el('.studio-recheck').addEventListener('click', function (event) {
      event.currentTarget.disabled = true;
      request('/admin/api/revisions/validate', {revision_id:revision.id}).then(pollWorkspace).catch(function (error) { el('.studio-workspace-actions').appendChild(document.createTextNode(error.message)); });
    });
    if (el('.studio-preview-retry')) el('.studio-preview-retry').addEventListener('click', function (event) {
      event.currentTarget.disabled = true;
      request('/admin/api/studio/preview/retry', {revision_id:revision.id}).then(pollWorkspace).catch(function (error) { event.currentTarget.disabled = false; event.currentTarget.parentNode.appendChild(document.createTextNode(error.message)); });
    });
    if (revision.source_kind==='admin_authored' && !active && !publishing && !testing && !state.stale && !state.review_outdated && !jobs.some(function (job) { return ['queued','running'].indexOf(job.status)>=0; })) {
      attachSuggestion({key:'revision:'+revision.id,revision_id:revision.id,state:state,report:state.assistance && state.assistance.report});
    }
    if (el('#studio-reviewer')) el('#studio-reviewer').value = revision.created_by;
    if (ready && !active) {
      try {
        var savedApproval = JSON.parse(sessionStorage.getItem('msfea_studio_approval') || 'null');
        if (savedApproval && savedApproval.revision_id === revision.id && savedApproval.run_id === run.id) {
          el('#studio-reviewer').value = savedApproval.reviewer;
          el('#studio-decision').value = savedApproval.decision;
          el('#studio-decision-reason').value = savedApproval.reason;
        }
      } catch (_) { /* Browser storage may be unavailable. */ }
      ['#studio-reviewer','#studio-decision','#studio-decision-reason'].forEach(function (selector) {
        el(selector).addEventListener('input', function () {
          try { sessionStorage.setItem('msfea_studio_approval', JSON.stringify({revision_id:revision.id,run_id:run.id,reviewer:el('#studio-reviewer').value,decision:el('#studio-decision').value,reason:el('#studio-decision-reason').value})); } catch (_) {}
        });
      });
    }
    if (el('.studio-publish')) el('.studio-publish').addEventListener('click', function (event) {
      var status = el('.studio-publish-status'), button = event.currentTarget;
      if (!el('#studio-publish-confirm').checked) { status.textContent = 'Confirm that you reviewed the facts and student previews.'; return; }
      var payload = {revision_id:revision.id, run_id:run.id, reviewer_label:el('#studio-reviewer').value.trim(), reason:el('#studio-decision-reason').value.trim(), decision:el('#studio-decision').value};
      if (payload.reviewer_label.length < 2 || payload.reason.length < 5 || !payload.decision) { status.textContent = 'Add your name or role, decision and a short approval note.'; return; }
      button.disabled = true; status.textContent = 'Recording your approval and publishing the checked version…';
      request('/admin/api/studio/approve', payload).then(function () { hooks.onSaved(''); pollWorkspace(); }).catch(function (error) { button.disabled = false; status.textContent = error.message; });
    });
    if (el('.studio-new')) el('.studio-new').addEventListener('click', function () { reset(false); hooks.onSaved(''); });
  }
  function updateCount() {
    el(".studio-count").textContent = el("#studio-guidance").value.length.toLocaleString() + " / 8,000";
  }
  function setPrograms(values) {
    host.querySelectorAll('.studio-program-choice input').forEach(function (input) {
      input.checked = values.indexOf(input.value) >= 0;
    });
  }
  function mount(node, config) {
    hooks = config;
    if (host === node && node.dataset.guided === "true") return;
    host = node; node.dataset.guided = "true"; node.classList.add("guided-studio");
    node.innerHTML =
      '<ol class="studio-progress" aria-label="Knowledge workflow"><li class="active"><span>01</span> Describe</li>' +
        '<li><span>02</span> Resolve</li><li><span>03</span> Preview</li><li><span>04</span> Publish</li></ol>' +
      '<div class="studio-origin hidden"></div><div class="studio-workspace"><section class="studio-input-panel">' +
        '<div class="studio-panel-heading"><span class="studio-panel-icon">' + icon("source") +
        '</span><div><span class="eyebrow">Start with the facts</span><h3>What should students know?</h3></div></div>' +
        '<p class="studio-help">Add one approved rule or clarification. Include conditions, exceptions and dates that matter.</p>' +
        '<label for="studio-topic">Student question or topic <small>optional</small></label><input id="studio-topic" maxlength="2000" placeholder="e.g. Can I reschedule my CO-OP interview?">' +
        '<div class="studio-guidance-heading"><label for="studio-guidance">Approved guidance</label><span class="studio-count">0 / 8,000</span></div>' +
        '<textarea id="studio-guidance" maxlength="8000" placeholder="Paste the approved guidance, an excerpt from a memo, or the policy clarification. You do not need to optimize its wording for search."></textarea>' +
        '<p class="studio-privacy">Use policy information only. Remove student names, IDs and personal contact details.</p>' +
        '<div class="studio-scope"><label>Department scope<select id="studio-department"><option value="">Choose scope…</option>' +
          options(hooks.options.departments, "") + '</select></label><fieldset class="studio-programs"><legend>Programs this applies to</legend><div>' +
          hooks.options.programs.map(function (item) {
            var value = item.code || item, label = item.label || humanLabel(item);
            return '<label class="studio-program-choice"><input type="checkbox" value="' + e(value) + '"><span>' + e(label) + '</span></label>';
          }).join('') + '</div></fieldset></div>' +
        '<p class="studio-scope-note">Choose “All departments” only if the guidance applies to every department.</p>' +
        '<button type="button" class="studio-review">' + icon("spark") + 'Prepare & review draft</button>' +
        '<div class="studio-status" role="status" aria-live="polite"></div>' +
        '<div class="studio-input-footer"><span>Grounded comparison · Human approval</span><button type="button" class="studio-reset">Start fresh</button></div>' +
      '</section><section class="studio-results" aria-label="Draft and comparison review" aria-live="polite"></section></div>';
    emptyReview();
    el(".studio-review").addEventListener("click", start);
    el(".studio-reset").addEventListener("click", function () {
      replaceWorking('Start a new entry? The current working guidance will be cleared; any saved draft remains in Drafts.', function () { reset(false); });
    });
    host.querySelectorAll("#studio-guidance, #studio-topic, #studio-department, .studio-program-choice input").forEach(function (input) {
      input.addEventListener("input", function () {
        if (input.id!=='studio-guidance') acceptedSuggestion=null;
        remember(); updateCount();
        if (draft) {
          message("Your input changed. Run a fresh review to update the comparisons.");
          if (el(".studio-save")) el(".studio-save").disabled = true;
        }
      });
    });
    try {
      var restored = JSON.parse(sessionStorage.getItem("msfea_studio_intake") || "null");
      if (restored && restored.intake) {
        feedback = restored.feedback; entry = restored.entry;
        el("#studio-topic").readOnly = !!feedback;
        requestKey = restored.requestKey; lastIntake = restored.lastIntake;
        Object.keys(restored.intake).forEach(function (key) {
          var mapping = {guidance:"#studio-guidance", question:"#studio-topic", department:"#studio-department"};
          if (mapping[key]) el(mapping[key]).value = restored.intake[key];
        });
        setPrograms(restored.intake.programs);
        current = restored.current; workspaceId = restored.workspaceId || null;
        proposal=restored.proposal || null; acceptedSuggestion=restored.intake.suggestion_id || null;
        if (feedback || entry) {
          el(".studio-origin").classList.remove("hidden");
          el(".studio-origin").innerHTML = entry ?
            '<strong>' + ((entry.working_draft || entry.active === false) ? 'Reviewing saved draft: ' : 'Updating published entry: ') + e(entry.document_title || entry.question) + '</strong><span>' + ((entry.working_draft || entry.active === false) ? 'The saved revision and its failed check stay in the history. A new AI review cannot waive that failure.' : 'The current published version stays active until a successor is approved.') + (feedback ? ' The original student question remains linked.' : '') + '</span>' : feedback ?
            '<span class="studio-origin-label">From Needs attention</span><strong>' + e(feedback.question) + '</strong><span>This question remains in the queue until publication or dismissal.</span>' :
            '';
        }
        if (workspaceId) pollWorkspace();
        else if (current) { setBusy(true); poll(); }
        updateCount();
      }
    } catch (_) { /* Ignore invalid or disabled browser storage. */ }
  }
  window.KnowledgeStudio = {
    mount: mount,
    resumeDraft: function (item) {
      if (!item.assistance) { this.openDraft(item); return; }
      replaceWorking('Resume this saved workspace in place of the current working guidance?', function () {
        reset(false); entry = Object.assign({}, item, {id:item.entry_id, working_draft:true});
        var original = item.assistance && item.assistance.intake;
        if (item.linked_feedback_ids.length && original) feedback = {id:item.linked_feedback_ids[0], question:original.question};
        el('#studio-guidance').value = item.answer;
        el('#studio-topic').value = feedback ? feedback.question : item.question;
        el('#studio-topic').readOnly = !!feedback;
        el('#studio-department').value = item.department || ''; setPrograms(item.programs || []);
        workspaceId = item.id; hooks.showStudio(); remember(); updateCount(); pollWorkspace();
      });
    },
    openQuestion: function (item) {
      if (busy) { hooks.showStudio(); message("Finish the current review before opening another question.", true); return; }
      replaceWorking('Open this student question in place of the current working guidance?', function () {
      reset(false); feedback = {id:item.id, question:item.question};
      el("#studio-topic").value = item.question;
      el("#studio-topic").readOnly = true;
      el(".studio-origin").innerHTML = '<span class="studio-origin-label">From Needs attention</span><strong>' +
        e(item.question) + '</strong><span>This question stays in the queue until reviewed knowledge is published or you dismiss it.</span>';
      el(".studio-origin").classList.remove("hidden");
      hooks.showStudio(); remember(); el("#studio-guidance").focus();
      });
    },
    openEntry: function (item) {
      if (busy) { hooks.showStudio(); message("Finish the current review before updating another entry.", true); return; }
      replaceWorking('Open this published entry in place of the current working guidance?', function () {
      reset(false); entry = item;
      el("#studio-guidance").value = item.answer; el("#studio-topic").value = item.question;
      el("#studio-department").value = item.department || "";
      setPrograms(item.programs || []);
      el(".studio-origin").innerHTML = 'Updating <strong>' + e(item.document_title || item.question) + '</strong>. Its current version stays active until the successor is approved.';
      el(".studio-origin").classList.remove("hidden");
      hooks.showStudio(); remember(); updateCount(); el("#studio-guidance").focus();
      });
    },
    openDraft: function (item) {
      if (busy) { hooks.showStudio(); message('Finish the current AI review first.', true); return; }
      replaceWorking('Review this saved draft in place of the current working guidance?', function () {
        reset(false); entry = Object.assign({}, item, {id:item.entry_id, working_draft:true});
        var original = item.assistance && item.assistance.intake;
        if (item.linked_feedback_ids.length && original) feedback = {id:item.linked_feedback_ids[0], question:original.question};
        el('#studio-guidance').value = item.answer;
        el('#studio-topic').value = feedback ? feedback.question : item.question;
        el('#studio-topic').readOnly = !!feedback;
        el('#studio-department').value = item.department || '';
        setPrograms(item.programs || []);
        el('.studio-origin').innerHTML = '<strong>Reviewing draft: ' + e(item.document_title) + '</strong><span>This will create a new revision of the same entry. The saved draft and failed test remain in its history. An AI review cannot waive the search failure.</span>';
        el('.studio-origin').classList.remove('hidden');
        hooks.showStudio(); remember(); updateCount(); el('#studio-guidance').focus();
      });
    },
    signOut: function () {
      if (host) reset(false);
      clearTimeout(timer); current = null; feedback = null; entry = null; draft = null; busy = false;
      try { sessionStorage.removeItem("msfea_studio_intake"); } catch (_) {}
      if (host) { host.dataset.guided = "false"; host = null; }
    }
  };
}());
