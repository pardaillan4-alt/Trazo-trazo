"""San Miguel: arreglos sobre las líneas automáticas (trazos_hd_auto.npy, trazo_mix.py 205).
Los ojos son muy chiquitos y el esqueleto los deja en pedacitos: párpados, pliegue, iris y pupila medidos a mano (crm)."""
import numpy as np,cv2
P=list(np.load('trazos_hd_auto.npy',allow_pickle=True)); WD=list(np.load('wid_hd_auto.npy'))
def muestra(p,step=0.25):
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(p,axis=0).T))]; t=np.linspace(0,d[-1],max(2,int(d[-1]/step)+1))
    return np.stack([np.interp(t,d,p[:,0]),np.interp(t,d,p[:,1])],1)
def plen(p): return float(np.sum(np.hypot(*np.diff(p,axis=0).T))) if len(p)>1 else 0.0
def crm(pts,n=12):
    p=np.array(pts,float); p=np.vstack([p[0],p,p[-1]]); out=[]
    for i in range(1,len(p)-2):
        p0,p1,p2,p3=p[i-1],p[i],p[i+1],p[i+2]
        for t in np.linspace(0,1,n,endpoint=False):
            t2,t3=t*t,t*t*t
            out.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3))
    out.append(p[-2]); return np.array(out,np.float32)
def dentro_pol(pol,q): return np.array([cv2.pointPolygonTest(pol,(float(a),float(b)),False)>=0 for a,b in q])
ZI=np.array([(444.5,102.0),(453.5,101.9),(456.2,103.0),(456.2,106.9),(444.5,106.9)],np.float32)
ZD=np.array([(463.8,105.4),(472.8,105.4),(473.6,106.5),(473.6,111.0),(463.8,111.0)],np.float32)
P2=[];W2=[]
for p,w in zip(P,WD):
    q=muestra(p)
    if dentro_pol(ZI,q).mean()>0.5 or dentro_pol(ZD,q).mean()>0.5: continue
    P2.append(p); W2.append(w)
print('ojos: quitados',len(P)-len(P2))
OJOS=[dict(arriba=[(445.8,103.75),(447.0,103.5),(448.5,103.35),(450.0,103.3),(451.6,103.45),(453.0,103.9),(454.0,104.6),(454.7,105.35),(455.0,106.0)],
           abajo=[(446.6,104.5),(447.6,105.2),(449.3,105.7),(451.2,105.95),(453.0,106.1),(454.6,106.15)],
           pliegue=[(446.3,102.35),(448.5,102.15),(451.2,102.15),(453.0,102.5),(454.3,103.0)],
           iris=((450.0,104.6),1.55),pupila=((450.0,104.5),0.6)),
      dict(arriba=[(464.2,107.8),(465.3,107.3),(467.0,107.0),(469.0,107.0),(470.3,107.45),(471.3,108.15),(472.15,108.95),(472.5,109.5)],
           abajo=[(464.6,108.3),(466.2,109.2),(467.8,109.8),(469.5,110.2),(471.2,110.3),(472.5,109.7)],
           pliegue=[(465.2,106.3),(467.0,105.9),(469.0,105.75),(470.7,106.05),(472.0,106.65),(472.7,107.3)],
           iris=((468.4,108.6),1.6),pupila=((468.4,108.5),0.62))]
nuevos=[]
for o in OJOS:
    up=crm(o['arriba']); lo=crm(o['abajo'])
    nuevos+=[(up,0.5),(lo,0.35),(crm(o['pliegue']),0.35)]
    abert=np.vstack([up,lo[::-1]]).astype(np.float32)
    t=np.linspace(0,2*np.pi,181)
    (cx,cy),r=o['iris']; ci=np.stack([cx+r*np.cos(t),cy+r*np.sin(t)],1); vis=dentro_pol(abert,ci); i=0
    while i<len(ci):                       # el iris, solo lo que se ve entre los párpados
        if not vis[i]: i+=1; continue
        j=i
        while j<len(ci) and vis[j]: j+=1
        if plen(ci[i:j])>0.8: nuevos.append((ci[i:j].astype(np.float32),0.35))
        i=j
    (px,py),rp=o['pupila']                 # la pupila rellena: círculos que van hacia adentro
    for rr in np.arange(rp,0.05,-0.3):
        c=np.stack([px+rr*np.cos(t),py+rr*np.sin(t)],1); nuevos.append((c.astype(np.float32),0.35))
P2+=[p for p,_ in nuevos]; W2+=[w for _,w in nuevos]
np.save('trazos_hd.npy',np.array(P2,dtype=object),allow_pickle=True); np.save('wid_hd.npy',np.array(W2))
print('ojos nuevos',len(nuevos),'total',len(P2))
