import cv2,numpy as np,sys; sys.path.insert(0,'..')
from tonal import smooth_closed,open_part
from scipy.ndimage import gaussian_filter1d as g1
im=cv2.imread('sq.png'); L=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32); H,W=L.shape
exec(open('gen.py').read().split("def poly(p):")[1].split("order=")[0].replace("\n    m=np.zeros","def poly(p):\n    m=np.zeros",1) if False else "")
def poly(p):
    m=np.zeros((H,W),np.uint8);cv2.fillPoly(m,[np.array(p,np.int32)],1);return m
src=open('gen.py').read(); a=src.index('PERSON=poly('); b=src.index('order=')
def ell(c,a,ang=0):
    m=np.zeros((H,W),np.uint8);cv2.ellipse(m,c,a,ang,0,360,1,-1);return m
exec(src[a:b])
person=PERSON.astype(np.uint8); R_tronco=P['tronco'].astype(np.uint8)
tree=(1-cv2.dilate(person,np.ones((7,7),np.uint8)))
yy=np.mgrid[0:H,0:W][0]
def cont(mask,min_area,sig,eps=0):
    cs,_=cv2.findContours(mask.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    return [smooth_closed(c[:,0,:],sig) for c in cs if cv2.contourArea(c)>=min_area]
b4=cv2.GaussianBlur(L,(0,0),4); b6=cv2.GaussianBlur(L,(0,0),6)
branch=((b4<120)&(tree>0)&(yy<600)).astype(np.uint8); branch=cv2.morphologyEx(branch,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(branch); branch=np.isin(lab,[i for i in range(1,n) if st[i,4]>400]).astype(np.uint8)
b8=cv2.GaussianBlur(L,(0,0),7)
leaf=((b8<205)&(tree>0)&(yy<615)).astype(np.uint8); leaf=cv2.morphologyEx(leaf,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
TR=cv2.dilate(R_tronco,np.ones((31,31),np.uint8))
trunk=((b6<160)&(TR>0)&(tree>0)&(yy>250)).astype(np.uint8); trunk=cv2.morphologyEx(trunk,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(trunk); trunk=(lab==1+np.argmax(st[1:,4])).astype(np.uint8)
leaf=(leaf*(1-cv2.dilate(trunk,np.ones((9,9),np.uint8)))).astype(np.uint8)
T={}
PD15=cv2.dilate(person,np.ones((31,31),np.uint8))
TRC=cv2.dilate(R_tronco,np.ones((21,21),np.uint8))*(yy>235)
PD15=np.maximum(PD15,TRC.astype(np.uint8))
def no_border(c): keep=(c[:,0]>3)&(c[:,0]<W-4)&(c[:,1]>3)&(c[:,1]<H-4)&(PD15[np.clip(c[:,1].astype(int),0,H-1),np.clip(c[:,0].astype(int),0,W-1)]==0); return open_part(c,keep)
T['ramas']=[s for c in cont(branch,400,2.5) for s in no_border(c)]
T['hojas']=[s for c in cont(leaf,1500,4) for s in no_border(c)]
sys.path.insert(0,'..'); from facelib import crm
T['tronco']=[crm([(399,105),(399,180),(398,240)]),crm([(345,380),(340,400),(337,450),(335,500),(328,535),(320,560),(310,582),(300,600),(287,622),(275,640),(258,655),(240,670),(215,690)]),
             crm([(400,450),(400,520),(400,600),(399,660),(400,700),(397,740),(386,780)])]
T['ramas']=[r for r in T['ramas'] if trunk[np.clip(r[:,1].astype(int),0,H-1),np.clip(r[:,0].astype(int),0,W-1)].mean()<0.6]
print({k:len(v) for k,v in T.items()}, sum(len(x) for x in T['hojas']))
np.save('arbol.npy',np.array(T,dtype=object))
o=im.copy(); w=np.full_like(im,250)
for t in (o,w):
    for p in T['hojas']: cv2.polylines(t,[np.round(p*4).astype(np.int32)],False,(0,140,255),2,cv2.LINE_AA,shift=2)
    for p in T['tronco']: cv2.polylines(t,[np.round(p*4).astype(np.int32)],False,(200,0,200),2,cv2.LINE_AA,shift=2)
    for p in T['ramas']: cv2.polylines(t,[np.round(p*4).astype(np.int32)],False,(40,80,240),2,cv2.LINE_AA,shift=2)
cv2.imwrite('arbol_cmp.jpg',np.vstack([o,w]))
