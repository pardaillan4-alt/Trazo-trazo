"""Manchas de la jirafa: se miden sobre la imagen gris (relleno gris dentro de la jirafa) y se vuelven contornos cerrados y suaves.
Escribe manchas.npy (trazos en escala 900)."""
import cv2,numpy as np
g=cv2.imread('gris_big.png',0).astype(np.float32); BH,BW=g.shape; s=BW/900
X0,Y0,X1,Y1=[int(v*s) for v in (338,22,612,486)]
c=g[Y0:Y1,X0:X1]; h,w=c.shape
ink=cv2.dilate((c<110).astype(np.uint8),np.ones((3,3),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(1-ink,4)
borde=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]).tolist())
den=np.isin(lab,[i for i in range(1,n) if i not in borde]).astype(np.uint8)        # dentro de la jirafa (no toca la orilla del recuadro)
# fuera las mariposas (sus alas también son huecos cerrados)
for bx in [(338,225,372,265),(548,140,612,215)]:
    a,b_,cc,d=[int(v*s) for v in bx]; den[b_-Y0:d-Y0,a-X0:cc-X0]=0
b=cv2.GaussianBlur(c,(0,0),3)
m=((b<232)&(b>150)).astype(np.uint8)&cv2.erode(den,np.ones((7,7),np.uint8))
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))      # a la orilla real de la mancha
cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); out=[]; vis=cv2.cvtColor(c.astype(np.uint8),cv2.COLOR_GRAY2BGR)
for k in cs:
    A=cv2.contourArea(k); hull=cv2.contourArea(cv2.convexHull(k)) or 1
    (_,_),(ra,rb),_=cv2.minAreaRect(k)
    if A<120 or A>9000 or A/hull<0.82 or max(ra,rb)>2.2*max(1,min(ra,rb)): 
        cv2.drawContours(vis,[k],-1,(255,0,0),1); continue
    p=k[:,0,:].astype(np.float32); 
    if len(p)>12:
        from scipy.ndimage import gaussian_filter1d as g1
        p=np.stack([g1(p[:,0],3,mode='wrap'),g1(p[:,1],3,mode='wrap')],1)
    p=cv2.approxPolyDP(p.reshape(-1,1,2),0.6,True).reshape(-1,2); p=np.vstack([p,p[:1]])
    q=((p+[X0,Y0])/s).astype(np.float32); cx,cy=q[:-1].mean(0)
    if cy<80 or cy>455 or (342<=cx<=398 and 58<=cy<=118) or (500<=cx<=568 and 72<=cy<=132):     # cuernos, orejas y pezuñas: no son manchas
        cv2.polylines(vis,[p.astype(np.int32)],False,(0,160,0),2); continue
    out.append(q); cv2.polylines(vis,[p.astype(np.int32)],False,(0,0,255),2)
np.save('manchas.npy',np.array(out,dtype=object),allow_pickle=True); print('manchas',len(out))
cv2.imwrite('manchas_chk.jpg',cv2.resize(vis,None,fx=0.6,fy=0.6))
