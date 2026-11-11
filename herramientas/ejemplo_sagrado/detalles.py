"""Correcciones del Sagrado Corazón (coordenadas de 900 de ancho).
Pupilas: son manchas negras rellenas con un brillo blanco; el trazo automático sale como una "U".
Se quitan esos trazos y se dibuja el contorno de cada pupila (círculo ajustado a la mancha real)."""
import cv2,numpy as np
ps=list(np.load('trazos_hd_auto.npy',allow_pickle=True)); W=list(np.load('wid_hd_auto.npy'))
big=cv2.imread('gris_big.png',0); s=900/big.shape[1]
# cada pupila: la mancha oscura dentro del iris (se cierra el brillo y se quitan las líneas delgadas de los párpados)
pupilas=[]
for gx,gy in [(423.5,197.0),(509.8,209.3)]:          # centro aproximado, medido en el acercamiento
    X,Y=int(round(gx/s)),int(round(gy/s)); R=13
    win=big[Y-R:Y+R+1,X-R:X+R+1]; yy,xx=np.mgrid[-R:R+1,-R:R+1]
    m=((win<100)&(xx*xx+yy*yy<=9.5**2)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    n,lab=cv2.connectedComponents(m); k=lab[R,R] if lab[R,R] else np.bincount(lab[lab>0]).argmax()
    cs,_=cv2.findContours((lab==k).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)
    (ex,ey),rr=cv2.minEnclosingCircle(c); req=np.sqrt(cv2.contourArea(c)/np.pi); mo=cv2.moments(c)
    cx,cy,r=(X-R+mo['m10']/mo['m00'])*s,(Y-R+mo['m01']/mo['m00'])*s,req*s
    pupilas.append((cx,cy,r)); print('pupila',round(cx,2),round(cy,2),'r',round(r,2),'(envolvente',round(rr*s,2),'por area',round(req*s,2),')')
quitar=set()
for i,p in enumerate(ps):
    for cx,cy,r in pupilas:
        if (np.hypot(p[:,0]-cx,p[:,1]-cy)<r+0.9).mean()>0.6: quitar.add(i)
ps=[p for i,p in enumerate(ps) if i not in quitar]; W=[w for i,w in enumerate(W) if i not in quitar]
for cx,cy,r in pupilas:
    t=np.linspace(np.pi/2,np.pi/2+2*np.pi,40); ps.append(np.stack([cx+(r-0.35)*np.cos(t),cy+(r-0.35)*np.sin(t)],1).astype(np.float32)); W.append(0.55)
print('quitados',len(quitar),'pupilas',len(pupilas),'total',len(ps))
np.save('trazos_hd.npy',np.array(ps,dtype=object)); np.save('wid_hd.npy',np.array(W))
