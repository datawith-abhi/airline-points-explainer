"""Original cut-paper presenter, articulated in layers with nine speech shapes."""
from pathlib import Path
import sys, math, bisect, json
from functools import lru_cache
ROOT=Path(__file__).parent
sys.path.insert(0,str(ROOT.parent/'airline-points-v2'/'deps'))
sys.path.insert(0,str(ROOT/'deps'))
from PIL import Image, ImageDraw, ImageFilter

INK='#203437'; SKIN='#bf7956'; LIGHT='#db9b72'; SHADE='#98573d'
HAIR='#302a2a'; TEAL='#287b73'; TEAL_LIGHT='#3c9286'; CREAM='#fff3d9'; GOLD='#e8af44'

def lerp(a,b,p): return tuple(x+(y-x)*p for x,y in zip(a,b))
def smooth(p): p=max(0,min(1,p)); return p*p*(3-2*p)
def bezier(points,n=18):
    out=[]
    for i in range(n+1):
        t=i/n; q=points
        while len(q)>1:q=[lerp(a,b,t) for a,b in zip(q,q[1:])]
        out.append(q[0])
    return out

class Art:
    def __init__(self,w=520,h=590,k=2):
        self.k=k;self.im=Image.new('RGBA',(w*k,h*k));self.d=ImageDraw.Draw(self.im)
    def p(self,xy):return (round((xy[0]+260)*self.k),round((xy[1]+580)*self.k))
    def line(self,p,fill=INK,w=2):
        p=[self.p(v) for v in p];self.d.line(p,fill=fill,width=max(1,round(w*self.k)),joint='curve')
    def ellipse(self,box,fill,outline=None,w=1):
        self.d.ellipse((*self.p(box[:2]),*self.p(box[2:])),fill=fill,outline=outline,width=max(1,round(w*self.k)))
    def poly(self,p,fill,outline=None,w=1):
        self.d.polygon([self.p(v) for v in p],fill=fill)
        if outline:self.line(p+[p[0]],outline,w)
    def path(self,start,segments,fill,outline=None,w=1):
        pts=[start]
        for seg in segments:
            if len(seg)==2:pts.append(seg)
            else:pts+=bezier([pts[-1],seg[:2],seg[2:4],seg[4:6]])[1:]
        self.poly(pts,fill,outline,w)

def capsule(a,pt1,pt2,width,fill):
    a.line([pt1,pt2],CREAM,width+5)
    for p in (pt1,pt2):a.ellipse((p[0]-(width+5)/2,p[1]-(width+5)/2,p[0]+(width+5)/2,p[1]+(width+5)/2),CREAM)
    a.line([pt1,pt2],fill,width)
    for p in (pt1,pt2):a.ellipse((p[0]-width/2,p[1]-width/2,p[0]+width/2,p[1]+width/2),fill)

def elbow(shoulder,hand,side):
    dx,dy=hand[0]-shoulder[0],hand[1]-shoulder[1];dist=math.hypot(dx,dy)
    if dist>158:hand=(shoulder[0]+dx*158/dist,shoulder[1]+dy*158/dist);dx,dy=hand[0]-shoulder[0],hand[1]-shoulder[1];dist=158
    mid=lerp(shoulder,hand,.49);bend=math.sqrt(max(0,84**2-(dist/2)**2))
    return (mid[0]-dy/max(dist,1)*bend*side,mid[1]+dx/max(dist,1)*bend*side),hand

POSES={
 'rest':((-77,-217),(82,-228)),
 'explain':((-108,-276),(133,-315)),
 'point':((-73,-236),(162,-355)),
 'hold':((-87,-237),(119,-326)),
 'count':((-100,-278),(88,-428)),
 'shrug':((-132,-338),(132,-338)),
 'wave':((-92,-237),(111,-435)),
 'stop':((-83,-247),(133,-372)),
 'both':((-132,-309),(138,-309)),
 'offer':((-102,-264),(145,-293)),
 'think':((-76,-240),(36,-387)),
 'push':((-94,-273),(143,-344)),
}

def pose_at(t,sequence):
    """Ease to meaningful beat poses; a pose never snaps at a keyframe."""
    previous=sequence[0][1]
    for at,name in sequence[1:]:
        if t<at:return POSES[previous],previous
        if t<at+.44:
            e=smooth((t-at)/.44);return tuple(lerp(a,b,e) for a,b in zip(POSES[previous],POSES[name])),name
        previous=name
    return POSES[previous],previous

def hand(a,at,side=1,mode='open',tilt=0):
    x,y=at
    def pt(px,py):
        ang=math.radians(tilt);return (x+side*(px*math.cos(ang)-py*math.sin(ang)),y+px*math.sin(ang)+py*math.cos(ang))
    if mode=='point':
        outline=[(-9,9),(-12,-4),(-5,-12),(23,-20),(29,-18),(28,-13),(7,-5),(19,-2),(20,4),(12,8),(6,14)]
    elif mode=='fist':outline=[(-11,10),(-13,-7),(-7,-14),(6,-15),(17,-9),(20,3),(12,14),(0,16)]
    else:
        outline=[(-10,12),(-15,-3),(-18,-14),(-14,-19),(-10,-16),(-5,-5),(-6,-28),(-2,-32),(2,-29),(4,-8),(6,-35),(10,-35),(13,-29),(12,-6),(18,-29),(22,-28),(24,-22),(21,-2),(27,-15),(31,-14),(32,-9),(26,11),(16,21),(0,20)]
    a.poly([pt(*v) for v in outline],LIGHT,CREAM,2.5)
    a.line([pt(-7,4),pt(0,1),pt(8,4)],SHADE,1.2)
    if mode=='fist':
        for j in range(3):a.line([pt(-4+j*6,-10),pt(-3+j*6,2)],SHADE,1)

@lru_cache(maxsize=120)
def head(mouth,blink,look,expression,tilt):
    a=Art(220,235,2);a.p=lambda p:(round((p[0]+110)*a.k),round((p[1]+110)*a.k))
    # Layered hair silhouette and loose bun.
    a.ellipse((-75,-105,-11,-39),HAIR,CREAM,3)
    a.path((-55,13),[(-95,-44,-63,-104,-8,-100),(43,-111,76,-69,60,-6),(65,18,75,47,46,63),(-12,77,-63,62,-55,13)],HAIR,CREAM,3)
    a.ellipse((-58,-14,-28,19),SKIN)
    a.ellipse((36,-10,60,20),SKIN)
    # A slightly asymmetric face gives a three-quarter editorial drawing.
    a.path((-45,-45),[(-25,-76,39,-68,44,-35),(50,-13,51,31,32,55),(11,79,-18,64,-36,43),(-47,22,-54,-15,-45,-45)],LIGHT,INK,1.2)
    a.path((29,-44),[(50,-31,52,28,32,55),(21,64,9,67,1,65),(24,43,33,-14,29,-44)],SKIN)
    # Swept paper hair pieces.
    a.path((-57,-18),[(-78,-70,-25,-112,20,-87),(48,-96,72,-48,40,-35),(21,-49,0,-58,-8,-63),(-17,-37,-35,-24,-57,-18)],HAIR)
    a.line(bezier([(-45,-54),(-27,-80),(-9,-83),(15,-77)]),'#66504a',2)
    a.line(bezier([(-40,-45),(-30,-62),(-14,-71),(-1,-69)]),'#66504a',1.4)
    a.ellipse((-45,26,-33,47),None,GOLD,3);a.ellipse((43,21,55,43),None,GOLD,3)
    # Cheeks, eyes, moving pupils, brows and nose.
    a.ellipse((-37,21,-12,31),'#cf8463');a.ellipse((24,21,44,31),'#bf7956')
    for cx in (-22,25):
        if blink:a.line(bezier([(cx-10,2),(cx-3,8),(cx+5,8),(cx+11,2)]),INK,2.3)
        else:
            a.ellipse((cx-11,-6,cx+11,10),CREAM)
            a.ellipse((cx-4+look,-6,cx+4+look,8),INK)
            a.ellipse((cx-1+look,-5,cx+1+look,-2),CREAM)
            a.line(bezier([(cx-12,-3),(cx-3,-10),(cx+7,-8),(cx+12,-2)]),INK,2.2)
    brow=-16 if expression!='surprised' else -24
    a.line(bezier([(-35,brow+2),(-27,brow-4),(-19,brow-3),(-11,brow)]),HAIR,3.1)
    a.line(bezier([(14,brow+1),(24,brow-5),(34,brow-2),(38,brow+2)]),HAIR,3.1)
    # Round wire glasses and bridge.
    for cx in (-22,25):a.ellipse((cx-19,-15,cx+19,22),None,INK,2)
    a.line([(-3,0),(6,-1)],INK,2);a.line([(-42,-2),(-49,-5)],INK,2);a.line([(44,-1),(51,-4)],INK,2)
    a.line(bezier([(5,2),(2,14),(1,18),(10,17)]),SHADE,1.6)
    mx,my=6,39
    if mouth=='X':a.line(bezier([(mx-13,my-1),(mx-4,my+8),(mx+8,my+8),(mx+16,my-4)]),INK,2)
    elif mouth=='A':
        a.line(bezier([(mx-13,my),(mx-4,my+2),(mx+8,my+2),(mx+14,my)]),'#794231',3)
        a.line([(mx-5,my+5),(mx+7,my+5)],SHADE,1)
    else:
        w,h={'B':(31,10),'C':(31,22),'D':(27,32),'E':(20,20),'F':(12,16),'G':(30,12),'H':(29,24)}[mouth]
        a.ellipse((mx-w/2,my-h/2,mx+w/2,my+h/2),'#512e2b',SHADE,1)
        if mouth not in ('E','F'):
            a.poly([(mx-w*.37,my-h*.40),(mx+w*.35,my-h*.40),(mx+w*.32,my-h*.40+5),(mx-w*.32,my-h*.40+5)],CREAM)
        if mouth in ('C','D','H'):
            a.ellipse((mx-w*.25,my+h*.05,mx+w*.3,my+h*.43),'#d98075')
        if mouth=='G':a.line([(mx-10,my),(mx+10,my)],CREAM,4)
    # A delicate highlight on the cheek keeps the paper layers dimensional.
    a.line(bezier([(-38,34),(-37,41),(-32,48),(-27,51)]),'#eab28d',1.5)
    im=a.im.resize((220,235),Image.Resampling.LANCZOS)
    return im.rotate(tilt,resample=Image.Resampling.BICUBIC,expand=False)

def draw_presenter(im,x,feet,scale,t,mouth='X',sequence=None,look=0,expression='warm',prop=None,walk=0):
    sequence=sequence or [(0,'explain'),(2.4,'point'),(4.5,'both'),(6.8,'explain')]
    targets,mode=pose_at(t,sequence)
    if prop is not None:
        # Keep the prop in one hand; the free hand carries the explanatory gesture.
        targets=((-targets[1][0],targets[1][1]),(116,-307))
    sway=2.2*math.sin(t*1.65);bob=1.7*math.sin(t*2.2)+(abs(math.sin(t*7))*4*walk)
    a=Art();d=a.d
    # Long trousers with a shifted stance and toe-to-heel walk cycle.
    for side in (-1,1):
        stride=math.sin(t*7+(0 if side==1 else math.pi))*23*walk
        hip=(side*25,-219+bob);knee=(side*34+stride*.35,-112);ankle=(side*42+stride, -24-abs(stride)*.12)
        pts=[(hip[0]-22,hip[1]),(hip[0]+22,hip[1]),(knee[0]+25,knee[1]),(ankle[0]+23,ankle[1]),(ankle[0]-23,ankle[1]),(knee[0]-22,knee[1])]
        a.poly(pts,GOLD if side==1 else '#cc963b',CREAM,3)
        a.line([(hip[0]+5,hip[1]+22),(knee[0]+6,knee[1]),(ankle[0]+6,ankle[1]-7)],'#b68434',1.4)
        ax,ay=ankle;a.path((ax-23,ay-3),[(ax+6,ay-3),(ax+22,ay+7,ax+42,ay+8,ax+38,ay+20),(ax-23,ay+20),(ax-29,ay+11,ax-29,ay+7,ax-23,ay-3)],CREAM,INK,1.5)
        a.line([(ax-25,ay+15),(ax+35,ay+15)],INK,1.3)
        for j in range(3):a.line([(ax+j*5,ay+2),(ax+5+j*5,ay+8)],INK,1)
    # Neck, shirt, jacket and tailored lapels.
    a.poly([(-18,-384+bob),(20,-383+bob),(21,-340+bob),(3,-324+bob),(-20,-342+bob)],SKIN,CREAM,3)
    a.path((-53+sway,-345+bob),[(-17,-357+bob),(0,-343+bob),(21,-355+bob),(54+sway,-343+bob),(69+sway,-274+bob),(62+sway,-211+bob),(-62+sway,-211+bob),(-63+sway,-285+bob)],TEAL,CREAM,3)
    a.poly([(-20,-347+bob),(0,-333+bob),(22,-348+bob),(26,-225+bob),(-25,-225+bob)],CREAM)
    for yy in (-323,-306,-289,-272,-255):a.line([(-21,yy+bob),(23,yy+bob)],'#d3c7ac',1.5)
    a.poly([(-24,-350+bob),(-47,-329+bob),(-29,-307+bob),(-40,-293+bob),(-12,-248+bob)],TEAL_LIGHT)
    a.poly([(26,-351+bob),(48,-328+bob),(33,-308+bob),(45,-297+bob),(16,-250+bob)],'#215f5b')
    a.line([(-48,-248+bob),(-22,-244+bob)],GOLD,2)
    a.ellipse((34,-257+bob,39,-252+bob),GOLD)
    # The arms are inverse-kinematic paper strips with natural elbow arcs.
    hands=[]
    for side,target in zip((-1,1),targets):
        shoulder=(side*52+sway,-331+bob)
        osc=3*math.sin(t*2.5+side)+(8*math.sin(t*7+side)*walk)
        target=(target[0]+sway,target[1]+bob+osc)
        gesture_side=-1 if prop is not None else 1
        if mode=='wave' and side==gesture_side:target=(target[0]+13*math.sin(t*8),target[1])
        e,h=elbow(shoulder,target,side)
        capsule(a,shoulder,e,30,TEAL if side==1 else '#24685f')
        cuff=lerp(e,h,.66);capsule(a,e,cuff,25,TEAL_LIGHT if side==1 else TEAL)
        capsule(a,cuff,h,17,LIGHT)
        hands.append(h)
    # Head nod, hair follow-through, gaze and blinks are independent of speech.
    blink=1 if (t+0.3)%3.71<.115 or (t+1.5)%8.1<.08 else 0
    tilt=round(2.6*math.sin(t*1.3)+1.1*math.sin(t*3.1)+(3 if mode=='think' else 0))
    hd=head(mouth,blink,int(look),expression,tilt)
    hx=round(260-110+sway);hy=round(580-447-110+bob)
    a.im.alpha_composite(hd.resize((440,470),Image.Resampling.BICUBIC),(hx*2,hy*2))
    # An actual held object moves with the wrist rather than floating independently.
    if prop is not None:
        pp=prop.copy();pp.thumbnail((150*2,108*2),Image.Resampling.LANCZOS);pp=pp.rotate(-8+3*math.sin(t*2),resample=Image.Resampling.BICUBIC,expand=True)
        h=hands[1];px,py=a.p((h[0]+7,h[1]-36));a.im.alpha_composite(pp,(int(px-pp.width/2),int(py-pp.height/2)))
    for side,h in zip((-1,1),hands):
        gesture_side=-1 if prop is not None else 1
        style='fist' if prop is not None and side==1 else ('point' if mode in ('point','count','think') and side==gesture_side else 'open')
        hand(a,h,side,style,(-32 if side==1 else 32) if mode in ('both','shrug','explain') else 0)
    layer=a.im.resize((round(520*scale),round(590*scale)),Image.Resampling.LANCZOS)
    # One offset translucent silhouette reads as paper sitting above the scene.
    mask=layer.getchannel('A');shadow=Image.new('RGBA',layer.size,(33,40,33,0));shadow.putalpha(mask.point(lambda z:round(z*.19)))
    xy=(round(x-260*scale),round(feet-580*scale))
    im.paste(shadow,(xy[0]+round(6*scale),xy[1]+round(6*scale)),shadow)
    im.paste(layer,xy,layer)
    return [(x+h[0]*scale,feet+h[1]*scale) for h in hands]

if __name__=='__main__':
    canvas=Image.new('RGB',(1280,720),'#ecdfc5')
    draw_presenter(canvas,335,650,1.08,1.5,'C',[(0,'wave')])
    draw_presenter(canvas,912,650,1.08,3.8,'F',[(0,'point')],look=3)
    canvas.save(ROOT/'presenter-design.png')
