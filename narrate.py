from pathlib import Path
import os,sys,json
R=Path(__file__).parent.resolve(); sys.path.insert(0,str(R/'deps'))
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1'
import numpy as np, soundfile as sf, onnxruntime as ort
from kokoro_onnx import Kokoro
spec=json.loads((R/'production.json').read_text())
(R/'audio').mkdir(exist_ok=True)
opts=ort.SessionOptions(); opts.intra_op_num_threads=4; opts.inter_op_num_threads=1
sess=ort.InferenceSession(str(R/'models/kokoro-v1.0.onnx'),sess_options=opts,providers=['CPUExecutionProvider'])
k=Kokoro.from_session(sess,str(R/'models/voices-v1.0.bin'))
speed=float(sys.argv[1]) if len(sys.argv)>1 else 1.03
durations=[]
for i,s in enumerate(spec['scenes']):
 path=R/f'audio/{i:02}.wav'
 if path.exists() and '--reuse' in sys.argv: a,sr=sf.read(path)
 else:
  a,sr=k.create(s['text'],voice=spec['voice'],speed=speed,lang='en-us')
  sf.write(path,a,sr)
 durations.append(len(a)/sr); print(i,s['kind'],round(len(a)/sr,2),flush=True)
total=sum(durations); print('TOTAL',total,flush=True)
if total>113: raise RuntimeError(f'Regenerate at speed {speed*total/110:.3f}')
holds=(120-total)/len(durations); cursor=0; final=np.zeros(120*24000,dtype=np.float32)
for i,(s,d) in enumerate(zip(spec['scenes'],durations)):
 a,sr=sf.read(R/f'audio/{i:02}.wav'); lead=min(.32,holds/2)
 start=round((cursor+lead)*24000); final[start:start+len(a)]=a
 s.update(start=cursor,duration=d+holds,audio_start=cursor+lead,audio_duration=d)
 cursor+=d+holds
sf.write(R/'narration.wav',final,24000)
spec['voice_speed']=speed; (R/'timeline.json').write_text(json.dumps(spec,indent=2))
