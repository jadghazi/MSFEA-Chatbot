const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function setup(saved, behavior = {}) {
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
  const requests=[], savedErrors=[];
  const context=vm.createContext({window:{crypto:{randomUUID:()=> 'test-request-0000000001'},
    confirm:()=>behavior.confirm !== false},
    sessionStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=v,removeItem:k=>delete storage[k]},
    setTimeout:()=>0,clearTimeout(){},fetch:(url,options)=>{requests.push({url,...options});
      return Promise.resolve({ok:!behavior.error,json:()=>Promise.resolve(behavior.error ?
        {detail:behavior.error} : {id:'review-1',status:'queued'})});}});
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../dashboard/studio.js'),'utf8'),context);
  const studio=context.window.KnowledgeStudio;
  studio.mount(host,{escape:String,api:'',headers:()=>({}),signedIn:()=>false,showStudio(){},
    onSaved:error=>savedErrors.push(error),
    feedbackItem:id=>({id,question:'and when?'}),options:{departments:['all'],programs:['internship']}});
  return {studio,nodes,program,storage,requests,savedErrors};
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

const privateDraft = {id:12,entry_id:3,linked_feedback_ids:[],question:'CDC location?',
  answer:'Verified CDC office location.',department:'all',programs:['internship'],
  assistance:{id:'review-1',intake:{question:'Where is the CDC?'}}};

test('discard closes the saved workspace and clears browser state for a fresh identical case', async()=>{
  const {studio,nodes,storage,requests,savedErrors}=setup();
  studio.resumeDraft(privateDraft);
  storage.msfea_studio_approval='previous approval';
  assert.ok(storage.msfea_studio_intake);
  await studio.discardDraft(privateDraft,{disabled:false});
  assert.equal(requests[0].url,'/admin/api/studio/discard');
  assert.deepEqual(JSON.parse(requests[0].body),{revision_id:12});
  assert.equal(nodes['#studio-guidance'].value,'');
  assert.equal(nodes['#studio-topic'].value,'');
  assert.equal(storage.msfea_studio_intake,undefined);
  assert.equal(storage.msfea_studio_approval,undefined);
  assert.deepEqual(savedErrors,['']);
});
test('cancelling discard keeps the saved workspace and sends no request',()=>{
  const {studio,storage,requests}=setup(null,{confirm:false});
  studio.resumeDraft(privateDraft);
  const before=storage.msfea_studio_intake;
  studio.discardDraft(privateDraft,{disabled:false});
  assert.equal(storage.msfea_studio_intake,before);
  assert.equal(requests.length,0);
});
test('failed discard preserves the workspace and displays the server reason',async()=>{
  const {studio,storage,savedErrors}=setup(null,{error:'Wait for the current previews to finish.'});
  studio.resumeDraft(privateDraft);
  const before=storage.msfea_studio_intake, button={disabled:false};
  await studio.discardDraft(privateDraft,button);
  assert.equal(storage.msfea_studio_intake,before);
  assert.equal(button.disabled,false);
  assert.deepEqual(savedErrors,['Wait for the current previews to finish.']);
});
