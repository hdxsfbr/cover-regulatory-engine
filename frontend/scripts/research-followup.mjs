import {chromium,expect} from '@playwright/test';
import fs from 'node:fs/promises';
const dir = new URL('../../data/delivery/enriched-research',import.meta.url).pathname;
const proof=JSON.parse(await fs.readFile(dir+'/stagg/live-proof.json','utf8'));
const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1440,height:1000}});
const responses=[];p.on('response',async r=>{if(r.url().includes('/questions')){responses.push({status:r.status(),body:await r.json()});}});
try{
 await p.goto('http://127.0.0.1:5173');
 await p.getByRole('button',{name:'Open a saved project'}).click();
 await p.getByLabel('Open saved project').selectOption(proof.project);
 await expect(p.locator('#parcel-research')).toContainText('4/4 sources returned');
 await p.getByRole('button',{name:'Property research',exact:true}).click();
 for(const label of ['Engineering & easements','Transit & walking access']){
  const card=p.getByLabel(label,{exact:true});await card.locator('summary').first().click();
  await card.getByRole('button',{name:'Refresh '+label.toLowerCase()}).click();
  await expect(card).not.toContainText('Loading records…',{timeout:110000});
 }
 await expect(p.getByLabel('Transit & walking access',{exact:true})).toContainText('Metro rail');
 await p.getByRole('button',{name:'Save / compare / ask'}).click();
 await p.getByLabel('Scenario name').fill('Research validation — bus and rail');
 await p.getByRole('button',{name:'Save scenario',exact:true}).click();
 await expect(p.getByRole('button',{name:'Ask follow-up',exact:true})).toBeEnabled();
 await p.getByLabel('Ask about this saved assessment').fill('Which permit records were found and does an issued permit prove final approval? Cite the saved permit evidence.');
 await p.getByRole('button',{name:'Ask follow-up',exact:true}).click();
 await expect(p.locator('.answer')).toBeVisible({timeout:40000});
 await p.locator('.answer').scrollIntoViewIfNeeded();
 await p.screenshot({path:dir+'/cited-followup.png'});
 await fs.writeFile(dir+'/cited-followup.json',JSON.stringify(responses,null,2));
 console.log(JSON.stringify(responses));
}finally{await b.close();}
