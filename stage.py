"""Paper sets and handheld props for the character-led film."""
import math,random
from functools import lru_cache
from PIL import Image,ImageDraw
import scene_props as a
W,H=a.W,a.H

def pill(im,box,fill,outline=None,width=2):
    ImageDraw.Draw(im).rounded_rectangle(box,12,fill=fill,outline=outline,width=width)

def label(im,x,y,text,size=22,fill=a.INK,paper=None):
    width=a.font(size,'bold').getlength(text)
    if paper:pill(im,(x-width/2-14,y-7,x+width/2+14,y+size+9),paper)
    a.txt(im,(x,y),text,size,fill,'bold','ma')

def table(im,x,y,w=600):
    d=ImageDraw.Draw(im)
    d.polygon([(x-22,y+10),(x+w+24,y+10),(x+w+10,y+37),(x-10,y+37)],fill='#e1ad63')
    d.polygon([(x-22,y+10),(x+8,y-12),(x+w+38,y-12),(x+w+24,y+10)],fill='#f3c788')
    for lx in (x+27,x+w-50):d.polygon([(lx,y+35),(lx+25,y+35),(lx+39,613),(lx+6,613)],fill='#bc8152')
    d.line((x-10,y+37,x+w+10,y+37),fill='#ad764d',width=3)

def leaf(d,x,y,size=27,color=a.TEAL):
    d.ellipse((x-size,y-size*.45,x+size,y+size*.45),fill=color)
    d.line((x-size*.7,y,x+size*.6,y),fill='#b4c5a1',width=2)

@lru_cache(maxsize=12)
def background(kind):
    palette={'shop':'#ebdbbd','airport':'#dce5d7','bank':'#d8e6df','cafe':'#f0d7b8','cabin':'#e5dbc7','studio':'#e9d8bf'}
    im=a.bg(palette.get(kind,'#e9d8bf'),17);d=ImageDraw.Draw(im)
    d.rectangle((0,542,1280,720),fill='#c5b998')
    d.polygon([(0,570),(1280,570),(1280,590),(0,590)],fill='#ad9f80')
    for x in range(-800,1600,220):d.line((x,720,640+(x-640)*.52,542),fill='#b3a787',width=2)
    d.line((0,640,1280,640),fill='#b3a787',width=2)
    if kind in ('airport','cabin'):
        for x in range(40,1240,240):
            pill(im,(x,105,x+196,390),'#b6d1ce',a.CREAM if hasattr(a,'CREAM') else a.WHITE,9)
            d.polygon([(x+9,292),(x+185,248),(x+185,378),(x+9,378)],fill='#8daeab')
            d.line((x+16,324,x+183,294),fill='#e2e4cc',width=4)
            d.ellipse((x+80,148,x+147,171),fill='#deebe3')
        if kind=='airport':
            d.rectangle((0,428,1280,445),fill='#c9d5c4')
            d.line((0,447,1280,447),fill='#91a99a',width=3)
    if kind in ('shop','cafe'):
        for sx in (60,790):
            pill(im,(sx,114,sx+407,439),'#d3bc93',a.WHITE,7)
            for row in range(3):
                yy=208+row*96;d.rectangle((sx+10,yy,sx+397,yy+14),fill='#927552')
                for j in range(7):
                    xx=sx+30+j*51
                    col=['#699470','#c46042','#dbaf53'][j%3]
                    d.rounded_rectangle((xx,yy-54,xx+30,yy-3),5,fill=col)
                    d.rectangle((xx+7,yy-61,xx+24,yy-51),fill=a.WHITE)
                    d.rectangle((xx+5,yy-34,xx+25,yy-20),fill='#e7dbb9')
        if kind=='cafe':
            pill(im,(479,117,746,266),a.INK,a.WHITE,7)
            label(im,612,150,'FRESH COFFEE',24,a.WHITE)
            label(im,612,198,'EVERYDAY REWARDS',15,a.GOLD)
    if kind=='bank':
        for j in range(6):
            x=30+j*218;hh=[265,338,292,225,325,267][j]
            d.rectangle((x,520-hh,x+174,532),fill=['#b3c6b5','#a2beb4','#c5cbbb'][j%3])
            for wx in range(x+20,x+166,38):
                for wy in range(530-hh,495,51):d.rectangle((wx,wy,wx+17,wy+28),fill='#dce4d4')
        d.rectangle((0,516,1280,548),fill='#99b2a6')
    if kind=='studio':
        d.ellipse((-250,-220,535,505),fill='#dfc396')
        d.ellipse((860,139,1550,780),fill='#d2ba91')
        for yy in range(121,498,23):
            for xx in range(955,1190,23):d.ellipse((xx,yy,xx+3,yy+3),fill='#b39f7d')
    return im

def shadow(im,x,y,w):ImageDraw.Draw(im).ellipse((x-w/2,y-8,x+w/2,y+14),fill='#a99c7c')

@lru_cache(maxsize=16)
def prop(name):
    if name in a.ASSETS:return a.ASSETS[name]
    im=Image.new('RGBA',(380,420));d=ImageDraw.Draw(im)
    if name=='seat':
        d.polygon([(90,300),(120,300),(130,400),(109,400)],fill=a.INK)
        d.polygon([(262,300),(292,300),(282,400),(261,400)],fill=a.INK)
        d.rounded_rectangle((99,24,292,286),35,fill=a.TEAL,outline=a.WHITE,width=8)
        d.rounded_rectangle((117,47,274,203),24,fill='#3e9489')
        d.rounded_rectangle((78,257,313,327),19,fill='#286e67',outline=a.WHITE,width=7)
        d.rounded_rectangle((60,230,108,297),12,fill=a.INK,outline=a.WHITE,width=6)
        d.rounded_rectangle((291,230,339,297),12,fill=a.INK,outline=a.WHITE,width=6)
        d.line((122,289,270,289),fill='#7aaba0',width=3)
        d.rounded_rectangle((133,56,261,90),10,fill='#e4dabe')
    elif name=='bag':
        d.polygon([(70,168),(307,159),(292,395),(85,403)],fill='#c09059',outline=a.WHITE,width=5)
        d.polygon([(70,168),(110,134),(325,132),(307,159)],fill='#e1b578')
        for xx,yy,cc in [(150,112,a.TEAL),(195,109,'#65915c'),(247,105,a.TEAL)]:
            d.ellipse((xx-42,yy-75,xx+33,yy+78),fill=cc)
            d.line((xx-7,yy-40,xx+2,yy+75),fill='#a0bc75',width=4)
        d.ellipse((218,119,286,184),fill=a.RED)
        d.polygon([(113,194),(160,69),(178,74),(159,200)],fill='#e6c792')
        d.arc((129,220,251,296),180,355,fill='#845732',width=7)
        a.txt(im,(190,324),'GROCERIES',25,a.WHITE,'bold','mm')
    elif name=='terminal':
        d.polygon([(110,220),(267,208),(300,377),(70,391)],fill=a.INK,outline=a.WHITE,width=5)
        d.polygon([(126,235),(252,227),(265,302),(110,311)],fill='#70b79a')
        for r in range(3):
            for c in range(3):d.rounded_rectangle((113+c*48-r*5,324+r*17,143+c*48-r*5,334+r*17),3,fill='#d9dac8')
        a.txt(im,(188,268),'TAP',30,a.INK,'bold','mm')
    elif name=='mug':
        d.ellipse((239,162,346,311),outline=a.WHITE,width=26)
        d.rounded_rectangle((83,140,279,348),32,fill=a.RED,outline=a.WHITE,width=6)
        d.ellipse((92,122,273,163),fill='#783e2d',outline=a.WHITE,width=6)
        a.txt(im,(182,249),'COFFEE',25,a.WHITE,'bold','mm')
    elif name=='cash':
        d.rounded_rectangle((38,142,338,309),12,fill='#78a981',outline=a.WHITE,width=7)
        d.rounded_rectangle((53,158,323,293),8,outline=a.INK,width=3)
        d.ellipse((144,181,229,270),fill='#b7ce96',outline=a.INK,width=3)
        a.txt(im,(188,224),'$',69,a.INK,'display','mm')
    elif name=='jar':
        d.rounded_rectangle((73,116,306,392),35,fill='#d7d6b2',outline=a.WHITE,width=8)
        d.rounded_rectangle((92,77,286,134),12,fill=a.TEAL,outline=a.WHITE,width=6)
        for j in range(7):
            x=139+(j%3)*43;y=305-(j//3)*40
            d.ellipse((x-27,y-27,x+27,y+27),fill=a.GOLD,outline='#88622f',width=3)
            a.txt(im,(x,y),'P',32,a.INK,'display','mm')
        d.rounded_rectangle((86,170,294,235),5,fill=a.WHITE)
        a.txt(im,(191,202),'MY MILES',29,a.INK,'bold','mm')
    return im

def put(im,name,x,y,scale=1,angle=0):
    pp=prop(name);pp=pp.resize((max(1,round(pp.width*scale)),max(1,round(pp.height*scale))),Image.Resampling.BICUBIC)
    if angle:pp=pp.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    im.paste(pp,(round(x-pp.width/2),round(y-pp.height/2)),pp)

def token(im,x,y,size=24,cash=False,rotation=0):
    if cash:put(im,'cash',x,y,size/82,rotation)
    else:a.place(im,'coin',x,y,size/46,rotation)

def stream(im,t,p1,p2,cash=False,count=5,speed=.35,arc=35,scale=20):
    for j in range(count):
        u=(t*speed-j/count)%1
        token(im,p1[0]+(p2[0]-p1[0])*u,p1[1]+(p2[1]-p1[1])*u-arc*math.sin(math.pi*u),scale,cash,7*math.sin(t+j))

def peep(im,x,y,s=1,color='#cb7050'):
    d=ImageDraw.Draw(im)
    def b(box):return tuple(round(v*s+(x if j%2==0 else y)) for j,v in enumerate(box))
    d.ellipse(b((-21,-110,26,-60)),fill='#bf855c',outline=a.WHITE,width=3)
    d.pieslice(b((-24,-120,28,-73)),180,360,fill=a.INK)
    d.rounded_rectangle(b((-34,-60,36,38)),14,fill=color,outline=a.WHITE,width=3)
    for xx in (-17,15):d.line((x+xx*s,y+35*s,x+xx*s,y+83*s),fill=a.INK,width=max(4,round(13*s)))
    for xx in (-7,12):d.ellipse(b((xx-2,-91,xx+2,-86)),fill=a.INK)
    d.arc(b((-6,-83,14,-72)),0,170,fill=a.INK,width=2)
