"""Silueta del león (leon_mask.png, escala 900): lo encerrado por su contorno en el dibujo de líneas, más el contorno completo."""
import cv2,numpy as np
L=cv2.imread('gris_big.png',0); BH,BW=L.shape; s=BW/900
X0,Y0,X1,Y1=[int(v*s) for v in (280,52,620,482)]
c=L[Y0:Y1,X0:X1]; ink=cv2.dilate((c<140).astype(np.uint8),np.ones((5,5),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(1-ink,4)
borde=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]).tolist())
den=np.isin(lab,[i for i in range(1,n) if i not in borde]).astype(np.uint8)
den=cv2.morphologyEx(den,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
cs,_=cv2.findContours(den,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cs=sorted(cs,key=cv2.contourArea,reverse=True)
m=np.zeros_like(den); cv2.drawContours(m,cs[:2],-1,1,-1)          # la cabeza con el cuerpo, y la cola
m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41)))   # todo el grosor del contorno, con un poquito de aire
full=np.zeros((BH,BW),np.uint8); full[Y0:Y1,X0:X1]=m
cv2.imwrite('leon_mask.png',(cv2.resize(full*255,(900,502),interpolation=cv2.INTER_AREA)>127).astype(np.uint8)*255)
