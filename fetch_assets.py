from pathlib import Path
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
R=Path(__file__).parent
(R/'models').mkdir(exist_ok=True); (R/'assets').mkdir(exist_ok=True)
items=[
 ('models/kokoro-v1.0.onnx','https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx'),
 ('models/voices-v1.0.bin','https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin'),
 ('assets/jet.jpg','https://images.pexels.com/photos/2961993/pexels-photo-2961993.jpeg?auto=compress&cs=tinysrgb&w=1800'),
 ('assets/groceries.jpg','https://images.pexels.com/photos/8900041/pexels-photo-8900041.jpeg?auto=compress&cs=tinysrgb&w=1500'),
 ('assets/airliner.jpg','https://images.pexels.com/photos/36219158/pexels-photo-36219158.jpeg?auto=compress&cs=tinysrgb&w=1800'),
 ('assets/cabin.jpg','https://images.unsplash.com/photo-1762960246763-dcb1e92b0b58?auto=format&fit=crop&fm=jpg&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&ixlib=rb-4.1.0&q=60&w=3000')]
def fetch(item):
 name,url=item; dest=R/name
 if dest.exists(): return
 with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=90) as r, dest.open('wb') as f:
  while True:
   b=r.read(1048576)
   if not b: break
   f.write(b)
 print(name,dest.stat().st_size,flush=True)
with ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(fetch,items))
