import json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
run=lambda args:subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def stamp(s):
 ms=round(s*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);sec,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{sec:02},{ms:03}'
timeline=json.loads((root/'timeline.json').read_text())['timeline']
assert len(timeline)==8,'Incomplete recording'
checks={r['id']:r for r in json.loads((root/'audio-check.json').read_text())}
subs=[];offset=0;chapters=[]
for s in timeline:
 duration=s['audioDuration']+1
 title=s['title']+('  |  Hypothetical design' if int(s['id'][:2])>=5 else '')
 titlefile=root/'clips'/(s['id']+'.txt');titlefile.write_text(title)
 vf=f"setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,fps=30,tpad=stop_mode=clone:stop_duration=2,drawbox=x=0:y=1030:w=iw:h=50:color=0x202020@0.92:t=fill,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:textfile={titlefile}:fontcolor=white:fontsize=22:x=36:y=1044"
 if s['duration']>duration+1: vf=vf.replace('setpts=PTS-STARTPTS',f"setpts=(PTS-STARTPTS)*{duration/s['duration']}")
 cmd=['ffmpeg','-y','-v','error','-ss',str(s['start']),'-t',str(s['duration']),'-i',str(root/'capture/walkthrough.webm'),'-i',str(root/'audio'/(s['id']+'.wav')),'-vf',vf,'-af','loudnorm=I=-16:TP=-1.5:LRA=11,apad','-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(root/'clips'/(s['id']+'.mp4'))]
 print('RENDER',s['id'],flush=True);run(cmd)
 words=[w for seg in checks[s['id']]['segments'] for w in seg['words']]
 for i in range(0,len(words),10):
  chunk=words[i:i+10];subs.append(f"{len(subs)+1}\n{stamp(offset+chunk[0]['start'])} --> {stamp(offset+chunk[-1]['end'])}\n{''.join(w['word'] for w in chunk).strip()}\n")
 chapters.append((offset,offset+duration,s['title']));offset+=duration
(root/'captions.srt').write_text('\n'.join(subs))
(root/'concat.txt').write_text('\n'.join("file '"+str(root/'clips'/(s['id']+'.mp4'))+"'" for s in timeline))
meta=';FFMETADATA1\ntitle=Cover — Property intelligence walkthrough\ncomment=Real application recording. Synthetic narration uses the author’s authorized voice with standard Chatterbox. ADU scenarios are hypothetical.\n'
for a,b,title in chapters:meta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(a*1000)}\nEND={round(b*1000)}\ntitle={title}\n'
(root/'chapters.txt').write_text(meta)
run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(root/'concat.txt'),'-i',str(root/'captions.srt'),'-i',str(root/'chapters.txt'),'-map','0:v','-map','0:a','-map','1:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','copy','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart',str(root/'cover-submission.mp4')])
print('FINISHED',offset,root/'cover-submission.mp4',flush=True)
