import cv2,numpy as np,sys; sys.path.insert(0,'..')
from tonal import smooth_closed,open_part
from facelib import resamp
from skimage.morphology import skeletonize
from scipy.ndimage import gaussian_filter1d as g1
exec(open('tono.py').read().split("def masses")[0])
def trace_sk(sk,minlen):
    pts=set(zip(*np.nonzero(sk))); nb=lambda p:[(p[0]+a,p[1]+b) for a in(-1,0,1) for b in(-1,0,1) if (a or b) and (p[0]+a,p[1]+b) in pts]
    deg={p:len(nb(p)) for p in pts}; seen=set(); out=[]
    for s0 in sorted(pts,key=lambda p:deg[p]!=1):
        if s0 in seen: continue
        path=[s0]; seen.add(s0); c=s0; pd=None
        while True:
            nx=[q for q in nb(c) if q not in seen]
            if not nx: break
            if pd is not None: nx.sort(key=lambda q:-((q[0]-c[0])*pd[0]+(q[1]-c[1])*pd[1]))
            q=nx[0]; pd=(q[0]-c[0],q[1]-c[1]); c=q; seen.add(c); path.append(c)
        if len(path)>=minlen: out.append(np.array([[x,y] for y,x in path],np.float32))
    return out
def split_turns(p,turn=55,minlen=8):
    if len(p)<9: return [p]
    d=np.diff(p[::4],axis=0); a=np.arctan2(d[:,1],d[:,0]); da=np.degrees(np.abs(np.angle(np.exp(1j*np.diff(a)))))
    cuts=[0]+[4*(k+1) for k,v in enumerate(da) if v>turn]+[len(p)]
    return [p[a:b] for a,b in zip(cuts[:-1],cuts[1:]) if b-a>=minlen]
def strokes(mask,thr=110,thick=7,minlen=10,sig=2.5,min_area=60):
    b=cv2.GaussianBlur(L,(0,0),1.0); bg=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8)),(0,0),4); ink=(((bg-b)>thr)&(b<175)&(mask>0)).astype(np.uint8)
    ink=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    ink=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    blob=cv2.morphologyEx(ink,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(thick,thick)))
    thin=(ink*(1-cv2.dilate(blob,np.ones((3,3),np.uint8)))).astype(np.uint8)
    out=[]
    for p in trace_sk(skeletonize(thin>0),minlen):
        p=np.stack([g1(p[:,0],sig,mode='nearest'),g1(p[:,1],sig,mode='nearest')],1)
        for q in split_turns(p): out.append(resamp(q,1.5))
    cs,_=cv2.findContours(blob,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for c in cs:
        if cv2.contourArea(c)<min_area: continue
        s=smooth_closed(c[:,0,:],sig); out.append(np.vstack([s,s[:1]]))
    return join(out)
def join(ps,gap=9,cosmin=0.8):
    ps=[p for p in ps if len(p)>1 and not np.allclose(p[0],p[-1])]+[p for p in ps if len(p)>1 and np.allclose(p[0],p[-1])]
    changed=True
    while changed:
        changed=False
        for i in range(len(ps)):
            a=ps[i]
            if np.allclose(a[0],a[-1]): continue
            for j in range(len(ps)):
                if i==j: continue
                b=ps[j]
                if np.allclose(b[0],b[-1]): continue
                for A in (a,a[::-1]):
                    for B in (b,b[::-1]):
                        d=np.linalg.norm(A[-1]-B[0])
                        if d>gap: continue
                        ta=A[-1]-A[max(0,len(A)-5)]; tb=B[min(4,len(B)-1)]-B[0]
                        na,nb=np.linalg.norm(ta),np.linalg.norm(tb)
                        if na<1e-3 or nb<1e-3 or ta@tb/(na*nb)<cosmin: continue
                        ps[i]=np.vstack([A,B]); ps.pop(j); changed=True; break
                    if changed: break
                if changed: break
            if changed: break
    from scipy.ndimage import gaussian_filter1d as g1
    return [resamp(np.stack([g1(p[:,0],1.5,mode='nearest'),g1(p[:,1],1.5,mode='nearest')],1),1.5) if not np.allclose(p[0],p[-1]) else p for p in ps]
THR=30
if __name__=='__main__':
    T={}
    for k in RG:
        fine=k in('ojos','nariz','boca','cara','manos')
        T[k]=strokes(RG[k],THR,6 if fine else 8,10 if fine else 22,1.5 if fine else 3,40 if fine else 220)
        T[k]=[p for p in T[k] if np.sum(np.hypot(*np.diff(p,axis=0).T))>(14 if fine else 30)]
    np.save('linea.npy',np.array(T,dtype=object)); print({k:len(v) for k,v in T.items()})
    o=im.copy(); w=np.full_like(im,250)
    for t in (o,w):
        for k,ps in T.items():
            for p in ps: cv2.polylines(t,[np.round(p*4).astype(np.int32)],False,(40,80,240),1,cv2.LINE_AA,shift=2)
    cv2.imwrite('linea_cmp.jpg',np.hstack([im,o,w]))
