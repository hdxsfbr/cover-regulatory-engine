import json,sys,time
from pathlib import Path
import torch
sys.path.insert(0,'/home/hdx/code/chatterbox-play/scripts')
from chatterbox_agent import ChatterboxTTS,generate_one
root=Path('/home/hdx/code/cover-regulatory-engine/data/submission')
assert torch.cuda.is_available()
model=ChatterboxTTS.from_pretrained(device='cuda')
for s in json.loads((root/'narration.json').read_text()):
 out=root/'audio'/f"{s['id']}.wav"
 if out.exists():continue
 print('GENERATING',s['id'],flush=True)
 generate_one(model=model,text=s['text'],voice_path=Path('/home/hdx/code/chatterbox-play/voices/andre_voice_clean_ref.wav'),out_path=out,exaggeration=.35,cfg_weight=.55,split_mode='sentence',silence_ms=220,normalize=False)
 print('DONE',s['id'],flush=True)
