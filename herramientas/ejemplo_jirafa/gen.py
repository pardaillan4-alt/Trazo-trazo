import cv2,numpy as np,json,os
from vec import to_svg
from furlib2 import Fur
sq=cv2.imread('color.png'); H,W=sq.shape[:2]; O='out'; os.system('rm -rf out'); os.makedirs(O,exist_ok=True)
orig=sq.astype(np.float32)/255; L=cv2.cvtColor(sq,cv2.COLOR_BGR2GRAY).astype(np.float32)
GL=np.load('G.npy',allow_pickle=True).item(); GWD=np.load('GW.npy',allow_pickle=True).item(); REG=np.load('REG.npy',allow_pickle=True).item()
REG={k:v.astype(np.float32) for k,v in REG.items()}
d=np.clip((250-cv2.GaussianBlur(L,(0,0),1.0))/250,0,1)
paper=np.ones((H,W,3),np.float32)*np.array([0.965,0.975,0.98],np.float32)
GR=np.array([0.20,0.19,0.19],np.float32); RED=np.array([0.25,0.37,0.95],np.float32); Z=np.zeros((H,W),np.float32)
def save(img,name): cv2.imwrite(f'{O}/{name}.png',(np.clip(img,0,1)*255).astype(np.uint8))
def ssl(segs,th=3,val=.5):
    big=np.zeros((H*4,W*4),np.uint8)
    for q in segs: cv2.polylines(big,[(np.asarray(q)*4).astype(np.int32)],False,255,th,cv2.LINE_AA)
    return np.clip(cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255*1.4,0,1)*val
def oval(c,a,b,ang=0):
    ca,sa=np.cos(np.radians(ang)),np.sin(np.radians(ang)); t=np.linspace(0,2*np.pi,80)
    return np.stack([c[0]+a*np.cos(t)*ca-b*np.sin(t)*sa,c[1]+a*np.cos(t)*sa+b*np.sin(t)*ca],1)
G=[oval((430,330),175,170),oval((680,450),95,90),np.array([(250,90),(330,250)]),np.array([(385,40),(400,180)]),
   np.array([(270,520),(275,700),(330,900)]),np.array([(415,525),(450,700),(540,900)])]
guide=ssl(G,3,.45); i=1; VEC={}; SV={}
lineas=cv2.imread('lineas.png',0).astype(np.float32)/255
INK=np.clip((0.92-lineas)/0.6,0,1)
STEPS=['contorno de la cabeza','ojo','hocico','manchas de la cara','contorno del cuello','manchas del cuello']
dist=[]
for k in STEPS:
    r=np.full((H,W),255,np.uint8)
    for p in GL.get(k,[]): cv2.polylines(r,[np.round(p).astype(np.int32)],False,0,1)
    dist.append(cv2.distanceTransform(r,cv2.DIST_L2,3))
lab=np.argmin(np.stack(dist),0); DONE=Z.copy()
def base():
    o=paper*(1-guide[:,:,None])+GR*guide[:,:,None]
    return o*(1-DONE[:,:,None])+GR*DONE[:,:,None]
F=Fur(L,(L<250).astype(np.uint8))
save(base(),'1'); save(base(),'1g')
for si,k in enumerate(STEPS):
    i+=1; segs=[np.asarray(q,np.float32) for q in GL.get(k,[])]
    VEC[i]=[v+[w] for v,w in zip(to_svg(segs,400/W),GWD.get(k,[]))]
    m=INK*(lab==si); o=base(); save(o*(1-m[:,:,None])+RED*m[:,:,None],str(i)); DONE=np.maximum(DONE,m*0.85); save(base(),f'{i}g'); print(i,k,len(VEC[i]))
NL=i; guide=Z.copy(); hbase=base(); save(hbase,f'{NL}h'); prev=hbase.copy(); acc_t=Z.copy()
nz=cv2.GaussianBlur(np.random.default_rng(7).random((H,W)).astype(np.float32),(0,0),6); nz=(nz-nz.min())/(nz.max()-nz.min())
def show(src):
    a=acc_t[:,:,None]; o=hbase*(1-a)+src*a
    return o*(1-0.6*DONE[:,:,None]*a)+GR*0.6*DONE[:,:,None]*a     # las líneas del dibujo quedan encima del color
def tstep(name):
    global i,prev
    i+=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=10,sc=400/W); prev=img; print(i,name,len(SV[i]))
for part,bands in [('cabeza',[0.6,0.35,0.0]),('cuello',[0.6,0.35,0.0]),('cielo',[0.4,0.0])]:
    reg=cv2.GaussianBlur(cv2.dilate(REG[part],np.ones((5,5),np.uint8)),(0,0),2 if part!='cielo' else 3)
    soft=np.clip((reg-0.5+0.2*(nz-0.5))*3+0.5,0,1)
    for bnd in bands:
        acc_t=np.maximum(acc_t,soft*np.clip((d-bnd)/0.06,0,1) if bnd>0 else soft); tstep(f'{part} {bnd}')
i+=1; acc_t[:]=1; DONE[:]=0; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=8,sc=400/W)
json.dump({'vec':{str(k):v for k,v in VEC.items()},'svec':{str(k):v for k,v in SV.items()},'nl':NL,'n':i},open('jirafa_v.json','w'),separators=(',',':'))
print('total',i)
