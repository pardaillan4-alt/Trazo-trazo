"""Correcciones medidas a mano (coordenadas de 900 de ancho) para la ballena y el delfín.
Ojos: se quitan los trazos automáticos (salían garabatos dentro de la pupila negra) y se dibujan
el contorno, el iris recortado por el contorno, los brillos y el párpado. Boca y aletas: fuera las rayitas de sombra."""
import numpy as np,cv2
ps=list(np.load('trazos_hd.npy',allow_pickle=True)); W=list(np.load('wid_hd.npy'))
def plen(p): return float(np.sum(np.hypot(*np.diff(p,axis=0).T))) if len(p)>1 else 0.0
def ell(cx,cy,rx,ry,n=72,a0=0.0):
    t=np.linspace(a0,a0+2*np.pi,n+1); return np.stack([cx+rx*np.cos(t),cy+ry*np.sin(t)],1).astype(np.float32)
def crm(P,n=10):
    P=np.asarray(P,np.float32); P=np.vstack([P[:1],P,P[-1:]]); out=[]
    for i in range(1,len(P)-2):
        p0,p1,p2,p3=P[i-1],P[i],P[i+1],P[i+2]
        for t in np.linspace(0,1,n,endpoint=False):
            out.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3))
    out.append(P[-2]); return np.array(out,np.float32)
def runs(P,keep):
    """parte una curva en tramos donde keep es verdadero (si es cerrada, une el último tramo con el primero)"""
    out=[]; cur=[]
    for p,k in zip(P,keep):
        if k: cur.append(p)
        elif cur: out.append(np.array(cur)); cur=[]
    if cur: out.append(np.array(cur))
    if len(out)>1 and keep[0] and keep[-1] and np.allclose(P[0],P[-1]): out[0]=np.vstack([out.pop(),out[0][1:]])
    return [o for o in out if len(o)>1]
def dentro_ell(p,cx,cy,rx,ry): return (((p[:,0]-cx)/rx)**2+((p[:,1]-cy)/ry)**2)<1
def dentro_poly(p,poly): return np.array([cv2.pointPolygonTest(np.array(poly,np.float32),(float(x),float(y)),False)>=0 for x,y in p])
quitar=[]
for i,p in enumerate(ps):
    L=plen(p)
    if dentro_ell(p,348.25,236.4,18.2,18.0).mean()>0.6: quitar.append(i)          # ojo de la ballena
    elif dentro_ell(p,608.3,174.4,11.8,11.0).mean()>0.6: quitar.append(i)         # ojo del delfín
    elif L<6 and dentro_poly(p,[(533,205),(552,203.5),(579,201.5),(579,207),(560,212.5),(547,219),(532,220)]).mean()>0.6: quitar.append(i)   # boca del delfín
    elif L<6 and dentro_poly(p,[(376,350),(425,337),(425,352),(380,369)]).mean()>0.6: quitar.append(i)   # aleta de abajo de la ballena
    elif L<6 and dentro_poly(p,[(597,239),(631,249),(631,263),(599,253)]).mean()>0.6: quitar.append(i)   # aleta del delfín
ps=[p for i,p in enumerate(ps) if i not in set(quitar)]; W=[w for i,w in enumerate(W) if i not in set(quitar)]
nuevos=[]
# ojo de la ballena
anillo=(348.25,236.2,16.55,16.8)
nuevos.append((ell(*anillo,n=90,a0=np.pi*0.55),1.1))
iris=ell(352.6,237.4,12.4,13.2,n=90,a0=np.pi*0.05)
for r in runs(iris,(((iris[:,0]-anillo[0])/anillo[2])**2+((iris[:,1]-anillo[1])/anillo[3])**2)<0.86): nuevos.append((r,0.6))
nuevos.append((ell(346.7,232.2,3.5,4.0,n=36),0.45)); nuevos.append((ell(356.4,235.7,1.25,2.0,n=24),0.4))
# ojo del delfín
borde=ell(608.3,174.2,10.0,9.4,n=90,a0=np.pi*0.5)
for r in runs(borde,borde[:,1]<181.6): nuevos.append((r,0.95))
pup=ell(605.5,175.5,7.0,7.0,n=72,a0=np.pi*0.5)
for r in runs(pup,((((pup[:,0]-608.3)/10.0)**2+((pup[:,1]-174.2)/9.4)**2)<0.8)&(pup[:,1]<181.2)): nuevos.append((r,0.6))
nuevos.append((ell(608.3,172.6,2.0,2.0,n=28),0.4))
nuevos.append((crm([(598.3,183.6),(603.5,182.8),(609,182.0),(614.5,181.2),(618.5,181.0),(621,182.3),(623,184.2)]),0.9))
for p,w in nuevos: ps.append(p.astype(np.float32)); W.append(w)
print('quitados',len(quitar),'nuevos',len(nuevos),'total',len(ps))
np.save('trazos_hd.npy',np.array(ps,dtype=object)); np.save('wid_hd.npy',np.array(W))
