import cv2,numpy as np,sys
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
d=sys.argv[1]; im=cv2.imread(f'{d}/sq.png'); R=np.load(f'{d}/rostro.npy',allow_pickle=True).item(); lm=np.load(f'{d}/lm.npy')
def box(ids,pad):
    p=lm[ids]; x0,y0=p.min(0)-pad; x1,y1=p.max(0)+pad; return [int(x0),int(y0),int(x1),int(y1)]
from lmidx import C
B={'ojoA':box(C['ojoA_sup']+C['cejaA_sup']+C['ojoA_inf'],14),'ojoB':box(C['ojoB_sup']+C['cejaB_sup']+C['ojoB_inf'],14),
   'nariz':box([129,98,97,2,326,327,358,64,294,48,278,4,195],12),'boca':box(C['labio_sup']+C['labio_inf'],10)}
for k,(x0,y0,x1,y1) in B.items():
    f=max(3,int(560/(x1-x0))); z=cv2.resize(im[y0:y1,x0:x1],None,fx=f,fy=f,interpolation=cv2.INTER_CUBIC); o=z.copy()
    for x in range(x0-x0%10+10,x1,10): cv2.line(z,((x-x0)*f,0),((x-x0)*f,6),(0,140,255),1); cv2.putText(z,str(x),((x-x0)*f+1,16),0,0.3,(200,0,0),1)
    for y in range(y0-y0%10+10,y1,10): cv2.line(z,(0,(y-y0)*f),(6,(y-y0)*f),(0,140,255),1); cv2.putText(z,str(y),(8,(y-y0)*f+4),0,0.3,(200,0,0),1)
    for ps in R.values():
        for p in ps: cv2.polylines(o,[np.round((np.asarray(p)-[x0,y0])*f*4).astype(np.int32)],False,(40,80,240),2,cv2.LINE_AA,shift=2)
    cv2.imwrite(f'{d}/z_{k}.jpg',np.vstack([z,o]))
print(B)
