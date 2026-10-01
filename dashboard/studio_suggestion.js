/* Safe tracked changes for optional, source-backed answer revisions. */
(function (root) {
  'use strict';
  function escape(value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
    });
  }
  function diff(before, after) {
    var a = String(before).match(/\S+\s*/g) || [], b = String(after).match(/\S+\s*/g) || [];
    var aw=a.map(function (word) { return word.trim(); }), bw=b.map(function (word) { return word.trim(); });
    if (before === after) return escape(before);
    if (a.length * b.length > 1000000) return '<del>' + escape(before) + '</del><ins>' + escape(after) + '</ins>';
    var rows = Array.from({length:a.length+1}, function () { return new Uint16Array(b.length+1); });
    for (var i=a.length-1;i>=0;i--) for (var j=b.length-1;j>=0;j--) {
      rows[i][j] = aw[i] === bw[j] ? rows[i+1][j+1]+1 : Math.max(rows[i+1][j],rows[i][j+1]);
    }
    var pieces=[], x=0, y=0;
    function push(kind,text) {
      var last=pieces[pieces.length-1];
      if (last && last.kind===kind) last.text+=text;
      else pieces.push({kind:kind,text:text});
    }
    while (x<a.length || y<b.length) {
      if (x<a.length && y<b.length && aw[x]===bw[y]) { push('same',b[y++]); x++; }
      else if (y<b.length && (x===a.length || rows[x][y+1]>=rows[x+1][y])) push('added',b[y++]);
      else push('removed',a[x++]);
    }
    return pieces.map(function (piece) { return piece.kind==='same' ? escape(piece.text) : '<'+(piece.kind==='added'?'ins':'del')+'>'+escape(piece.text)+'</'+(piece.kind==='added'?'ins':'del')+'>'; }).join('');
  }
  function card(job, edited) {
    var report=job.report, answer=edited == null ? report.suggested_answer : edited;
    var changes=report.claim_changes || [];
    return '<div class="studio-suggestion-head"><div><span class="eyebrow">Optional AI revision · '+escape(job.model)+'</span><h4>A suggested answer, with changes visible</h4></div><span class="studio-private">Awaiting your choice</span></div>'+
      '<p class="studio-suggestion-why">'+escape(report.explanation)+'</p>'+
      '<h4>Suggested answer</h4><div class="studio-suggested-answer studio-canonical">'+escape(answer)+'</div>'+
      (report.missing_details.length ? '<div class="studio-suggestion-missing"><strong>These details still need you</strong><ul>'+report.missing_details.map(function (detail) { return '<li>'+escape(detail)+'</li>'; }).join('')+'</ul><p>The AI could not find approved facts for these details. Add them only if you can confirm them.</p></div>' : '')+
      (changes.length ? '<section class="studio-claim-changes" aria-label="Changes to your claims"><span class="eyebrow">Meaning changed · Review before using</span><h4>Changes to your claims</h4><p>'+(edited != null ? 'These explanations describe the AI’s offered version. Your edits appear below and will receive a fresh review.' : 'The AI proposes these corrections based on current KB facts. They are suggestions for your decision, not approved policy updates.')+'</p>'+changes.map(function (change) {
        var sources=change.sources.filter(function (source,index,all) { return all.findIndex(function (item) { return item.text===source.text; })===index; });
        var quotes=sources.map(function (source) { return '<div class="studio-suggestion-source"><strong>KB evidence · '+escape(source.source)+' · '+escape(source.section)+'</strong><blockquote>'+escape(source.text)+'</blockquote></div>'; });
        return '<article class="studio-claim-change"><div class="studio-claim-pair"><div><strong>You wrote</strong><blockquote>'+escape(change.before)+'</blockquote></div><div><strong>AI proposes</strong><blockquote>'+escape(change.after)+'</blockquote></div></div><p><strong>Why this changes: </strong>'+escape(change.reason)+'</p>'+quotes[0]+(quotes.length>1 ? '<details class="studio-evidence"><summary>Additional KB evidence ('+(quotes.length-1)+')</summary>'+quotes.slice(1).join('')+'</details>' : '')+'</article>';
      }).join('')+'</section>' : '')+
      '<details class="studio-evidence"><summary>See highlighted word changes</summary><div class="studio-change-legend"><span><ins>Added wording</ins></span><span><del>Removed wording</del></span></div>'+
      '<div class="studio-tracked-answer" aria-label="Suggested answer with tracked changes">'+diff(job.intake.guidance,answer)+'</div></details>'+
      '<details class="studio-evidence"><summary>Read your original answer</summary><div class="studio-canonical">'+escape(job.intake.guidance)+'</div></details>'+
      '<label class="studio-suggestion-editor hidden">Edit the suggested answer<textarea maxlength="8000" rows="7" class="studio-suggestion-text"></textarea></label>'+
      '<details class="studio-evidence"><summary>Facts used in this suggestion ('+report.sources.length+')</summary>'+report.sources.map(function (source) { return '<div class="studio-suggestion-source"><strong>'+escape(source.source)+' · '+escape(source.section)+'</strong><blockquote>'+escape(source.text)+'</blockquote></div>'; }).join('')+'</details>'+
      '<p class="studio-suggestion-verification">'+(edited != null ? 'You edited this suggestion. The previous AI check applies to the offered wording; your version will receive a fresh review.' : 'AI source and change check: '+escape(report.verification.explanation))+'</p>'+
      '<div class="studio-suggestion-actions"><button class="studio-suggestion-use">Use & review again</button><button class="studio-suggestion-edit secondary">Edit suggestion</button><button class="studio-suggestion-discard secondary">Discard suggestion</button></div>'+
      '<p class="studio-source-note">Using this revision updates your working answer and starts a fresh AI review. Private tests, student previews and your publication approval are still required.</p>'+
      '<div class="studio-suggestion-status" role="status" aria-live="polite"></div>';
  }
  var api={diff:diff,card:card};
  if (typeof module==='object' && module.exports) module.exports=api;
  else root.StudioSuggestion=api;
}(typeof window==='undefined' ? this : window));
