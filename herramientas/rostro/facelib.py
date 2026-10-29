"""Rostro a mano: detector de puntos + ajuste al trazo real + revisión automática."""
import cv2,numpy as np
from lmidx import C
def crm(pts,n=10):
    P=np.array(pts,np.float32); P=np.vstack([P[:1],P,P[-1:]]); o=[]
    for k in range(1,len(P)-2):
        p0,p1,p2,p3=P[k-1],P[k],P[k+1],P[k+2]
        for t in np.linspace(0,1,n,endpoint=False): o.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3))
    o.append(P[-2]); return np.array(o,np.float32)
def resamp(c,step=1.0):
    c=np.asarray(c,np.float32); s=np.r_[0,np.cumsum(np.hypot(*np.diff(c,axis=0).T))]
    t=np.linspace(0,s[-1],max(int(s[-1]/step),2)); return np.stack([np.interp(t,s,c[:,0]),np.interp(t,s,c[:,1])],1)
class Face:
    def __init__(s,img_bgr,lm):
        s.im=img_bgr; L=cv2.cvtColor(img_bgr,cv2.COLOR_BGR2GRAY).astype(np.float32); s.L=L; s.lm=lm
        bg=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((11,11),np.uint8)),(0,0),6)
        raw=bg-cv2.GaussianBlur(L,(0,0),0.8)                                # tinta: qué tan oscuro vs su alrededor
        x0,y0=np.maximum(lm.min(0).astype(int),0); x1,y1=lm.max(0).astype(int)
        v=raw[y0:y1,x0:x1]; lo,hi=np.percentile(v,50),np.percentile(v,99.5)   # se ajusta al papel y lápiz de cada dibujo
        s.dk=np.clip((raw-lo)/(hi-lo+1e-6),0,1)
        g=cv2.GaussianBlur(L,(0,0),1.2); s.gx=cv2.Sobel(g,cv2.CV_32F,1,0,5)/40; s.gy=cv2.Sobel(g,cv2.CV_32F,0,1,5)/40
        s.scale=np.linalg.norm(lm[33]-lm[263])/180.0                        # tamaño de la cara (1 = ojos a 180 px)
    def samp(s,a,p):
        from scipy.ndimage import map_coordinates
        p=np.atleast_2d(p); return map_coordinates(a,[p[:,1],p[:,0]],order=1,mode='nearest')
    def seed(s,key,n=10): return crm(s.lm[C[key]],n)
    def evidence(s,pts,nrm,mode):
        if mode=='tinta': return s.samp(s.dk,pts)
        if mode=='cresta':      # centro de una línea: más oscuro que a sus dos lados
            w=2.0*max(s.scale,0.6); a=s.samp(s.dk,pts); b=s.samp(s.dk,pts+nrm*w); c=s.samp(s.dk,pts-nrm*w)
            return np.clip(a-0.5*(b+c),0,None)*(a>0.15)
        # borde: se oscurece al cruzar en dirección de la normal
        return np.clip(-(s.samp(s.gx,pts)*nrm[:,0]+s.samp(s.gy,pts)*nrm[:,1]),0,None)
    def refine(s,curve,R=5,mode='tinta',lam=0.35,keep_ends=False,step=0.5,prior=0.02):
        """Pega la curva al trazo real: busca a lo largo de la normal, con programación dinámica para que quede suave."""
        c=resamp(curve,1.0*max(s.scale,0.5)); t=np.gradient(c,axis=0); t/=np.linalg.norm(t,axis=1,keepdims=True)+1e-6
        n=np.stack([-t[:,1],t[:,0]],1); R=R*max(s.scale,0.5); offs=np.arange(-R,R+1e-6,step*max(s.scale,0.5))
        E=np.stack([s.evidence(c+n*o,n,mode) for o in offs],1)            # N x K
        E=E/(np.percentile(E,98)+1e-6); E=np.clip(E,0,1)-prior*np.abs(offs)[None,:]; N,K=E.shape; cost=np.zeros((N,K)); bk=np.zeros((N,K),int)
        pen=lam*((offs[:,None]-offs[None,:])/(step*max(s.scale,0.5)))**2
        cost[0]=-E[0]+(0 if not keep_ends else 5*np.abs(offs))
        for i in range(1,N):
            tot=cost[i-1][None,:]+pen; bk[i]=np.argmin(tot,1); cost[i]=tot[np.arange(K),bk[i]]-E[i]
        if keep_ends: cost[-1]+=5*np.abs(offs)
        k=int(np.argmin(cost[-1])); path=[k]
        for i in range(N-1,0,-1): k=bk[i][k]; path.append(k)
        o=offs[np.array(path[::-1])]
        from scipy.ndimage import gaussian_filter1d
        o=gaussian_filter1d(o,2.0,mode='nearest'); return (c+n*o[:,None]).astype(np.float32)
    def check(s,curve,mode='tinta',tol=1.5):
        """Revisión automática: % de la línea que cae sobre trazo real (buscando ± tol px)."""
        c=resamp(curve,1.0); t=np.gradient(c,axis=0); t/=np.linalg.norm(t,axis=1,keepdims=True)+1e-6; n=np.stack([-t[:,1],t[:,0]],1)
        best=np.max(np.stack([s.evidence(c+n*o,n,mode) for o in np.linspace(-tol,tol,7)],1),1)
        thr={'tinta':0.25,'borde':0.35,'cresta':0.05}[mode]
        return float((best>thr).mean())
