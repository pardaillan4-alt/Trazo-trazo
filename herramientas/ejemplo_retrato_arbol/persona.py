import cv2,numpy as np,sys; sys.path.insert(0,'..')
from facelib import Face,crm,resamp
from skimage.morphology import skeletonize
from scipy.ndimage import gaussian_filter1d as g1
im=cv2.imread('sq.png'); L=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32); H,W=L.shape
lm=np.load('lm.npy'); F=Face(im,lm); yy,xx=np.mgrid[0:H,0:W]
exec(open('arbol.py').read().split("person=PERSON")[0].split("im=cv2.imread")[0])
def poly(p): m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
def ell(c,a,ang=0): m=np.zeros((H,W),np.uint8); cv2.ellipse(m,c,a,ang,0,360,1,-1); return m
src=open('gen.py').read(); exec(src[src.index('PERSON=poly('):src.index('order=')])
bg=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((11,11),np.uint8)),(0,0),6); raw=bg-cv2.GaussianBlur(L,(0,0),1.0)
def paths(mask,q,minlen,turn=50):
    v=raw[mask>0]; thr=np.percentile(v,q); ink=((raw>thr)&(mask>0)).astype(np.uint8)
    ink=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)); sk=skeletonize(ink>0)
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
        p=np.array([[x,y] for y,x in path],np.float32)
        if len(p)<minlen: continue
        p=np.stack([g1(p[:,0],4,mode='nearest'),g1(p[:,1],4,mode='nearest')],1)
        # cortar en vueltas fuertes
        d=np.diff(p[::4],axis=0); ang=np.degrees(np.abs(np.angle(np.exp(1j*(np.arctan2(d[1:,1],d[1:,0])-np.arctan2(d[:-1,1],d[:-1,0]))))))
        cuts=[0]+[4*(k+1) for k,a in enumerate(ang) if a>turn]+[len(p)]
        for a,b in zip(cuts[:-1],cuts[1:]):
            if b-a>=minlen: out.append(resamp(p[a:b],2.0))
    return out
X={}
# contorno de la cara: óvalo del detector pegado al trazo real, solo donde hay trazo
from rostro import only_real
# contorno medido renglón por renglón sobre el trazo real
X['cara']=[crm([(688,362),(693,380),(698,395),(703,410),(707,425),(711,440),(715,455),(717,470),(718,485),(718,500),(717,515),(715,530),(711,545),(709,560),(705,575),(700,590),(693,603),(680,610),(660,614),(645,619),(630,622),(615,624),(600,625),(585,625),(570,620),(555,611),(540,600),(530,594),(520,585),(510,572),(502,557),(494,542),(487,527),(482,510),(477,490),(473,465),(472,440),(473,425)])]
manos=np.clip(P['manos']+P['hombro'],0,1).astype(np.uint8)
X['manos']=paths(manos,90,40)
np.save('persona.npy',np.array(X,dtype=object)); print({k:len(v) for k,v in X.items()})
o=im.copy()
RF=np.load('rostro_final.npy',allow_pickle=True).item()
for ps in RF.values():
    for p in ps: cv2.polylines(o,[np.round(np.asarray(p)*4).astype(np.int32)],False,(40,80,240),2,cv2.LINE_AA,shift=2)
for k,ps in X.items():
    for p in ps: cv2.polylines(o,[np.round(p*4).astype(np.int32)],False,(0,150,0) if k=='manos' else (200,0,200),2,cv2.LINE_AA,shift=2)
cv2.imwrite('persona_cmp.jpg',np.vstack([im[260:800,380:1100],o[260:800,380:1100]]))
# ---------- cabello y pasto ----------
dk=np.clip((raw-np.percentile(raw,50))/(np.percentile(raw,99.5)-np.percentile(raw,50)),0,1)
g=cv2.GaussianBlur(L,(0,0),1.0); gx=cv2.Sobel(g,cv2.CV_32F,1,0,3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,3)
Jxx,Jyy,Jxy=[cv2.GaussianBlur(a_,(0,0),5) for a_ in (gx*gx,gy*gy,gx*gy)]
th=0.5*np.arctan2(2*Jxy,Jxx-Jyy)+np.pi/2; DX,DY=np.cos(th),np.sin(th)
def fur(mm,n,length,q=85,space=16,step=1.5,minfrac=0.35):
    thr=np.percentile(dk[mm>0],q); ink=(dk>thr)&(mm>0); cov=np.zeros((H,W),np.uint8); out=[]
    ys,xs=np.nonzero(ink)
    for k in np.argsort(-dk[ys,xs]):
        y,x=ys[k],xs[k]
        if cov[y,x]: continue
        pts=[(float(x),float(y))]
        for sgn in (1,-1):
            cx_,cy_=float(x),float(y); d0=np.array([DX[y,x],DY[y,x]])*sgn; seg=[]; miss=0
            for _ in range(int(length/step)):
                ix,iy=int(cx_),int(cy_)
                if not(0<=ix<W and 0<=iy<H) or not mm[iy,ix]: break
                miss=0 if ink[iy,ix] else miss+1
                if miss>6: break
                d=np.array([DX[iy,ix],DY[iy,ix]]); d=d if d@d0>0 else -d; d0=0.85*d0+0.15*d; d0/=np.linalg.norm(d0)
                cx_+=d0[0]*step; cy_+=d0[1]*step; seg.append((cx_,cy_))
            pts=(seg[::-1]+pts) if sgn==-1 else pts+seg
        p=np.array(pts,np.float32)
        if len(p)*step<length*minfrac: cov[y,x]=1; continue
        p=np.stack([g1(p[:,0],3,mode='nearest'),g1(p[:,1],3,mode='nearest')],1)
        cv2.polylines(cov,[np.round(p).astype(np.int32)],False,1,space); out.append(p[::2])
        if len(out)>=n: break
    return out
face=np.zeros((H,W),np.uint8); cv2.fillPoly(face,[np.round(X['cara'][0]).astype(np.int32)],1)
hair=(P['cabello']*(1-cv2.dilate(face,np.ones((9,9),np.uint8)))*(1-cv2.dilate(manos,np.ones((9,9),np.uint8)))).astype(np.uint8)
X['cabello']=fur(hair,110,170,70,14)
cm=np.zeros((H,W),np.uint8)
for p in X['cara']: cv2.polylines(cm,[np.round(p).astype(np.int32)],False,1,9)
X['cabello']=[p for p in X['cabello'] if cm[np.clip(np.round(p[:,1]).astype(int),0,H-1),np.clip(np.round(p[:,0]).astype(int),0,W-1)].mean()<0.4]
pasto=((1-PERSON)*(1-P['tronco'])*(yy>=600)).astype(np.uint8)
X['pasto']=fur(pasto,45,30,88,12,1.0,0.5)
np.save('persona.npy',np.array(X,dtype=object)); print({k:len(v) for k,v in X.items()})
T=np.load('arbol.npy',allow_pickle=True).item()
o=im.copy(); w=np.full_like(im,250)
for t in (o,w):
    for D_,c in ((RF,(40,80,240)),(X,(40,80,240)),(T,(0,140,255))):
        for k,ps in D_.items():
            for p in ps: cv2.polylines(t,[np.round(np.asarray(p)*4).astype(np.int32)],False,(160,120,60) if k=='cabello' else (0,140,0) if k=='pasto' else c,2,cv2.LINE_AA,shift=2)
cv2.imwrite('retrato_mano.jpg',np.vstack([np.hstack([im,o]),np.hstack([w,np.full_like(im,255)])])[:1600,:])
cv2.imwrite('retrato_mano.jpg',np.hstack([im,o,w]))
