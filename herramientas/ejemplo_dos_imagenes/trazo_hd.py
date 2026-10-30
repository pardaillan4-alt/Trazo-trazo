import cv2,numpy as np,sys
from scipy.ndimage import gaussian_filter1d as g1
from skimage.morphology import skeletonize
A='/mnt/user-data/attachments/2a8fc66a-2bf4-5ad0-b410-99770220e857/9a03d3b5-image.png'
big=cv2.imread(A,0); BH,BW=big.shape; W=900; s=W/BW
ink=(big<140).astype(np.uint8)
sk=skeletonize(ink>0).astype(np.uint8)
# grafo del esqueleto: recorrer cada tramo entre cruces; en cada cruce seguir el tramo más derecho
H_,W_=sk.shape
nbr=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
ys,xs=np.nonzero(sk); P=set(zip(ys.tolist(),xs.tolist()))
deg={p:sum((p[0]+a,p[1]+b) in P for a,b in nbr) for p in P}
seen=set(); paths=[]
def walk(start,first):
    path=[start,first]; seen.add((start,first)); seen.add((first,start)); prev,cur=start,first
    while True:
        cand=[(cur[0]+a,cur[1]+b) for a,b in nbr if (cur[0]+a,cur[1]+b) in P and (cur[0]+a,cur[1]+b)!=prev and (cur,(cur[0]+a,cur[1]+b)) not in seen]
        if not cand: break
        k=min(len(path)-1,6); d0=np.array(cur)-np.array(path[-1-k]); d0=d0/(np.linalg.norm(d0)+1e-9)
        sc=[(np.dot((np.array(q)-np.array(cur))/np.linalg.norm(np.array(q)-np.array(cur)),d0),q) for q in cand]
        sc.sort(reverse=True); best=sc[0]
        if deg[cur]>2 and best[0]<0.3: break          # en un cruce, solo seguir si va casi derecho
        q=best[1]; seen.add((cur,q)); seen.add((q,cur)); path.append(q); prev,cur=cur,q
    return path
starts=sorted(P,key=lambda p:(deg[p]!=1,deg[p]<3))
for p in starts:
    for a,b in nbr:
        q=(p[0]+a,p[1]+b)
        if q in P and (p,q) not in seen:
            pt=walk(p,q)
            if len(pt)>=4: paths.append(np.array([[x,y] for y,x in pt],np.float32))
out=[]
for p in paths:
    if len(p)>5: p=np.stack([g1(p[:,0],1.2,mode='nearest'),g1(p[:,1],1.2,mode='nearest')],1)
    p=cv2.approxPolyDP(p.reshape(-1,1,2),0.5,False).reshape(-1,2)*s
    L=np.sum(np.hypot(*np.diff(p,axis=0).T)) if len(p)>1 else 0
    if L>1.5: out.append(p.astype(np.float32))
np.save('trazos_hd.npy',np.array(out,dtype=object)); print(len(out))
# comparación de cerca: dibujo original vs. líneas trazadas
def crop(x0,y0,x1,y1,f):
    o=cv2.resize(big[int(y0/s):int(y1/s),int(x0/s):int(x1/s)],None,fx=f*s,fy=f*s,interpolation=cv2.INTER_AREA); o=cv2.cvtColor(o,cv2.COLOR_GRAY2BGR)
    w=np.full_like(o,250)
    for p in out:
        q=(p-[x0,y0])*f; cv2.polylines(w,[np.round(q*4).astype(np.int32)],False,(40,80,240),1,cv2.LINE_AA,shift=2)
    return np.hstack([o,w])
cv2.imwrite('hd_ojos.jpg',crop(340,90,510,170,5)); cv2.imwrite('hd_pelo.jpg',crop(260,30,660,400,2.2))
