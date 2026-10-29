"""Método 'rostro a mano' para Trazo a Trazo.
1) detector de puntos de la cara (MediaPipe)  2) cada línea se pega al trazo real con reglas fijas por parte
3) solo se dibuja lo que de verdad tiene trazo en la imagen  4) revisión automática + imagen comparativa."""
import cv2,numpy as np,sys
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from facelib import Face,crm,resamp
from scipy.ndimage import map_coordinates,gaussian_filter1d
from scipy.signal import find_peaks
REGLAS={'ojo_arriba':('cresta',3),'ojo_abajo':('cresta',3),'labio_arriba':('borde',3),'labio_abajo':('tinta',3),
        'linea_boca':('tinta',3),'nariz':('tinta',4),'pliegue':('cresta',3)}
def support(F,c,mode,tol=1.5):
    c=resamp(c,1.0); t=np.gradient(c,axis=0); t/=np.linalg.norm(t,axis=1,keepdims=True)+1e-6; n=np.stack([-t[:,1],t[:,0]],1)
    best=np.max(np.stack([F.evidence(c+n*o,n,mode) for o in np.linspace(-tol,tol,7)],1),1)
    thr={'tinta':0.22,'borde':0.3,'cresta':0.04}[mode]; return c,gaussian_filter1d((best>thr).astype(float),2)>0.5
def only_real(F,c,mode,minlen=6):
    """Corta la curva donde no hay trazo en la imagen (el artista no dibujó ahí)."""
    c,ok=support(F,c,mode); out=[]; i=0
    while i<len(c):
        if ok[i]:
            j=i
            while j<len(c) and ok[j]: j+=1
            if j-i>=minlen*max(F.scale,0.6): out.append(c[i:j])
            i=j
        else: i+=1
    return out
def fit(F,seed,regla,R=None):
    mode,r=REGLAS[regla]; return F.refine(seed,R=R or r,mode=mode,lam=0.5,prior=0.03),mode
# ---------- pelos (cejas) y pestañas: siguen la dirección de cada pelo ----------
def _orient(F):
    if hasattr(F,'DX'): return
    g=cv2.GaussianBlur(F.L,(0,0),0.8); gx=cv2.Sobel(g,cv2.CV_32F,1,0,3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,3)
    Jxx,Jyy,Jxy=[cv2.GaussianBlur(a,(0,0),2.0) for a in (gx*gx,gy*gy,gx*gy)]
    th=0.5*np.arctan2(2*Jxy,Jxx-Jyy)+np.pi/2; F.DX,F.DY=np.cos(th),np.sin(th)
def _trace(F,x,y,ink,maxlen):
    segs=[]
    for sgn in (1,-1):
        cx,cy=float(x),float(y); d0=np.array([F.DX[y,x],F.DY[y,x]])*sgn; seg=[]
        for _ in range(maxlen):
            ix,iy=int(round(cx)),int(round(cy)); d=np.array([F.DX[iy,ix],F.DY[iy,ix]])
            if d@d0<0: d=-d
            if d@d0<0.94: break
            d0=0.8*d0+0.2*d; d0/=np.linalg.norm(d0); cx+=d0[0]; cy+=d0[1]
            if not ink[int(round(cy)),int(round(cx))]: break
            seg.append((cx,cy))
        segs.append(seg)
    return np.array(segs[1][::-1]+[(float(x),float(y))]+segs[0],np.float32)
def _hand_hair(p):
    c=p.mean(0); u,s_,vt=np.linalg.svd(p-c); ax=vt[0]; nr=np.array([-ax[1],ax[0]])
    t=(p-c)@ax; o=(p-c)@nr; t0,t1=t.min(),t.max(); Lh=t1-t0
    co=np.polyfit(t,o,2) if len(p)>5 else [0,0,0]
    sag=np.clip(np.polyval(co,(t0+t1)/2)-(np.polyval(co,t0)+np.polyval(co,t1))/2,-0.12*Lh,0.12*Lh)
    ts=np.linspace(t0,t1,8); base=np.polyval(co,t0)+(np.polyval(co,t1)-np.polyval(co,t0))*(ts-t0)/Lh
    return c+np.outer(ts,ax)+np.outer(base+sag*(1-((ts-(t0+t1)/2)/(Lh/2))**2),nr)
def hairs(F,poly,maxn):
    _orient(F); sc=max(F.scale,0.5)
    m=np.zeros(F.L.shape,np.uint8); cv2.fillPoly(m,[np.round(poly).astype(np.int32)],1)
    ink=(F.dk>0.33)&(m>0); cov=np.zeros(F.L.shape,np.uint8); out=[]
    ys,xs=np.nonzero(ink)
    for k in np.argsort(-F.dk[ys,xs]):
        y,x=ys[k],xs[k]
        if cov[y,x]: continue
        p=_trace(F,x,y,ink,int(24*sc))
        if len(p)<7*sc: cov[y,x]=1; continue
        h=_hand_hair(p); cv2.polylines(cov,[np.round(h).astype(np.int32)],False,1,max(3,int(5*sc)))
        out.append(h)
        if len(out)>=maxn: break
    return out
def brow_poly(F,sup,inf,grow=3):
    a=F.lm[C_[sup]]; b=F.lm[C_[inf]]; P=np.vstack([a,b[::-1]]); c=P.mean(0)
    return c+(P-c)*(1+grow*F.scale/np.linalg.norm(P-c,axis=1,keepdims=True).mean())
def lashes_up(F,alm,crease,outer):
    """Pestañas de arriba: rayitas que cruzan de la orilla del ojo a la línea gruesa, con la punta curva."""
    S=lambda p:map_coordinates(cv2.GaussianBlur(F.dk,(0,0),0.6),[np.atleast_2d(p)[:,1],np.atleast_2d(p)[:,0]],order=1)
    def yx(c): o=np.argsort(c[:,0]); return lambda x: np.interp(x,c[o,0],c[o,1])
    ya,yp=yx(alm),yx(crease); x0,x1=max(alm[:,0].min(),crease[:,0].min())+2,min(alm[:,0].max(),crease[:,0].max())-2
    if x1-x0<10: return []
    xs=np.arange(x0,x1,0.5); mid=np.stack([xs,(ya(xs)+yp(xs))/2],1); pk,_=find_peaks(S(mid),prominence=0.03,distance=int(6*F.scale)+1); out=[]
    for j in pk:
        xm=xs[j]; best=None; w=4*F.scale
        for xb in np.arange(xm-w,xm+w+.1,0.5):
            for xt in np.arange(xm-w,xm+w+.1,0.5):
                a=np.array([xb,ya(xb)]); b=np.array([xt,yp(xt)]); n=max(int(np.hypot(*(b-a))*2),2)
                s=S(a+np.outer(np.linspace(0,1,n),b-a)).mean()
                if best is None or s>best[0]: best=(s,a,b)
        s,a,b=best
        if s<0.3: continue
        d=(b-a)/np.linalg.norm(b-a); k=0
        while k<10*F.scale and S(b+d*(k+1)*0.5)[0]>0.3: k+=1
        b=b+d*k*0.5; nn=np.array([d[1],-d[0]]); nn*=np.sign(nn[0]*outer+1e-9); ts=np.linspace(0,1,10)
        cur=a+np.outer(ts,b-a)+np.outer(0.25*np.linalg.norm(b-a)*ts**2,nn)
        if not any(_cross(cur,o) for o in out): out.append(cur)
    return out
def _cross(p,q):
    f=lambda a,b,c:(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]); a,b,c,d=p[0],p[-1],q[0],q[-1]
    return f(a,b,c)*f(a,b,d)<0 and f(c,d,a)*f(c,d,b)<0
from lmidx import C as C_
# ---------- todo el rostro ----------
def build(img_bgr,lm,parts=('ojos','nariz','boca'),pestanas=True):
    F=Face(img_bgr,lm); R={}; rep={}
    def add(k,curves,mode):
        R.setdefault(k,[]).extend(curves); rep.setdefault(k,[]).append(round(np.mean([F.check(c,mode) for c in curves]) if curves else 0,2))
    if 'ojos' in parts:
        for e,outer in (('A',-1),('B',1)):
            up,m1=fit(F,F.seed(f'ojo{e}_sup'),'ojo_arriba'); lo,m2=fit(F,F.seed(f'ojo{e}_inf'),'ojo_abajo')
            add('ojo',[up,lo],m1)
            ic=lm[468] if e=='A' else lm[473]; ir=np.mean(np.linalg.norm(lm[469:473]-lm[468],axis=1) if e=='A' else np.linalg.norm(lm[474:478]-lm[473],axis=1))
            poly=np.vstack([up,lo[::-1]]); t=np.linspace(0,2*np.pi,90); circ=ic+ir*np.stack([np.cos(t),np.sin(t)],1)
            ins=np.array([cv2.pointPolygonTest(poly.astype(np.float32),tuple(map(float,p)),True)>-0.5 for p in circ])
            if ins.all(): R.setdefault('iris',[]).append(circ)
            else:
                k=np.argmin(ins); ins=np.roll(ins,-k); circ=np.roll(circ,-k,0); i=0
                while i<len(circ):
                    if ins[i]:
                        j=i
                        while j<len(circ) and ins[j]: j+=1
                        if j-i>4: R.setdefault('iris',[]).append(circ[i:j])
                        i=j
                    else: i+=1
            R.setdefault('pupila',[]).append(ic+ir*0.4*np.stack([np.cos(t),np.sin(t)],1))
            h=np.median(np.linalg.norm(F.seed(f'ojo{e}_sup')-F.seed(f'ojo{e}_inf')[::-1],axis=1))
            cr=up.copy(); cr[:,1]-=max(h*0.55,4*F.scale); cr,_=fit(F,cr,'pliegue',R=3)
            cr=[c for c in only_real(F,cr,'cresta',minlen=15)]
            R.setdefault('parpado',[]).extend(cr)
            if pestanas and cr: R.setdefault('pestanas',[]).extend(lashes_up(F,up,max(cr,key=len),outer))
            R.setdefault('ceja',[]).extend(hairs(F,brow_poly(F,f'ceja{e}_sup',f'ceja{e}_inf'),30))
    if 'nariz' in parts:
        for ks in ([48,64,98,97],[97,2,326],[327,294,278]):
            c,m=F.refine(crm(lm[ks]),R=4,mode='tinta',lam=0.5,prior=0.03),'tinta'
            R.setdefault('nariz',[]).extend(only_real(F,c,'tinta'))
    if 'boca' in parts:
        mid=(F.seed('boca_sup')+F.seed('boca_inf'))/2; mid[0]=lm[61]; mid[-1]=lm[291]
        a,m=fit(F,mid,'linea_boca'); b,m2=fit(F,F.seed('labio_sup'),'labio_arriba'); c,m3=fit(F,F.seed('labio_inf'),'labio_abajo')
        add('boca',[a],m); add('boca',[b],m2); add('boca',[c],m3)
    return R,rep,F
def compare(img_bgr,R,box,f,path):
    x0,y0,x1,y1=box; z=cv2.resize(img_bgr[y0:y1,x0:x1],None,fx=f,fy=f,interpolation=cv2.INTER_CUBIC); o=z.copy(); w=np.full_like(z,250)
    for t in (o,w):
        for ps in R.values():
            for p in ps: cv2.polylines(t,[np.round((np.asarray(p)-[x0,y0])*f*4).astype(np.int32)],False,(40,80,240),2,cv2.LINE_AA,shift=2)
    s=np.full((6,z.shape[1],3),200,np.uint8); cv2.imwrite(path,np.vstack([z,s,o,s,w]))
# ================= reglas v2 =================
def extend_ends(F,c,maxlen=40,thr=0.3,no_down=False):
    """Si el trazo real sigue más allá de la punta (delineado, comisura), la línea también sigue."""
    c=np.asarray(c,np.float32); sc=max(F.scale,0.6)
    S=lambda p:F.samp(F.dk,p)[0]
    def grow(c):
        d=c[-1]-c[-4]; d/=np.linalg.norm(d)+1e-6; p=c[-1].copy(); add=[]
        d0=d.copy()
        for _ in range(int(maxlen*sc)):
            if d@d0<0.5 or (no_down and d[1]>0.35): break                     # no da vuelta: el delineado sigue casi derecho
            n=np.array([-d[1],d[0]]); cand=[p+d+n*o for o in (-0.7,-0.35,0,0.35,0.7)]
            v=[S(q) for q in cand]; k=int(np.argmax(v))
            if v[k]<thr: break
            q=cand[k]; d=0.75*d+0.25*(q-p)/np.linalg.norm(q-p); d/=np.linalg.norm(d); p=q; add.append(p)
        return np.vstack([c,np.array(add)]) if len(add)>=3 else c
    c=grow(c); c=grow(c[::-1])[::-1]
    return resamp(c,1.0)
def ink_thr(F,mask,q=70,lo=0.15):
    v=F.dk[mask>0]; return max(lo,float(np.percentile(v,q))) if len(v) else lo
def hairs2(F,poly,maxn,axis=None,inner_free=0.25,inner_end=None):
    """Cejas: pelo por pelo, solo trazos que van con la ceja (fuera los del cabello)."""
    _orient(F); sc=max(F.scale,0.5)
    m=np.zeros(F.L.shape,np.uint8); cv2.fillPoly(m,[np.round(poly).astype(np.int32)],1)
    thr=ink_thr(F,m,60,0.18); ink=(F.dk>thr)&(m>0); cov=np.zeros(F.L.shape,np.uint8); out=[]
    ys,xs=np.nonzero(ink)
    for k in np.argsort(-F.dk[ys,xs]):
        y,x=ys[k],xs[k]
        if cov[y,x]: continue
        p=_trace(F,x,y,ink,int(24*sc))
        if len(p)<7*sc: cov[y,x]=1; continue
        h=_hand_hair(p)
        if axis is not None:
            d=h[-1]-h[0]; d/=np.linalg.norm(d)+1e-6
            free=inner_end is not None and np.linalg.norm(h.mean(0)-inner_end)<inner_free*np.linalg.norm(axis)
            if not free and abs(d@(axis/np.linalg.norm(axis)))<0.8: cov[y,x]=1; continue
        cv2.polylines(cov,[np.round(h).astype(np.int32)],False,1,max(3,int(5*sc))); out.append(h)
        if len(out)>=maxn: break
    return out
def lashes_out(F,lid,outer,below=False,band=(1.0,13.0),minlen=4.0,maxn=26,from_frac=0.0):
    """Pestañas que salen hacia afuera del párpado (cuando no hay franja entre párpado y pliegue)."""
    _orient(F); sc=max(F.scale,0.6); c=resamp(lid,1.0); t=np.gradient(c,axis=0); t/=np.linalg.norm(t,axis=1,keepdims=True)
    n=np.stack([-t[:,1],t[:,0]],1); want=1 if below else -1; n*=np.sign(n[:,1].mean()*want+1e-9)
    a=int(len(c)*from_frac) if outer>0 else 0; b=len(c) if outer>0 else int(len(c)*(1-from_frac))
    if outer<0 and c[0,0]>c[-1,0]: pass
    P=np.vstack([c+n*band[0]*sc,(c+n*band[1]*sc)[::-1]])
    m=np.zeros(F.L.shape,np.uint8); cv2.fillPoly(m,[np.round(P).astype(np.int32)],1)
    thr=ink_thr(F,m,80,0.3); ink=(F.dk>thr)&(m>0); cov=np.zeros(F.L.shape,np.uint8); out=[]
    ys,xs=np.nonzero(ink)
    for k in np.argsort(-F.dk[ys,xs]):
        y,x=ys[k],xs[k]
        if cov[y,x]: continue
        p=_trace(F,x,y,ink,int(16*sc))
        if len(p)<minlen*sc: cov[y,x]=1; continue
        h=_hand_hair(p); j=np.argmin(np.linalg.norm(c-h.mean(0),axis=1)); d=h[-1]-h[0]; d/=np.linalg.norm(d)+1e-6
        if abs(d@t[j])>0.8: cov[y,x]=1; continue
        if (h[0]-c[j])@n[j]>(h[-1]-c[j])@n[j]: h=h[::-1]          # de la raíz a la punta
        if np.min(np.linalg.norm(c-h[0],axis=1))>5*sc or np.linalg.norm(h[-1]-h[0])>band[1]*sc*1.1: cov[y,x]=1; continue
        Lh=np.linalg.norm(h[-1]-h[0]); nn=np.array([h[-1][1]-h[0][1],-(h[-1][0]-h[0][0])])/Lh; nn*=np.sign(nn[0]*outer+1e-9)
        ts=np.linspace(0,1,10); cur=h[0]+np.outer(ts,h[-1]-h[0])+np.outer(0.2*Lh*ts**2,nn)
        cv2.polylines(cov,[np.round(cur).astype(np.int32)],False,1,3); out.append(cur)
        if len(out)>=maxn: break
    return out
def nose_lines(F,lm):
    """Nariz: solo los trazos más fuertes (orificios y aletas) en la base de la nariz, como líneas limpias."""
    from skimage.morphology import skeletonize
    pts=lm[[129,98,97,2,326,327,358,64,294,48,278,4,1,19,94]]; x0,y0=pts.min(0); x1,y1=pts.max(0)
    pad=6*F.scale; x0,y0,x1,y1=int(x0-pad),int(y0-pad*2.5),int(x1+pad),int(y1+pad*0.6)
    m=np.zeros(F.L.shape,np.uint8); m[y0:y1,x0:x1]=1
    thr=ink_thr(F,m,80,0.3); ink=((F.dk>thr)&(m>0)).astype(np.uint8)
    ink=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    sk=skeletonize(ink>0); out=[]
    n_,lab=cv2.connectedComponents(sk.astype(np.uint8),connectivity=8)
    for i in range(1,n_):
        yy,xx=np.nonzero(lab==i)
        if len(xx)<8*F.scale: continue
        p=np.stack([xx,yy],1).astype(np.float32)
        # ordenar puntos por el recorrido (eje principal) y suavizar
        cc=p.mean(0); u,s_,vt=np.linalg.svd(p-cc); o=np.argsort((p-cc)@vt[0]); p=p[o]
        from scipy.ndimage import gaussian_filter1d as g1
        p=np.stack([g1(p[:,0],3,mode='nearest'),g1(p[:,1],3,mode='nearest')],1); out.append(resamp(p,1.0))
    return out
def build2(img_bgr,lm,parts=('ojos','nariz','boca')):
    F=Face(img_bgr,lm); R={}; rep={}
    def put(k,cs,mode=None):
        R.setdefault(k,[]).extend(cs)
        if mode: rep.setdefault(k,[]).extend([round(F.check(c,mode),2) for c in cs])
    if 'ojos' in parts:
        for e,outer in (('A',-1),('B',1)):
            up,_=fit(F,F.seed(f'ojo{e}_sup'),'ojo_arriba'); lo,_=fit(F,F.seed(f'ojo{e}_inf'),'ojo_abajo')
            up=extend_ends(F,up,no_down=True); put('ojo',[up,lo],'cresta')
            ic=lm[468] if e=='A' else lm[473]; rr=lm[469:473] if e=='A' else lm[474:478]; ir=np.mean(np.linalg.norm(rr-ic,axis=1))
            poly=np.vstack([up,lo[::-1]]).astype(np.float32); t=np.linspace(0,2*np.pi,90); circ=ic+ir*np.stack([np.cos(t),np.sin(t)],1)
            ins=np.array([cv2.pointPolygonTest(poly,tuple(map(float,p)),True)>-0.5 for p in circ])
            if ins.all(): put('iris',[circ])
            else:
                k=np.argmin(ins); ins=np.roll(ins,-k); circ=np.roll(circ,-k,0); i=0
                while i<len(circ):
                    if ins[i]:
                        j=i
                        while j<len(circ) and ins[j]: j+=1
                        if j-i>4: put('iris',[circ[i:j]])
                        i=j
                    else: i+=1
            put('pupila',[ic+ir*0.4*np.stack([np.cos(t),np.sin(t)],1)])
            # pliegue: solo si hay una línea clara encima del ojo, a lo largo del ojo
            h=np.median(np.linalg.norm(F.seed(f'ojo{e}_sup')-F.seed(f'ojo{e}_inf')[::-1],axis=1))
            cr=up.copy(); cr[:,1]-=max(h*0.55,4*F.scale); cr,_=fit(F,cr,'pliegue',R=3)
            cr=[c for c in only_real(F,cr,'cresta',minlen=15) if np.ptp(c[:,0])>0.45*np.ptp(up[:,0])]
            put('parpado',cr)
            la=lashes_up(F,up,max(cr,key=len),outer) if cr else []
            if len(la)<3: la=lashes_out(F,up,outer)
            put('pestanas',la); put('pestanas',lashes_out(F,lo,outer,below=True,band=(1.5,9.0),maxn=14))
            sup=F.lm[C_[f'ceja{e}_sup']]; ax=sup[-1]-sup[0]
            inner=sup[-1] if e=='A' else sup[0]
            put('ceja',hairs2(F,brow_poly(F,f'ceja{e}_sup',f'ceja{e}_inf',grow=2),30,axis=ax,inner_end=inner))
    if 'nariz' in parts: put('nariz',nose_lines(F,lm))
    if 'boca' in parts:
        mid=(F.seed('boca_sup')+F.seed('boca_inf'))/2; mid[0]=lm[61]; mid[-1]=lm[291]
        a,_=fit(F,mid,'linea_boca'); a=extend_ends(F,a,maxlen=12)
        b,_=fit(F,F.seed('labio_sup'),'labio_arriba'); c,_=fit(F,F.seed('labio_inf'),'labio_abajo')
        put('boca',[a],'tinta'); put('boca',[b],'borde'); put('boca',[c],'tinta')
    return R,rep,F
# ================= reglas v3 =================
def trim_regrow(F,c,outer,frac=0.15,maxlen=45,thr=0.22):
    """Las esquinas del detector no son exactas: corto la punta de afuera y la vuelvo a crecer siguiendo el trazo real."""
    c=resamp(c,1.0); n=len(c); k=int(n*frac)
    oe=0 if (c[0,0]<c[-1,0])==(outer<0) else -1        # índice de la esquina de afuera
    c=c[k:] if oe==0 else c[:n-k]
    if oe==0: c=c[::-1]
    c=extend_ends(F,c,maxlen=maxlen,thr=thr) if False else _grow_one(F,c,maxlen,thr)
    return c[::-1] if oe==0 else c
def _grow_one(F,c,maxlen,thr):
    sc=max(F.scale,0.6); d=c[-1]-c[-5]; d/=np.linalg.norm(d)+1e-6; d0=d.copy(); p=c[-1].copy(); add=[]
    for _ in range(int(maxlen*sc)):
        if d@d0<0.5: break
        n=np.array([-d[1],d[0]]); cand=[p+d+n*o for o in (-0.7,-0.35,0,0.35,0.7)]
        v=[F.samp(F.dk,q)[0] for q in cand]; j=int(np.argmax(v))
        if v[j]<thr: break
        q=cand[j]; d=0.75*d+0.25*(q-p)/np.linalg.norm(q-p); d/=np.linalg.norm(d); p=q; add.append(p)
    if len(add)<3: return c
    from scipy.ndimage import gaussian_filter1d as g1
    out=np.vstack([c,np.array(add)]); k=len(c)-6
    out[k:]=np.stack([g1(out[k:,0],2,mode='nearest'),g1(out[k:,1],2,mode='nearest')],1); return resamp(out,1.0)
def lashes_liner(F,up,outer):
    """Pestañas cuando hay delineado grueso: salen de encima de la línea gruesa."""
    sc=max(F.scale,0.6); c=resamp(up,1.0); t=np.gradient(c,axis=0); t/=np.linalg.norm(t,axis=1,keepdims=True)
    n=np.stack([-t[:,1],t[:,0]],1); n*=np.sign(-n[:,1].mean()+1e-9)       # hacia arriba
    # grosor del delineado: hasta dónde sigue oscuro hacia arriba
    th=[]
    for j in range(0,len(c),3):
        k=0
        while k<12 and F.samp(F.dk,c[j]+n[j]*(k+1)*0.5*sc)[0]>0.45: k+=1
        th.append(k*0.5*sc)
    top=c+n*(np.median(th)+0.5)
    return lashes_up(F,top,top+n*9*sc,outer)
def build3(img_bgr,lm,parts=('ojos','nariz','boca')):
    F=Face(img_bgr,lm); R={}; rep={}
    def put(k,cs,mode=None):
        R.setdefault(k,[]).extend(cs)
        if mode: rep.setdefault(k,[]).extend([round(F.check(c,mode),2) for c in cs])
    if 'ojos' in parts:
        for e,outer in (('A',-1),('B',1)):
            up,_=fit(F,F.seed(f'ojo{e}_sup'),'ojo_arriba'); lo,_=fit(F,F.seed(f'ojo{e}_inf'),'ojo_abajo')
            up=trim_regrow(F,up,outer)
            put('ojo',[up,lo],'cresta')
            ic=lm[468] if e=='A' else lm[473]; rr=lm[469:473] if e=='A' else lm[474:478]; ir=np.mean(np.linalg.norm(rr-ic,axis=1))
            poly=np.vstack([up,lo[::-1]]).astype(np.float32); t=np.linspace(0,2*np.pi,90); circ=ic+ir*np.stack([np.cos(t),np.sin(t)],1)
            ins=np.array([cv2.pointPolygonTest(poly,tuple(map(float,p)),True)>-0.5 for p in circ])
            if ins.all(): put('iris',[circ])
            else:
                k=np.argmin(ins); ins=np.roll(ins,-k); circ=np.roll(circ,-k,0); i=0
                while i<len(circ):
                    if ins[i]:
                        j=i
                        while j<len(circ) and ins[j]: j+=1
                        if j-i>4: put('iris',[circ[i:j]])
                        i=j
                    else: i+=1
            put('pupila',[ic+ir*0.4*np.stack([np.cos(t),np.sin(t)],1)])
            h=np.median(np.linalg.norm(F.seed(f'ojo{e}_sup')-F.seed(f'ojo{e}_inf')[::-1],axis=1))
            cr=up.copy(); cr[:,1]-=max(h*0.55,4*F.scale); cr,_=fit(F,cr,'pliegue',R=3)
            cr=[c for c in only_real(F,cr,'cresta',minlen=15) if np.ptp(c[:,0])>0.45*np.ptp(up[:,0])]
            put('parpado',cr)
            la=lashes_up(F,up,max(cr,key=len),outer) if cr else []
            if len(la)<3: la=lashes_liner(F,up,outer)
            if len(la)<3: la=lashes_out(F,up,outer)
            put('pestanas',la); put('pestanas',lashes_out(F,lo,outer,below=True,band=(1.5,9.0),maxn=14))
            sup=F.lm[C_[f'ceja{e}_sup']]; ax=sup[-1]-sup[0]; inner=sup[-1] if e=='A' else sup[0]
            put('ceja',hairs2(F,brow_poly(F,f'ceja{e}_sup',f'ceja{e}_inf',grow=2),30,axis=ax,inner_end=inner))
    if 'nariz' in parts: put('nariz',nose_lines(F,lm))
    if 'boca' in parts:
        mid=(F.seed('boca_sup')+F.seed('boca_inf'))/2; mid[0]=lm[61]; mid[-1]=lm[291]
        a,_=fit(F,mid,'linea_boca'); a=_grow_one(F,_grow_one(F,a,14,0.3)[::-1],14,0.3)[::-1]
        if a[0,0]>a[-1,0]: a=a[::-1]
        b,_=fit(F,F.seed('labio_sup'),'labio_arriba'); c,_=fit(F,F.seed('labio_inf'),'labio_abajo')
        def snap(cv):      # los labios terminan justo en las comisuras de la línea de la boca
            cv=resamp(cv,1.0)
            if cv[0,0]>cv[-1,0]: cv=cv[::-1]
            n=len(cv); w=np.clip(1-np.arange(n)/(0.25*n),0,1)[:,None]
            cv=cv+w*(a[0]-cv[0])+w[::-1]*(a[-1]-cv[-1]); return cv
        put('boca',[a],'tinta'); put('boca',[snap(b)],'borde'); put('boca',[snap(c)],'tinta')
    return R,rep,F
