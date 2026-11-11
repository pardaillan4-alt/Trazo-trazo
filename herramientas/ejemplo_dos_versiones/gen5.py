import cv2,numpy as np,json,os,sys
from vec import to_svg
from furlib2 import Fur
SRC,OUT,TAG=sys.argv[1],sys.argv[2],sys.argv[3]
cfg=json.load(open('cfg.json')); H=cfg['H']; W=900
sq=cv2.resize(cv2.imread(SRC),(W,H),interpolation=cv2.INTER_AREA); O='out_'+TAG; os.system(f'rm -rf {O}'); os.makedirs(O)
orig=sq.astype(np.float32)/255; L=cv2.cvtColor(sq,cv2.COLOR_BGR2GRAY).astype(np.float32)
GL=np.load('G.npy',allow_pickle=True).item(); GWD=np.load('GW.npy',allow_pickle=True).item()
def mk(sh):
    m=np.zeros((H,W),np.uint8)
    if sh[0]=='p': cv2.fillPoly(m,[np.array(sh[1],np.int32)],1)
    else: cv2.ellipse(m,tuple(sh[1]),tuple(sh[2]),0,0,360,1,-1)
    return m
Z_={k:np.clip(sum(mk(s) for s in v),0,1) for k,v in cfg['zonas'].items()}
head=np.clip(Z_['cabeza y orejas']+Z_['ojos']+Z_['nariz y boca'],0,1)
# silueta del animal: relleno de las líneas del animal
anim=np.zeros((H,W),np.uint8)
for k in cfg['pasos']:
    if k==cfg.get('fondo'): continue
    for p in GL.get(k,[]): cv2.polylines(anim,[np.round(p).astype(np.int32)],False,1,9)
anim=cv2.morphologyEx(anim,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41)))
cs,_=cv2.findContours(anim,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea); anim=np.zeros((H,W),np.uint8); cv2.drawContours(anim,[c],-1,1,-1)
head=head&anim
body=(anim&(1-head)).astype(np.uint8); headm=(anim&head).astype(np.uint8)
REG=[('cabeza',headm,[0.6,0.35,0.0]),('cuerpo',body,[0.6,0.35,0.0])]
if cfg.get('fondo'): REG.append(('fondo',(1-anim).astype(np.uint8),[0.5,0.25,0.0]))
else: REG.append(('fondo',(1-anim).astype(np.uint8),[0.0]))
d=np.clip((250-cv2.GaussianBlur(L,(0,0),1.0))/250,0,1)
paper=np.ones((H,W,3),np.float32)*np.array([0.965,0.975,0.98],np.float32)
GR=np.array([0.20,0.19,0.19],np.float32); RED=np.array([0.25,0.37,0.95],np.float32); Zr=np.zeros((H,W),np.float32)
def save(img,name): cv2.imwrite(f'{O}/{name}.png',(np.clip(img,0,1)*255).astype(np.uint8))
def ssl(segs,th=3,val=.5):
    big=np.zeros((H*4,W*4),np.uint8)
    for q in segs: cv2.polylines(big,[(np.asarray(q)*4).astype(np.int32)],False,255,th,cv2.LINE_AA)
    return np.clip(cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255*1.4,0,1)*val
def ell(m):
    cs,_=cv2.findContours(m.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)
    (cx,cy),(a,b),ang=cv2.fitEllipse(c); t=np.linspace(0,2*np.pi,90); ca,sa=np.cos(np.radians(ang)),np.sin(np.radians(ang)); a/=2;b/=2
    return np.stack([cx+a*np.cos(t)*ca-b*np.sin(t)*sa,cy+a*np.cos(t)*sa+b*np.sin(t)*ca],1)
G=[ell(headm),ell(body)]
hm=headm; ys,xs=np.nonzero(hm); cx=xs.mean(); e=Z_['ojos']; ey,ex=np.nonzero(e)
G.append(np.array([(xs.min()+10,ey.mean()),(xs.max()-10,ey.mean())])); G.append(np.array([(cx,ys.min()+10),(cx,ys.max()-10)]))
guide=ssl(G,3,.45); i=1; VEC={}; SV={}
lin=cv2.resize(cv2.imread('gris_big.png',0),(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)
INK=np.clip((cfg['th']-lin)/60,0,1)
STEPS=cfg['pasos']; dist=[]
for k in STEPS:
    r=np.full((H,W),255,np.uint8)
    for p in GL.get(k,[]): cv2.polylines(r,[np.round(p).astype(np.int32)],False,0,1)
    dist.append(cv2.distanceTransform(r,cv2.DIST_L2,3))
lab=np.argmin(np.stack(dist),0); near=np.min(np.stack(dist),0)<6; DONE=Zr.copy()
def base():
    o=paper*(1-guide[:,:,None])+GR*guide[:,:,None]; return o*(1-DONE[:,:,None])+GR*DONE[:,:,None]
F=Fur(L,(L<250).astype(np.uint8)); save(base(),'1'); save(base(),'1g')
for si,k in enumerate(STEPS):
    i+=1; segs=[np.asarray(q,np.float32) for q in GL.get(k,[])]
    VEC[i]=[v+[w] for v,w in zip(to_svg(segs,400/W),GWD.get(k,[]))]
    m=INK*(lab==si)*near; o=base(); save(o*(1-m[:,:,None])+RED*m[:,:,None],str(i)); DONE=np.maximum(DONE,m*0.85); save(base(),f'{i}g')
NL=i; guide=Zr.copy(); hbase=base(); save(hbase,f'{NL}h'); prev=hbase.copy(); acc=Zr.copy()
nz=cv2.GaussianBlur(np.random.default_rng(7).random((H,W)).astype(np.float32),(0,0),6); nz=(nz-nz.min())/(nz.max()-nz.min())
def show(src): a=acc[:,:,None]; return hbase*(1-a)+src*a
def tstep():
    global i,prev
    i+=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=10,sc=400/W); prev=img
for nm,m,bands in REG:
    reg=cv2.GaussianBlur(cv2.dilate(m.astype(np.float32),np.ones((7,7),np.uint8)),(0,0),3)
    soft=np.clip((reg-0.5+0.25*(nz-0.5))*3+0.5,0,1)
    for b in bands: acc=np.maximum(acc,soft*np.clip((d-b)/0.06,0,1) if b>0 else soft); tstep()
i+=1; acc[:]=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=8,sc=400/W)
json.dump({'vec':{str(k):v for k,v in VEC.items()},'svec':{str(k):v for k,v in SV.items()},'nl':NL,'n':i},open(f'{TAG}_v.json','w'),separators=(',',':'))
ims=[cv2.resize(cv2.imread(f'{O}/{j}.png'),(200,int(200*H/W))) for j in range(1,i+1)]
while len(ims)%8: ims.append(np.full_like(ims[0],255))
cv2.imwrite(f'pasos_{TAG}.jpg',np.vstack([np.hstack(ims[r*8:(r+1)*8]) for r in range(len(ims)//8)])); print(TAG,'pasos',i,'lineas',NL)
