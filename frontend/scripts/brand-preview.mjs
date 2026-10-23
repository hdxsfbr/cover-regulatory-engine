import {chromium,expect} from '@playwright/test';
import fs from 'node:fs/promises';
const dir=new URL('../../data/delivery/cover-brand',import.meta.url).pathname;
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:1000}});
const errors=[];p.on('pageerror',e=>errors.push(String(e)));
try{
await p.goto('http://127.0.0.1:5173');await p.screenshot({path:dir+'/landing-desktop.png'});
expect(await p.locator('.brand img').evaluate(i=>i.complete&&i.naturalWidth>0)).toBeTruthy();
await p.setViewportSize({width:390,height:844});await p.screenshot({path:dir+'/landing-mobile.png'});expect(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
await p.setViewportSize({width:1440,height:1000});
await p.getByRole('button',{name:'Open a saved project'}).click();await p.getByLabel('Open saved project').selectOption('a29f7473-af8d-4f2f-9847-4705a978fe7b');
await expect(p.locator('#parcel-research')).toContainText('4/4 sources returned');
await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:dir+'/assessment-desktop.png'});
await p.getByRole('button',{name:'Property research',exact:true}).click();await p.screenshot({path:dir+'/research-desktop.png'});
for(const width of [760,390]){
await p.setViewportSize({width,height:929});await p.locator('#parcel-research').scrollIntoViewIfNeeded();await p.screenshot({path:dir+`/research-${width}.png`});
const card=p.getByLabel('Planning profile & cases',{exact:true});const summary=card.locator('summary').first();await summary.focus();await p.keyboard.press('Enter');await expect(card).toHaveAttribute('open','');await p.keyboard.press('Enter');await expect(card).not.toHaveAttribute('open','');expect(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
}
await fs.writeFile(dir+'/browser-proof.json',JSON.stringify({widths:[1440,760,390],errors,keyboardDisclosure:'passed',logoLoaded:true},null,2));console.log({errors});
}finally{await b.close()}
