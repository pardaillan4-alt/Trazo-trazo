import cv2,numpy as np,json,os
from vec import to_svg
from furlib2 import Fur
sq=cv2.imread('color.png'); H,W=sq.shape[:2]; O='out'; os.system('rm -rf out'); os.makedirs(O,exist_ok=True)
orig=sq.astype(np.float32)/255; L=cv2.cvtColor(sq,cv2.COLOR_BGR2GRAY).astype(np.float32)
GL=np.load('G_hd.npy',allow_pickle=True).item(); GWD=np.load('GW_hd.npy',allow_pickle=True).item(); GU=np.load('guias.npy',allow_pickle=True).item(); REG=np.load('REG.npy',allow_pickle=True).item()
REG['fondo']=(1-np.clip(sum(REG.values()),0,1)).astype(np.uint8); REG={k:v.astype(np.float32) for k,v in REG.items()}
big=cv2.imread('/mnt/user-data/attachments/2a8fc66a-2bf4-5ad0-b410-99770220e857/9a03d3b5-image.png',0)
INK=np.clip((235-cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32))/180,0,1)   # tinta real, con su grosor
STEPS=['contorno de la cara','ojos y cejas','nariz y boca','barba','cabello','cuello','tunica y manto','aureola y rayos','nubes']
# cada pixel de tinta pertenece al paso cuya línea le queda más cerca
dist=[]
for k in STEPS:
    r=np.full((H,W),255,np.uint8)
    for p in GL.get(k,[]): cv2.polylines(r,[np.round(p).astype(np.int32)],False,0,1)
    dist.append(cv2.distanceTransform(r,cv2.DIST_L2,3))
lab=np.argmin(np.stack(dist),0)
d=np.clip((250-cv2.GaussianBlur(L,(0,0),1.0))/250,0,1)
paper=np.ones((H,W,3),np.float32)*np.array([0.965,0.975,0.98],np.float32)
GR=np.array([0.20,0.19,0.19],np.float32); RED=np.array([0.25,0.37,0.95],np.float32); Z=np.zeros((H,W),np.float32)
def save(img,name): cv2.imwrite(f'{O}/{name}.png',(np.clip(img,0,1)*255).astype(np.uint8))
def ssl(segs,th=3,val=.5):
    big=np.zeros((H*4,W*4),np.uint8)
    for q in segs: cv2.polylines(big,[(np.asarray(q)*4).astype(np.int32)],False,255,th,cv2.LINE_AA)
    return np.clip(cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255*1.4,0,1)*val
def oval(c,a,b,ang=0,t0=0,t1=2*np.pi):
    ca,sa=np.cos(np.radians(ang)),np.sin(np.radians(ang)); t=np.linspace(t0,t1,80)
    return np.stack([c[0]+a*np.cos(t)*ca-b*np.sin(t)*sa,c[1]+a*np.cos(t)*sa+b*np.sin(t)*ca],1)
G=GU['g1']+GU['g4']
guide=ssl(G,3,.45); i=1; VEC={}; SV={}; DONE=Z.copy()
def base():
    o=paper*(1-guide[:,:,None])+GR*guide[:,:,None]
    return o*(1-DONE[:,:,None])+GR*DONE[:,:,None]
F=Fur(L,(L<250).astype(np.uint8))
save(base(),'1'); save(base(),'1g')
i+=1; segs=GU['g2']+GU['g3']; VEC[i]=to_svg(segs,400/W); nl_=ssl(segs,4,1.0); o=base(); save(o*(1-nl_[:,:,None])+RED*nl_[:,:,None],str(i))
guide=np.maximum(guide,ssl(segs,3,.45)); save(base(),f'{i}g'); print(i,'guias de la cara')
for si,k in enumerate(STEPS):
    i+=1; segs=[np.asarray(q,np.float32) for q in GL.get(k,[])]
    VEC[i]=[v+[w] for v,w in zip(to_svg(segs,400/W),GWD.get(k,[]))]
    m=INK*(lab==si); o=base(); o=o*(1-m[:,:,None])+RED*m[:,:,None]
    save(o,str(i)); DONE=np.maximum(DONE,m*0.85); save(base(),f'{i}g'); print(i,k,len(VEC[i]))
NL=i; guide=Z.copy(); hbase=base(); save(hbase,f'{NL}h'); prev=hbase.copy(); acc_t=Z.copy()
nz=cv2.GaussianBlur(np.random.default_rng(7).random((H,W)).astype(np.float32),(0,0),6); nz=(nz-nz.min())/(nz.max()-nz.min())
def show(src): a=acc_t[:,:,None]; return hbase*(1-a)+src*a
def tstep(name):
    global i,prev
    i+=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=10,sc=400/W); prev=img; print(i,name,len(SV[i]))
for part in ['cara','cabello y barba','tunica','fondo']:
    reg=cv2.GaussianBlur(cv2.dilate(REG[part],np.ones((7,7),np.uint8)),(0,0),3 if part!='fondo' else 8)
    soft=np.clip((reg-0.5+0.3*(nz-0.5))*2.5+0.5,0,1)
    for bnd in [0.55,0.3,0.0]:
        acc_t=np.maximum(acc_t,soft*np.clip((d-bnd)/0.06,0,1)); tstep(f'{part} {bnd}')
i+=1; acc_t[:]=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=8,sc=400/W)
json.dump({'vec':{str(k):v for k,v in VEC.items()},'svec':{str(k):v for k,v in SV.items()},'nl':NL,'n':i},open('cielo3_v.json','w'),separators=(',',':'))
print('total',i,os.path.getsize('cielo3_v.json')//1024,'KB')
