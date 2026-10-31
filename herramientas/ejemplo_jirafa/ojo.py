import cv2,numpy as np
from tonal import smooth_closed
big=cv2.imread('/mnt/user-data/attachments/2a8fc66a-2bf4-5ad0-b410-99770220e857/cee5f759-image.jpg',0); s=900/big.shape[1]
ink=(big<140).astype(np.uint8); dt=cv2.distanceTransform(ink,cv2.DIST_L2,5)
n,lab,st,cen=cv2.connectedComponentsWithStats((dt>4).astype(np.uint8))
k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]; print('ojo',x,y,w,h,a)
blob=cv2.dilate((lab==k).astype(np.uint8),np.ones((9,9),np.uint8))&ink
cs,hier=cv2.findContours(blob,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
ojo=[]
for c in cs:
    if len(c)<10: continue
    q=smooth_closed(c[:,0,:].astype(np.float32),1.5); ojo.append(np.vstack([q,q[:1]])*s)
print(len(ojo))
ps=list(np.load('trazos_hd.npy',allow_pickle=True)); W=list(np.load('wid_hd.npy'))
x0,y0,x1,y1=(x-4)*s,(y-4)*s,(x+w+4)*s,(y+h+4)*s
keep=[(p,ww) for p,ww in zip(ps,W) if not ((p[:,0]>x0)&(p[:,0]<x1)&(p[:,1]>y0)&(p[:,1]<y1)).mean()>0.6]
ps=[p for p,_ in keep]+ojo; W=[w_ for _,w_ in keep]+[0.5]*len(ojo)
np.save('trazos_hd.npy',np.array(ps,dtype=object)); np.save('wid_hd.npy',np.array(W))
o=np.full((140,200,3),250,np.uint8)
for p in ojo: cv2.polylines(o,[np.round((p-[x0-20,y0-20])*1*4).astype(np.int32)],False,(40,80,240),1,cv2.LINE_AA,shift=2)
cv2.imwrite('ojo.jpg',cv2.resize(o,None,fx=4,fy=4))
