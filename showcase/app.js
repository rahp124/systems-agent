const actionNames={field_chlorine_grab:'Collect a field chlorine sample',lab_chlorine_assay:'Run a lab chlorine assay',portable_pressure_reading:'Take a portable pressure reading',wait:'Wait for new telemetry'};
const shortActionNames={field_chlorine_grab:'Field chlorine checked',lab_chlorine_assay:'Lab chlorine checked',portable_pressure_reading:'Pressure checked',wait:'Telemetry observed'};
const hypothesisNames={contamination:'Contamination',leak:'Leak',sensor_fault:'Sensor fault'};
const evidenceNames={clear:'Clear',detected:'Detected',normal:'Normal pressure',low:'Low pressure',high:'High',trace:'Trace',elevated:'Elevated',below_threshold:'Below threshold'};
const form=document.querySelector('#run-form');
const runButton=document.querySelector('#run');
const seedInput=document.querySelector('#seed');
const replayButton=document.querySelector('#replay');
const nextButton=document.querySelector('#next-step');
const status=document.querySelector('#run-status');
const workspace=document.querySelector('#guided-workspace');
const resultStory=document.querySelector('#result-story');
const emptyResult=document.querySelector('#empty-result');
const stepResult=document.querySelector('#step-result');
const historyButtons=[...document.querySelectorAll('[data-step]')];
const candidateRows=document.querySelector('#candidate-rows');
const apiBase=(window.WATER_AGENT_API_BASE||'').replace(/\/$/,'');
let currentRun=null;
let currentStep=0;
let revealedThrough=-1;

function formatPercent(value){return `${(value*100).toFixed(1)}%`}
function formatDelta(value){const points=value*100;return `${points>0?'+':''}${points.toFixed(1)} pp`}
function displayEvidence(value){return evidenceNames[value]||value.replaceAll('_',' ').replace(/^./,letter=>letter.toUpperCase())}
function setStatus(message,detail,state='ready'){status.dataset.state=state;status.querySelector('span').textContent=message;status.querySelector('small').textContent=detail}

function priorForStep(index){return index===0?currentRun.initial_belief:currentRun.steps[index-1].posterior}

function interpretationFor(step,prior){
  const ranked=Object.entries(step.posterior).sort((a,b)=>b[1]-a[1]);
  const [leader,leaderValue]=ranked[0];
  const [runnerUp,runnerValue]=ranked[1];
  const gap=(leaderValue-runnerValue)*100;
  const change=(leaderValue-prior[leader])*100;
  const title=gap<5?`${hypothesisNames[leader]} leads, but only narrowly.`:`${hypothesisNames[leader]} is now the leading explanation.`;
  const direction=change>=0?'increased':'decreased';
  const copy=`Confidence in ${hypothesisNames[leader].toLowerCase()} ${direction} to ${formatPercent(leaderValue)}. ${hypothesisNames[runnerUp]} remains ${formatPercent(runnerValue)}, so this observation does not prove a cause.`;
  return {leader,title,copy,gap};
}

function renderRanking(step){
  const ranked=[...step.candidates].sort((a,b)=>b.score-a.score);
  candidateRows.replaceChildren(...ranked.map(candidate=>{
    const row=document.createElement('tr');
    if(candidate.action===step.selected)row.className='selected';
    const heading=document.createElement('th');heading.scope='row';heading.textContent=actionNames[candidate.action]||candidate.action;row.append(heading);
    for(const value of [candidate.information_gain,candidate.cost,candidate.score]){const cell=document.createElement('td');cell.textContent=typeof value==='number'&&!Number.isInteger(value)?value.toFixed(3):String(value);row.append(cell)}
    return row;
  }));
}

function updateHistory(){
  historyButtons.forEach((button,index)=>{
    const step=currentRun.steps[index];
    button.disabled=index>revealedThrough;
    button.setAttribute('aria-current',index===currentStep?'step':'false');
    button.querySelector('strong').textContent=index<=revealedThrough?`${shortActionNames[step.selected]} · ${step.evidence.map(displayEvidence).join(', ')}`:'Waiting';
  });
}

function renderBeliefs(step,prior,leader){
  const rows=[...document.querySelectorAll('#beliefs>div')];
  Object.keys(hypothesisNames).forEach((name,index)=>{
    const row=rows[index];
    const before=prior[name];
    const after=step.posterior[name];
    row.querySelector(':scope>span:first-child').textContent=hypothesisNames[name];
    row.querySelector('.before').textContent=formatPercent(before);
    const progress=row.querySelector('progress');progress.value=after;progress.textContent=formatPercent(after);progress.setAttribute('aria-label',`${hypothesisNames[name]} changed from ${formatPercent(before)} to ${formatPercent(after)}`);
    row.querySelector('output').textContent=formatPercent(after);
    row.querySelector('.delta').textContent=formatDelta(after-before);
    row.classList.toggle('leading',name===leader);
  });
}

function renderStep(index,{focus=false}={}){
  if(!currentRun)return;
  currentStep=index;
  const step=currentRun.steps[index];
  const prior=priorForStep(index);
  const interpretation=interpretationFor(step,prior);
  emptyResult.hidden=true;
  stepResult.hidden=false;
  resultStory.setAttribute('aria-labelledby','step-title');
  workspace.dataset.state='result';
  document.querySelector('#round-label').textContent=`Observation ${index+1} of ${currentRun.steps.length}`;
  document.querySelector('#step-title').textContent=index===0?'The agent chose where to begin.':'The agent chose the next check.';
  document.querySelector('#budget-remaining').textContent=`Relative budget remaining: ${step.remaining_budget}`;
  document.querySelector('#recommendation-title').textContent=actionNames[step.selected]||step.selected;
  document.querySelector('#recommendation-reason').textContent='Among the available actions, this check has the highest expected uncertainty reduction for its relative cost.';
  document.querySelector('#evidence-value').textContent=step.evidence.map(displayEvidence).join(', ');
  document.querySelector('#evidence-explanation').textContent=`Returned after the agent selected ${actionNames[step.selected].toLowerCase()}.`;
  document.querySelector('#interpretation-title').textContent=interpretation.title;
  document.querySelector('#interpretation-copy').textContent=interpretation.copy;
  document.querySelector('#belief-summary').textContent=`The strongest change from the previous belief is shown in percentage points; all alternatives remain visible.`;
  renderBeliefs(step,prior,interpretation.leader);
  renderRanking(step);
  updateHistory();
  const isFinal=index===currentRun.steps.length-1;
  nextButton.hidden=isFinal;
  nextButton.innerHTML=isFinal?'':`Continue to observation ${index+2} <span aria-hidden="true">→</span>`;
  const finalSummary=document.querySelector('#final-summary');
  finalSummary.hidden=!isFinal;
  if(isFinal){
    document.querySelector('#final-copy').textContent=`After three observations, the model’s leading explanation is ${hypothesisNames[currentRun.prediction].toLowerCase()} at ${formatPercent(step.posterior[currentRun.prediction])}. This is a model estimate, not a confirmed incident type.`;
    document.querySelector('#truth-copy').textContent=currentRun.correct?`In this synthetic case, that matches the hidden generated cause: ${hypothesisNames[currentRun.evaluation_truth].toLowerCase()}.`:`In this synthetic case, it does not match the hidden generated cause (${hypothesisNames[currentRun.evaluation_truth].toLowerCase()}). Incorrect cases remain visible because this is an evaluation harness, not a scripted success.`;
  }
  setStatus(`Seed ${String(currentRun.seed).padStart(3,'0')} · observation ${index+1} of ${currentRun.steps.length}`,isFinal?'Investigation complete':'Review the result, then continue when ready');
  if(focus){
    const resultIsBelowHistory=window.matchMedia('(max-width: 900px)').matches;
    resultStory.focus({preventScroll:!resultIsBelowHistory});
  }
}

async function runInvestigation(seed,{focus=true}={}){
  runButton.disabled=true;
  runButton.querySelector('span').textContent='Running…';
  workspace.dataset.state='loading';
  workspace.setAttribute('aria-busy','true');
  setStatus('Investigation running','Scoring possible observations against the current uncertainty','loading');
  try{
    const response=await fetch(`${apiBase}/api/investigate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({seed})});
    if(!response.ok){if(response.status===400)throw new Error('Enter a whole-number seed from 0 to 999999.');throw new Error(`The investigation service returned ${response.status}. Try again.`)}
    currentRun=await response.json();
    revealedThrough=0;
    renderStep(0,{focus});
  }catch(error){
    workspace.dataset.state='error';
    setStatus('Investigation could not run',error.message,'error');
  }finally{
    runButton.disabled=false;
    runButton.querySelector('span').textContent='Run investigation';
    workspace.removeAttribute('aria-busy');
  }
}

function submitCurrentSeed({focus=true}={}){
  const seed=Number(seedInput.value);
  if(!Number.isInteger(seed)||seed<0||seed>999999){seedInput.setCustomValidity('Enter a whole number from 0 to 999999.');seedInput.reportValidity();return}
  seedInput.setCustomValidity('');
  runInvestigation(seed,{focus});
}

form.addEventListener('submit',event=>{event.preventDefault();submitCurrentSeed()});
document.querySelector('[data-run-trigger]').addEventListener('click',()=>submitCurrentSeed());
seedInput.addEventListener('input',()=>{seedInput.setCustomValidity('');document.querySelector('[data-run-trigger]').textContent=`Run seed ${seedInput.value||'—'}`});
replayButton.addEventListener('click',()=>runInvestigation(currentRun.seed));
nextButton.addEventListener('click',()=>{if(currentStep<currentRun.steps.length-1){revealedThrough=Math.max(revealedThrough,currentStep+1);renderStep(currentStep+1,{focus:true})}});
historyButtons.forEach(button=>button.addEventListener('click',()=>renderStep(Number(button.dataset.step),{focus:true})));

const tabs=[...document.querySelectorAll('[role="tab"]')];
function selectTab(tab){
  tabs.forEach(item=>{const selected=item===tab;item.setAttribute('aria-selected',String(selected));item.tabIndex=selected?0:-1;document.querySelector(`#${item.getAttribute('aria-controls')}`).hidden=!selected});
}
tabs.forEach((tab,index)=>{tab.addEventListener('click',()=>selectTab(tab));tab.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight'].includes(event.key))return;event.preventDefault();const offset=event.key==='ArrowRight'?1:-1;const next=tabs[(index+offset+tabs.length)%tabs.length];selectTab(next);next.focus()})});
