// Opt-in live release run: uses public services and the configured subscription worker.
import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
const root=new URL('../../',import.meta.url);
const corpus=JSON.parse(await fs.readFile(new URL('data/delivery/corpus.json',root),'utf8'));
const browser=await chromium.launch();
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const offset=Number(process.env.COVER_ACCEPTANCE_OFFSET||0);
const results=offset?JSON.parse(await fs.readFile(new URL('data/delivery/live-browser-holdouts.json',root),'utf8')):[];
try {
 for(const parcel of corpus.holdouts.slice(offset)){
  let context,extracted;
  const listener=async response=>{
   if(!response.ok())return;
   if(response.url().includes(`/api/parcels/${parcel.AIN}/context`))context=await response.json();
   if(/\/api\/evidence-jobs\/[^/]+\/context$/.test(response.url()))extracted=await response.json();
  };
  page.on('response',listener);
  await page.goto(process.env.COVER_ACCEPTANCE_URL||'http://127.0.0.1:5173');
  await page.getByLabel('Property address or assessor parcel number').fill(parcel.SitusFullAddress||parcel.AIN);
  const started=Date.now();
  await page.getByRole('button',{name:'Find property'}).click();
  await page.locator('.candidate').first().waitFor({timeout:30000});
  await page.locator('.candidate').first().click();
  let error;
  try{await page.getByRole('button',{name:'Inspect map readings',exact:true}).waitFor({timeout:245000});}catch(e){error=String(e).slice(0,500);}
  const row={ain:parcel.AIN,query:parcel.SitusFullAddress,total_seconds:(Date.now()-started)/1000,context,extracted,error,manual_transcriptions:0};
  results.push(row);
  await fs.writeFile(new URL('data/delivery/live-browser-holdouts.json',root),JSON.stringify(results,null,2));
  await page.screenshot({path:new URL(`data/delivery/${parcel.AIN}-live.png`,root).pathname,fullPage:true});
  console.log(parcel.AIN,row.total_seconds,extracted?.automatic_evidence?.observations?.map(o=>[o.key,o.value]),error||'');
  page.off('response',listener);
 }
}finally{await browser.close();}
