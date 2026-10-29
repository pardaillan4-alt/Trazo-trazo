import cv2,numpy as np,sys; sys.path.insert(0,'..')
from facelib import crm
im=cv2.imread('sq.png'); T=np.load('linea.npy',allow_pickle=True).item()
C={}
C['ceja']=[crm([(243,146),(250,139),(262,135),(275,133),(288,135),(293,139)])]
C['ojo']=[crm([(262,178),(267,180),(272,181)]),crm([(205,193),(212,192),(220,188),(226,182)]),crm([(258,173),(266,169),(276,166),(284,162),(289,158)])]
C['cara']=[crm([(190,168),(198,163),(208,161),(218,165),(225,173),(229,185),(233,197),(237,210),(241,221),(246,227),(252,228)]),crm([(196,190),(201,205),(207,220),(215,234),(228,247),(242,257),(258,266),(272,273),(285,279)])]
C['nariz']=[crm([(252,217),(257,212),(262,210),(264,215)])]
C['boca']=[crm([(255,238),(262,236),(270,233),(278,231),(282,229)]),crm([(258,250),(265,250),(272,248)]),crm([(243,242),(246,244)])]
# fuera las líneas automáticas que caen en los ojos, la nariz y la boca
box=lambda p:((p[:,0]>185)&(p[:,0]<300)&(p[:,1]>125)&(p[:,1]<258)).mean()>0.5
for k in list(T): T[k]=[p for p in T[k] if not box(p)]
T['rayos']=[p for p in T.get('rayos',[]) if np.sum(np.hypot(*np.diff(p,axis=0).T))>24]
np.save('cara_mano.npy',np.array(C,dtype=object)); np.save('linea_f.npy',np.array(T,dtype=object))
x0,y0,x1,y1,f=185,110,330,290,4
z=cv2.resize(im[y0:y1,x0:x1],None,fx=f,fy=f,interpolation=cv2.INTER_CUBIC); o=z.copy()
for D in (C,T):
    for k,ps in D.items():
        for p in ps: cv2.polylines(o,[np.round((np.asarray(p)-[x0,y0])*f*4).astype(np.int32)],False,(40,40,230),2,cv2.LINE_AA,shift=2)
cv2.imwrite('cara_cmp.jpg',np.hstack([z,o]))
o=im.copy(); w=np.full_like(im,250)
for t in (o,w):
    for D in (C,T):
        for k,ps in D.items():
            for p in ps: cv2.polylines(t,[np.round(np.asarray(p)*4).astype(np.int32)],False,(40,80,240),1,cv2.LINE_AA,shift=2)
cv2.imwrite('gua_cmp.jpg',np.hstack([im,o,w]))
