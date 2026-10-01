/* One guided composer for knowledge intake and unanswered-question review. */
(function () {
  "use strict";
  var host, hooks, current = null, timer = null, feedback = null, entry = null;
  var draft = null, requestKey = null, lastIntake = null, busy = false;
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
      entry_id: entry ? entry.id : null
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
    node.className = 'studio-status';
    node.innerHTML = '<p>' + e(text) + '</p><div class="actions"><button type="button" class="studio-replace">Replace working guidance</button><button type="button" class="studio-keep secondary">Keep editing</button></div>';
    node.querySelector('.studio-replace').addEventListener('click', action);
    node.querySelector('.studio-keep').addEventListener('click', function () { message('Your working guidance has been kept.'); });
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
  function progress(stage, model) {
    var comparing = stage === "comparing";
    rail(1);
    el(".studio-results").innerHTML =
      '<div class="studio-working" role="status"><span class="studio-orbit working">' + icon("spark") + '</span>' +
      '<span class="eyebrow">' + (comparing ? 'AI review · ' + e(model || 'staff review model') : 'Preparing the AI review') + '</span>' +
      '<h3>' + (comparing ? "The AI is reviewing your guidance" : stage === "queued" ? "Waiting for the review worker" : "Finding policies for the AI to compare") +
      '</h3><p>' + (comparing ? "The AI is checking coverage, facts, conditions and scope, then preparing its explanation and suggested questions." :
        "The system retrieves related passages. The AI will compare their claims with your proposed guidance next.") + '</p>' +
      '<div class="studio-loading-track"><span></span></div><small>Nothing is visible to students. You can leave this page and return.</small></div>';
  }
  function poll() {
    clearTimeout(timer);
    if (!current || !hooks.signedIn()) return;
    request("/admin/api/studio/reviews/" + encodeURIComponent(current)).then(function (data) {
      if (!hooks.signedIn()) return;
      if (data.status === "completed") {
        setBusy(false); renderReport(data); remember(); return;
      }
      if (data.status === "failed") {
        setBusy(false); remember(); rail(0);
        message(errors[data.error_code] || errors.review_unavailable, true);
        el('.studio-results').innerHTML = '<section class="studio-report"><div class="review-section-head"><span class="review-label">AI WRITING & POLICY REVIEW</span><span class="review-chip attention">Review did not finish</span></div><h3>There is no AI assessment yet</h3><div class="review-model">Review model: ' + e(data.model) + '</div><p class="review-ai-summary">' + e(errors[data.error_code] || errors.review_unavailable) + '</p><div class="review-next"><h4>Your next step</h4><p>Keep the approved guidance you entered. Retry when the review service is available, or use the existing manual review route. This failure does not mean your policy is wrong, and it cannot authorize publication.</p></div><p class="review-caption">No knowledge was published. Your input and the failed review remain available for inspection.</p><details class="review-disclosure"><summary>Review reference for the maintainer</summary><p>' + e(data.id) + ' · ' + e(data.error_code) + '</p></details></section>'; return;
      }
      progress(data.stage, data.model);
      timer = setTimeout(poll, 2500);
    }).catch(function (error) {
      setBusy(false);
      message(error.message + " Your input is preserved. Use Resume review to check again.", true);
      el(".studio-results").innerHTML = '<button type="button" class="studio-resume secondary">Resume review</button>';
      el(".studio-resume").addEventListener("click", function () { setBusy(true); poll(); });
    });
  }
  function start() {
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
    draft = report.draft;
    var duplicate = report.classification === "duplicate" && !entry;
    var blocked = report.blocked || duplicate;
    rail(2); message("");
    el(".studio-results").innerHTML =
      '<section class="studio-report"><div class="studio-report-top"><span class="eyebrow">AI review complete</span><span class="studio-private">' +
      icon("shield") + ' Private draft</span></div>' +
      '<div class="studio-verdict"><span class="studio-tag ' + e(report.classification) + '">' + e(labels[report.classification]) +
      '</span><h3>' + e(draft.document_title) + '</h3></div>' +
      '<div class="review-next"><h4>Your next step</h4><p>' + (report.blocked ? 'Answer the AI’s specific questions below by adding approved information on the left, then run a fresh AI review. Saving is paused until those details are complete.' : duplicate ? 'Use the existing source rather than adding another copy. A retrieval failure should be investigated separately.' : report.requires_decision ? 'Read the quoted policy differences below and verify the approved rule with its owner. You can save a private draft for testing; a named policy decision is still required before publication.' : 'Check the AI’s feedback and the unchanged guidance below. Add the source owner and contributor, then save the private draft to run search tests.') + '</p></div>' +
      KnowledgeReview.ai(data) +
      (duplicate ? '<div class="studio-clear">This guidance is already covered. Use the existing source; creating a second copy usually adds no retrieval value. If the student could not find it, inspect the original retrieval evidence.</div>' : '') +
      '<details class="studio-evidence"><summary>Inspect the comparison sources (' + e(data.evidence.length) + ')</summary>' +
        data.evidence.map(function (source) { return '<details><summary>' + e(source.source_doc + " · " + source.section) +
          '</summary><p>' + e(source.text) + '</p></details>'; }).join("") + '</details>' +
      '<section class="studio-draft-preview"><div class="studio-section-title"><h4>Prepared knowledge entry</h4><span>Canonical content</span></div>' +
        '<div class="studio-prepared-question">' + e(draft.question) + '</div><div class="studio-canonical">' + e(draft.answer) +
        '</div><p class="studio-source-note">Your approved guidance is preserved verbatim. The title and questions help organize and test it.</p></section>' +
      '<section class="studio-tests"><div class="studio-section-title"><h4>How students might ask</h4><span>To be tested privately</span></div>' +
        '<ol><li>' + e(draft.representative_question) + '</li><li>' + e(draft.paraphrase_question) +
        '</li></ol><div class="studio-verify">Expected evidence <q>' + e(draft.expected_evidence) + '</q></div></section>' +
      '<section class="studio-approval"><h4>Confirm the source</h4>' +
        '<div class="studio-metadata"><label>Contributor name or role<input id="studio-author" autocomplete="name" maxlength="120" placeholder="Your name or staff role"></label>' +
        '<label>Responsible office / policy owner<input id="studio-authority" maxlength="200" placeholder="e.g. MSFEA CDC"></label>' +
        '<label>Effective date <small>optional</small><input id="studio-effective" type="date"></label>' +
        '<label>Supporting reference <small>optional</small><input id="studio-reference" maxlength="1000" placeholder="Approved memo, meeting or URL"></label>' +
        '<label class="wide">Reason for adding or updating<textarea id="studio-reason" maxlength="2000" placeholder="What gap does this guidance address?"></textarea></label></div>' +
        '<label class="studio-confirm"><input id="studio-confirm" type="checkbox"><span>I verified the factual guidance, its authority and scope' +
          (report.requires_decision ? ', and read the flagged claims. I understand these still require a recorded decision during validation' : '') +
          '.</span></label><div class="studio-save-row"><button type="button" class="studio-save"' + (blocked ? ' disabled' : '') +
          '>Save draft & run checks ' + icon("arrow") + '</button><small>Final human review is required before publishing.</small></div>' +
        (blocked ? '<p class="review-caption">Saving is paused: ' + (duplicate ? 'the guidance is already covered by an existing source.' : 'the requested approved information is missing.') + '</p>' : '') +
        '<div class="studio-save-status" role="status" aria-live="polite"></div></section>' +
      '<details class="studio-audit"><summary>Review provenance</summary><p>Model: ' + e(data.model) + ' · ' + e(data.prompt_version) +
        '<br>Review: ' + e(data.id) + '<br>Knowledge generation: ' + e(data.kb_generation) + '</p></details></section>';
    el("#studio-reason").value = feedback ? "Address the reviewed student question: " + feedback.question :
      entry ? "Update existing CDC guidance after staff review." : "";
    if (entry) {
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
    el(".studio-save").addEventListener("click", function () { save(data); });
    if (data.accepted_revision_id) {
      el(".studio-save").disabled = true;
      el(".studio-save-status").textContent = "This review already has a saved draft. Continue in Drafts.";
    }
    if (!sameIntake(intake(), data.intake)) {
      el(".studio-save").disabled = true;
      message("The guidance or scope changed while this review was running. Review the updated input again.", true);
    }
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
      status.textContent = "Draft saved. Preparing private retrieval and regression checks…"; rail(3);
      return request("/admin/api/revisions/validate", {revision_id: saved.revision_id}).catch(function (error) {
        // Saving succeeded; do not offer to save again or imply that it failed.
        return {validation_error: error.message};
      });
    }).then(function (validation) {
      clearTimeout(timer); current = null;
      try { sessionStorage.removeItem("msfea_studio_intake"); } catch (_) {}
      hooks.onSaved(validation.validation_error || "");
      reset(false);
    }).catch(function (error) { button.disabled = false; status.textContent = error.message; });
  }
  function reset(preserveFeedback) {
    clearTimeout(timer); current = null; requestKey = null; draft = null; entry = null;
    if (!preserveFeedback) feedback = null;
    el("#studio-guidance").value = ""; el("#studio-topic").value = "";
    el("#studio-topic").readOnly = false;
    el("#studio-department").value = ""; setPrograms([]);
    el(".studio-origin").classList.add("hidden"); message(""); rail(0); emptyReview(); setBusy(false);
    try { sessionStorage.removeItem("msfea_studio_intake"); } catch (_) {}
    updateCount();
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
      '<ol class="studio-progress" aria-label="Knowledge workflow"><li class="active"><span>01</span> Add guidance</li>' +
        '<li><span>02</span> AI comparison</li><li><span>03</span> Staff review</li><li><span>04</span> Validate & publish</li></ol>' +
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
            var value = item.code || item, label = item.label || item;
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
        current = restored.current;
        if (feedback || entry) {
          el(".studio-origin").classList.remove("hidden");
          el(".studio-origin").innerHTML = entry ?
            '<strong>' + ((entry.working_draft || entry.active === false) ? 'Reviewing saved draft: ' : 'Updating published entry: ') + e(entry.document_title || entry.question) + '</strong><span>' + ((entry.working_draft || entry.active === false) ? 'The saved revision and its failed check stay in the history. A new AI review cannot waive that failure.' : 'The current published version stays active until a successor is approved.') + (feedback ? ' The original student question remains linked.' : '') + '</span>' : feedback ?
            '<span class="studio-origin-label">From Needs attention</span><strong>' + e(feedback.question) + '</strong><span>This question remains in the queue until publication or dismissal.</span>' :
            '';
        }
        if (current) { setBusy(true); poll(); }
        updateCount();
      }
    } catch (_) { /* Ignore invalid or disabled browser storage. */ }
  }
  window.KnowledgeStudio = {
    mount: mount,
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
