"""Deterministic, offline studio rendering of the PERPETUA PM-1."""
import os
import sys
import math
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    _pillow_dir = tempfile.TemporaryDirectory(prefix='perpetua-pillow-')
    with zipfile.ZipFile(ROOT / 'vendor' / 'pillow.whl') as wheel:
        wheel.extractall(_pillow_dir.name)
    sys.path.insert(0, _pillow_dir.name)
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2
N = 2048
im = Image.new('RGB', (N, N))
pix = im.load()
for y in range(N):
    for x in range(N):
        glow = math.exp(-(((x / S - 610) / 580) ** 2 + ((y / S - 355) / 580) ** 2))
        floor = max(0, y / S - 690) / 334
        v = int(221 + 24 * glow - 6 * floor)
        pix[x, y] = (v + 3, v + 1, v - 3)
# A restrained, feathered floor-to-backdrop transition.
horizon = Image.new('RGBA', (N, N))
ImageDraw.Draw(horizon).line((0, 1380, N, 1380), fill=(166, 168, 164, 19), width=2)
im.paste(horizon.filter(ImageFilter.GaussianBlur(11 * S)), (0, 0), horizon.filter(ImageFilter.GaussianBlur(11 * S)))

def box(b): return tuple(round(v * S) for v in b)
def layer(): return Image.new('RGBA', (N,N))
def paste(l): im.paste(l, (0,0), l)
def ellipse(b, c, target=None, outline=None, width=1):
    ImageDraw.Draw(im if target is None else target).ellipse(box(b), fill=c, outline=outline, width=round(width*S))
def line(points, c, w, target=None):
    ImageDraw.Draw(im if target is None else target).line([(round(x*S),round(y*S)) for x,y in points],fill=c,width=round(w*S),joint='curve')
def text(x,y,t,size,color=(81,84,80),bold=False,anchor=None):
    font=ImageFont.truetype(str(ROOT/'assets'/('LiberationSans-Bold.ttf' if bold else 'LiberationSans-Regular.ttf')),round(size*S))
    ImageDraw.Draw(im).text((round(x*S),round(y*S)),t,font=font,fill=color,anchor=anchor)
def shadow(b, blur, alpha):
    l=layer(); ellipse(b,(40,42,37,alpha),l); paste(l.filter(ImageFilter.GaussianBlur(blur*S)))
def rounded(b,r,c): ImageDraw.Draw(im).rounded_rectangle(box(b),radius=r*S,fill=c)
def gradient_shape(b, maskfn, top, bottom):
    l=Image.new('RGB',(N,N)); d=ImageDraw.Draw(l)
    for y in range(int(b[1]*S),int(b[3]*S)+1):
        t=(y/S-b[1])/(b[3]-b[1]); c=tuple(round(a*(1-t)+z*t) for a,z in zip(top,bottom)); d.line((int(b[0]*S),y,int(b[2]*S),y),fill=c)
    m=Image.new('L',(N,N)); maskfn(ImageDraw.Draw(m)); im.paste(l,(0,0),m)
def bezier(a,b,c,d,n=100):
    return [((1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*c[0]+t**3*d[0],(1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*c[1]+t**3*d[1]) for t in (i/n for i in range(n+1))]

# Render the fan separately so its scale and placement change as one assembly.
backdrop = im
im = layer()
# Grounding shadows travel with the product.
shadow((427,753,848,837),22,65)
shadow((470,784,819,820),6,60)
# Neck, with a softly shaded moulded cross-section.
gradient_shape((593,552,672,760),lambda d:d.rounded_rectangle(box((593,552,672,760)),radius=25*S,fill=255),(222,225,219),(167,174,168))
for i in range(35):
    c=int(224-i*.7); line([(606+i,572),(606+i,736)],(c,c+3,c-1),1)
# Weighted base: front skirt, top crown, and seam.
gradient_shape((460,711,821,815),lambda d:d.rounded_rectangle(box((460,711,821,815)),radius=44*S,fill=255),(208,212,205),(157,165,158))
gradient_shape((460,687,821,794),lambda d:d.rounded_rectangle(box((460,687,821,794)),radius=49*S,fill=255),(239,240,233),(199,205,197))
line([(497,793),(785,793)],(167,176,167),1)
# Tilt pivot, behind the head.
ellipse((601,559,668,625),(162,170,161)); ellipse((610,566,660,616),(205,210,201))
# Head body: offset rear shell and nested radial moulded shading.
cx,cy=634,414
ellipse((392,166,888,662),(164,173,164))
ellipse((389,162,879,652),(244,245,237))
for r in range(242,0,-1):
    t=r/242
    v=int(211+25*(1-t))
    ellipse((cx-r,cy-r,cx+r,cy+r),(v+1,v+4,v-1))
# Deep inner air chamber.
ellipse((410,190,858,638),(153,164,155))
for r in range(219,0,-1):
    t=r/219; v=int(186-27*t)
    ellipse((cx-r,cy-r,cx+r,cy+r),(v,v+9,v+1))
# Three swept blades, exposed for multiple fractions of a revolution.
def blade(angle):
    pts=bezier((30,-15),(105,-137),(222,-152),(192,-39),36)
    pts+=bezier((192,-39),(166,31),(78,57),(30,15),36)
    co,si=math.cos(angle),math.sin(angle)
    return [(round((cx+x*co-y*si)*S),round((cy+x*si+y*co)*S)) for x,y in pts]
l=layer(); d=ImageDraw.Draw(l)
for offset in range(0,51,5):
    for k in range(3): d.polygon(blade(math.radians(k*120+offset-28)),fill=(226,236,221,27))
l=l.filter(ImageFilter.GaussianBlur(3*S)); paste(l)
for k in range(3):
    l=layer(); ImageDraw.Draw(l).polygon(blade(math.radians(k*120-1)),fill=(231,238,225,84)); paste(l.filter(ImageFilter.GaussianBlur(1.8*S)))
# Fine grille: a softly lit wire cage, no black outlines.
for k in range(20):
    a=k*math.tau/20; p=[(cx+48*math.cos(a),cy+48*math.sin(a)),(cx+219*math.cos(a),cy+219*math.sin(a))]
    line(p,(137,150,140),2.2); line([(x-.6,y-1) for x,y in p],(220,226,214),.85)
for r in range(63,221,11):
    ellipse((cx-r,cy-r,cx+r,cy+r),None,outline=(136,150,139),width=2.3)
    ellipse((cx-r-.6,cy-r-1,cx+r-.6,cy+r-1),None,outline=(223,228,216),width=.9)
for r,c,w in [(225,(130,143,132),3),(231,(232,235,225),7),(240,(213,219,207),6),(244,(244,246,238),2)]:
    ellipse((cx-r,cy-r,cx+r,cy+r),None,outline=c,width=w)
# Domed centre, a restrained embossed wordmark.
shadow((584,379,689,471),5,35)
for r in range(54,0,-1):
    t=r/54; v=int(237-35*t*t)
    ellipse((cx-r,cy-r,cx+r,cy+r),(v,v+4,v-2))
text(cx,cy-4,'PERPETUA',12,(106,119,107),True,'mm')
text(cx,cy+13,'P M – 1',6.5,(143,153,141),False,'mm')
# Knob, green running indicator, and product plate.
ellipse((509,712,568,747),(155,165,153)); ellipse((511,707,566,739),(244,245,236))
ellipse((516,709,562,733),(220,225,213)); line([(539,711),(539,719)],(110,122,108),2)
l=layer(); ellipse((581,723,595,737),(116,235,122,70),l); paste(l.filter(ImageFilter.GaussianBlur(5*S)))
ellipse((584,725,592,733),(64,136,66)); ellipse((586,726,590,730),(185,255,162))
rounded((614,716,795,756),4,(185,194,183))
text(704,729,'PM-1 · PERPETUAL DESK FAN',8.1,(66,80,67),True,'mm')
text(704,744,'INPUT: ITSELF',9,(76,90,75),False,'mm')
# The self-connected cable: leaves the rear right and comes home to its front port.
path=bezier((808,747),(902,745),(951,847),(855,875))
path+=bezier((855,875),(747,909),(484,902),(512,850))[1:]
path+=bezier((512,850),(530,815),(600,844),(649,808))[1:]
l=layer(); line([(x,y+7) for x,y in path],(43,44,38,60),11,l); paste(l.filter(ImageFilter.GaussianBlur(5*S)))
line(path,(43,48,44),10); line([(x-1,y-1.7) for x,y in path],(91,98,89),2)
# Recess and inserted USB-A connector, metal still visible around the shoulder.
rounded((650,775,701,793),4,(129,140,128)); rounded((654,778,697,790),2,(39,48,41))
rounded((659,782,691,802),2,(161,170,159)); line([(662,784),(688,784)],(228,232,218),1)
rounded((656,792,694,815),5,(47,54,47)); line([(660,796),(689,796)],(98,106,95),1)
line([(650,809),(662,804)],(44,50,44),9)
# Enlarge the complete fan, base and connected cable by ten percent.
# Keep the studio backdrop and the accessory at their original scale.
fan = im.transform((N, N), Image.Transform.AFFINE,
                   (1 / 1.1, 0, 165 * S / 1.1,
                    0, 1 / 1.1, 73 * S / 1.1),
                   resample=Image.Resampling.BICUBIC)
im = backdrop
paste(fan)
shadow((161,763,321,807),15,66)
# Exactly one accessory: a terracotta succulent, wind combing the fan-side foliage left.
# Pot, lip, soil.
gradient_shape((176,703,303,793),lambda d:d.polygon([tuple(round(v*S) for v in p) for p in [(176,703),(303,703),(286,785),(194,785)]],fill=255),(188,112,82),(145,78,57))
ellipse((194,773,286,798),(153,84,61))
ellipse((172,691,307,722),(202,132,98)); ellipse((181,696,298,716),(91,75,53))
# Succulent leaves have curved edges, central veins, and a lit upper surface.
def leaf(start,end,width,col):
    x,y=start; ex,ey=end; dx,dy=ex-x,ey-y; length=math.hypot(dx,dy); nx,ny=-dy/length,dx/length
    a=bezier(start,(x+dx*.1+nx*width,y+dy*.1+ny*width),(ex+nx*width*.5,ey+ny*width*.5),end,25)
    a+=bezier(end,(ex-nx*width*.4,ey-ny*width*.4),(x+dx*.3-nx*width,y+dy*.3-ny*width),start,25)
    ImageDraw.Draw(im).polygon([(round(a*S),round(b*S)) for a,b in a],fill=col)
    line(bezier(start,(x+dx*.3,y+dy*.3),(ex+7,ey+8),end,25),(col[0]+19,col[1]+16,col[2]+13),1)
for start,end,w,c in [((241,706),(170,641),16,(96,125,91)),((241,706),(198,604),18,(107,139,99)),((245,705),(244,600),17,(118,147,104)),((247,706),(284,637),18,(91,126,87)),((245,706),(207,670),18,(89,123,82)),((242,706),(160,675),18,(116,144,99)),((241,706),(192,658),18,(133,157,111)),((245,706),(220,636),17,(139,165,118)),((245,707),(220,654),17,(111,146,97))]: leaf(start,end,w,c)

im=im.resize((1024,1024),Image.Resampling.LANCZOS)
out=Path(os.environ.get('ENTRY_OUT','/output/entry.png'))
out.parent.mkdir(parents=True,exist_ok=True)
im.save(out,format='PNG',optimize=True,compress_level=9)
print(f'Wrote {out} ({out.stat().st_size:,} bytes)')

if __name__ == '__main__':
    pass
