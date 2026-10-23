import {chromium,expect} from '@playwright/test';
import fs from 'node:fs/promises';
const root=new URL('../../',import.meta.url);
const token=(await fs.readFile(new URL('data/workspace.operator-token',root),'utf8')).trim();
const candidate=await fs.readFile(new URL('data/delivery/probes/operator-reviewed-candidate.json',root),'utf8');
const job=JSON.parse(await fs.readFile(new URL('data/delivery/probes/operator-live-job.json',root),'utf8'));
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:1000}});
try{
 await p.goto('http://127.0.0.1:5173/operator');
 await p.getByLabel('Operator token').fill(token);
 await p.getByRole('button',{name:'Unlock review workspace'}).click();
 await p.getByLabel('Resume operator job').selectOption(job.id);
 await expect(p.getByLabel('Candidate JSON')).not.toHaveValue('');
 await p.getByLabel('Candidate JSON').fill(candidate);
 await p.getByLabel('Reviewer',{exact:true}).fill('Codex source comparison 2026-10-22');
 await p.getByLabel('Review rationale').fill('Actual source-derived candidate. Corrected missing foot unit on side-yard increment; numeric thresholds match inspected12.08 and12.21.1 passages. Unresolved site predicates are retained as required checks; hillside/coastal, accessory and special approval branches remain excluded. Source12.03 supplies dimensional definitions. Agent interpretation review, not independent professional approval. See dependency_resolutions per rule.');
 const saved=p.waitForResponse(r=>r.url().endsWith('/api/operator/reviews')&&r.request().method()==='POST');
 await p.getByRole('button',{name:'Record reviewed correction'}).click();
 const review=await (await saved).json();
 if(!review.id)throw new Error(JSON.stringify(review));
 const detail=p.locator('details').filter({has:p.locator('summary').filter({hasText:review.id.slice(0,8)})}).first();
 await detail.locator('summary').click();
 await detail.getByRole('button',{name:'Activate this reviewed version'}).click();
 await p.getByText('Reviewed package activated. New assessments use this version.',{exact:true}).waitFor({timeout:15000});
 await p.screenshot({path:new URL('data/delivery/operator-activation.png',root).pathname,fullPage:true});
 console.log('Reviewed source-derived candidate activated through browser');
}finally{await b.close();}
