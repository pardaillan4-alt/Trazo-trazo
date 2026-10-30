import cv2,numpy as np
im=cv2.imread('color.png'); H,W=im.shape[:2]; lm=np.load('lm.npy')
ps=list(np.load('trazos_hd.npy',allow_pickle=True))
OVAL=[10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
def poly(p): m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
face=poly(lm[OVAL]); face=cv2.dilate(face,np.ones((9,9),np.uint8))
def box(ids,pad): p=lm[ids]; x0,y0=p.min(0)-pad; x1,y1=p.max(0)+pad; m=np.zeros((H,W),np.uint8); m[int(y0):int(y1),int(x0):int(x1)]=1; return m
from lmidx import C
ojos=box(C['ojoA_sup']+C['ojoA_inf']+C['cejaA_sup']+C['cejaA_inf'],8)|box(C['ojoB_sup']+C['ojoB_inf']+C['cejaB_sup']+C['cejaB_inf'],8)
nariz=box([129,98,97,2,326,327,358,64,294,48,278,4,195,5],6)
boca=box(C['labio_sup']+C['labio_inf'],6)
y_n=lm[2][1]
beard=face.copy(); beard[:int(y_n)+4]=0; beard=cv2.dilate(beard,np.ones((15,15),np.uint8))&(1-boca)
hair=poly([(300,60),(380,30),(480,30),(580,70),(625,150),(640,280),(665,370),(640,410),(560,395),(520,330),(390,350),(330,410),(275,395),(300,300),(305,200)])
neck=poly([(380,290),(505,262),(525,420),(360,440)])
robe=poly([(150,514),(250,395),(340,375),(570,365),(720,380),(850,514)])
nub=poly([(0,148),(40,145),(90,155),(130,175),(160,215),(200,250),(250,270),(290,300),(310,340),(290,420),(200,514),(0,514)])|poly([(900,190),(860,195),(820,215),(790,250),(740,270),(690,280),(640,310),(630,380),(760,400),(900,514)])
G={}; order=[('ojos y cejas',ojos),('nariz y boca',nariz|boca),('barba',beard),('contorno de la cara',face),('cabello',hair),('cuello',neck),('tunica y manto',robe)]
for p in ps:
    x=np.clip(np.round(p[:,0]).astype(int),0,W-1); y=np.clip(np.round(p[:,1]).astype(int),0,H-1); k=None
    for nm,m in order:
        if m[y,x].mean()>0.5: k=nm; break
    if k is None:
        k='nubes' if nub[y,x].mean()>0.5 else 'aureola y rayos'
    G.setdefault(k,[]).append(p)
np.save('G_hd.npy',np.array(G,dtype=object)); print({k:len(v) for k,v in G.items()})
cols={'ojos y cejas':(255,0,0),'nariz y boca':(200,0,200),'barba':(0,120,255),'contorno de la cara':(40,80,240),'cabello':(60,60,60),'cuello':(0,128,128),'tunica y manto':(0,150,0),'aureola y rayos':(150,150,150),'nubes':(255,150,0)}
w_=np.full((H,W,3),250,np.uint8)
for k,pp in G.items():
    for p in pp: cv2.polylines(w_,[np.round(p*4).astype(np.int32)],False,cols[k],1,cv2.LINE_AA,shift=2)
cv2.imwrite('grupos_hd.jpg',cv2.resize(w_,None,fx=1.6,fy=1.6))
REG={'cara':(face|neck).astype(np.uint8),'cabello y barba':((hair|beard)&(1-face)|beard).astype(np.uint8),'tunica':robe&(1-hair)&(1-neck)}
np.save('REG.npy',np.array(REG,dtype=object))
