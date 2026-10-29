import cv2,numpy as np,sys
from facelib import resamp,crm
from tonal import smooth_closed
from scipy.ndimage import gaussian_filter1d as g1
from skimage.morphology import skeletonize
src=open('../guadalupe/linea.py').read()
exec("def trace_sk"+src.split("def trace_sk")[1].split("def split_turns")[0])
exec("def split_turns"+src.split("def split_turns")[1].split("def strokes")[0])
exec("def join"+src.split("def join")[1].split("THR=")[0])
im=cv2.imread('sq.png'); H,W=im.shape[:2]
hsv=cv2.cvtColor(cv2.GaussianBlur(im,(0,0),0.8),cv2.COLOR_BGR2HSV)
ink=(hsv[:,:,2]<80).astype(np.uint8)
ink=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(ink); ink=np.isin(lab,[i for i in range(1,n) if st[i,4]>40]).astype(np.uint8)
blob=cv2.morphologyEx(ink,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
n,lab,st,_=cv2.connectedComponentsWithStats(blob); blob=np.isin(lab,[i for i in range(1,n) if st[i,4]>150]).astype(np.uint8)
thin=(ink*(1-cv2.dilate(blob,np.ones((5,5),np.uint8)))).astype(np.uint8)
ps=[]
for p in trace_sk(skeletonize(thin>0),10):
    p=np.stack([g1(p[:,0],2.5,mode='nearest'),g1(p[:,1],2.5,mode='nearest')],1)
    ps+=[resamp(q,1.5) for q in split_turns(p,60,10)]
ps=[p for p in ps if np.sum(np.hypot(*np.diff(p,axis=0).T))>12]
ps=join(ps,10,0.7)
cs,hier=cv2.findContours(blob,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
for c in cs:
    if cv2.contourArea(c)<60: continue
    s=smooth_closed(c[:,0,:],2.5); ps.append(np.vstack([s,s[:1]]))
np.save('lineas.npy',np.array(ps,dtype=object)); print(len(ps))
o=im.copy(); w=np.full_like(im,250)
for t in (o,w):
    for p in ps: cv2.polylines(t,[np.round(p*4).astype(np.int32)],False,(40,80,240) if t is w else (0,255,255),2,cv2.LINE_AA,shift=2)
cv2.imwrite('lineas.jpg',np.hstack([im,o,w]))
