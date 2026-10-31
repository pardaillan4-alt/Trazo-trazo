import cv2,numpy as np
H=W=900
ps=list(np.load('trazos_hd.npy',allow_pickle=True)); WD=list(np.load('wid_hd.npy'))
l=cv2.imread('lineas.png',0); ink=cv2.dilate((l<150).astype(np.uint8),np.ones((5,5),np.uint8))
ff=ink.copy()*255; m=np.zeros((H+2,W+2),np.uint8); cv2.floodFill(ff,m,(890,890),128)
outside=(ff==128).astype(np.uint8); body=1-outside; body=cv2.morphologyEx(body,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
edge=cv2.dilate(outside,np.ones((9,9),np.uint8))&body
yy,xx=np.mgrid[0:H,0:W]
head=((yy<520)|(xx>560)).astype(np.uint8)
eye=np.zeros((H,W),np.uint8); cv2.ellipse(eye,(375,262),(70,50),0,0,360,1,-1)
hoc=np.zeros((H,W),np.uint8); cv2.fillPoly(hoc,[np.array([(560,330),(700,320),(780,420),(780,560),(560,560),(540,420)],np.int32)],1)
G={};GW={}
def put(k,p,w): G.setdefault(k,[]).append(p); GW.setdefault(k,[]).append(float(w))
for p,w in zip(ps,WD):
    x=np.clip(np.round(p[:,0]).astype(int),0,W-1); y=np.clip(np.round(p[:,1]).astype(int),0,H-1)
    e=edge[y,x].mean(); hd=head[y,x].mean()
    if eye[y,x].mean()>0.5: k='ojo'
    elif e>0.5: k='contorno de la cabeza' if hd>0.5 else 'contorno del cuello'
    elif hoc[y,x].mean()>0.5: k='hocico'
    elif hd>0.5: k='manchas de la cara'
    else: k='manchas del cuello'
    put(k,p,w)
np.save('G.npy',np.array(G,dtype=object)); np.save('GW.npy',np.array(GW,dtype=object)); print({k:len(v) for k,v in G.items()})
cols={'contorno de la cabeza':(40,80,240),'ojo':(255,0,0),'hocico':(200,0,200),'manchas de la cara':(0,140,0),'contorno del cuello':(0,120,255),'manchas del cuello':(120,120,0)}
o=np.full((H,W,3),250,np.uint8)
for k,pp in G.items():
    for p in pp: cv2.polylines(o,[np.round(p*4).astype(np.int32)],False,cols[k],2,cv2.LINE_AA,shift=2)
cv2.imwrite('grupos.jpg',o)
ph=cv2.imread('color.png'); hsv=cv2.cvtColor(cv2.GaussianBlur(ph,(0,0),2),cv2.COLOR_BGR2HSV)
REG={'cabeza':(body&head).astype(np.uint8),'cuello':(body&(1-head)).astype(np.uint8)}
REG['cielo']=(1-body).astype(np.uint8)
np.save('REG.npy',np.array(REG,dtype=object))
