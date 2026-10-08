const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.join(__dirname, '..');
function fixture() {
  return {day:'2026-10-08',enabled:true,environment_enabled:true,price_valid_until:'2026-12-31',
    limits:{requests:100,tokens:500000,cost_usd:0.5,ip_requests:200,chat_questions:40,concurrency:8},
    usage:[{day:'2026-10-08',model:'student-model',purpose:'student',requests:2,input_tokens:1000,
      visible_output_tokens:100,reasoning_tokens:800,charged_tokens:1900,charged_usd:0.004125,uncertain_attempts:0}],events:[]};
}
function setup() {
  const elements = {};
  for (const id of ['paid-report','paid-status','paid-toggle']) elements[id] = {
    innerHTML:'',textContent:'',disabled:false,attrs:{},setAttribute(k,v){this.attrs[k]=v;},removeAttribute(k){delete this.attrs[k];}};
  const context = vm.createContext({document:{getElementById:id=>elements[id]},API:'',
    token:()=> 'test-admin',headers:()=>({Authorization:'Bearer test-admin'}),
    fetch:()=>Promise.resolve({ok:true,json:()=>Promise.resolve(fixture())})});
  const html=fs.readFileSync(path.join(root,'dashboard/index.html'),'utf8');
  vm.runInContext(html.slice(html.indexOf('function esc(s)'),html.indexOf('function timeAgo')),context);
  vm.runInContext(fs.readFileSync(path.join(root,'dashboard/paid-usage.js'),'utf8'),context);
  return {context,elements};
}
test('includes reasoning in output and spending, preserves visible output separately',()=>{
  const {context,elements}=setup();context.renderPaidUsage(fixture());
  const html=elements['paid-report'].innerHTML;
  assert.match(html,/900<\/div>/);assert.match(html,/100 visible \+ 800 reasoning/);
  assert.match(html,/\$0\.0041/);assert.match(html,/not your Gemini balance or invoice/);
});
test('aggregates numeric totals across models without concatenating legacy decimal strings',()=>{
  const {context}=setup();const data=fixture();
  data.usage[0].charged_tokens='1900';
  data.usage.push({...data.usage[0],model:'staff-model',charged_tokens:'2100'});
  data.usage.push({...data.usage[0],day:'2026-10-07',charged_tokens:'99999'});
  assert.equal(context.paidUsageSummary(data).charged_tokens,4000);
  assert.equal(context.paidUsageSummary(data).requests,4);
});
test('alerts on high usage, operator pause, circuit and expired pricing',()=>{
  const {context}=setup();const data=fixture();data.enabled=false;
  data.circuit_until='2099-01-01T00:00:00Z';data.price_valid_until='2020-01-01';
  data.usage[0].charged_usd=0.4;data.usage[0].uncertain_attempts=1;
  const messages=context.paidUsageAlerts(data,context.paidUsageSummary(data)).join(' ');
  for(const pattern of [/paused/,/failure protection/,/expired/,/80%/,/retain/])assert.match(messages,pattern);
});
test('escapes workload, model and event text',()=>{
  const {context,elements}=setup();const data=fixture();const attack='<img src=x onerror=alert(1)>';
  data.usage[0].model=attack;data.usage[0].purpose=attack;data.events=[{day:data.day,reason:attack,count:1}];
  context.renderPaidUsage(data);const html=elements['paid-report'].innerHTML;
  assert.doesNotMatch(html,/<img/);assert.equal((html.match(/&lt;img/g)||[]).length,3);
});
test('toggle sends an authenticated boolean only and verifies the resulting state',async()=>{
  const {context,elements}=setup();const calls=[];context.renderPaidUsage(fixture());
  context.fetch=(url,options)=>{calls.push({url,options});const data=fixture();data.enabled=false;
    return Promise.resolve({ok:true,json:()=>Promise.resolve(data)});};
  await elements['paid-toggle'].onclick.call(elements['paid-toggle']);
  assert.equal(calls[0].url,'/admin/api/llm-control');assert.equal(calls[0].options.method,'POST');
  assert.equal(calls[0].options.headers.Authorization,'Bearer test-admin');
  assert.deepEqual(JSON.parse(calls[0].options.body),{enabled:false});
  assert.match(elements['paid-report'].innerHTML,/Paid calls: paused/);
});
test('failed refresh disables stale controls until status can be verified',async()=>{
  const {context,elements}=setup();context.renderPaidUsage(fixture());
  context.fetch=()=>Promise.resolve({ok:false});await context.loadPaidUsage();
  assert.match(elements['paid-status'].textContent,/unavailable/);assert.equal(elements['paid-toggle'].disabled,true);
  assert.equal(elements['paid-report'].attrs['aria-busy'],undefined);
});
test('a lost toggle response requires refresh, preventing a blind inverse action',async()=>{
  const {context,elements}=setup();context.renderPaidUsage(fixture());
  context.fetch=()=>Promise.reject(new Error('Disconnected'));
  await elements['paid-toggle'].onclick.call(elements['paid-toggle']);
  assert.equal(elements['paid-toggle'].disabled,true);
});
test('old or signed-out responses cannot overwrite newer status',async()=>{
  const {context,elements}=setup();const pending=[];
  context.fetch=()=>new Promise(resolve=>pending.push(resolve));
  const first=context.loadPaidUsage();const second=context.loadPaidUsage();const paused=fixture();paused.enabled=false;
  pending[1]({ok:true,json:()=>Promise.resolve(paused)});await second;
  pending[0]({ok:true,json:()=>Promise.resolve(fixture())});await first;
  assert.match(elements['paid-report'].innerHTML,/Paid calls: paused/);
  const signedOut=context.loadPaidUsage();context.token=()=>'';
  pending[2]({ok:true,json:()=>Promise.resolve(fixture())});await signedOut;
  assert.match(elements['paid-report'].innerHTML,/Paid calls: paused/);
});
