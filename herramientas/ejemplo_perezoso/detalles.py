"""Perezoso: las manchas negras rellenas (pupilas y fosas de la nariz) se rellenan con contornos que van hacia adentro
(el brillo del ojo queda en blanco), en lugar de las rayitas que salen del esqueleto."""
import numpy as np,cv2
from scipy.ndimage import gaussian_filter1d as g1
P=list(np.load('trazos_hd_auto.npy',allow_pickle=True)); WD=list(np.load('wid_hd_auto.npy'))
g=cv2.imread('gris_big.png',0); BH,BW=g.shape; s=BW/900
ZONAS=[((429.2,126.3),6.2,100),((488.6,126.4),6.4,100),((459.3,141.2),3.6,115),((473.0,140.6),3.6,115)]   # iris de los ojos y fosas de la nariz: centro, radio y umbral, medidos a mano
def muestra(p,step=1.0):
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(p,axis=0).T))]; t=np.linspace(0,d[-1],max(2,int(d[-1]/step)+1))
    return np.stack([np.interp(t,d,p[:,0]),np.interp(t,d,p[:,1])],1)
quitar=set(); nuevos=[]; step=2.6
for (px,py),r0,th in ZONAS:
    el=np.zeros((BH,BW),np.uint8); cv2.circle(el,(int(px*s),int(py*s)),int(r0*s),1,-1)
    mk=(g<th).astype(np.uint8)&el
    mk=cv2.morphologyEx(mk,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
    dil=cv2.dilate(el,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    for j,p in enumerate(P):
        q=muestra(p)*s; x=np.clip(q[:,0].astype(int),0,BW-1); y=np.clip(q[:,1].astype(int),0,BH-1)
        if dil[y,x].mean()>0.6: quitar.add(j)
    cur=mk.copy()
    while cur.sum()>0:
        cs,_=cv2.findContours(cur,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        for c in cs:
            if len(c)<4: continue
            c=c[:,0,:].astype(np.float32)
            if len(c)>8: c=np.stack([g1(c[:,0],1.4,mode='wrap'),g1(c[:,1],1.4,mode='wrap')],1)
            c=np.vstack([c,c[:1]])/s; nuevos.append(cv2.approxPolyDP(c.reshape(-1,1,2),0.15,False).reshape(-1,2))
        r=int(round(step)); cur=cv2.erode(cur,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1)))
w=round(step*1.35/s*400/900,2)
P2=[p for j,p in enumerate(P) if j not in quitar]+nuevos; W2=[x for j,x in enumerate(WD) if j not in quitar]+[w]*len(nuevos)
np.save('trazos_hd.npy',np.array(P2,dtype=object),allow_pickle=True); np.save('wid_hd.npy',np.array(W2))
print('quitados',len(quitar),'relleno',len(nuevos),'trazos',len(P2))
