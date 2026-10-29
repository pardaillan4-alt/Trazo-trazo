import cv2,numpy as np
from facelib import resamp
im=cv2.imread('sq.png'); H,W=im.shape[:2]; hsv=cv2.cvtColor(cv2.GaussianBlur(im,(0,0),1.5),cv2.COLOR_BGR2HSV)
ps=list(np.load('lineas2.npy',allow_pickle=True)); E=list(np.load('espadas.npy',allow_pickle=True))
em=np.zeros((H,W),np.uint8)
for p in E: cv2.fillPoly(em,[np.round(p).astype(np.int32)],1)
em=cv2.dilate(em,np.ones((9,9),np.uint8))
inside=lambda m,p:m[np.clip(np.round(p[:,1]).astype(int),0,H-1),np.clip(np.round(p[:,0]).astype(int),0,W-1)].mean()
ps=[p for p in ps if inside(em,p)<0.5]
h,s,v=hsv[:,:,0].astype(int),hsv[:,:,1].astype(int),hsv[:,:,2].astype(int)
dark=(v<70).astype(np.uint8); n,lab,st,_=cv2.connectedComponentsWithStats(dark); hat=(lab==1+np.argmax(st[1:,4])).astype(np.uint8)
red=(((h<8)|(h>168))&(s>120)&(v>120)).astype(np.uint8)
pink=(((h>150)|(h<8))&(s>30)&(s<=120)&(v>150)).astype(np.uint8)
P={}
patch=np.zeros((H,W),np.uint8); cv2.ellipse(patch,(255,515),(90,55),-10,0,360,1,-1)
skull=np.zeros((H,W),np.uint8); cv2.ellipse(skull,(440,250),(80,70),0,0,360,1,-1)
eye=np.zeros((H,W),np.uint8); cv2.circle(eye,(378,540),38,1,-1)
NAMES=['sombrero','calavera','panuelo','parche','ojo','cuerpo','tentaculos']
for p in ps:
    q=resamp(p,2.0); t=np.gradient(q,axis=0); t/=np.linalg.norm(t,axis=1,keepdims=True)+1e-6; n_=np.stack([-t[:,1],t[:,0]],1)
    lab_=[]
    for j in range(len(q)):
        pts=np.array([q[j]+n_[j]*o for o in (-7,-4,4,7)]); x=np.clip(pts[:,0].astype(int),0,W-1); y=np.clip(pts[:,1].astype(int),0,H-1)
        X,Y=int(np.clip(q[j][0],0,W-1)),int(np.clip(q[j][1],0,H-1))
        if skull[Y,X]: k=1
        elif eye[Y,X]: k=4
        elif red[y,x].any(): k=2
        elif patch[Y,X]: k=3
        elif (hat[y,x].any() and Y<520) or Y<300: k=0
        elif Y>650: k=6
        else: k=5
        lab_.append(k)
    lab_=np.array(lab_)
    for _ in range(2):
        l2=lab_.copy()
        for j in range(len(lab_)): w_=lab_[max(0,j-4):j+5]; l2[j]=np.bincount(w_).argmax()
        lab_=l2
    i=0
    while i<len(q):
        j=i
        while j<len(q) and lab_[j]==lab_[i]: j+=1
        if j-i>=5: P.setdefault(NAMES[lab_[i]],[]).append(q[max(0,i-1):min(len(q),j+1)])
        i=j
P['cuerpo']=[q for q in P.get('cuerpo',[]) if q[:,1].mean()>450 or (q[:,0].mean()>150 and q[:,0].mean()<600)]
P['espadas']=E
np.save('P.npy',np.array(P,dtype=object)); print({k:len(v) for k,v in P.items()})
cols={'sombrero':(0,0,0),'calavera':(150,150,150),'espadas':(0,150,0),'panuelo':(0,0,220),'parche':(200,0,200),'ojo':(255,0,0),'cuerpo':(255,0,255),'tentaculos':(0,140,255)}
w=np.full_like(im,250)
for k,pp in P.items():
    for p in pp: cv2.polylines(w,[np.round(p*4).astype(np.int32)],False,cols.get(k,(0,0,0)),2,cv2.LINE_AA,shift=2)
cv2.imwrite('partes.jpg',w)
