"""Retrato familiar: las manchas negras rellenas (pupilas, fosas de la nariz) se miden sobre la mancha real
y se rellenan con contornos que van hacia adentro, en lugar de los trazos sueltos que salen del trazado."""
import numpy as np,cv2
P=list(np.load('trazos_hd_auto.npy',allow_pickle=True)); WD=list(np.load('wid_hd_auto.npy'))
g=cv2.imread('gris_big.png',0); s=g.shape[1]/900
m=(g<110).astype(np.uint8)
hs,hier=cv2.findContours(m,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
for c,hh in zip(hs,hier[0]):
    if hh[3]>=0 and cv2.contourArea(c)<75: cv2.drawContours(m,[c],-1,1,-1)     # brillos y huequitos chicos
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))   # tapa el brillo
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))   # quedan solo las manchas gruesas, sin las líneas
n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
dt=cv2.distanceTransform(m,cv2.DIST_L2,5)
OJOS=np.array([(237.8,557.1),(295.7,552.9),(459.4,632.6),(571.6,635.9),(236.0,883.0),(324.6,897.4)])   # los seis ojos, medidos a mano
manchas=[]
for i in range(1,n):
    x,y,w,h,a=st[i]
    if a<60 or w>90 or h>90: continue
    if min(np.hypot(*(cen[i]/s-o)) for o in OJOS)>9: continue
    manchas.append(i); print('mancha',(cen[i]/s).round(1).tolist(),'área',a,'dt',round(float(dt[y:y+h,x:x+w][lab[y:y+h,x:x+w]==i].max()),1))
quitar=set(); nuevos=[]; step=2.6
for i in manchas:
    mk=(lab==i).astype(np.uint8)
    cs,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cv2.drawContours(mk,cs,-1,1,-1)   # sin el hueco del brillo
    mk=cv2.morphologyEx(mk,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    d=cv2.distanceTransform(mk,cv2.DIST_L2,5); r=float(d.max()); cy,cx=np.unravel_index(int(d.argmax()),d.shape)
    disco=np.zeros_like(mk); cv2.circle(disco,(int(cx),int(cy)),int(round(r*1.08)),1,-1); mk&=disco   # el iris es redondo: sin el párpado grueso
    d=cv2.distanceTransform(mk,cv2.DIST_L2,5); r=float(d.max()); cy,cx=np.unravel_index(int(d.argmax()),d.shape)
    disco=np.zeros_like(mk); cv2.circle(disco,(int(cx),int(cy)),int(round(r*1.08)),1,-1); mk&=disco   # el iris es redondo: sin el párpado grueso
    dil=cv2.dilate(mk,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    for j,p in enumerate(P):
        q=np.round(p*s).astype(int); q[:,0]=np.clip(q[:,0],0,g.shape[1]-1); q[:,1]=np.clip(q[:,1],0,g.shape[0]-1)
        fr=dil[q[:,1],q[:,0]].mean(); L=float(np.sum(np.hypot(*np.diff(p,axis=0).T)))*s
        if fr>0.75: quitar.add(j)
    k=0; cur=cv2.erode(mk,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
    while cur.sum()>0:
        cs,_=cv2.findContours(cur,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        for c in cs:
            c=c[:,0,:].astype(np.float32)
            if len(c)<3: c=np.vstack([c,c+0.5])
            c=np.vstack([c,c[:1]])/s; nuevos.append(c)
        r=int(round(step))
        cur=cv2.erode(cur,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1)))
w=round(step*1.35/s*400/900,2)
P2=[p for j,p in enumerate(P) if j not in quitar]+nuevos; W2=[x for j,x in enumerate(WD) if j not in quitar]+[w]*len(nuevos)
np.save('trazos_hd.npy',np.array(P2,dtype=object),allow_pickle=True); np.save('wid_hd.npy',np.array(W2))
print('manchas',len(manchas),'quitados',len(quitar),'relleno',len(nuevos),'trazos',len(P2),'grosor',w)
