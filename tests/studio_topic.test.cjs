const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function setup(saved) {
  const nodes = {};
  function node() {
    const classes = new Set();
    return {value:'',innerHTML:'',textContent:'',readOnly:false,disabled:false,checked:false,
      listeners:{},dataset:{},classList:{add:v=>classes.add(v),remove:v=>classes.delete(v),
        contains:v=>classes.has(v),toggle(){}},
      addEventListener(k,v){this.listeners[k]=v;},setAttribute(){},removeAttribute(){},focus(){}};
  }
  const selectors=['#studio-topic','#studio-guidance','#studio-department','.studio-origin',
    '.studio-status','.studio-results','.studio-count','.studio-review','.studio-reset'];
  for (const s of selectors) nodes[s]=node();
  for (const s of ['#studio-topic','#studio-guidance','#studio-department']) nodes[s].id=s.slice(1);
  const program=node();program.value='internship';
  const host=node();
  host.querySelector=s=>nodes[s]||null;
  host.querySelectorAll=s=>s==='.studio-progress li'?[]:
    s==='.studio-program-choice input:checked'?(program.checked?[program]:[]):
    s==='.studio-program-choice input'?[program]:
    [nodes['#studio-guidance'],nodes['#studio-topic'],nodes['#studio-department'],program];
  const storage=saved?{msfea_studio_intake:JSON.stringify(saved)}:{};
  const requests=[];
  const context=vm.createContext({window:{crypto:{randomUUID:()=> 'test-request-0000000001'}},
    sessionStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=v,removeItem:k=>delete storage[k]},
    setTimeout:()=>0,clearTimeout(){},fetch:(url,options)=>{requests.push({url,...options});
      return Promise.resolve({ok:true,json:()=>Promise.resolve({id:'review-1',status:'queued'})});}});
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../dashboard/studio.js'),'utf8'),context);
  const studio=context.window.KnowledgeStudio;
  studio.mount(host,{escape:String,api:'',headers:()=>({}),signedIn:()=>false,showStudio(){},
    feedbackItem:id=>({id,question:'and when?'}),options:{departments:['all'],programs:['internship']}});
  return {studio,nodes,program,storage,requests};
}
test('linked question is editable; submitted clarification keeps the original feedback link',async()=>{
  const {studio,nodes,program,storage,requests}=setup();
  studio.openQuestion({id:7,question:'and when?'});
  assert.equal(nodes['#studio-topic'].readOnly,false);
  nodes['#studio-topic'].value='When should I complete the internship?';
  nodes['#studio-topic'].listeners.input();
  const remembered=JSON.parse(storage.msfea_studio_intake);
  assert.equal(remembered.feedback.question,'and when?');
  assert.deepEqual(remembered.intake.linked_feedback_ids,[7]);
  assert.equal(remembered.intake.question,'When should I complete the internship?');
  nodes['#studio-guidance'].value='Approved guidance for the internship timing.';
  nodes['#studio-department'].value='all';program.checked=true;
  nodes['.studio-review'].listeners.click();
  await new Promise(resolve=>setImmediate(resolve));
  const body=JSON.parse(requests[0].body);
  assert.equal(body.intake.question,'When should I complete the internship?');
  assert.deepEqual(body.intake.linked_feedback_ids,[7]);
  assert.match(nodes['.studio-origin'].innerHTML,/and when\?/);
});
test('refresh keeps the clarified topic editable and preserves the original question',()=>{
  const {nodes}=setup({intake:{question:'When should I complete the internship?',guidance:'',
    department:'all',programs:['internship'],linked_feedback_ids:[7]},
    feedback:{id:7,question:'and when?'},entry:null,current:null});
  assert.equal(nodes['#studio-topic'].readOnly,false);
  assert.equal(nodes['#studio-topic'].value,'When should I complete the internship?');
  assert.match(nodes['.studio-origin'].innerHTML,/and when\?/);
});
for (const action of ['openDraft','resumeDraft']) {
  test(action+' retains the reviewed topic instead of resetting it to the vague original',()=>{
    const {studio,nodes}=setup();
    studio[action]({id:12,entry_id:3,linked_feedback_ids:[7],question:'Generated entry title',
      answer:'',department:'all',programs:['internship'],assistance:{
        intake:{question:'When should I complete the internship?'}}});
    assert.equal(nodes['#studio-topic'].readOnly,false);
    assert.equal(nodes['#studio-topic'].value,'When should I complete the internship?');
  });
}
