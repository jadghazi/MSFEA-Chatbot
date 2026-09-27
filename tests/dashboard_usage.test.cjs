const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.join(__dirname, '..');

function setup() {
  const elements = {};
  for (const id of ['usage-report','usage-status','usage-range','usage-period','usage-retry']) {
    elements[id] = {innerHTML:'',textContent:'',value:'30',attrs:{},
      setAttribute(k,v){this.attrs[k]=v;},removeAttribute(k){delete this.attrs[k];},
      querySelectorAll(){return [];}};
  }
  const context = vm.createContext({document:{getElementById:id=>elements[id],addEventListener(){}},
    API:'',headers:()=>({}),fetch:()=>Promise.resolve({ok:true,json:()=>Promise.resolve(fixture())})});
  const html = fs.readFileSync(path.join(root,'dashboard/index.html'),'utf8');
  vm.runInContext(html.slice(html.indexOf('function esc(s)'),html.indexOf('function timeAgo')),context);
  vm.runInContext(fs.readFileSync(path.join(root,'dashboard/usage.js'),'utf8'),context);
  return {context,elements};
}
function fixture() {
  return {start:'2026-09-01T00:00:00Z',end:'2026-09-07T12:00:00Z',
    summary:{total:10,answered:6,refused:2,temporary_errors:2,pending:2,thumbs_up:3,thumbs_down:1,
      latency_samples:0,avg_llm_latency_ms:null,p95_llm_latency_ms:null,token_samples:0,
      llm_input_tokens:null,llm_output_tokens:null,answers_with_citations:5},
    daily:[],unanswered:[],sources:[],negative_reasons:[]};
}
test('uses distinct denominators for answer rate, helpfulness, participation and outcomes',()=>{
  const {context,elements}=setup();context.renderUsage(fixture());
  const html=elements['usage-report'].innerHTML;
  assert.match(html,/kpi-value">75%/); // 6 / (6 + 2), not 6 / 10
  assert.match(html,/3 helpful \/ 4 answer ratings/);
  assert.match(html,/40%<\/strong><span>Questions rated/);
  assert.match(html,/60%<\/small>/); // answer outcome / all logged questions
  assert.match(html,/83.3%<\/small>/); // citation presence / answered
  assert.doesNotMatch(html,/NaN|Infinity/);
});
test('empty and missing measurements stay unavailable, never 0% satisfaction or 0ms latency',()=>{
  const {context,elements}=setup();const data=fixture();
  for(const k of Object.keys(data.summary))if(data.summary[k]!==null)data.summary[k]=0;
  context.renderUsage(data);const html=elements['usage-report'].innerHTML;
  assert.equal((html.match(/kpi-value">—/g)||[]).length,2);
  assert.match(html,/No interactions logged/);
  assert.match(html,/Average generation<\/span><strong>—/);
  assert.doesNotMatch(html,/NaN|Infinity|0\.00 s/);
});
test('escapes logged questions, source labels and rating reasons',()=>{
  const {context,elements}=setup();const data=fixture();const attack='<img src=x onerror=alert(1)>';
  data.unanswered=[{question:attack,count:1,oldest:data.start}];
  data.sources=[{source:attack,count:1}];data.negative_reasons=[{reason:attack,count:1}];
  context.renderUsage(data);const html=elements['usage-report'].innerHTML;
  assert.doesNotMatch(html,/<img/);assert.equal((html.match(/&lt;img/g)||[]).length,3);
});
test('an older range response cannot overwrite the latest selected range',async()=>{
  const {context,elements}=setup();const requests=[];
  context.fetch=()=>new Promise(resolve=>requests.push(resolve));
  const first=context.loadUsage();elements['usage-range'].value='7';const second=context.loadUsage();
  const newer=fixture();newer.summary.total=77;
  requests[1]({ok:true,json:()=>Promise.resolve(newer)});await second;
  requests[0]({ok:true,json:()=>Promise.resolve(fixture())});await first;
  assert.match(elements['usage-report'].innerHTML,/kpi-value">77/);
  assert.equal(elements['usage-status'].textContent,'');
  assert.equal(elements['usage-report'].attrs['aria-busy'],undefined);
});
test('failed refresh clears stale metrics and offers a working retry',async()=>{
  const {context,elements}=setup();context.renderUsage(fixture());
  context.fetch=()=>Promise.resolve({ok:false,status:503});await context.loadUsage();
  assert.equal(elements['usage-report'].innerHTML,'');
  assert.match(elements['usage-status'].innerHTML,/Usage data could not be loaded/);
  context.fetch=()=>Promise.resolve({ok:true,json:()=>Promise.resolve(fixture())});
  await elements['usage-retry'].onclick();assert.match(elements['usage-report'].innerHTML,/kpi-value">10/);
});
