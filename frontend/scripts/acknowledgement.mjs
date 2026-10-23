import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
const b=await chromium.launch();const p=await b.newPage();
try{
 await p.route('**/api/parcels?*',async r=>{await new Promise(resolve=>setTimeout(resolve,1000));await r.fulfill({json:{status:'no-match',features:[]}})});
 await p.goto('http://127.0.0.1:5173');await p.getByLabel('Property address or assessor parcel number').fill('7537 Louise Avenue');
 const result=await p.evaluate(async()=>{
  const button=[...document.querySelectorAll('button')].find(b=>b.textContent.includes('Find property'));
  const start=performance.now();button.click();await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame);
  return {milliseconds:performance.now()-start,button_disabled:button.disabled,spinner_visible:!!document.querySelector('.spinner'),button_text:button.textContent};
 });
 await fs.writeFile(new URL('../../data/delivery/ui-acknowledgement.json',import.meta.url),JSON.stringify(result,null,2));console.log(result);
 if(result.milliseconds>100||!result.spinner_visible)throw new Error('Acknowledgement gate failed');
}finally{await b.close()}
