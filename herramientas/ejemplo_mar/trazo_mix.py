"""Líneas de un dibujo sombreado a lápiz.
Tinta = lo oscuro (gris < TH)  +  las líneas finas por contraste local (black-hat > BHT) que son líneas de verdad:
piezas largas (contornos que cruzan un rayo de luz, cuerdas, algas) o piezas cerradas (peces, burbujas, manchitas).
Las rayitas sueltas de textura se quedan fuera. Luego se recorre el esqueleto de la tinta, como trazo_hd3.
Uso: python3 trazo_mix.py TH [BHT]   (lee gris_big.png, escribe trazos_hd.npy y wid_hd.npy en escala 900)"""
import cv2,numpy as np,sys
from scipy.ndimage import gaussian_filter1d as g1
from skimage.morphology import skeletonize
TH=int(sys.argv[1]); BHT=int(sys.argv[2]) if len(sys.argv)>2 else 0
big=cv2.imread('gris_big.png',0); BH,BW=big.shape; W=900; s=W/BW
NB=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
def plen(p): return float(np.sum(np.hypot(*np.diff(p,axis=0).T))) if len(p)>1 else 0.0
def lineas_finas(g,bht,largo=120,area_cerrada=4000):
    bh=cv2.morphologyEx(g,cv2.MORPH_BLACKHAT,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
    inkB=(bh>bht).astype(np.uint8); sk=skeletonize(inkB>0)
    n,lab,st,_=cv2.connectedComponentsWithStats(inkB,connectivity=8)
    skl=np.bincount(lab[sk],minlength=n)
    cs,hier=cv2.findContours(inkB,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE); hole=np.zeros(n,bool)
    for i,c in enumerate(cs):
        if hier[0][i][3]>=0 and cv2.contourArea(c)>15:
            x,y=c[0][0]
            for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
                yy,xx=min(BH-1,max(0,y+dy)),min(BW-1,max(0,x+dx))
                if lab[yy,xx]>0: hole[lab[yy,xx]]=True; break
    keep=(skl>=largo)|(hole&(st[:,4]<area_cerrada)); keep[0]=False
    return (inkB&keep[lab]).astype(np.uint8)
def trace(ink):
    sk=skeletonize(ink>0).astype(np.uint8)
    ys,xs=np.nonzero(sk); P=set(zip(ys.tolist(),xs.tolist()))
    deg={p:sum((p[0]+a,p[1]+b) in P for a,b in NB) for p in P}
    seen=set(); paths=[]
    def walk(start,first):
        path=[start,first]; seen.add((start,first)); seen.add((first,start)); prev,cur=start,first
        while True:
            cand=[(cur[0]+a,cur[1]+b) for a,b in NB if (cur[0]+a,cur[1]+b) in P and (cur[0]+a,cur[1]+b)!=prev and (cur,(cur[0]+a,cur[1]+b)) not in seen]
            if not cand: break
            k=min(len(path)-1,6); d0=np.array(cur)-np.array(path[-1-k]); d0=d0/(np.linalg.norm(d0)+1e-9)
            sc=[(np.dot((np.array(q)-np.array(cur))/np.linalg.norm(np.array(q)-np.array(cur)),d0),q) for q in cand]
            sc.sort(reverse=True); best=sc[0]
            if deg[cur]>2 and best[0]<0.3: break
            q=best[1]; seen.add((cur,q)); seen.add((q,cur)); path.append(q); prev,cur=cur,q
        return path
    for p in sorted(P,key=lambda p:(deg[p]!=1,deg[p]<3)):
        for a,b in NB:
            q=(p[0]+a,p[1]+b)
            if q in P and (p,q) not in seen:
                pt=walk(p,q)
                if len(pt)>=4: paths.append(np.array([[x,y] for y,x in pt],np.float32))
    dt=cv2.distanceTransform(ink.astype(np.uint8),cv2.DIST_L2,5); out=[]; WID=[]
    for p in paths:
        wpx=-1.3+2*float(np.median(dt[np.clip(p[:,1].astype(int),0,BH-1),np.clip(p[:,0].astype(int),0,BW-1)]))
        if len(p)>5: p=np.stack([g1(p[:,0],1.2,mode='nearest'),g1(p[:,1],1.2,mode='nearest')],1)
        p=cv2.approxPolyDP(p.reshape(-1,1,2),0.5,False).reshape(-1,2)*s
        if plen(p)>1.5: out.append(p.astype(np.float32)); WID.append(round(max(0.35,wpx*400/BW),2))
    return out,WID
ink=(big<TH).astype(np.uint8)
if BHT: ink=ink|lineas_finas(big,BHT)
cv2.imwrite('tinta.png',(1-ink)*255)
A,WA=trace(ink); print('trazos',len(A))
# fuera las motitas de textura (se quedan los puntitos cerrados)
keep=[(p,w) for p,w in zip(A,WA) if plen(p)>=2.5 or (len(p)>2 and np.linalg.norm(p[0]-p[-1])<0.8)]
print('final',len(keep),'(sin',len(A)-len(keep),'motitas)')
np.save('trazos_hd.npy',np.array([p for p,_ in keep],dtype=object)); np.save('wid_hd.npy',np.array([w for _,w in keep]))
