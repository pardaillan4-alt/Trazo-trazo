"""Jirafita: dentro de la jirafa, las rayitas claras (orillas sueltas de las manchas y el rayado de sombra de las patas)
se cambian por las manchas completas, medidas con manchas.py."""
import numpy as np,cv2
from scipy.ndimage import gaussian_filter1d as g1
P=list(np.load('trazos_hd_auto.npy',allow_pickle=True)); WD=list(np.load('wid_hd_auto.npy'))
g=cv2.imread('gris_big.png',0); BH,BW=g.shape; s=BW/900
X0,Y0,X1,Y1=[int(v*s) for v in (338,22,612,486)]
c=g[Y0:Y1,X0:X1]
ink=cv2.dilate((c<110).astype(np.uint8),np.ones((3,3),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(1-ink,4)
borde=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]).tolist())
den=np.zeros((BH,BW),np.uint8); den[Y0:Y1,X0:X1]=np.isin(lab,[i for i in range(1,n) if i not in borde])
for bx in [(338,225,372,265),(548,140,612,215)]:
    a,b_,cc,d=[int(v*s) for v in bx]; den[b_:d,a:cc]=0
den=cv2.dilate(den,np.ones((5,5),np.uint8))
def muestra(p,step=1.0):
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(p,axis=0).T))]; t=np.linspace(0,d[-1],max(2,int(d[-1]/step)+1))
    return np.stack([np.interp(t,d,p[:,0]),np.interp(t,d,p[:,1])],1)
keep=[];kw=[];fuera=0
for p,w in zip(P,WD):
    q=muestra(p)*s; x=np.clip(q[:,0].astype(int),0,BW-1); y=np.clip(q[:,1].astype(int),0,BH-1)
    if den[y,x].mean()>0.6 and np.median(g[y,x])>95: fuera+=1; continue      # rayita clara dentro de la jirafa
    keep.append(p); kw.append(w)
# ojos: la pupila negra, el aro del iris y el párpado son una sola mancha negra; el esqueleto la llena de rayitas.
# Dentro del iris (elipse medida a mano) la mancha negra se rellena con contornos que van hacia adentro, y el brillo queda en blanco.
OJOS=[((463.3,144.2),(15.4,15.4)),((395.6,138.5),(11.6,14.6))]
nuevos=[]; quitar=set(); step=2.6
for (cx,cy),(ax,ay) in OJOS:
    el=np.zeros((BH,BW),np.uint8); cv2.ellipse(el,(int(cx*s),int(cy*s)),(int(ax*s),int(ay*s)),0,0,360,1,-1)
    mk=((g<80).astype(np.uint8))&el
    mk=cv2.morphologyEx(mk,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
    dil=cv2.dilate(el,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    for j,p in enumerate(keep):
        q=muestra(p)*s; x=np.clip(q[:,0].astype(int),0,BW-1); y=np.clip(q[:,1].astype(int),0,BH-1)
        if dil[y,x].mean()>0.6: quitar.add(j)
    cur=cv2.erode(mk,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
    while cur.sum()>0:
        cs,_=cv2.findContours(cur,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        for c in cs:
            if len(c)<4: continue
            c=c[:,0,:].astype(np.float32)
            if len(c)>8: c=np.stack([g1(c[:,0],1.6,mode='wrap'),g1(c[:,1],1.6,mode='wrap')],1)
            c=np.vstack([c,c[:1]])/s
            nuevos.append(cv2.approxPolyDP(c.reshape(-1,1,2),0.15,False).reshape(-1,2))
        r=int(round(step)); cur=cv2.erode(cur,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1)))
wo=round(step*1.35/s*400/900,2)
print('ojos: quitados',len(quitar),'relleno',len(nuevos),'grosor',wo)
kw=[w for j,w in enumerate(kw) if j not in quitar]+[wo]*len(nuevos); keep=[p for j,p in enumerate(keep) if j not in quitar]+nuevos
M=list(np.load('manchas.npy',allow_pickle=True)); wm=0.4
np.save('trazos_hd.npy',np.array(keep+M,dtype=object),allow_pickle=True); np.save('wid_hd.npy',np.array(kw+[wm]*len(M)))
print('quitadas',fuera,'manchas',len(M),'total',len(keep)+len(M))
