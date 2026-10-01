const {test}=require('node:test');
const assert=require('node:assert/strict');
const suggestion=require('../dashboard/studio_suggestion.js');
const job={model:'staff-model',intake:{guidance:'AI text is limited to 25%.'},report:{suggested_answer:'AI text is limited to 25%. Disclose and cite its use.',explanation:'Added the source-backed disclosure requirement.',missing_details:[],sources:[{source:'guidelines.md',section:'AI policy',text:'AI use must be disclosed and cited.'}],verification:{explanation:'The original limit and added condition are supported.'}}};
test('an addition highlights the new condition while keeping the original rule readable',()=>{
 const html=suggestion.diff(job.intake.guidance,job.report.suggested_answer);
 assert.match(html,/<ins>Disclose and cite its use\.<\/ins>/);
 assert.doesNotMatch(html,/<del>/);
 assert.match(html,/25%\./);
});
test('replacement shows removed and added words and preserves the accepted text',()=>{
 const html=suggestion.diff('Attend Thursday at 2 p.m.','Attend Tuesday at 2 p.m.');
 assert.match(html,/<del>Thursday /);
 assert.match(html,/<ins>Tuesday /);
 const accepted=html.replace(/<del>[\s\S]*?<\/del>/g,'').replace(/<[^>]+>/g,'');
 assert.equal(accepted,'Attend Tuesday at 2 p.m.');
});
test('unchanged short answers have no manufactured diff',()=>{
 assert.equal(suggestion.diff('A complete answer.','A complete answer.'),'A complete answer.');
});
test('suggestion content and source text are escaped',()=>{
 const bad={...job,model:'<script>bad</script>',report:{...job.report,suggested_answer:'<img src=x>',sources:[{source:'<iframe>',section:'x',text:'<script>oops</script>'}]}};
 const html=suggestion.card(bad);
 assert.doesNotMatch(html,/<script>|<iframe>|<img/);
 assert.match(html,/&lt;img/);
});
test('missing facts are questions and human choices explicitly require fresh review',()=>{
 const html=suggestion.card({...job,report:{...job.report,missing_details:['What are the approved opening hours?']}});
 assert.match(html,/These details still need you/);
 assert.match(html,/approved opening hours/);
 assert.match(html,/Use & review again/);
 assert.match(html,/Edit suggestion/);
 assert.match(html,/Discard suggestion/);
 assert.match(html,/publication approval are still required/);
 assert.match(html,/Read your original answer/);
});
test('large edits stay bounded and show both original and proposed text',()=>{
 const html=suggestion.diff('before '.repeat(1200),'after '.repeat(1200));
 assert.match(html,/^<del>/); assert.match(html,/<ins>/);
});
test('restored human edits do not display the original AI verification as their own',()=>{
 const html=suggestion.card(job,'A manually edited answer.');
 assert.match(html,/You edited this suggestion/);
 assert.match(html,/your version will receive a fresh review/);
 assert.doesNotMatch(html,/AI source and change check:/);
});
test('policy corrections display original claim, replacement, reason and exact KB evidence',()=>{
 const corrected={...job,intake:{guidance:'The course is 5 credits.'},report:{...job.report,suggested_answer:'The course is 1 credit.',claim_changes:[{before:'5 credits',after:'1 credit',reason:'The official source lists 1 credit.',sources:[{source:'official.md',section:'Credits',text:'The course is 1 credit.'}]}]}};
 const html=suggestion.card(corrected);
 for(const text of ['Changes to your claims','Meaning changed','You wrote','AI proposes','5 credits','1 credit','Why this changes','KB evidence','official.md','not approved policy updates']) assert.ok(html.includes(text),text);
 assert.match(html,/<del>5 credits\./);
 assert.match(html,/<ins>1 credit\./);
 assert.match(suggestion.card(corrected,'My edited version.'),/These explanations describe the AI’s offered version/);
});
test('claim corrections cannot inject HTML into explanations or source quotes',()=>{
 const corrected={...job,report:{...job.report,claim_changes:[{before:'<script>x</script>',after:'<img src=x>',reason:'<iframe>',sources:[{source:'<svg>',section:'x',text:'<script>y</script>'}]}]}};
 const html=suggestion.card(corrected);
 assert.doesNotMatch(html,/<script>|<iframe>|<img|<svg/);
 assert.match(html,/&lt;script/);
});
