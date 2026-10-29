import cv2,numpy as np,sys; sys.path.insert(0,'..')
from facelib import crm
im=cv2.imread('sq.png'); R=np.load('rostro_final.npy',allow_pickle=True).item()
inbox=lambda c,x0,y0,x1,y1:(np.asarray(c)[:,0].mean()>x0)&(np.asarray(c)[:,0].mean()<x1)&(np.asarray(c)[:,1].mean()>y0)&(np.asarray(c)[:,1].mean()<y1)
def curl(a,b,up_sign,k=0.25,n=10):
    a=np.array(a,np.float32); b=np.array(b,np.float32); d=b-a; Lh=np.linalg.norm(d); nn=np.array([d[1],-d[0]])/Lh
    if nn[1]*up_sign<0: nn=-nn
    ts=np.linspace(0,1,n); return a+np.outer(ts,d)+np.outer(k*Lh*ts**2,nn)
def rs(c,n): s=np.r_[0,np.cumsum(np.hypot(*np.diff(c,axis=0).T))]; tt=np.linspace(0,s[-1],n); return np.stack([np.interp(tt,s,c[:,0]),np.interp(tt,s,c[:,1])],1)
# ---- ojo izquierdo: la parte larga a la izquierda son pestañas, no ojo ----
for k in ['ojo','pestanas']: R[k]=[c for c in R[k] if not inbox(c,455,360,560,420)]
up=crm([(494,388),(500,381),(508,377),(518,379),(528,384),(535,391),(541,399)])
lo=crm([(494,388),(498,398),(504,404),(512,408),(524,407),(533,404),(541,399)])
R['ojo']+=[up,lo]
R['pestanas']+=[curl((496,384),(476,384),-1,0.22),curl((499,381),(477,378),-1,0.25),curl((503,379),(481,372),-1,0.25),curl((508,377),(488,369),-1,0.22),curl((514,377),(499,368),-1,0.2),curl((494,389),(477,392),-1,0.12)]
# ---- cejas: las dos con el mismo estilo, pelito por pelito, acostándose hacia la orilla de afuera ----
R['ceja']=[]
def ceja(top,bot,outer,n=16):
    T_,B_=rs(crm(top),n),rs(crm(bot),n)
    inner_first = (T_[0][0]-T_[-1][0])*outer<0      # empieza junto a la nariz
    out=[]
    for i,(a,b) in enumerate(zip(B_,T_)):
        fr=i/(n-1) if inner_first else 1-i/(n-1)      # 0 = junto a la nariz, 1 = orilla
        tip=a+(b-a)*(1.0-0.25*fr)+np.array([outer*(2+9*fr),0])
        out.append(curl(tuple(a),tuple(tip),-1,0.12,8))
    return out
R['ceja']+=ceja([(538,360),(530,352),(518,347),(503,344),(490,344),(479,346)],[(540,364),(531,358),(518,354),(503,352),(490,353),(480,355)],-1)
R['ceja']+=ceja([(598,352),(612,348),(628,346),(645,347),(662,350),(676,356),(682,361)],[(600,358),(614,356),(630,354),(647,354),(663,356),(676,360),(682,363)],1)
np.save('rostro_final.npy',np.array(R,dtype=object))
x0,y0,x1,y1,f=460,330,720,425,4
z=cv2.resize(im[y0:y1,x0:x1],None,fx=f,fy=f,interpolation=cv2.INTER_CUBIC); o=z.copy()
for k,ps in R.items():
    for p in ps: cv2.polylines(o,[np.round((np.asarray(p)-[x0,y0])*f*4).astype(np.int32)],False,(40,40,230),1,cv2.LINE_AA,shift=2)
cv2.imwrite('z_ojos2.jpg',np.vstack([z,o]))
