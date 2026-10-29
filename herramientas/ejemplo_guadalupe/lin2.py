import cv2,numpy as np,sys; sys.path.insert(0,'..')
exec(open('linea.py').read().split("THR=")[0])
from skimage.morphology import skeletonize
b=cv2.GaussianBlur(L,(0,0),1.0); bg=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((11,11),np.uint8)),(0,0),4)
ink=(((bg-b)>26)&(b<185)).astype(np.uint8)
ink=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
n,lab,st,_=cv2.connectedComponentsWithStats(ink); ink=np.isin(lab,[i for i in range(1,n) if st[i,4]>30]).astype(np.uint8)
ps=[]
for p in trace_sk(skeletonize(ink>0),10):
    p=np.stack([g1(p[:,0],2.5,mode='nearest'),g1(p[:,1],2.5,mode='nearest')],1)
    ps+= [resamp(q,1.5) for q in split_turns(p,60,10)]
ps=join(ps,10,0.75)
ps=[p for p in ps if np.sum(np.hypot(*np.diff(p,axis=0).T))>16]
T={}
for p in ps:
    x,y=np.clip(np.round(p[len(p)//2]).astype(int),0,[W-1,H-1]); k=next((k for k in RG if RG[k][y,x]),'rayos'); T.setdefault(k,[]).append(p)
np.save('linea.npy',np.array(T,dtype=object)); print({k:len(v) for k,v in T.items()})
o=im.copy(); w=np.full_like(im,250)
for t in (o,w):
    for k,pp in T.items():
        for p in pp: cv2.polylines(t,[np.round(p*4).astype(np.int32)],False,(40,80,240),1,cv2.LINE_AA,shift=2)
cv2.imwrite('linea_cmp.jpg',np.hstack([im,o,w]))
