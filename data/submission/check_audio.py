from faster_whisper import WhisperModel
from pathlib import Path
import json,difflib,re
root=Path('/home/hdx/code/cover-regulatory-engine/data/submission')
model=WhisperModel('small.en',device='cpu',compute_type='int8',cpu_threads=6,local_files_only=True)
report=[]
for row in json.loads((root/'narration.json').read_text()):
 segs,info=model.transcribe(str(root/'audio'/f"{row['id']}.wav"),language='en',beam_size=3,word_timestamps=True)
 segments=[{'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word} for w in s.words]} for s in segs]
 text=' '.join(s['text'] for s in segments);norm=lambda t:re.sub('[^a-z ]','',t.lower()).split()
 score=difflib.SequenceMatcher(None,norm(row['text']),norm(text)).ratio()
 report.append({'id':row['id'],'transcription':text,'similarity':score,'segments':segments})
 print(row['id'],round(score,3),text,flush=True)
 (root/'audio-check.json').write_text(json.dumps(report,indent=2))
