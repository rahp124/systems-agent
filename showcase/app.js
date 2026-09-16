const actionNames={field_chlorine_grab:'Field chlorine grab',lab_chlorine_assay:'Lab chlorine assay',portable_pressure_reading:'Portable pressure reading',wait:'Wait for telemetry'};
const hypothesisNames={contamination:'Contamination',leak:'Leak',sensor_fault:'Sensor fault'};
const form=document.querySelector('#run-form');
const runButton=document.querySelector('#run');
const seedInput=document.querySelector('#seed');
const dockSeed=document.querySelector('#dock-seed');
const replayButton=document.querySelector('#replay');
const status=document.querySelector('#run-status');
const candidateRows=document.querySelector('#candidate-rows');
const evidenceValue=document.querySelector('#evidence-value');
const selectedAction=document.querySelector('#selected-action');
const stepButtons=[...document.querySelectorAll('[data-step]')];
let currentRun=null;

function formatPercent(value){return `${(value*100).toFixed(1)}%`}
function setStatus(message,detail,state='ready'){status.dataset.state=state;status.querySelector('span').textContent=message;status.querySelector('small').textContent=detail}

function renderStep(index){
  if(!currentRun)return;
  const step=currentRun.steps[index];
  const ranked=[...step.candidates].sort((a,b)=>b.score-a.score);
  candidateRows.replaceChildren(...ranked.map(candidate=>{
    const row=document.createElement('tr');
    if(candidate.action===step.selected)row.className='selected';
    const heading=document.createElement('th');heading.scope='row';heading.textContent=actionNames[candidate.action]||candidate.action;row.append(heading);
    for(const value of [candidate.information_gain,candidate.cost,candidate.score]){
      const cell=document.createElement('td');cell.textContent=typeof value==='number'&&!Number.isInteger(value)?value.toFixed(3):String(value);row.append(cell)
    }
    return row
  }));
  evidenceValue.textContent=step.evidence.map(value=>value.replaceAll('_',' ')).join(', ');
  selectedAction.textContent=`Collected by ${actionNames[step.selected]}. Relative budget remaining: ${step.remaining_budget}.`;
  const beliefRows=[...document.querySelectorAll('.beliefs>div')];
  const leading=Object.entries(step.posterior).sort((a,b)=>b[1]-a[1])[0][0];
  Object.entries(step.posterior).forEach(([name,value],rowIndex)=>{
    const beliefRow=beliefRows[rowIndex];beliefRow.querySelector('span').textContent=hypothesisNames[name];
    const progress=beliefRow.querySelector('progress');progress.value=value;progress.textContent=formatPercent(value);progress.setAttribute('aria-label',`${hypothesisNames[name]} probability`);
    beliefRow.querySelector('output').textContent=formatPercent(value);beliefRow.classList.toggle('leading',name===leading)
  });
  stepButtons.forEach((button,buttonIndex)=>button.setAttribute('aria-pressed',String(buttonIndex===index)));
  dockSeed.textContent=String(currentRun.seed).padStart(3,'0');
  setStatus(`Last run: seed ${String(currentRun.seed).padStart(3,'0')} · step ${index+1} of ${currentRun.steps.length}`,'Synthetic evaluation · advisory only')
}

async function runInvestigation(seed,focusResults=false){
  runButton.disabled=true;runButton.querySelector('span').textContent='Running investigation…';setStatus('Investigation running','Scoring possible observations against current uncertainty','loading');
  try{
    const response=await fetch('/api/investigate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({seed})});
    if(!response.ok){if(response.status===400)throw new Error('The seed must be a whole number from 0 to 999999.');throw new Error(`The investigation service returned ${response.status}. Try again.`)}
    currentRun=await response.json();stepButtons.forEach(button=>{button.disabled=false});renderStep(0);
    if(focusResults)document.querySelector('.actions-stage').focus({preventScroll:true})
  }catch(error){setStatus('Investigation could not run',error.message,'error')}
  finally{runButton.disabled=false;runButton.querySelector('span').textContent='Run a synthetic case'}
}

form.addEventListener('submit',event=>{
  event.preventDefault();const seed=Number(seedInput.value);
  if(!Number.isInteger(seed)||seed<0||seed>999999){seedInput.setCustomValidity('Enter a whole number from 0 to 999999.');seedInput.reportValidity();return}
  seedInput.setCustomValidity('');runInvestigation(seed,true)
});
seedInput.addEventListener('input',()=>seedInput.setCustomValidity(''));
stepButtons.forEach(button=>button.addEventListener('click',()=>renderStep(Number(button.dataset.step))));
replayButton.addEventListener('click',()=>runInvestigation(Number(seedInput.value),true));
runInvestigation(7);
