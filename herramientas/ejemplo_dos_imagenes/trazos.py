import cv2,numpy as np
from facelib import resamp
from scipy.ndimage import gaussian_filter1d as g1
from skimage.morphology import skeletonize
src=open('../guadalupe/linea.py').read()
exec("def trace_sk"+src.split("def trace_sk")[1].split("def split_turns")[0])
exec("def split_turns"+src.split("def split_turns")[1].split("def strokes")[0])
col=cv2.imread('color.png'); H,W=col.shape[:2]
l=cv2.resize(cv2.imread('/mnt/user-data/attachments/2a8fc66a-2bf4-5ad0-b410-99770220e857/bbf7e3ff-image.jpg',0),(W,H),interpolation=cv2.INTER_CUBIC)
cv2.imwrite('lineas.png',l)
ink=(l<150).astype(np.uint8); ink[:3]=0; ink[-3:]=0; ink[:,:3]=0; ink[:,-3:]=0
sk=skeletonize(ink>0)
ps=[]
for p in trace_sk(sk,6):
    p=np.stack([g1(p[:,0],1.5,mode='nearest'),g1(p[:,1],1.5,mode='nearest')],1)
    ps+=[resamp(q,1.2) for q in split_turns(p,70,6)]
ps=[p for p in ps if np.sum(np.hypot(*np.diff(p,axis=0).T))>5]
# estrellas: componentes chicos con forma de estrella
n,lab,st,cen=cv2.connectedComponentsWithStats(ink)
starm=np.zeros((H,W),np.uint8)
for i in range(1,n):
    x,y,w,h,a=st[i]
    if 18<w<45 and 18<h<45 and a<350: starm[lab==i]=1
np.save('trazos.npy',np.array(ps,dtype=object)); np.save('starm.npy',starm); print(len(ps),starm.sum())
w_=np.full_like(col,250)
for p in ps: cv2.polylines(w_,[np.round(p*4).astype(np.int32)],False,(40,80,240),1,cv2.LINE_AA,shift=2)
cv2.imwrite('trazos.jpg',w_)
