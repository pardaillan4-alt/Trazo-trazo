import cv2,numpy as np
from tonal import smooth_closed,open_part
im=cv2.imread('sq.png'); H,W=im.shape[:2]; hsv=cv2.cvtColor(cv2.GaussianBlur(im,(0,0),1.5),cv2.COLOR_BGR2HSV)
ps=list(np.load('lineas.npy',allow_pickle=True))
area=lambda p:cv2.contourArea(np.asarray(p,np.float32)) if np.allclose(p[0],p[-1]) else 1e9
ps=[p for p in ps if not ((p[:,0]>700)&(p[:,1]>780)).mean()>0.3 and area(p)>120]
# espadas: el mango dorado y la hoja, por color, solo en las esquinas de arriba
gold=((hsv[:,:,0]>15)&(hsv[:,:,0]<40)&(hsv[:,:,1]>90)&(hsv[:,:,2]>90)).astype(np.uint8)
zone=np.zeros((H,W),np.uint8); zone[60:300,30:200]=1; zone[60:320,560:778]=1
gold=cv2.morphologyEx(gold*zone,cv2.MORPH_OPEN,np.ones((3,3),np.uint8)); gold=cv2.morphologyEx(gold,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
cs,_=cv2.findContours(gold,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); esp=[]
for c in cs:
    if cv2.contourArea(c)<150: continue
    s=smooth_closed(c[:,0,:],2.5); esp.append(np.vstack([s,s[:1]]))
blade=((hsv[:,:,1]<60)&(hsv[:,:,2]>110)).astype(np.uint8)*zone
blade=cv2.morphologyEx(blade,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
cs,_=cv2.findContours(blade,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
for c in cs:
    if cv2.contourArea(c)<60: continue
    s=smooth_closed(c[:,0,:],2); esp.append(np.vstack([s,s[:1]]))
# las líneas viejas que caen dentro de las espadas se van (para no repetir)
em=np.zeros((H,W),np.uint8)
for p in esp: cv2.fillPoly(em,[np.round(p).astype(np.int32)],1)
em=cv2.dilate(em,np.ones((7,7),np.uint8))
ps=[p for p in ps if em[np.clip(np.round(p[:,1]).astype(int),0,H-1),np.clip(np.round(p[:,0]).astype(int),0,W-1)].mean()<0.6]
np.save('lineas2.npy',np.array(ps,dtype=object)); np.save('espadas.npy',np.array(esp,dtype=object)); print(len(ps),len(esp))
o=im.copy(); w=np.full_like(im,250)
for t in (o,w):
    for p in ps: cv2.polylines(t,[np.round(p*4).astype(np.int32)],False,(40,80,240),2,cv2.LINE_AA,shift=2)
    for p in esp: cv2.polylines(t,[np.round(p*4).astype(np.int32)],False,(0,160,0),2,cv2.LINE_AA,shift=2)
cv2.imwrite('lineas.jpg',np.hstack([im,o,w]))
