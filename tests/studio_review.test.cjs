const {test} = require('node:test');
const assert = require('node:assert/strict');
const review = require('../dashboard/review.js');
const ai = {model:'recorded-model', report:{classification:'new_information', summary:'The proposed schedule is new.', findings:[], draft:{document_title:'CDC Weekly Advising Window', representative_question:'When is advising open?', paraphrase_question:'Which day can I attend advising?'}}};
const item = {id:1, source_kind:'admin_authored', document_title:'CDC Weekly Advising Window', answer:'Thursday, 2–4 p.m.', assistance:ai};
const run = {id:'recorded-run', status:'failed', results:[{step:'regression', status:'failed', details:{lost_cases:[{id:'followup-letter-location', question:'Where do I get it?', history:[{role:'user',content:'Can the CDC provide a required-internship letter?'},{role:'assistant',content:'Yes, it can.'}], expected_answer:'Request the letter through the CDC letter request form.', source_doc:'summer-training-guidelines-2026.md', source_section:'Requesting a Letter'}]}}]};

test('a regression shows the conversation, expected answer and a maintainer action above positive AI advice', () => {
  const html = review.render(run,item);
  assert.match(html,/Can the CDC provide a required-internship letter/);
  assert.match(html,/Where do I get it\?/);
  assert.match(html,/Request the letter through the CDC letter request form/);
  assert.match(html,/Required evidence found/);
  assert.match(html,/Required evidence missing/);
  assert.match(html,/Copy issue for maintainer/);
  assert.match(html,/You do not need to diagnose search rankings/);
  assert.ok(html.indexOf('The affected conversation') < html.indexOf('What the AI found'));
  assert.match(html,/The proposed schedule is new/);
  assert.doesNotMatch(html,/undefined|null|would be lost/);
});
test('historical explanations do not invent stored rankings', () => {
  const html = review.render(run,item);
  assert.match(html,/exact ranking cause has not been established/);
  assert.doesNotMatch(html,/rank 1|displaced by this draft/);
});
test('source and model content is escaped', () => {
  const dangerous = {...item, assistance:{model:'<script>alert(1)</script>',report:{...ai.report,summary:'<img src=x onerror=alert(1)>'}}};
  const html = review.render(run,dangerous);
  assert.doesNotMatch(html,/<script>|<img/);
  assert.match(html,/&lt;script&gt;/);
});
test('manual revisions do not claim an AI review occurred', () => {
  const html = review.render(null,{...item,assistance:null});
  assert.match(html,/No AI feedback was recorded/);
  assert.match(html,/Next: test this draft privately/);
  assert.doesNotMatch(html,/Reviewed by|AI review completed/);
});
test('passing search tests still require a policy decision', () => {
  const passed = {...run,status:'passed',results:Object.keys({schema_source:1,candidate_index:1,conflict_review:1,positive_retrieval:1,department_isolation:1,unknown_department:1,regression:1}).map(step=>({step,status:'passed',details:{}}))};
  const html = review.render(passed,item);
  assert.match(html,/7 \/ 7 passed/);
  assert.match(html,/Your policy decision is next/);
  assert.match(html,/Passing search tests does not establish that a policy is correct/);
  assert.match(html,/Required before publishing/);
});
test('AI conflict advice shows both literal claims and its explanation', () => {
  const html = review.ai({model:'test-model',report:{...ai.report,classification:'direct_conflict',requires_decision:true,findings:[{category:'direct_conflict',explanation:'The two days differ under the same scope.',proposed_claim:'Thursday.',existing_claim:'Wednesday.',source_doc:'policy.md',section:'Advising'}]}});
  assert.match(html,/Your proposed claim/);
  assert.match(html,/Thursday\./);
  assert.match(html,/Wednesday\./);
  assert.match(html,/The two days differ under the same scope/);
  assert.match(html,/AI finding/);
});
test('new-answer failures show the actual failing question and reason', () => {
  const html = review.render({...run,results:[{step:'positive_retrieval',status:'failed',details:{cases:[{question:'Which day is advising open?',passed:false,candidate_hit:false,expected_evidence:'Thursday'}]}}]},item);
  assert.match(html,/Which day is advising open/);
  assert.match(html,/draft was absent from the selected search results/);
  assert.match(html,/Copy issue for maintainer/);
});
test('a copied issue includes the original run and advice without claiming it was sent', () => {
  const text = review.diagnostic(item,run);
  assert.match(text,/recorded-run/);
  assert.match(text,/followup-letter-location/);
  assert.match(text,/AI feedback \(advisory\)/);
  assert.match(text,/evaluation questions unchanged/);
});
test('missing coverage is explicit AI advice and never displayed as a passed check', () => {
  const html = review.ai({model:'test-model',report:{...ai.report,one_focused_topic:false,question_supported:false,clarifications:['Provide the approved eligibility conditions.']}});
  assert.match(html,/Topic check · AI says/);
  assert.match(html,/split the topics/);
  assert.match(html,/approved details are missing/);
  assert.match(html,/Provide the approved eligibility conditions/);
  assert.doesNotMatch(html,/guidance covers the supplied question/);
});
