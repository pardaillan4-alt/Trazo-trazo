"""Limpieza de la ballena y el barco (coordenadas de 900 de ancho).
1) Fuera los montoncitos de rayitas cortas: son sombra rayada, no líneas (se quedan las rayitas sueltas: manchas, burbujas, detalles).
2) Fuera las rayitas cortas donde se juntan las aletas con el cuerpo y bajo la barbilla (sombra oscura)."""
import numpy as np,cv2
from scipy.spatial import cKDTree
ps=list(np.load('trazos_hd.npy',allow_pickle=True)); W=list(np.load('wid_hd.npy'))
def plen(p): return float(np.sum(np.hypot(*np.diff(p,axis=0).T))) if len(p)>1 else 0.0
def dentro_poly(p,poly): return np.array([cv2.pointPolygonTest(np.array(poly,np.float32),(float(x),float(y)),False)>=0 for x,y in p])
L=np.array([plen(p) for p in ps]); mid=np.array([p[len(p)//2] for p in ps])
corto=np.where(L<6)[0]; T=cKDTree(mid[corto]); quitar=set()
for j,i in enumerate(corto):
    if len(T.query_ball_point(mid[i],5.0))>=6: quitar.add(int(i))
n_mont=len(quitar)
LIMPIAR=[([(330,232),(365,238),(368,262),(335,262)],7),          # bajo la barbilla
         ([(468,292),(525,292),(525,322),(468,322)],10),         # aleta de atrás, junto al cuerpo
         ([(592,244),(645,244),(645,272),(592,272)],10)]         # aleta larga, junto al cuerpo
for i,p in enumerate(ps):
    for poly,lmax in LIMPIAR:
        if L[i]<lmax and dentro_poly(p,poly).mean()>0.6: quitar.add(i)
v=np.full((502*2,900*2,3),255,np.uint8)
for i,p in enumerate(ps): cv2.polylines(v,[np.round(p*2*4).astype(np.int32)],False,(0,0,255) if i in quitar else (90,90,90),1,cv2.LINE_AA,shift=2)
cv2.imwrite('quitados.jpg',v)
ps=[p for i,p in enumerate(ps) if i not in quitar]; W=[w for i,w in enumerate(W) if i not in quitar]
print('montoncitos',n_mont,'quitados',len(quitar),'quedan',len(ps))
np.save('trazos_hd.npy',np.array(ps,dtype=object)); np.save('wid_hd.npy',np.array(W))
