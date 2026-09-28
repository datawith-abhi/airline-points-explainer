from pathlib import Path
import sys,math,random,json,subprocess
from functools import lru_cache
R=Path(__file__).parent.resolve();sys.path.insert(0,str(R/'deps'))
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
SPEC=json.loads((R/'timeline.json').read_text());CAPS=json.loads((R/'captions.json').read_text()) if (R/'captions.json').exists() else []
def render(i,t,captions=True):
 s=SPEC['scenes'][i];dur=s['duration'];p=t/dur;kind=s['kind'];dark=i in (1,3,5,7,9,12);theme='dark' if dark else ('red' if i==11 else 'light');im=BG[theme].copy();fg=WHITE if dark or i==11 else INK
 d=ImageDraw.Draw(im);txt(im,(50,28),'THE POINTS ECONOMY',16,fg,'mono');txt(im,(1230,28),f'{i+1:02} / 14',16,fg,'mono','ra')
 if kind=='hook':
  dots(im,930,90,290,220,TEAL);enter(im,'grocery',920,355,t,.1,1.14,6,dx=200);enter(im,'card',946,489,t,1.3,.85,-12,dy=180)
  headline(im,['YOUR GROCERIES.','THEIR CASH.'],50,138,83,t=t)
  enter(im,'NO BOARDING PASS REQUIRED.',305,487,t,2.7,.87,-3)
  for j in range(3):enter(im,'coin',585+j*48,524-j*64,t,1.5+j*.4,.62,8*j)
 elif kind=='reveal':
  txt(im,(60,105),'AN AIRLINE HAS TWO BUSINESSES.',24,GOLD,'mono');enter(im,'plane',637,263-30*p,t,0,1.15,3,dx=-550)
  headline(im,['FLIGHTS + POINTS'],76,408,120,WHITE,t,1.2);enter(im,'card',1040,360,t,2,.56,-13,dy=180)
 elif kind=='costs':
  enter(im,'runway',451,354,t,0,1,-5,dx=-400);headline(im,['A SEAT HAS','BILLS TO PAY.'],773,144,68,t=t)
  for j,key in enumerate(['FUEL','CREWS','AIRCRAFT','MAINTENANCE','AIRPORTS']):enter(im,key,180+j*192,466+(j%2)*59,t,.8+j*.56,.88,(-1)**j*6,dy=200)
 elif kind=='bank':
  headline(im,['THE BANK BUYS THE MILES.'],54,98,68,WHITE,t)
  enter(im,'bank',232,360,t,.2,.81,-3,dx=-260);enter(im,'plane',1000,330,t,.5,.5,4,dx=260)
  line_arrow(im,path((421,289),(786,289),-40),t,GOLD,1);txt(im,(608,232),'CASH',26,GOLD,'mono','mm');line_arrow(im,path((801,429),(427,429),40),t,RED,2);txt(im,(610,493),'POINTS',26,WHITE,'mono','mm');particles(im,t,(785,430),(435,430))
 elif kind=='spend':
  enter(im,'receipt',242,343,t,.1,.87,-6,dx=-200);enter(im,'card',645,348,t,.4,.85,7,dy=200)
  headline(im,['SWIPE.','EARN.','REPEAT.'],916,149,74,t=t)
  particles(im,t,(741,479),(1012,500),5);enter(im,'BANK PAYS FIRST',687,530,t,2.1,.84,-2)
 elif kind=='why':
  headline(im,['WHY BANKS','PLAY ALONG'],56,138,91,WHITE,t);enter(im,'bank',1035,364,t,.2,.93,0,dx=250)
  for j,k in enumerate(['MERCHANT FEES','ANNUAL FEES','INTEREST']):enter(im,k,478+j*145,431+j*57,t,1+j*.6,.9,(-1)**j*4,dx=-350)
 elif kind=='stat':
  txt(im,(67,99),'DELTA × AMERICAN EXPRESS / 2025',25,TEAL,'mono');value=8.2*ease(t/1.8);txt(im,(51,151),f'${value:.1f}',214,INK,'display');headline(im,['BILLION'],544,183,164,RED,t,.45)
  txt(im,(66,410),'PARTNERSHIP CASH RECEIVED',32,INK);enter(im,'NOT ALL PROFIT',265,507,t,3.5,.88,-3)
  for j in range(5):enter(im,'coin',800+j*72,510-14*j,t,1.8+j*.2,.85,15*j)
  txt(im,(65,578),'Source: Delta 2025 full-year financial results',18,TEAL,'mono')
 elif kind=='split':
  headline(im,['CASH ARRIVES.','OBLIGATIONS REMAIN.'],51,90,65,WHITE,t)
  enter(im,'coin',249,361,t,0,1.5,-3);line_arrow(im,path((355,342),(620,289),-25),t,GOLD,.5);line_arrow(im,path((355,369),(617,487),25),t,GOLD,1)
  enter(im,'ticket',912,296,t,.7,.8,-3,dx=240);enter(im,'MARKETING',786,498,t,1.3,.83,4);enter(im,'BENEFITS',1083,498,t,1.6,.83,-3)
 elif kind=='empty':
  enter(im,'cabin',408,343,t,0,1.01,-5,dx=-300);headline(im,['EMPTY SEAT.','REAL UPSIDE.'],770,136,75,t=t)
  for j in range(4):enter(im,'coin',824+j*79,422-j*21,t,1+j*.32,.7,7*j)
  enter(im,'ILLUSTRATION',985,543,t,.3,.73,2);txt(im,(72,577),'Lower incremental cost can make reward travel attractive.',20,TEAL,'mono')
 elif kind=='full':
  headline(im,['A REWARD STILL HAS A COST.'],54,99,66,WHITE,t)
  enter(im,'cabin',908,375,t,.2,.87,5,dx=200);enter(im,'ticket',318,350,t,.6,.88,-7,dx=-250)
  txt(im,(59,529),'PAID PASSENGER  ↔  AWARD PASSENGER',29,GOLD,'mono');d=ImageDraw.Draw(im);d.line((781,433,1045,206),fill=RED,width=9);d.line((792,210,1044,438),fill=RED,width=9)
 elif kind=='unused':
  headline(im,['POINTS ARE A PROMISE.'],54,95,79,t=t);txt(im,(59,204),'NOT EVERY PROMISE IS REDEEMED.',25,TEAL,'mono')
  for j in range(10):
   x=116+j*112;y=360+16*math.sin(j*.7+t*.5);enter(im,'coin',x,y,t,j*.13,.75,0,dy=100)
  enter(im,'UNUSED',1041,475,t,2,.9,8);txt(im,(67,531),'Award prices also change your buying power.',28,INK,'serif')
 elif kind=='truth':
  headline(im,['CASH ≠ PROFIT.'],52,100,128,WHITE,t)
  for j,key in enumerate(['TICKET REVENUE','PARTNERSHIP CASH','PROFIT']):enter(im,key,220+j*413,394,t,.7+j*.5,.96,(-1)**j*5,dy=150)
  txt(im,(63,537),'A BIG NUMBER NEEDS THE RIGHT COMPARISON.',26,WHITE,'mono')
 elif kind=='engine':
  headline(im,['LOYALTY TURNS SPENDING','INTO AIRLINE CASH.'],53,92,68,WHITE,t)
  enter(im,'grocery',242,395,t,.1,.58,-5,dx=-200);enter(im,'card',659,370,t,.4,.7,6,dy=150);enter(im,'plane',1070,364,t,.7,.44,-1,dx=230)
  particles(im,t,(395,470),(970,470),8);line_arrow(im,path((381,520),(1000,520),10),t,GOLD,1)
 elif kind=='end':
  dots(im,980,103,220,290,TEAL);enter(im,'plane',755-38*p,216-35*p,t,0,1.05,3,dx=-350);headline(im,['YOUR SPENDING','TAKES FLIGHT.'],55,333,100,t=t,delay=.7);enter(im,'card',1054,486,t,1,.69,-13,dy=190);enter(im,'ON THE GROUND.',265,574,t,3,.77,-2)
 # Captions follow Whisper word timestamps and highlight the word being spoken.
 gt=s['start']+t
 if captions:
  for c in CAPS:
   if c['start']<=gt<c['end']:
    words=c['words'];widths=[font(31,'bold').getlength(w['text']+' ') for w in words];total=sum(widths)-font(31,'bold').getlength(' ');x=(W-total)/2
    d=ImageDraw.Draw(im);d.rounded_rectangle((x-23,625,x+total+23,678),radius=7,fill=INK)
    for w,wd in zip(words,widths):txt(im,(x,635),w['text'],31,GOLD if w['start']<=gt<w['end'] else WHITE,'bold');x+=wd
    break
 d=ImageDraw.Draw(im);d.line((50,697,1230,697),fill='#9c9789',width=2);d.line((50,697,50+1180*gt/120,697),fill=GOLD if dark else RED,width=3)
 # A brief angled paper wipe joins successive chapters.
 if t<.32 and i>0:
  edge=int(W*(1-ease(t/.32)));ImageDraw.Draw(im).polygon([(0,0),(edge+100,0),(edge-40,H),(0,H)],fill=PAPER)
 return im
def mix_audio():
 voice,sr=sf.read(R/'narration.wav');n=len(voice);music=np.zeros(n,dtype=np.float32);rng=np.random.default_rng(44)
 chords=[[48,55,60,64],[45,52,57,60],[41,48,53,57],[43,50,55,59]]
 beat=60/94
 for j,start in enumerate(np.arange(0,120,beat)):
  chord=chords[(j//16)%4];note=chord[[0,2,1,3][j%4]]+12;dur=1.0;t=np.arange(int(sr*dur))/sr;hz=440*2**((note-69)/12);sig=(np.sin(2*np.pi*hz*t)+.25*np.sin(2*np.pi*hz*2*t))*np.exp(-5*t)*np.minimum(1,t/.012)*.014
  a=int(start*sr);b=min(n,a+len(sig));music[a:b]+=sig[:b-a]
 for s in SPEC['scenes'][1:]:
  t=np.arange(int(sr*.24))/sr;noise=rng.normal(0,1,len(t));smooth=np.convolve(noise,np.ones(15)/15,mode='same')*np.sin(np.pi*t/.24)*.028;a=int(s['start']*sr);music[a:a+len(t)]+=smooth[:n-a]
 envelope=np.minimum(1,np.arange(n)/sr/2)*np.minimum(1,(n-np.arange(n))/sr/2);voice=voice/max(.001,np.max(np.abs(voice)))*.83
 sf.write(R/'mix.wav',np.clip(voice+music*envelope,-.98,.98),sr)
if __name__=='__main__':
 if '--preview' in sys.argv:
  sheet=Image.new('RGB',(1280,5*256),PAPER)
  for i in range(14):
   im=render(i,min(4,SPEC['scenes'][i]['duration']*.6));im.save(R/f'frame-{i:02}.jpg',quality=90);sheet.paste(im.resize((426,240)),((i%3)*426,(i//3)*256))
  sheet.save(R/'storyboard.jpg',quality=92);print('Preview ready');sys.exit()
 mix_audio();(R/'site').mkdir(exist_ok=True)
 ff=imageio_ffmpeg.get_ffmpeg_exe();cmd=[ff,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(FPS),'-i','-','-i',str(R/'mix.wav'),'-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-crf','21','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t','120','-movflags','+faststart',str(R/'site/airline-points.mp4')]
 with (R/'render.log').open('w') as log:
  process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log);scene=0
  for f in range(120*FPS):
   gt=f/FPS
   while scene<13 and gt>=SPEC['scenes'][scene+1]['start']:scene+=1;print('Rendering chapter',scene+1,flush=True)
   process.stdin.write(render(scene,gt-SPEC['scenes'][scene]['start']).tobytes())
  process.stdin.close();assert process.wait()==0
 render(0,3,False).save(R/'site/poster.jpg',quality=94);print('Render complete',flush=True)
