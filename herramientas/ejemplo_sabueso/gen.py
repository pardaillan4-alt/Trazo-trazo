import cv2,numpy as np,json,os
from vec import to_svg
from furlib2 import Fur
H,W=900,900; O='out'; os.makedirs(O,exist_ok=True)
sq=cv2.imread('sq.png'); orig=sq.astype(np.float32)/255*np.array([0.965,0.975,0.98],np.float32)
L=cv2.cvtColor(sq,cv2.COLOR_BGR2GRAY).astype(np.float32)
RF=np.load('perro_final.npy',allow_pickle=True).item()
P={k:v for k,v in json.load(open('../foto/dib/perro.json'))['parts']}
def pm(name,grow=0):
    m=np.zeros((H,W),np.uint8)
    for sh in P[name]:
        if sh[0]=='p': cv2.fillPoly(m,[np.array(sh[1],np.int32)],1)
        if sh[0]=='e': cv2.ellipse(m,(sh[1],sh[2]),(sh[3],sh[4]),sh[5],0,360,1,-1)
    return cv2.dilate(m,np.ones((grow*2+1,)*2,np.uint8)) if grow else m
b=cv2.GaussianBlur(L,(0,0),3); SIL=(b<240).astype(np.uint8); SIL=cv2.morphologyEx(SIL,cv2.MORPH_CLOSE,np.ones((31,31),np.uint8))
n_,lab_,st_,_=cv2.connectedComponentsWithStats(SIL); SIL=(lab_==1+np.argmax(st_[1:,4])).astype(np.uint8)
EAR=np.zeros((H,W),np.uint8); cv2.fillPoly(EAR,[np.round(RF['oreja'][0]).astype(np.int32)],1)
for c in RF['oreja_fondo']: cv2.fillPoly(EAR,[np.round(c).astype(np.int32)],1)
CAB=np.clip(pm('cabeza')+pm('hocico')+pm('nariz')+pm('ojo')+pm('barbilla'),0,1)*(1-EAR)
CUE=pm('cuello')*(1-EAR)*(1-CAB); PEC=np.clip(SIL.astype(int)-EAR-CAB-CUE,0,1).astype(np.uint8)
REG={'cabeza':CAB,'oreja':EAR,'cuello':CUE,'pecho':PEC}
for k in REG: REG[k]=(REG[k]*cv2.dilate(SIL,np.ones((9,9),np.uint8))).astype(np.float32)
pers=np.clip(sum(REG.values()),0,1)
dog=cv2.GaussianBlur(L,(0,0),2.5)-cv2.GaussianBlur(L,(0,0),0.8)
LM=np.clip((dog-4)/16,0,1)*np.clip((235-L)/60,0,1)
d=np.clip((240-cv2.GaussianBlur(L,(0,0),1.0))/240,0,1)
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
# paso 1: guías (círculo de la cabeza, círculo del hocico, óvalo de la oreja, cuello y pecho)
G=[oval((455,250),160,160),oval((715,305),78,72),oval((372,265),120,170,-22),np.array([(250,420),(175,600),(120,890)]),np.array([(520,440),(540,600),(600,890)])]
guide=ssl(G,3,.45); i=1; VEC={}; SV={}
DONE=np.zeros((H,W),np.float32)      # líneas ya dibujadas: quedan como trazo de lápiz
def mixlines(lm,new=None):
    o=paper*(1-guide[:,:,None])+GR*guide[:,:,None]
    o=o*(1-0.6*DONE[:,:,None])+GR*0.6*DONE[:,:,None]
    o=o*(1-lm[:,:,None])+orig*lm[:,:,None]
    if new is not None: o=o*(1-new[:,:,None])+CO*new[:,:,None]*0.9+o*0.1*new[:,:,None]
    return o
F=Fur(L,(L<250).astype(np.uint8))
acc=Z.copy(); save(mixlines(acc),'1'); save(mixlines(acc),'1g'); prev=mixlines(acc)
def hand_step(name,keys,reveal=None,th=5):
    """Paso a mano: líneas limpias medidas sobre el dibujo; debajo aparecen solo los trazos reales de esa parte."""
    global i,acc,prev,DONE
    i+=1; segs=[np.asarray(q,np.float32) for k in keys for q in RF.get(k,[])]
    ln=ssl(segs,th,1.0); VEC[i]=to_svg(segs,400/W)
    save(mixlines(acc,ln),str(i))
    rv=cv2.dilate((ln>0.05).astype(np.uint8),np.ones((9,9),np.uint8)) if reveal is None else cv2.dilate(reveal.astype(np.uint8),np.ones((5,5),np.uint8))
    acc=np.maximum(acc,LM*rv); DONE=np.maximum(DONE,ssl(segs,3,1.0))
    save(mixlines(acc),f'{i}g'); prev=mixlines(acc); print(i,name,len(VEC[i]))
hand_step('contorno de la cabeza',['sil_cabeza','sil_oreja'])
hand_step('ojo',['ojo','iris','pupila'],pm('ojo',10))
hand_step('nariz',['nariz','orificio'],pm('nariz',8))
hand_step('contorno del hocico',['sil_hocico','sil_nariz','sil_barbilla','boca'])
hand_step('detalles de la cara',['bigotes','pelo_hocico','pelo_cabeza'],REG['cabeza'])
hand_step('contorno de la oreja',['oreja','oreja_fondo'])
hand_step('pelo de la oreja',['pelo_oreja'],REG['oreja'])
hand_step('cuello',['sil_cuello','pelo_cuello'],REG['cuello'])
hand_step('pecho',['sil_pecho','manchas'],REG['pecho'])
NL=i; guide=Z.copy(); hbase=mixlines(acc); save(hbase,f'{NL}h'); prev=hbase.copy()
# ---------- sombreado: por partes, de lo oscuro a lo claro ----------
Lb=cv2.GaussianBlur(L,(0,0),6)
hl=np.clip((L-Lb-8)/25,0,1)*(L>190)*cv2.GaussianBlur(pers,(0,0),3)
onh=orig*(1-hl[:,:,None]*0.8)+cv2.GaussianBlur(orig,(0,0),5)*hl[:,:,None]*0.8
nz=cv2.GaussianBlur(np.random.default_rng(7).random((H,W)).astype(np.float32),(0,0),6); nz=(nz-nz.min())/(nz.max()-nz.min())
acc_t=Z.copy(); base=Z.copy()
def show(src):
    b=base[:,:,None]; o=hbase*(1-b)+(hbase*0.55+GR*0.45)*b
    a=acc_t[:,:,None]; return o*(1-a)+src*a
def tstep(name):
    global i,prev
    i+=1; img=show(onh); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=10,sc=400/W); prev=img; print(i,name,len(SV[i]))
for part in ['cabeza','oreja','cuello','pecho']:
    reg=cv2.GaussianBlur(cv2.dilate(REG[part],np.ones((7,7),np.uint8)),(0,0),3 if part in('cabeza','oreja') else 16)
    soft=np.clip((reg-0.5+0.35*(nz-0.5))*2.5+0.5,0,1)
    for bnd in [0.45,0.2,0.0]:
        acc_t=np.maximum(acc_t,soft*np.clip((d-bnd)/0.06,0,1)); tstep(f'{part} {bnd}')
i+=1; acc_t[:]=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=8,sc=400/W); print(i,'final',len(SV[i]))
json.dump({'vec':{str(k):v for k,v in VEC.items()},'svec':{str(k):v for k,v in SV.items()},'nl':NL,'n':i},open('perro_v.json','w'),separators=(',',':'))
print('total',i,os.path.getsize('perro_v.json')//1024,'KB')
