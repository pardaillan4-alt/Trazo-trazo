import cv2,numpy as np,json,os
from vec import to_svg
from furlib2 import Fur
sq=cv2.imread('sq.png'); H,W=sq.shape[:2]; O='out'; os.makedirs(O,exist_ok=True)
orig=sq.astype(np.float32)/255; L=cv2.cvtColor(sq,cv2.COLOR_BGR2GRAY).astype(np.float32)
RF=np.load('F.npy',allow_pickle=True).item(); GL=np.load('G.npy',allow_pickle=True).item(); S=np.load('S.npy',allow_pickle=True).item()
def fillc(curves,extra=None):
    m=np.zeros((H,W),np.uint8); P=np.vstack([np.asarray(c) for c in curves]+([np.array(extra,np.float32)] if extra else [])).astype(np.int32)
    cv2.fillPoly(m,[P],1); return m
cara=fillc([S['cara'][1]],[(175,200),(128,250),(118,320),(140,390)])
cuello=np.zeros((H,W),np.uint8); cv2.fillPoly(cuello,[np.array([(240,470),(350,440),(360,555),(250,560)],np.int32)],1)
manos=fillc([RF['manos'][0],RF['manos'][1][::-1]])
punos=fillc([RF['punos'][0]])|fillc([RF['punos'][1]])
piel=(cara|cuello|manos)&(1-punos)
velo=fillc([S['velo_izq'][0],S['velo_azul'][0][::-1]],[(639,1136),(0,1136)])
mant=np.zeros((H,W),np.uint8); cv2.fillPoly(mant,[np.array([(0,640),(60,600),(130,565),(170,560),(170,1136),(0,1136)],np.int32)],1); cv2.fillPoly(mant,[np.array([(639,575),(560,535),(500,470),(470,600),(470,1136),(639,1136)],np.int32)],1)
manto=(velo|mant)
pelo=fillc([S['pelo_izq'][0],S['pelo_der'][0][::-1]])&(1-piel)
tun=np.zeros((H,W),np.uint8); cv2.fillPoly(tun,[np.array([(205,560),(470,560),(475,1136),(130,1136),(170,900),(212,800)],np.int32)],1)
tunica=tun&(1-piel)&(1-punos)&(1-pelo)
manto=manto&(1-piel)&(1-punos)&(1-pelo)&(1-tunica)
rayos=(1-np.clip(piel+punos+pelo+tunica+manto,0,1)).astype(np.uint8)
REG={'cara y manos':piel,'cabello':pelo,'tunica':(tunica|punos).astype(np.uint8),'manto':manto,'rayos':rayos}
for k in REG: REG[k]=REG[k].astype(np.float32)
dog=cv2.GaussianBlur(L,(0,0),2.5)-cv2.GaussianBlur(L,(0,0),0.8)
LM=np.clip((dog-4)/16,0,1)*np.clip((235-L)/60,0,1)
d=np.clip((250-cv2.GaussianBlur(L,(0,0),1.0))/250,0,1)
paper=np.ones((H,W,3),np.float32)*np.array([0.965,0.975,0.98],np.float32)
GR=np.array([0.20,0.19,0.19],np.float32); CO=np.array([0.25,0.38,0.95],np.float32); Z=np.zeros((H,W),np.float32)
def save(img,name): cv2.imwrite(f'{O}/{name}.png',(np.clip(img,0,1)*255).astype(np.uint8))
def ssl(segs,th=3,val=.5,closed=False):
    big=np.zeros((H*4,W*4),np.uint8)
    for s in segs: cv2.polylines(big,[(np.asarray(s)*4).astype(np.int32)],closed,255,th,cv2.LINE_AA)
    return np.clip(cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255*1.4,0,1)*val
def oval(c,a,b,ang=0,t0=0,t1=2*np.pi):
    ca,sa=np.cos(np.radians(ang)),np.sin(np.radians(ang)); t=np.linspace(t0,t1,80)
    return np.stack([c[0]+a*np.cos(t)*ca-b*np.sin(t)*sa,c[1]+a*np.cos(t)*sa+b*np.sin(t)*ca],1)
G=[oval((238,345),118,150,-12),np.array([(268,200),(222,495)]),np.array([(130,330),(345,300)]),np.array([(170,420),(330,395)]),
   oval((300,840),70,140,-8),oval((290,330),205,270,-8,np.pi,2*np.pi),np.array([(110,420),(100,1130)]),np.array([(470,520),(530,1130)])]
guide=ssl(G,3,.45); i=1; VEC={}; SV={}
DONE=np.zeros((H,W),np.float32)
def mixlines(lm,new=None):
    o=paper*(1-guide[:,:,None])+GR*guide[:,:,None]
    o=o*(1-0.6*DONE[:,:,None])+GR*0.6*DONE[:,:,None]
    o=o*(1-lm[:,:,None])+orig*lm[:,:,None]
    if new is not None: o=o*(1-new[:,:,None])+CO*new[:,:,None]*0.9+o*0.1*new[:,:,None]
    return o
F=Fur(L,(L<250).astype(np.uint8))
acc=Z.copy(); save(mixlines(acc),'1'); save(mixlines(acc),'1g'); prev=mixlines(acc)
def hand_step(name,keys,closed=False):
    global i,acc,prev,DONE
    i+=1; segs=[np.asarray(q,np.float32) for k in keys for q in GL.get(k,[])]
    ln=ssl(segs,5,1.0); VEC[i]=to_svg(segs,400/W)
    save(mixlines(acc,ln),str(i)); DONE=np.maximum(DONE,ssl(segs,3,1.0))
    save(mixlines(acc),f'{i}g'); prev=mixlines(acc); print(i,name,len(VEC[i]))
hand_step('contorno de la cara',['contorno de la cara'])
hand_step('ojos y cejas',['ojos y cejas'])
hand_step('nariz y boca',['nariz y boca'])
hand_step('cabello',['cabello'])
hand_step('cuello y broche',['cuello y broche'])
hand_step('velo y manto',['velo y manto'])
hand_step('manos',['manos'])
hand_step('tunica',['tunica'])
hand_step('estrellas',['estrellas'])
hand_step('rayos',['rayos'])
NL=i; guide=Z.copy(); hbase=mixlines(acc); save(hbase,f'{NL}h'); prev=hbase.copy()
nz=cv2.GaussianBlur(np.random.default_rng(7).random((H,W)).astype(np.float32),(0,0),6); nz=(nz-nz.min())/(nz.max()-nz.min())
acc_t=Z.copy()
def show(src):
    a=acc_t[:,:,None]; return hbase*(1-a)+src*a
def tstep(name):
    global i,prev
    i+=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=10,sc=400/W); prev=img; print(i,name,len(SV[i]))
for part in REG:
    reg=cv2.GaussianBlur(cv2.dilate(REG[part],np.ones((7,7),np.uint8)),(0,0),3 if part in('cara y manos','cabello') else 10)
    soft=np.clip((reg-0.5+0.35*(nz-0.5))*2.5+0.5,0,1)
    for bnd in [0.6,0.35,0.0]:
        acc_t=np.maximum(acc_t,soft*np.clip((d-bnd)/0.06,0,1)); tstep(f'{part} {bnd}')
i+=1; acc_t[:]=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=8,sc=400/W); print(i,'final',len(SV[i]))
json.dump({'vec':{str(k):v for k,v in VEC.items()},'svec':{str(k):v for k,v in SV.items()},'nl':NL,'n':i},open('gua3_v.json','w'),separators=(',',':'))
print('total',i,os.path.getsize('gua3_v.json')//1024,'KB')
