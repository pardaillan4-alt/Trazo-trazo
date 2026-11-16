"""Virgen Milagrosa: arreglos sobre las líneas automáticas (trazos_hd_auto.npy).
1) La firma «Corazón de Paúl» no es parte del dibujo que se aprende: sus trazos se quitan (se ve con el sombreado).
2) Los ojos son muy chiquitos y el esqueleto los deja chuecos: párpados, pliegue, iris y pupila medidos a mano (crm)."""
import numpy as np,cv2
P=list(np.load('trazos_hd_auto.npy',allow_pickle=True)); WD=list(np.load('wid_hd_auto.npy'))
g=cv2.imread('gris_big.png',0); BH,BW=g.shape; s=BW/900
def muestra(p,step=0.5):
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
# 1) la firma: se recortan los pedazos de trazo que caen sobre las letras
F=np.load('firma_mask.npy')
P2=[];W2=[]
for p,w in zip(P,WD):
    q=muestra(p); x=np.clip((q[:,0]*s).astype(int),0,BW-1); y=np.clip((q[:,1]*s).astype(int),0,BH-1); dentro=F[y,x]>0
    if not dentro.any(): P2.append(p); W2.append(w); continue
    i=0
    while i<len(q):
        if dentro[i]: i+=1; continue
        j=i
        while j<len(q) and not dentro[j]: j+=1
        seg=q[i:j]
        if plen(seg)>=3: P2.append(cv2.approxPolyDP(seg.reshape(-1,1,2).astype(np.float32),0.15,False).reshape(-1,2)); W2.append(w)
        i=j
print('firma: trazos',len(P),'->',len(P2))
# 2) los ojos
OJO_I=np.array([(428.5,115.3),(437,114.9),(440.5,116.2),(442.6,118.2),(442.6,122.3),(428.5,122.3)],np.float32)
OJO_D=np.array([(454,118.2),(463,117.8),(466.5,119.8),(468,122.5),(467.5,125.3),(454,125.3)],np.float32)
def dentro_pol(pol,q): return np.array([cv2.pointPolygonTest(pol,(float(a),float(b)),False)>=0 for a,b in q])
P3=[];W3=[]
for p,w in zip(P2,W2):
    q=muestra(p)
    if dentro_pol(OJO_I,q).mean()>0.5 or dentro_pol(OJO_D,q).mean()>0.5: continue
    P3.append(p); W3.append(w)
print('ojos: quitados',len(P2)-len(P3))
OJOS=[dict(arriba=[(429.1,118.75),(431.0,118.0),(433.5,117.6),(436.0,117.55),(438.0,117.8),(439.5,118.55),(440.75,119.5),(441.6,120.6),(441.75,121.25)],
           abajo=[(429.75,119.1),(431.0,120.0),(432.5,120.9),(434.25,121.45),(436.0,121.6),(438.0,121.6),(440.0,121.45),(441.6,121.25)],
           pliegue=[(430.5,116.6),(432.25,115.75),(434.75,115.4),(436.75,115.45),(438.5,116.0),(440.0,117.0),(441.25,118.1),(441.75,118.75)],
           iris=((435.3,119.0),2.43),pupila=((436.0,119.1),0.75)),
      dict(arriba=[(454.6,122.1),(456.0,121.25),(457.5,120.75),(459.5,120.55),(461.5,120.55),(463.0,120.8),(464.5,121.5),(465.75,122.4),(466.75,123.4)],
           abajo=[(454.75,122.5),(456.0,123.4),(457.75,124.25),(459.5,124.75),(461.5,124.8),(463.25,124.5),(465.0,124.0),(466.75,123.5)],
           pliegue=[(455.1,119.9),(457.0,119.0),(459.5,118.5),(462.0,118.6),(463.75,119.4),(465.0,120.5),(466.0,121.75)],
           iris=((459.75,122.4),2.5),pupila=((460.0,121.6),0.8))]
nuevos=[]
for o in OJOS:
    up=crm(o['arriba']); lo=crm(o['abajo'])
    nuevos+= [(up,0.5),(lo,0.4),(crm(o['pliegue']),0.35)]
    abert=np.vstack([up,lo[::-1]]).astype(np.float32)          # la abertura del ojo
    (cx,cy),r=o['iris']; t=np.linspace(0,2*np.pi,181); ci=np.stack([cx+r*np.cos(t),cy+r*np.sin(t)],1)
    vis=dentro_pol(abert,ci); i=0
    while i<len(ci):                                             # el iris, solo lo que se ve entre los párpados
        if not vis[i]: i+=1; continue
        j=i
        while j<len(ci) and vis[j]: j+=1
        if plen(ci[i:j])>0.8: nuevos.append((ci[i:j].astype(np.float32),0.35))
        i=j
    (px,py),rp=o['pupila']                                       # la pupila rellena: círculos que van hacia adentro
    for rr in np.arange(rp,0.05,-0.42):
        c=np.stack([px+rr*np.cos(t),py+rr*np.sin(t)],1); v=dentro_pol(abert,c)
        if v.all(): nuevos.append((c.astype(np.float32),0.35))
        else:
            i=0
            while i<len(c):
                if not v[i]: i+=1; continue
                j=i
                while j<len(c) and v[j]: j+=1
                if plen(c[i:j])>0.4: nuevos.append((c[i:j].astype(np.float32),0.35))
                i=j
P3+= [p for p,_ in nuevos]; W3+= [w for _,w in nuevos]
np.save('trazos_hd.npy',np.array(P3,dtype=object),allow_pickle=True); np.save('wid_hd.npy',np.array(W3))
print('ojos nuevos',len(nuevos),'total',len(P3))
