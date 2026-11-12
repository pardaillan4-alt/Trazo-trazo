"""Divina Misericordia: correcciones medidas sobre el dibujo de líneas.
- Pupilas: son puntos negros rellenos; el trazado no las sigue. Se miden sobre la mancha real y se dibujan como un punto.
- Franja de luz (y 860-1080): ahí los rayos y la ropa casi desaparecen; las motitas sueltas que quedan se quitan."""
import numpy as np,cv2
P=list(np.load('trazos_hd_auto.npy',allow_pickle=True)); WD=list(np.load('wid_hd_auto.npy'))
g=cv2.imread('gris_big.png',0); s=g.shape[1]/900          # px por unidad
def plen(p): return float(np.sum(np.hypot(*np.diff(p,axis=0).T)))
# 1) pupilas
pup=[]
for gx,gy in [(725.6,220.5),(816.6,205.6)]:                 # en px de la imagen
    X,Y=int(round(gx)),int(round(gy)); R=14
    win=g[Y-R:Y+R+1,X-R:X+R+1]
    m=(win<95).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    j=min(range(1,n),key=lambda i:np.hypot(*(cen[i]-[R,R])))
    cx,cy=cen[j]+[X-R,Y-R]; r=np.sqrt(st[j,4]/np.pi)
    pup.append((cx/s,cy/s,r/s)); print('pupila',round(cx/s,2),round(cy/s,2),'radio',round(r/s,2),'área px',st[j,4])
quitar=set()
for cx,cy,r in pup:
    for i,p in enumerate(P):
        if np.mean(np.hypot(p[:,0]-cx,p[:,1]-cy)<r+0.8)>0.6: quitar.add(i)
# 2) motitas en la franja de luz
for i,p in enumerate(P):
    if 860<p[:,1].mean()<1080 and plen(p)<6: quitar.add(i)
print('quitados',len(quitar))
P2=[p for i,p in enumerate(P) if i not in quitar]; W2=[w for i,w in enumerate(WD) if i not in quitar]
for cx,cy,r in pup:      # punto relleno: círculo de radio r/2 con grosor r (en unidades de 400)
    t=np.linspace(0,2*np.pi,25); P2.append(np.stack([cx+r/2*np.cos(t),cy+r/2*np.sin(t)],1).astype(np.float32)); W2.append(round(r*400/900,2))
np.save('trazos_hd.npy',np.array(P2,dtype=object),allow_pickle=True); np.save('wid_hd.npy',np.array(W2))
print('trazos',len(P2))
