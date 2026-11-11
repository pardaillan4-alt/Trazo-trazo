import cv2,numpy as np,sys
from tonal import smooth_closed
TH=int(sys.argv[1]); big=cv2.imread('gris_big.png',0); s=900/big.shape[1]
ink=(big<TH).astype(np.uint8); dt=cv2.distanceTransform(ink,cv2.DIST_L2,5)
n,lab,st,_=cv2.connectedComponentsWithStats((dt>5).astype(np.uint8))
ps=list(np.load('trazos_hd.npy',allow_pickle=True)); W=list(np.load('wid_hd.npy')); add=[]
for k in range(1,n):
    if st[k,4]<150: continue
    blob=cv2.dilate((lab==k).astype(np.uint8),np.ones((11,11),np.uint8))&ink
    x,y,w,h,_=cv2.boundingRect(blob)+(0,)
    x0,y0,x1,y1=(x-3)*s,(y-3)*s,(x+w+3)*s,(y+h+3)*s
    keep=[(p,ww) for p,ww in zip(ps,W) if not (((p[:,0]>x0)&(p[:,0]<x1)&(p[:,1]>y0)&(p[:,1]<y1)).mean()>0.7 and len(p)<200)]
    ps=[a for a,_ in keep]; W=[b for _,b in keep]
    cs,_=cv2.findContours(blob,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
    for c in cs:
        if len(c)<12: continue
        q=smooth_closed(c[:,0,:].astype(np.float32),1.5); add.append(np.vstack([q,q[:1]])*s)
ps+=add; W+=[0.55]*len(add)
np.save('trazos_hd.npy',np.array(ps,dtype=object)); np.save('wid_hd.npy',np.array(W)); print('manchas',len(add))
