import {chromium,expect} from '@playwright/test';
import fs from 'node:fs/promises';
const root=new URL('../../',import.meta.url),b=await chromium.launch();
const p=await b.newPage({viewport:{width:1440,height:1000},acceptDownloads:true});let latest;
p.on('response',async r=>{if(r.ok()&&r.url().endsWith('/api/assessments'))latest=await r.json()});
try{
 await p.goto('http://127.0.0.1:5173');await p.getByLabel('Property address or assessor parcel number').fill('7745 Louise Avenue');await p.getByRole('button',{name:'Find property'}).click();await p.locator('.candidate').first().click();
 await p.getByRole('button',{name:'Inspect map readings',exact:true}).waitFor({timeout:245000});
 await p.locator('.input-panel summary').click();await p.locator('#input-building_height_ft').fill('16');await p.locator('#input-roof_slope_percent').fill('20');await p.locator('#input-proposed_area_sqft').fill('600');await p.locator('#input-existing_floor_area_sqft').fill('2000');
 for(const box of await p.locator('.input-panel input[type=checkbox]').all())await box.check();
 await p.getByLabel('Evidence or basis for these inputs').fill('Acceptance design assumptions; public source reading provides dimensions. Building-line conflict remains conditional.');
 await p.getByRole('button',{name:'Export setback GeoJSON'}).waitFor({timeout:15000});
 await p.locator('#constraint-front-yard').getByRole('button',{name:'Locate on map'}).click();
 const highlighted=p.locator('.map path[stroke="#a44524"]');await expect(highlighted).toHaveCount(1);
 await highlighted.dispatchEvent('click');await expect(p.locator('#constraint-front-yard')).toBeFocused();
 const downloadPromise=p.waitForEvent('download');await p.getByRole('button',{name:'Export setback GeoJSON'}).click();const download=await downloadPromise;await download.saveAs(new URL('data/delivery/live-setbacks.geojson',root).pathname);
 const geo=JSON.parse(await fs.readFile(new URL('data/delivery/live-setbacks.geojson',root),'utf8'));if(geo.metadata.status!=='conditional'||geo.metadata.calculation_crs!=='EPSG:2229')throw new Error('Geometry provenance incorrect');
 await p.locator('.map').screenshot({path:new URL('data/delivery/setback-map.png',root).pathname});
 await p.getByRole('button',{name:'Inspect evidence',exact:true}).click();
 await p.locator('.observation').filter({hasText:'lot_depth_ft'.replaceAll('_',' ')}).getByText('Inspect printed measurement').click();
 await p.getByRole('button',{name:'Save / compare / ask'}).click();
 await p.getByLabel('Scenario name').fill('Geometry acceptance baseline');await p.getByRole('button',{name:'Save scenario',exact:true}).click();await p.getByRole('button',{name:'Geometry acceptance baseline · selected'}).waitFor();
 await p.getByLabel('Ask about this saved assessment').fill('Why is the front-yard setback conditional?');await p.getByRole('button',{name:'Ask follow-up'}).click();await p.locator('.answer').waitFor({timeout:35000});
 await p.locator('.answer details').first().locator('summary').click();
 await p.screenshot({path:new URL('data/delivery/geometry-desktop.png',root).pathname,fullPage:true});
 await p.setViewportSize({width:390,height:844});await p.screenshot({path:new URL('data/delivery/geometry-mobile.png',root).pathname,fullPage:true});
 await fs.writeFile(new URL('data/delivery/geometry-browser-assessment.json',root),JSON.stringify(latest,null,2));console.log('Map/card linkage both directions, conditional export, crop, saved scenario and actual cited browser follow-up passed');
}finally{await b.close()}
