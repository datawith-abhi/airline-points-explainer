"""A 120-second character performance, with scene action and audio-derived visemes."""
from pathlib import Path
import sys,math,json,bisect,subprocess,time
ROOT=Path(__file__).parent.resolve()
sys.path.insert(0,str(ROOT/'deps'));sys.path.insert(0,str(ROOT.parent/'airline-points-v2'/'deps'))
from PIL import Image,ImageDraw,ImageOps
import imageio_ffmpeg
import scene_props as a
import stage as st
from puppet import draw_presenter,smooth

W,H=1280,720;FPS=30
SPEC=json.loads((ROOT/'timeline.json').read_text())
CAPS=json.loads((ROOT/'captions.json').read_text())
CUES=json.loads((ROOT/'mouth-cues.json').read_text())['mouthCues']
CUE_STARTS=[v['start'] for v in CUES]
SCENES=SPEC['scenes']

def mouth_at(t):
    i=bisect.bisect_right(CUE_STARTS,t)-1
    return CUES[i]['value'] if i>=0 and t<CUES[i]['end'] else 'X'

def title(im,name,color=a.INK):
    a.txt(im,(44,25),'THE POINTS ECONOMY',15,color,'mono')
    a.txt(im,(1236,25),name,15,color,'mono','ra')

def figure(im,x,t,gt,sequence,feet=605,scale=1.0,prop=None,look=2,walk=0,expression='warm'):
    st.shadow(im,x,feet+3,185*scale)
    return draw_presenter(im,x,feet,scale,t,mouth_at(gt),sequence,look,expression,prop,walk)

def sign(im,x,y,label,size=24,color=a.INK):
    st.label(im,x,y,label,size,color,a.WHITE)

def camera(im,t,host,mode='normal'):
    # Shot changes show a performance close-up, a prop demonstration and the full set.
    phase=int(t/2.45)%3
    if mode=='wide':phase=0
    if phase==0:z=1.0+.016*math.sin(t*.6);cx,cy=640,360
    elif phase==1:z=1.48+.015*math.sin(t*.5);cx,cy=host,250
    else:z=1.0+.018*math.sin(t*.45);cx,cy=640,354
    ww,hh=W/z,H/z;left=max(0,min(W-ww,cx-ww/2));top=max(0,min(H-hh,cy-hh/2))
    return im.crop((round(left),round(top),round(left+ww),round(top+hh))).resize((W,H),Image.Resampling.BICUBIC)

def subtitles(im,gt):
    for c in CAPS:
        if c['start']<=gt<c['end']:
            words=c['words'];widths=[a.font(29,'bold').getlength(w['text']+' ') for w in words]
            total=sum(widths)-a.font(29,'bold').getlength(' ');x=(W-total)/2
            st.pill(im,(x-22,639,x+total+22,687),a.INK)
            for w,ww in zip(words,widths):
                a.txt(im,(x,648),w['text'],29,a.GOLD if w['start']<=gt<w['end'] else a.WHITE,'bold');x+=ww
            break

def render(i,t,captions=True):
    s=SCENES[i];gt=s['start']+t;p=t/s['duration'];kind=s['kind'];host=340
    settings=['shop','airport','airport','bank','cafe','bank','airport','studio','cabin','cabin','studio','studio','bank','airport']
    im=st.background(settings[i]).copy();d=ImageDraw.Draw(im)
    if kind=='hook':
        host=305+130*smooth((t-.8)/1.4)
        st.table(im,632,422,540)
        st.put(im,'bag',992,300,.62,-4);st.put(im,'terminal',644,322,.55)
        # A card in the host's hand meets the reader while she speaks to camera.
        figure(im,host,t,gt,[(0,'wave'),(.6,'hold'),(3.6,'offer'),(5.3,'point')],prop=st.prop('card'),walk=1 if .8<t<2.2 else 0)
        if t>2.2:
            st.stream(im,t-2.2,(665,334),(1095,193),True,3,.29,60,16)
            a.place(im,'plane',1089,153,.26,0)
            for r in range(3):d.arc((606-r*9,295-r*9,677+r*9,365+r*9),200,295,fill=a.TEAL,width=2)
        sign(im,940,476,'EVERYDAY SPENDING',23)
        im=camera(im,t,host)
    elif kind=='reveal':
        host=345+22*math.sin(t*.6)
        a.place(im,'plane',750+100*math.sin(t*.4),241,.58,-3)
        st.table(im,619,464,530)
        a.place(im,'ticket',800,411,.5,-4)
        st.put(im,'jar',1023,357,.62)
        figure(im,host,t,gt,[(0,'explain'),(1.6,'point'),(3.4,'hold'),(5.0,'both')],prop=st.prop('coin'),look=3)
        st.stream(im,t,(984,263),(735,418),False,3,.3,40,19)
        sign(im,815,505,'FLIGHTS',23);sign(im,1023,505,'POINTS',23)
        im=camera(im,t,host)
    elif kind=='costs':
        host=326
        st.put(im,'seat',797,414,.95)
        bills=['FUEL','CREWS','AIRCRAFT','MAINTENANCE','AIRPORTS']
        for j,tx in enumerate(bills):
            if t>.55+j*.76:
                y=180+70*j;xx=1060+9*math.sin(t+j)
                a.place(im,tx,xx,y,.63,(-1)**j*5)
                st.token(im,962+15*math.sin(t*2+j),y,15,True)
        figure(im,host,t,gt,[(0,'point'),(2.0,'count'),(3.8,'explain'),(6.0,'shrug'),(8.0,'point')],expression='surprised')
        st.stream(im,t,(760,470),(1030,483),True,3,.35,65,17)
        sign(im,791,563,'THE SEAT HAS BILLS',22)
        im=camera(im,t,host)
    elif kind=='bank':
        host=280
        st.table(im,546,458,636)
        a.place(im,'bank',1000,343,.65)
        sign(im,1000,494,'BANK',20)
        a.place(im,'plane',661,350,.31,-4)
        sign(im,654,494,'AIRLINE',20)
        st.stream(im,t,(975,295),(644,303),True,4,.32,67,19)
        st.stream(im,t,(642,422),(1000,424),False,4,.29,-5,18)
        figure(im,host,t,gt,[(0,'point'),(1.6,'offer'),(3.2,'point'),(5.1,'both')],look=3)
        sign(im,817,186,'CASH',20,a.TEAL);sign(im,818,494,'MILES',20)
        im=camera(im,t,host)
    elif kind=='spend':
        host=360+60*smooth((t-1.0)/1.0)
        st.table(im,603,432,590)
        st.put(im,'terminal',635,333,.53);st.put(im,'mug',842,353,.57,-3)
        st.put(im,'bag',1081,327,.55,4)
        figure(im,host,t,gt,[(0,'hold'),(1.5,'offer'),(3.1,'hold'),(4.7,'point'),(7.0,'both')],prop=st.prop('card'),walk=1 if 1<t<2 else 0)
        st.stream(im,t,(682,302),(1060,157),False,5,.34,70,18)
        a.place(im,'plane',1084,118,.24,-5)
        st.stream(im,t,(1077,218),(823,194),True,3,.25,15,14)
        sign(im,959,487,'THE BANK PAYS FIRST',23)
        im=camera(im,t,host)
    elif kind=='why':
        host=972
        st.table(im,67,455,673)
        a.place(im,'bank',385,204,.51)
        for j,label in enumerate(['MERCHANT FEES','ANNUAL FEES','INTEREST']):
            x=167+j*227;yy=402-18*math.sin(t*1.3+j)
            a.place(im,label,x,yy,.58,4*math.sin(t*.8+j))
            st.stream(im,t+j,(x,380),(382,275),True,2,.24,15,13)
        figure(im,host,t,gt,[(0,'both'),(1.7,'count'),(3.4,'shrug'),(5.3,'explain'),(7.4,'hold')],prop=st.prop('card'),look=-3)
        im=camera(im,t,host)
    elif kind=='stat':
        host=285
        # An airport-style split-flap board is a physical prop the presenter introduces.
        d.rounded_rectangle((563,107,1192,365),16,fill=a.INK,outline=a.WHITE,width=8)
        a.txt(im,(878,131),'DELTA × AMERICAN EXPRESS',23,a.GOLD,'bold','ma')
        a.txt(im,(878,173),'2025 PARTNERSHIP CASH',18,a.WHITE,'mono','ma')
        val=8.2*smooth((t-1)/1.8)
        a.txt(im,(878,223),f'${val:.1f}B',111,a.WHITE,'display','ma')
        for x in range(594,1156,94):d.line((x,268,x+79,268),fill='#667977',width=2)
        st.table(im,641,486,500)
        for j in range(7):st.token(im,700+j*62,434-abs(math.sin(t*1.2+j))*44,24,True,5*math.sin(t+j))
        figure(im,host,t,gt,[(0,'explain'),(1.4,'point'),(3.2,'count'),(5.6,'shrug'),(8.0,'both')],look=3,expression='surprised')
        sign(im,902,539,'CASH RECEIVED ≠ PROFIT',22)
        im=camera(im,t,host,'wide')
    elif kind=='split':
        host=306
        st.table(im,544,445,656)
        for j,tx in enumerate(['FUTURE FLIGHTS','MARKETING','BENEFITS']):
            x=637+j*224
            d.polygon([(x-83,388),(x+82,388),(x+70,437),(x-70,437)],fill=['#bd8555','#ce9661','#d8a774'][j])
            sign(im,x,469,tx,17)
            cyc=(t*.55-j*.35)%1
            st.token(im,435+(x-435)*cyc,311+(393-311)*cyc-105*math.sin(math.pi*cyc),19,True,cyc*14)
        figure(im,host,t,gt,[(0,'stop'),(1.6,'offer'),(3.2,'point'),(4.9,'offer'),(6.8,'both')],look=2)
        sign(im,873,154,'TODAY’S CASH, TOMORROW’S OBLIGATIONS',23)
        im=camera(im,t,host,'wide')
    elif kind=='empty':
        host=325
        st.put(im,'seat',862,412,1.02)
        sign(im,862,120,'OTHERWISE EMPTY',23)
        if t>2.3:
            x=1132-270*smooth((t-2.3)/1.5)
            st.peep(im,x,389,1.25)
            st.token(im,664,290+7*math.sin(t*2),30,True)
        figure(im,host,t,gt,[(0,'point'),(1.8,'offer'),(3.9,'both'),(6.1,'point')],prop=st.prop('ticket'),look=3)
        sign(im,862,556,'LOWER INCREMENTAL COST',19)
        im=camera(im,t,host)
    elif kind=='full':
        host=321
        for x in (790,1070):
            st.put(im,'seat',x,430,.85)
            st.peep(im,x,404,1.07,a.RED if x==790 else '#407b74')
        sign(im,931,124,'FULL FLIGHT',24)
        figure(im,host,t,gt,[(0,'stop'),(1.8,'shrug'),(3.8,'point'),(5.7,'both'),(7.7,'explain')],prop=st.prop('ticket'),expression='surprised')
        # A new award request approaches occupied seats, then is held back.
        x=590+70*math.sin(t*.9)
        a.place(im,'ticket',x,442,.3,-9)
        d.line((x-44,407,x+40,476),fill=a.RED,width=7);d.line((x-44,476,x+40,407),fill=a.RED,width=7)
        sign(im,976,565,'REWARDS STILL HAVE A COST',19)
        im=camera(im,t,host)
    elif kind=='unused':
        host=966
        st.table(im,66,476,615)
        st.put(im,'jar',342,309,.87)
        d.ellipse((549,106,718,275),fill=a.WHITE,outline=a.INK,width=6)
        for ang in range(0,360,30):
            rr=math.radians(ang);d.line((633+61*math.sin(rr),191-61*math.cos(rr),633+69*math.sin(rr),191-69*math.cos(rr)),fill=a.INK,width=3)
        ang=t*.9;d.line((633,191,633+57*math.sin(ang),191-57*math.cos(ang)),fill=a.RED,width=5)
        d.line((633,191,604,164),fill=a.INK,width=6)
        figure(im,host,t,gt,[(0,'think'),(2,'point'),(4,'count'),(6.2,'shrug'),(8.4,'explain')],look=-3)
        sign(im,346,530,'SOME MILES GO UNUSED',21)
        if t>4.5:sign(im,482,105,'AWARD PRICES CAN CHANGE',19)
        im=camera(im,t,host)
    elif kind=='truth':
        host=332
        st.table(im,573,466,625)
        for j,tx in enumerate(['CASH','REVENUE','PROFIT']):
            x=660+j*221
            d.rounded_rectangle((x-66,291,x+66,444),10,fill=['#74a58e','#c5995b','#df8764'][j],outline=a.WHITE,width=5)
            sign(im,x,383,tx,18)
            st.token(im,x,291-15*math.sin(t+j),20,j==0)
            if j<2:a.txt(im,(x+108,337),'≠',46,a.RED,'bold','mm')
        figure(im,host,t,gt,[(0,'think'),(1.6,'shrug'),(3.0,'stop'),(4.9,'point'),(7.0,'count')],expression='surprised')
        sign(im,892,145,'COMPARE THE RIGHT MEASURES',23)
        im=camera(im,t,host,'wide')
    elif kind=='engine':
        host=980
        st.table(im,65,462,696)
        st.put(im,'bag',184,346,.38,-3)
        a.place(im,'card',431,376,.38,-9)
        a.place(im,'plane',655,338,.27,-3)
        st.stream(im,t,(220,299),(622,286),False,5,.3,42,16)
        st.stream(im,t,(430,441),(681,442),True,3,.25,23,16)
        figure(im,host,t,gt,[(0,'both'),(1.8,'count'),(3.4,'point'),(5.4,'offer'),(7.8,'both')],look=-3)
        sign(im,428,517,'EVERYDAY SPENDING → AIRLINE CASH',20)
        im=camera(im,t,host)
    elif kind=='end':
        host=590+28*smooth(t/2)
        a.place(im,'plane',850+50*t,211-15*t,.53,-3)
        figure(im,host,t,gt,[(0,'point'),(1.8,'hold'),(3.7,'explain'),(5.7,'wave'),(7.4,'wave')],scale=1.05,prop=st.prop('card'),look=0)
        for j in range(5):st.token(im,970+j*39,441-28*j-12*math.sin(t+j),21,False,8*j)
        sign(im,234,251,'YOUR SPENDING',24);sign(im,234,295,'TAKES FLIGHT.',24)
        im=camera(im,t,host)
    title(im,['AT THE CHECKOUT','THE SECOND BUSINESS','THE COST OF A SEAT','FOLLOW THE MONEY','EVERYDAY SPENDING','WHY BANKS BUY MILES','THE SCALE','CASH HAS OBLIGATIONS','THE EMPTY SEAT','WHEN THE FLIGHT IS FULL','POINTS ARE A PROMISE','CASH IS NOT PROFIT','THE LOYALTY BUSINESS','EVEN ON THE GROUND'][i])
    if captions:subtitles(im,gt)
    # Short foreground paper wipe, never a long still at a scene boundary.
    if i>0 and t<.16:
        xx=round(1280*(1-t/.16));ImageDraw.Draw(im).polygon([(0,0),(xx+24,0),(xx-35,720),(0,720)],fill=a.PAPER)
    return im

def encode(start=0,duration=120,out=None):
    out=out or ROOT/'site'/'airline-points-character.mp4';out.parent.mkdir(exist_ok=True)
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    cmd=[ff,'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(FPS),'-i','-','-ss',str(start),'-i',str(ROOT/'mix.wav'),'-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-crf','23','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t',str(duration),'-movflags','+faststart',str(out)]
    now=time.time();last=-1
    with (ROOT/(out.stem+'-render.log')).open('w') as log:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for f in range(round(duration*FPS)):
                gt=start+f/FPS;i=min(13,bisect.bisect_right([s['start'] for s in SCENES],gt)-1)
                if i!=last:print('Rendering performance',i+1,'of 14',flush=True);last=i
                p.stdin.write(render(i,gt-SCENES[i]['start']).tobytes())
            p.stdin.close();assert p.wait()==0
        except BaseException:
            p.kill();raise
    print('Saved',out.name,'in',round(time.time()-now),'seconds',flush=True)

if __name__=='__main__':
    if '--frames' in sys.argv:
        sheet=Image.new('RGB',(1280,5*252),a.PAPER)
        for i,s in enumerate(SCENES):
            frame=render(i,min(3.4,s['duration']*.55));frame.save(ROOT/f'frame-{i:02}.jpg',quality=93)
            sheet.paste(frame.resize((426,240)),((i%3)*426,(i//3)*252))
        sheet.save(ROOT/'storyboard.jpg',quality=93)
        render(0,2.2,False).save(ROOT/'site'/'poster.jpg',quality=95)
        print('Character storyboard ready')
    elif '--sample' in sys.argv:encode(0,13.08,ROOT/'performance-preview.mp4')
    else:encode()
