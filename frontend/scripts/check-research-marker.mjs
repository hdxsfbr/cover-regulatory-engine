import { chromium, expect } from '@playwright/test';
const b = await chromium.launch();
const p = await b.newPage();
try {
 await p.goto('http://127.0.0.1:5173');
 await p.getByRole('button',{name:'Open a saved project'}).click();
 await p.getByLabel('Open saved project').selectOption('a29f7473-af8d-4f2f-9847-4705a978fe7b');
 const card=p.getByLabel('Planning profile & cases',{exact:true});
 await expect(card).toBeVisible();
 for(const width of [760,390]){
  await p.setViewportSize({width,height:929});
  await card.scrollIntoViewIfNeeded();
  const summary=card.locator('summary').first();
  const bounds=await summary.evaluate(el=>{const title=el.querySelector('strong');return {summaryTop:el.getBoundingClientRect().top,titleTop:title.getBoundingClientRect().top,display:getComputedStyle(title).display};});
  expect(bounds.display).toBe('inline');
  expect(bounds.titleTop-bounds.summaryTop).toBeLessThan(8);
  await p.screenshot({path:`/home/hdx/code/cover-regulatory-engine/data/delivery/enriched-research/marker-${width}.png`});
  await summary.focus();await p.keyboard.press('Enter');await expect(card).toHaveAttribute('open','');
  await p.keyboard.press('Enter');await expect(card).not.toHaveAttribute('open','');
 }
 console.log('Marker aligned with title; keyboard expand/collapse passed at 760px and 390px.');
}finally{await b.close();}
