from pathlib import Path
import sys,subprocess,json,re,shutil
R=Path(__file__).parent.resolve();sys.path.insert(0,str(R/'deps'))
import imageio_ffmpeg
from PIL import ImageFont
ff=imageio_ffmpeg.get_ffmpeg_exe();site=R/'site';video=site/'airline-points.mp4'
run=subprocess.run([ff,'-hide_banner','-i',str(video),'-progress','pipe:1','-f','null','-'],capture_output=True,text=True)
assert run.returncode==0,run.stderr
assert 'Duration: 00:02:00.00' in run.stderr and '1920x1080' in run.stderr
assert re.findall(r'frame=(\d+)',run.stdout)[-1]=='3600'
assert video.stat().st_size<25*1024*1024,'Video exceeds GitHub browser upload limit'
caps=json.loads((R/'captions.json').read_text());f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',31)
for c in caps:
 assert 0<=c['start']<c['end']<=120,c
 assert f.getlength(c['text'])<1100,c
 assert all(c['start']<=w['start']<=w['end']<=c['end']+.001 for w in c['words']),c
transcript=' '.join(c['text'] for c in caps)
assert '$8.2' in transcript and 'planes' in transcript
assert not any(s in transcript for s in ["I'm tired",'Thank you','Perfect.','plains'])
files=['subtitles.srt','timeline.json','production.json','captions.json','film.py','narrate.py','captions.py','fetch_assets.py','package.py']
for name in files:shutil.copy2(R/name,site/name)
(site/'renderer-requirements.txt').write_text('kokoro-onnx==0.6.1\nsoundfile==0.14.0\npillow==12.3.0\nimageio-ffmpeg==0.6.0\nfaster-whisper==1.2.1\n')
(site/'render.yaml').write_text('services:\n  - type: web\n    name: airline-points-explainer\n    runtime: static\n    buildCommand: echo Ready\n    staticPublishPath: .\n')
report={'duration_seconds':120,'resolution':'1920x1080','fps':30,'decoded_frames':3600,'full_decode':'passed','captions':len(caps),'subtitle_timing':'Whisper small.en on the narration audio','voice':'Kokoro af_heart','size_bytes':video.stat().st_size,'purchases':0}
(site/'validation.json').write_text(json.dumps(report,indent=2));(R/'decode.log').write_text(run.stderr+'\n'+run.stdout)
for sec in (4,22,51,88,114):
 subprocess.run([ff,'-y','-ss',str(sec),'-i',str(video),'-frames:v','1',str(R/f'final-{sec}.jpg')],capture_output=True,check=True)
print(json.dumps(report,indent=2))
