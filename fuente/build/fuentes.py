"""Fuentes OFL incrustadas (subconjunto latino, WOFF) para que la app se vea igual sin internet."""
import base64,os
from fontTools import subset
F='/mnt/skills/examples/canvas-design/canvas-fonts/'
U=list(range(0x20,0x7f))+list(range(0xa0,0x100))+[0x152,0x153,0x2013,0x2014,0x2018,0x2019,0x201c,0x201d,0x2022,0x2026,0x20ac,0x2122,0x2190,0x2191,0x2192,0x2193,0xd7]
FACES=[('Bricolage Grotesque','BricolageGrotesque-Bold.ttf',700),('Outfit','Outfit-Regular.ttf',400),('Outfit','Outfit-Bold.ttf',700),('Nothing You Could Do','NothingYouCouldDo-Regular.ttf',400)]
css=[]
for fam,fn,w in FACES:
    o=subset.Options(); o.flavor='woff'; o.layout_features=['kern','liga','calt','ccmp','locl','mark','mkmk']; o.notdef_outline=True
    f=subset.load_font(F+fn,o); s=subset.Subsetter(o); s.populate(unicodes=U); s.subset(f)
    out=f'fuentes/{fn[:-4]}.woff'; subset.save_font(f,out,o)
    b=base64.b64encode(open(out,'rb').read()).decode()
    css.append(f"@font-face{{font-family:'{fam}';src:url(data:font/woff;base64,{b}) format('woff');font-weight:{w};font-style:normal;font-display:swap}}")
    print(fn,os.path.getsize(out)//1024,'KB')
open('fuentes.css','w').write('\n'.join(css)+'\n')
