const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function setup() {
  const filters = ['all','refused','incomplete','down'].map(value => ({
    attrs:{'data-attention-filter':value},
    getAttribute(k){return this.attrs[k];}, setAttribute(k,v){this.attrs[k]=v;}
  }));
  const list = {innerHTML:'',children:[],appendChild(card){this.children.push(card);}};
  const count = {textContent:''};
  const context = vm.createContext({
    document:{querySelectorAll:()=>filters, createElement:()=>({innerHTML:'',className:'',
      querySelector:()=>({addEventListener(){}})})},
    $:id=>id==='list'?list:count, _revisionItems:[], timeAgo:()=> 'just now'
  });
  const html = fs.readFileSync(path.join(__dirname,'../dashboard/index.html'),'utf8');
  vm.runInContext(html.slice(html.indexOf('function esc(s)'),html.indexOf('function timeAgo')),context);
  vm.runInContext(html.slice(html.indexOf('var _attentionItems'),html.indexOf('// ---- Published knowledge sources')),context);
  return {context,list,count,filters};
}
function item(extra={}) {
  return {id:1,question:'and the duration?',answer:'I cannot confirm that.',refused:false,
    possible_incomplete:true,conversation_history:[],retrieved:[],...extra};
}
test('review filters select their reason and distinguish a filtered empty state',()=>{
  const {context,list,count,filters}=setup();
  context.renderList([item(),item({id:2,refused:true}),item({id:3,possible_incomplete:false,rating:-1})]);
  context._attentionFilter='incomplete';list.children=[];context.drawAttention();
  assert.equal(list.children.length,1);assert.match(count.textContent,/1 of 3 loaded/);
  assert.equal(filters[2].attrs['aria-pressed'],'true');
  context.renderList([item({refused:true})]);
  assert.match(list.innerHTML,/No responses match this filter/);
  context.renderList([]);assert.match(list.innerHTML,/No unresolved responses/);
});
test('refusal answers remain visible, with prior user and assistant messages escaped',()=>{
  const {context}=setup();const attack='<img src=x onerror=alert(1)>';
  const card=context.buildCard(item({refused:true,answer:attack,conversation_history:[
    {role:'user',content:attack},{role:'assistant',content:'Earlier response'}],history_source:'request'}));
  assert.match(card.innerHTML,/The bot replied/);assert.match(card.innerHTML,/Previous conversation · 2 messages/);
  assert.match(card.innerHTML,/Earlier response/);assert.doesNotMatch(card.innerHTML,/<img/);
  assert.equal((card.innerHTML.match(/&lt;img/g)||[]).length,2);
  assert.doesNotMatch(card.innerHTML,/Possible incomplete answer/);
});
test('advisory wording and staff-supplied context are labeled without pretending to be policy',()=>{
  const {context}=setup();const card=context.buildCard(item({history_source:'staff_reported',
    conversation_history:[{role:'user',content:'When should I do the internship?'}]}));
  assert.match(card.innerHTML,/Possible incomplete answer/);
  assert.match(card.innerHTML,/may still be a useful partial answer/);
  assert.match(card.innerHTML,/Provided by staff/);assert.match(card.innerHTML,/not captured by the original request/);
  assert.match(card.innerHTML,/Review this response/);
});
test('missing legacy context is honest and a fresh standalone question has a distinct message',()=>{
  const {context}=setup();assert.match(context.buildCard(item()).innerHTML,/not recorded for this older interaction/);
  assert.match(context.buildCard(item({history_source:'request'})).innerHTML,/No previous messages were submitted/);
});
