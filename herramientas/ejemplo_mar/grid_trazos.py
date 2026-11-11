import cv2,numpy as np,sys
d=sys.argv[1]; f=2.0; H=502
ps=list(np.load(f'{d}/trazos_hd.npy',allow_pickle=True))
o=np.full((int(H*f),int(900*f),3),255,np.uint8)
for x in range(0,900,25):
    cv2.line(o,(int(x*f),0),(int(x*f),int(H*f)),(170,210,255) if x%50 else (60,160,255),1)
    if x%50==0: cv2.putText(o,str(x),(int(x*f)+2,14),0,0.45,(0,0,200),1)
for y in range(0,H,25):
    cv2.line(o,(0,int(y*f)),(int(900*f),int(y*f)),(170,210,255) if y%50 else (60,160,255),1)
    if y%50==0: cv2.putText(o,str(y),(2,int(y*f)-3),0,0.45,(0,0,200),1)
for p in ps: cv2.polylines(o,[np.round(p*f*4).astype(np.int32)],False,(60,60,60),1,cv2.LINE_AA,shift=2)
cv2.imwrite(f'{d}/grid_trazos.jpg',o)
