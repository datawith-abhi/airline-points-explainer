from pathlib import Path
import os,sys,json
R=Path(__file__).parent.resolve();sys.path.insert(0,str(R/'deps'))
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1';os.environ['HF_HUB_DISABLE_XET']='1'
from faster_whisper import WhisperModel
model=WhisperModel('small.en',device='cpu',compute_type='int8',cpu_threads=4,download_root=str(R/'models'))
if '--download' in sys.argv: print('Whisper ready');sys.exit()
spec=json.loads((R/'timeline.json').read_text());words=[]
saved=json.loads((R/'words.json').read_text()) if '--reuse' in sys.argv else None
for i,s in enumerate(spec['scenes']):
 if saved is not None: found=[w.copy() for w in saved if w['scene']==i]
 else:
  segments,_=model.transcribe(str(R/f'audio/{i:02}.wav'),beam_size=5,language='en',word_timestamps=True,vad_filter=True,vad_parameters={'min_silence_duration_ms':200},condition_on_previous_text=False,hallucination_silence_threshold=.5)
  found=[]
  for segment in segments:
   for w in segment.words: found.append({'start':w.start+s['audio_start'],'end':w.end+s['audio_start'],'text':w.word.strip(),'scene':i})
 # Correct homophones and punctuation against the authored narration; retain ASR timing.
 if found: found[0]['text']=found[0]['text'][0].upper()+found[0]['text'][1:]
 for j,w in enumerate(found):
  if i==1 and w['text'].lower().startswith('plains'):w['text']=w['text'].replace('plains','planes')
  if i==5 and w['text']=='Rewards' and j+1<len(found) and found[j+1]['text']=='can':w['text']='Cards'
  if i==11 and w['text']=='seats.':w['text']='seats?'
 if i==6:
  for j in range(len(found)-1):
   if found[j]['text']=='$8' and found[j+1]['text']=='.2':
    found[j]['text']='$8.2';found[j]['end']=found[j+1]['end'];found.pop(j+1);break
 print(i,' '.join(x['text'] for x in found),flush=True);words.extend(found)
(R/'words.json').write_text(json.dumps(words,indent=2))
groups=[];group=[]
for w in words:
 if group and (w['scene']!=group[-1]['scene'] or len(group)>=5 or len(' '.join(x['text'] for x in group))+len(w['text'])>34): groups.append(group);group=[]
 group.append(w)
 if w['text'].endswith(('.', '?', '!')): groups.append(group);group=[]
if group: groups.append(group)
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
out=[];result=[]
for i,g in enumerate(groups):
 start=g[0]['start'];end=max(start+.15,g[-1]['end']);phrase=' '.join(w['text'] for w in g)
 out.append(f'{i+1}\n{stamp(start)} --> {stamp(end)}\n{phrase}\n');result.append({'start':start,'end':end,'words':g,'text':phrase})
(R/'subtitles.srt').write_text('\n'.join(out),encoding='utf-8');(R/'captions.json').write_text(json.dumps(result,indent=2))
