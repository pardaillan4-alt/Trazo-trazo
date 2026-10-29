import cv2,numpy as np,json,os
from vec import to_svg
from furlib2 import Fur
sq=cv2.imread('sq.png'); H,W=sq.shape[:2]; O='out'; os.makedirs(O,exist_ok=True)
orig=sq.astype(np.float32)/255; L=cv2.cvtColor(sq,cv2.COLOR_BGR2GRAY).astype(np.float32)
RF=np.load('P.npy',allow_pickle=True).item()
hsv=cv2.cvtColor(cv2.GaussianBlur(sq,(0,0),1.5),cv2.COLOR_BGR2HSV); h,s,v=[hsv[:,:,i].astype(int) for i in range(3)]
def fill(keys):
    m=np.zeros((H,W),np.uint8)
    for k in keys:
        for p in RF[k]:
            if np.allclose(p[0],p[-1]) or len(p)>40: cv2.fillPoly(m,[np.round(p).astype(np.int32)],1)
    return m
fig=np.zeros((H,W),np.uint8)
dark=(v<80).astype(np.uint8); n,lab,st,_=cv2.connectedComponentsWithStats(dark); hat=(lab==1+np.argmax(st[1:,4])).astype(np.uint8)
hat=cv2.morphologyEx(hat,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
red=cv2.morphologyEx((((h<8)|(h>168))&(s>110)&(v>110)).astype(np.uint8),cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
pink=cv2.morphologyEx(((((h>145)|(h<8))&(s>25)&(s<=110)&(v>140))|((s<40)&(v>150))).astype(np.uint8),cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
esp=fill(['espadas'])
bg=((h>80)&(h<110)&(s>60)).astype(np.uint8)
cuerpo=(pink&(1-red)&(1-hat)&(1-esp)&(1-bg)).astype(np.uint8)
REG={'sombrero':hat&(1-red),'espadas':esp,'panuelo':red,'pulpo':cuerpo}
REG['fondo']=(1-np.clip(sum(REG.values()),0,1)).astype(np.uint8)
for k in REG: REG[k]=REG[k].astype(np.float32)
d=np.clip((250-cv2.GaussianBlur(L,(0,0),1.0))/250,0,1)
paper=np.ones((H,W,3),np.float32)*np.array([0.965,0.975,0.98],np.float32)
GR=np.array([0.20,0.19,0.19],np.float32); CO=np.array([0.25,0.38,0.95],np.float32); Z=np.zeros((H,W),np.float32)
def save(img,name): cv2.imwrite(f'{O}/{name}.png',(np.clip(img,0,1)*255).astype(np.uint8))
def ssl(segs,th=3,val=.5,closed=False):
    big=np.zeros((H*4,W*4),np.uint8)
    for q in segs: cv2.polylines(big,[(np.asarray(q)*4).astype(np.int32)],closed,255,th,cv2.LINE_AA)
    return np.clip(cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255*1.4,0,1)*val
def oval(c,a,b,ang=0,t0=0,t1=2*np.pi):
    ca,sa=np.cos(np.radians(ang)),np.sin(np.radians(ang)); t=np.linspace(t0,t1,80)
    return np.stack([c[0]+a*np.cos(t)*ca-b*np.sin(t)*sa,c[1]+a*np.cos(t)*sa+b*np.sin(t)*ca],1)
G=[oval((345,580),150,130),oval((330,300),300,200),np.array([(70,800),(345,560),(650,800)]),np.array([(80,130),(200,260)]),np.array([(720,130),(600,260)])]
guide=ssl(G,3,.45); i=1; VEC={}; SV={}; DONE=np.zeros((H,W),np.float32)
def mixlines(new=None):
    o=paper*(1-guide[:,:,None])+GR*guide[:,:,None]
    o=o*(1-0.75*DONE[:,:,None])+GR*0.75*DONE[:,:,None]
    if new is not None: o=o*(1-new[:,:,None])+CO*new[:,:,None]*0.9+o*0.1*new[:,:,None]
    return o
F=Fur(L,(L<250).astype(np.uint8))
save(mixlines(),'1'); save(mixlines(),'1g'); prev=mixlines()
def hand_step(name,keys):
    global i,prev,DONE
    i+=1; segs=[np.asarray(q,np.float32) for k in keys for q in RF.get(k,[])]
    ln=ssl(segs,5,1.0); VEC[i]=to_svg(segs,400/W)
    save(mixlines(ln),str(i)); DONE=np.maximum(DONE,ssl(segs,4,1.0))
    save(mixlines(),f'{i}g'); prev=mixlines(); print(i,name,len(VEC[i]))
for nm,ks in [('sombrero',['sombrero']),('calavera',['calavera']),('espadas',['espadas']),('panuelo',['panuelo']),('parche y ojo',['parche','ojo']),('cuerpo',['cuerpo']),('tentaculos',['tentaculos'])]: hand_step(nm,ks)
NL=i; guide=Z.copy(); hbase=mixlines(); save(hbase,f'{NL}h'); prev=hbase.copy()
acc_t=Z.copy()
nz=cv2.GaussianBlur(np.random.default_rng(7).random((H,W)).astype(np.float32),(0,0),6); nz=(nz-nz.min())/(nz.max()-nz.min())
# los contornos negros se quedan encima siempre
INK=np.clip((90-cv2.GaussianBlur(L,(0,0),0.7))/40,0,1)*np.clip(1-REG['sombrero']*0,0,1)
def show(src):
    a=acc_t[:,:,None]; o=hbase*(1-a)+src*a; return o
def tstep(name):
    global i,prev
    i+=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=10,sc=400/W); prev=img; print(i,name,len(SV[i]))
for part in REG:
    reg=cv2.GaussianBlur(cv2.dilate(REG[part],np.ones((5,5),np.uint8)),(0,0),2 if part!='fondo' else 6)
    soft=np.clip((reg-0.5+0.25*(nz-0.5))*3+0.5,0,1)
    bands=[0.6,0.0] if part in('sombrero','espadas','panuelo') else [0.6,0.3,0.0]
    for bnd in bands:
        acc_t=np.maximum(acc_t,soft*np.clip((d-bnd)/0.06,0,1) if bnd>0 else soft); tstep(f'{part} {bnd}')
i+=1; acc_t[:]=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=8,sc=400/W); print(i,'final',len(SV[i]))
json.dump({'vec':{str(k):v for k,v in VEC.items()},'svec':{str(k):v for k,v in SV.items()},'nl':NL,'n':i},open('pulpo2_v.json','w'),separators=(',',':'))
print('total',i)
