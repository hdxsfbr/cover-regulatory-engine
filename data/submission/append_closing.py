from pathlib import Path
import subprocess,json
r=Path('data/submission').resolve()
def duration(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],text=True))
def run(args):subprocess.run(['ffmpeg','-y','-v','error']+args,check=True)
base=duration(r/'clips/original-av.mp4');voice=duration(r/'audio/09-closing.wav');length=voice+1.5
run(['-loop','1','-framerate','30','-i',str(r/'closing-frame.png'),'-i',str(r/'audio/09-closing.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=11,adelay=600:all=1,apad','-t',str(length),'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',str(r/'clips/09-closing.mp4')])
(r/'closing-concat.txt').write_text(f"file '{r}/clips/original-av.mp4'\nfile '{r}/clips/09-closing.mp4'\n")
def stamp(t):
 ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
subs=(r/'captions.srt').read_text().rstrip();n=len(subs.split('\n\n'))+1
subs+=f'\n\n{n}\n{stamp(base+.6)} --> {stamp(base+2.3)}\nThanks for watching.\n\n{n+1}\n{stamp(base+2.3)} --> {stamp(base+.6+voice)}\nThat’s the prototype: property research, clear evidence,\nand design comparisons in one place.\n'
(r/'captions-with-closing.srt').write_text(subs)
meta=(r/'closing-metadata.txt').read_text();meta+=f'\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(base*1000)}\nEND={round((base+length)*1000)}\ntitle=Thank you\n';(r/'closing-metadata.txt').write_text(meta)
run(['-f','concat','-safe','0','-i',str(r/'closing-concat.txt'),'-i',str(r/'captions-with-closing.srt'),'-i',str(r/'closing-metadata.txt'),'-map','0:v','-map','0:a','-map','1:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','copy','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart',str(r/'cover-submission-final.mp4')])
print(json.dumps({'original_seconds':base,'closing_voice_seconds':voice,'total_seconds':duration(r/'cover-submission-final.mp4')}))
