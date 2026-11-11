import numpy as np,cv2,json
from skimage.morphology import skeletonize
NB=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
def trace(mask,minlen=6):
    sk=skeletonize(mask>0.3).astype(np.uint8)
    H,W=sk.shape; seen=np.zeros_like(sk); paths=[]
    ys,xs=np.nonzero(sk); pts=set(zip(ys.tolist(),xs.tolist()))
    def nbrs(p): return [(p[0]+a,p[1]+b) for a,b in NB if (p[0]+a,p[1]+b) in pts]
    deg={p:len(nbrs(p)) for p in pts}
    order=sorted(pts,key=lambda p:(deg[p]!=1,p))  # empieza por extremos
    for s in order:
        if seen[s]: continue
        path=[s]; seen[s]=1; cur=s
        while True:
            nx=[q for q in nbrs(cur) if not seen[q]]
            if not nx: break
            # preferir vecino en línea recta
            nx.sort(key=lambda q:abs(q[0]-cur[0])+abs(q[1]-cur[1]))
            cur=nx[0]; seen[cur]=1; path.append(cur)
        if len(path)>=minlen: paths.append(np.array([[p[1],p[0]] for p in path],np.float32))
    out=[]
    for p in paths:
        a=cv2.approxPolyDP(p.reshape(-1,1,2),0.8,False).reshape(-1,2)
        if len(a)>=2: out.append(a)
    # orden de dibujo: de arriba hacia abajo, izquierda a derecha
    out.sort(key=lambda a:(round(a[:,1].min()/40),a[:,0].min()))
    return out
def to_svg(paths,scale=400/900):
    res=[]
    for p in paths:
        q=p*scale
        d='M'+' '.join(f'{x:.1f} {y:.1f}' for x,y in q[:1])+'L'+' '.join(f'{x:.1f} {y:.1f}' for x,y in q[1:])
        L=float(np.sum(np.hypot(*np.diff(q,axis=0).T)))
        res.append([d,round(L,1)])
    return res
