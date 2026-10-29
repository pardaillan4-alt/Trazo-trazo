import cv2,numpy as np,sys; sys.path.insert(0,'..')
from facelib import crm
exec(open('persona.py').read().split("X={}")[0])
exec("dk="+open('persona.py').read().split("\ndk=")[1].split("face=np.zeros")[0])
RF=np.load('rostro_final.npy',allow_pickle=True).item(); X=np.load('persona.npy',allow_pickle=True).item()
def curl(a,b,outer,k=0.25,n=10):
    a=np.array(a,np.float32); b=np.array(b,np.float32); d=b-a; Lh=np.linalg.norm(d); nn=np.array([d[1],-d[0]])/Lh; nn*=np.sign(nn[0]*outer+1e-9)
    ts=np.linspace(0,1,n); return a+np.outer(ts,d)+np.outer(k*Lh*ts**2,nn)
# ---- ojo izquierdo medido ----
box=lambda c,x0,y0,x1,y1:(np.asarray(c)[:,0].mean()>x0)&(np.asarray(c)[:,0].mean()<x1)&(np.asarray(c)[:,1].mean()>y0)&(np.asarray(c)[:,1].mean()<y1)
for k in ['ojo','iris','pupila','parpado','pestanas','ceja']:
    RF[k]=[c for c in RF.get(k,[]) if not box(c,455,335,560,420)]
up=crm([(477,387),(485,381),(495,377),(505,375),(515,376),(525,380),(533,386),(540,393),(543,398)]); lo=crm([(477,387),(487,395),(497,402),(508,407),(520,408),(530,405),(538,401),(543,398)])
RF['ojo']+= [up,lo]
t=np.linspace(0,2*np.pi,90); polyE=np.vstack([up,lo[::-1]]).astype(np.float32)
def clip(c):
    ins=np.array([cv2.pointPolygonTest(polyE,tuple(map(float,p)),True)>-0.3 for p in c]); out=[]; k=np.argmin(ins); ins=np.roll(ins,-k); c=np.roll(c,-k,0); i=0
    while i<len(c):
        if ins[i]:
            j=i
            while j<len(c) and ins[j]: j+=1
            if j-i>4: out.append(c[i:j])
            i=j
        else: i+=1
    return out
RF['iris']+=clip(np.array([510,392])+14*np.stack([np.cos(t),np.sin(t)],1))
RF['pupila']+=[np.array([510,392])+5*np.stack([np.cos(t),np.sin(t)],1)]
RF['parpado']+=[crm([(488,371),(503,368),(518,369),(531,373),(541,381)])]
RF['pestanas']+=[curl((479,385),(471,380),-1),curl((482,382),(475,375),-1),curl((488,379),(483,371),-1),curl((496,377),(493,369),-1,0.18)]
top=crm([(478,348),(495,344),(515,345),(535,352),(548,362)]); bot=crm([(480,358),(498,355),(518,357),(535,363),(546,370)])
def rs(c,n): s=np.r_[0,np.cumsum(np.hypot(*np.diff(c,axis=0).T))]; tt=np.linspace(0,s[-1],n); return np.stack([np.interp(tt,s,c[:,0]),np.interp(tt,s,c[:,1])],1)
T_,B_=rs(top,16)[:15],rs(bot,16)[:15]
for i,(a,b) in enumerate(zip(B_,T_)):
    fr=i/15; tip=a+(b-a)*0.95+np.array([3+4*fr,0])     # los pelos se acuestan hacia la orilla (derecha)
    RF['ceja'].append(curl(tuple(a),tuple(tip),1,0.12,8))
# ---- cabello: fuera los mechones que cruzan el ojo; arriba, el borde de la cabeza junto al árbol ----
X['cabello']=[p for p in X['cabello'] if not (((p[:,0]>468)&(p[:,0]<550)&(p[:,1]>340)&(p[:,1]<415)).mean()>0.1)]
X['cabello']+=[crm([(540,135),(520,150),(505,168),(495,185),(482,200),(468,220),(456,240),(448,260),(444,280),(441,300),(440,320),(440,340),(436,360)])]
reg=np.zeros((H,W),np.uint8); cv2.fillPoly(reg,[np.array([(540,130),(480,200),(440,260),(430,380),(470,380),(475,300),(500,262),(560,230),(600,180)],np.int32)],1)
X['cabello']+=fur(reg,18,120,55,12)
# ---- dedo ----
X['manos']=[p for p in X['manos'] if not (((p[:,0]>485)&(p[:,0]<575)&(p[:,1]>600)&(p[:,1]<648)).mean()>0.5)]
X['manos']+=[crm([(568,640),(545,628),(525,616),(510,609),(500,608),(494,612),(493,620),(497,630),(505,643)])]
np.save('rostro_final.npy',np.array(RF,dtype=object)); np.save('persona.npy',np.array(X,dtype=object))
print({k:len(v) for k,v in X.items()})
