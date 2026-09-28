from pathlib import Path
import sys,math,random,json,subprocess
from functools import lru_cache
R=Path(__file__).parent.resolve();sys.path.insert(0,str(R/'deps'));sys.path.insert(0,str(R.parent/'airline-points-v2'/'deps'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageOps,ImageEnhance
import imageio_ffmpeg,soundfile as sf
W,H=1280,720;FPS=30
PAPER='#f0e5ce';INK='#182d31';RED='#e75332';GOLD='#f1bd55';TEAL='#28766b';WHITE='#fff8e8'
@lru_cache(maxsize=100)
def font(size,kind='sans'):
 names={'sans':'arial.ttf','bold':'arialbd.ttf','display':'impact.ttf','serif':'georgiai.ttf','mono':'consola.ttf'}
 return ImageFont.truetype('C:/Windows/Fonts/'+names[kind],int(size))
def txt(im,xy,s,size=28,color=INK,kind='bold',anchor=None):
 ImageDraw.Draw(im).text(xy,s,font=font(size,kind),fill=color,anchor=anchor)
def ease(t):t=max(0,min(1,t));return 1-(1-t)**3
def rectpaper(size,color=PAPER,seed=1):
 w,h=size;r=random.Random(seed);out=Image.new('RGBA',(w+22,h+22));d=ImageDraw.Draw(out)
 pts=[(10+i*(w-20)/18,10+r.randint(-4,4)) for i in range(19)]+[(w-10+r.randint(-4,4),10+i*(h-20)/12) for i in range(1,13)]+[(w-10-i*(w-20)/18,h-10+r.randint(-4,4)) for i in range(1,19)]+[(10+r.randint(-4,4),h-10-i*(h-20)/12) for i in range(1,12)]
 d.polygon([(x+7,y+9) for x,y in pts],fill=(0,0,0,45));d.polygon(pts,fill=color)
 # Fine fibers stay on the paper, not across the transparent silhouette.
 rng=random.Random(seed+100)
 for _ in range(w*h//70):
  x,y=rng.randrange(16,w-16),rng.randrange(16,h-16);rgb=Image.new('RGB',(1,1),color).getpixel((0,0));d.line((x,y,x+2,y),fill=tuple(max(0,v-12) for v in rgb)+(255,))
 return out
def photo(name,size,tint=False):
 w,h=size;a=Image.open(R/'assets'/name).convert('RGB');a=ImageOps.fit(a,(w-36,h-54),centering=(.5,.4));a=ImageEnhance.Color(a).enhance(.60)
 if tint:a=ImageOps.colorize(ImageOps.grayscale(a),INK,'#ebdcb7')
 out=rectpaper(size,WHITE,7);out.paste(a,(18,18));return out
ASSETS={}
ASSETS['grocery']=photo('groceries.jpg',(600,470))
ASSETS['cabin']=photo('cabin.jpg',(675,410))
ASSETS['runway']=photo('airliner.jpg',(765,400),True)
def make_plane():
 a=Image.open(R/'assets/airliner.jpg').convert('RGB');mask=Image.new('L',a.size);d=ImageDraw.Draw(mask)
 p=[(63,283),(84,249),(130,223),(190,207),(267,208),(346,239),(625,340),(983,447),(1238,480),(1360,473),(1470,434),(1623,279),(1738,315),(1608,530),(1650,563),(1765,610),(1699,638),(1687,653),(1554,666),(1420,658),(1230,642),(927,592),(908,647),(804,650),(794,598),(740,644),(674,635),(677,576),(520,563),(420,538),(413,478),(328,441),(285,431),(266,506),(226,504),(223,470),(245,431),(205,395),(108,352),(73,319)]
 d.polygon(p,fill=255);a=ImageOps.colorize(ImageOps.grayscale(a),INK,WHITE).convert('RGBA')
 a.putalpha(mask);outer=mask.filter(ImageFilter.MaxFilter(23));border=Image.new('RGBA',a.size,WHITE);border.putalpha(outer);border.alpha_composite(a)
 border=border.crop((30,180,1790,690));border.thumbnail((1000,310));return border
ASSETS['plane']=make_plane()
def make_card():
 out=Image.new('RGBA',(450,285));d=ImageDraw.Draw(out);d.rounded_rectangle((8,12,441,276),25,fill=(0,0,0,65));d.rounded_rectangle((0,0,432,264),25,fill=RED)
 for x in range(-250,450,25):d.line((x,0,x+350,264),fill='#d7482b',width=1)
 txt(out,(32,28),'EVERYDAY',25,WHITE);txt(out,(32,58),'REWARDS',41,WHITE,'display');d.rounded_rectangle((34,116,99,164),8,fill=GOLD)
 for x in (54,78):d.line((x,117,x,164),fill=INK,width=1)
 d.line((34,140,99,140),fill=INK,width=1);txt(out,(33,185),'••••  ••••  ••••  2040',23,WHITE,'mono');txt(out,(34,230),'GOOD SPENDING. GREAT TRIPS.',15,WHITE,'mono');d.ellipse((350,40,385,75),outline=WHITE,width=3);d.ellipse((366,40,401,75),outline=WHITE,width=3)
 return out
ASSETS['card']=make_card()
def make_ticket():
 out=rectpaper((540,228),WHITE,55);d=ImageDraw.Draw(out);d.rectangle((10,10,527,55),fill=TEAL);txt(out,(30,20),'BOARDING PASS',24,WHITE,'mono');txt(out,(35,86),'HOME',50,INK,'display');txt(out,(330,86),'AWAY',50,INK,'display');txt(out,(35,158),'REWARD FLIGHT',20,TEAL,'mono');txt(out,(338,162),'SEAT 12A',20,TEAL,'mono')
 for x in range(230,296,5):d.line((x,80,x,186),fill=INK,width=2)
 for y in range(18,210,13):d.line((308,y,308,y+6),fill='#8a8b7d',width=2)
 return out
ASSETS['ticket']=make_ticket()
def make_bank():
 out=Image.new('RGBA',(310,340));d=ImageDraw.Draw(out);d.polygon([(15,90),(153,10),(295,90)],fill=WHITE);d.polygon([(32,88),(153,26),(276,88)],fill=INK)
 for j in range(4):
  x=40+j*65;d.rectangle((x,114,x+34,275),fill=WHITE)
  for k in range(4):d.line((x+7+k*6,120,x+7+k*6,268),fill='#afa995',width=2)
  d.rectangle((x-7,105,x+41,120),fill=WHITE);d.rectangle((x-7,270,x+41,287),fill=WHITE)
 d.rectangle((13,295,295,311),fill=WHITE);d.rectangle((3,318,305,336),fill=WHITE);return out
ASSETS['bank']=make_bank()
def make_receipt():
 out=rectpaper((270,480),WHITE,49);txt(out,(135,43),'EVERYDAY STORE',21,INK,'mono','mm');txt(out,(135,83),'THANK YOU!',17,INK,'mono','mm');d=ImageDraw.Draw(out);d.line((28,113,243,113),fill=INK,width=2)
 for j,(a,b) in enumerate([('COFFEE','4.50'),('GROCERIES','48.00'),('FUEL','35.00')]):txt(out,(27,148+j*54),a,20,INK,'mono');txt(out,(244,148+j*54),b,20,INK,'mono','ra')
 d.line((28,321,243,321),fill=INK,width=2);txt(out,(28,345),'POINTS',27,TEAL);txt(out,(243,388),'+ + +',35,TEAL,'display','ra');return out
ASSETS['receipt']=make_receipt()
def sticker(label,color=GOLD,size=27):
 w=round(font(size,'bold').getlength(label))+52;out=rectpaper((w,67),color,4);txt(out,(w/2,31),label,size,INK,'bold','mm');return out
for label in ['FUEL','CREWS','AIRCRAFT','MAINTENANCE','AIRPORTS','BANK PAYS FIRST','FUTURE FLIGHT','MARKETING','BENEFITS','MERCHANT FEES','ANNUAL FEES','INTEREST','ILLUSTRATION','NOT ALL PROFIT','UNUSED','TICKET REVENUE','PARTNERSHIP CASH','PROFIT','ON THE GROUND.','NO BOARDING PASS REQUIRED.']:
 ASSETS[label]=sticker(label)
def make_coin():
 out=Image.new('RGBA',(94,99));d=ImageDraw.Draw(out);d.ellipse((5,9,88,94),fill='#865828');d.ellipse((2,2,85,86),fill=GOLD,outline=WHITE,width=3);d.ellipse((11,11,76,76),outline=INK,width=2);txt(out,(43,43),'P',44,INK,'display','mm');return out
ASSETS['coin']=make_coin()
def bg(color,seed):
 rgb=np.array(Image.new('RGB',(1,1),color))[0,0];rng=np.random.default_rng(seed);noise=rng.normal(0,1.75,(H,W,1));a=np.clip(rgb+noise,0,255).astype('uint8');im=Image.fromarray(a);d=ImageDraw.Draw(im)
 for _ in range(380):
  x,y=int(rng.integers(W)),int(rng.integers(H));d.line((x,y,x+int(rng.integers(1,6)),y),fill=tuple(int(c) for c in np.clip(rgb-14,0,255)))
 return im
BG={'light':bg(PAPER,4),'dark':bg(INK,8),'red':bg(RED,6)}
@lru_cache(maxsize=230)
def transform(key,sc,angle):
 a=ASSETS[key];size=(max(1,round(a.width*sc)),max(1,round(a.height*sc)));a=a.resize(size,Image.Resampling.BICUBIC)
 if angle:a=a.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
 return a
def place(im,key,x,y,scale=1,angle=0):
 a=transform(key,round(scale,2),round(angle*2)/2);im.paste(a,(int(x-a.width/2),int(y-a.height/2)),a)
def enter(im,key,x,y,t,delay=0,scale=1,angle=0,dx=0,dy=90):
 if t<delay:return
 e=ease((t-delay)/.8);place(im,key,x+dx*(1-e)+2*math.sin(t*.6+delay),y+dy*(1-e)+3*math.sin(t*.7+delay),scale*(.92+.08*e)*(1+.012*math.sin(t*.5)),angle+(1-e)*7+.5*math.sin(t*.8+delay))
def headline(im,lines,x,y,size=86,color=INK,t=10,delay=0):
 for j,s in enumerate(lines):
  if t<delay+j*.18:continue
  e=ease((t-delay-j*.18)/.55);txt(im,(x,y+j*(size+.5)-25*(1-e)),s,size,color,'display')
def dots(im,x,y,w,h,color):
 d=ImageDraw.Draw(im)
 for a in range(x,x+w,13):
  for b in range(y,y+h,13):d.ellipse((a,b,a+2,b+2),fill=color)
def line_arrow(im,points,t,color=GOLD,delay=0):
 progress=ease((t-delay)/1.25)
 if progress<=0:return
 n=max(2,int(len(points)*progress));p=points[:n];d=ImageDraw.Draw(im);d.line(p,fill=color,width=5)
 if len(p)>3:
  x,y=p[-1];a=math.atan2(y-p[-3][1],x-p[-3][0]);d.polygon([(x,y),(x-17*math.cos(a-.6),y-17*math.sin(a-.6)),(x-17*math.cos(a+.6),y-17*math.sin(a+.6))],fill=color)
def path(a,b,curve=0):return [(a[0]+(b[0]-a[0])*v/59,a[1]+(b[1]-a[1])*v/59+curve*math.sin(math.pi*v/59)) for v in range(60)]
def particles(im,t,a,b,count=6):
 for j in range(count):
  p=((t*.26-j*.15)%1);x=a[0]+(b[0]-a[0])*p;y=a[1]+(b[1]-a[1])*p-40*math.sin(math.pi*p);place(im,'coin',x,y,.34,10*math.sin(t+j))

