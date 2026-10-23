import { chromium, expect } from '@playwright/test';
import fs from 'node:fs/promises';
const query = process.argv[2] || '17404 Stagg St Los Angeles';
const label = query.startsWith('17404') ? 'stagg' : 'louise';
const dir = new URL('../../data/delivery/enriched-research/' + label, import.meta.url).pathname;
await fs.mkdir(dir, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[]; const results=[];
page.on('pageerror',e=>errors.push(String(e)));
page.on('response',async r=>{if(r.url().includes('/api/research/') && r.ok()) {try{results.push(await r.json());}catch{}}});
try {
 await page.goto('http://127.0.0.1:5173');
 await page.getByLabel('Property address or assessor parcel number').fill(query);
 await page.getByRole('button',{name:'Find property'}).click();
 await page.locator('.candidate').first().click();
 await expect(page.locator('.constraint')).toHaveCount(5,{timeout:45000});
 await page.getByRole('button',{name:'Property research',exact:true}).click();
 await page.screenshot({path:dir+'/loading.png'});
 await expect(page.locator('#parcel-research')).toContainText('4/4 sources returned',{timeout:125000});
 await page.screenshot({path:dir+'/stagg-summary.png'});
 for(const title of ['Permit history','Planning profile & cases','Engineering & easements','Transit & walking access']) {
  const card=page.getByLabel(title,{exact:true});
  await card.locator('summary').first().click();
  await card.scrollIntoViewIfNeeded();
  if(title==='Planning profile & cases') await card.getByText('Case Numbers ·', {exact:false}).click();
  if(title==='Transit & walking access') await card.getByText('Estimated walking directions',{exact:true}).first().click();
  await page.screenshot({path:dir+'/'+title.split(' ')[0].toLowerCase()+'.png'});
  await card.locator('summary').first().click();
 }
 await page.getByRole('button',{name:'Save / compare / ask'}).click();
 const name='Source research — '+label+' '+Date.now();
 await page.getByLabel('Scenario name').fill(name);
 await page.getByRole('button',{name:'Save scenario',exact:true}).click();
 await expect(page.getByRole('button',{name:name+' · selected',exact:true})).toBeVisible();
 const project=await page.getByLabel('Open saved project').inputValue();
 await page.reload();
 await page.getByRole('button',{name:'Open a saved project'}).click();
 await page.getByLabel('Open saved project').selectOption(project);
 await expect(page.locator('#parcel-research')).toContainText('4/4 sources returned');
 await page.getByRole('button',{name:'Property research',exact:true}).click();
 await page.setViewportSize({width:390,height:844});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.screenshot({path:dir+'/mobile.png'});
 await fs.writeFile(dir+'/live-proof.json',JSON.stringify({project,name,results,errors},null,2));
 console.log(JSON.stringify({project,results:results.map(r=>({source:r.source,ain:r.ain,status:r.status,summary:r.summary})),errors}));
} finally { await browser.close(); }
