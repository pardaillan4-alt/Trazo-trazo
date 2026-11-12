"""Polígonos ajustados a cada mano y a cada pie (la envolvente de sus trazos), para buscar ahí el color de la piel.
Así no se cuela el fondo que está junto a los dedos."""
import numpy as np,cv2,json
c=json.load(open('cfg.json')); G=np.load('G.npy',allow_pickle=True).item(); H=c['H']; W=900
pols=[]
for paso in ('Las manos','Los pies'):
    for sh in c['zonas'][paso]:
        zm=np.zeros((H,W),np.uint8); cv2.fillPoly(zm,[np.array(sh[1],np.int32)],1)
        pts=[]
        for p in G.get(paso,[]):
            xi=np.clip(np.round(p[:,0]).astype(int),0,W-1); yi=np.clip(np.round(p[:,1]).astype(int),0,H-1)
            if zm[yi,xi].mean()>0.5: pts.append(p)
        if not pts: continue
        pts=np.vstack(pts).astype(np.float32); hull=cv2.convexHull(pts)[:,0,:]
        m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.round(hull).astype(np.int32)],1)
        m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
        cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE); cc=max(cs,key=cv2.contourArea)[:,0,:]
        pols.append(cc.tolist())
c['regiones'][1][1]['mas_color']['pol']=pols
json.dump(c,open('cfg.json','w'),ensure_ascii=False,indent=1); print('polígonos',len(pols))
