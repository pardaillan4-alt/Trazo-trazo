from snap import *
from scipy.signal import find_peaks
F=np.load('F.npy',allow_pickle=True).item(); S=np.load('S.npy',allow_pickle=True).item()
L=cv2.cvtColor(cv2.GaussianBlur(im,(0,0),2),cv2.COLOR_BGR2GRAY).astype(np.float32)
vm=np.zeros((H,W),np.uint8); poly=np.vstack([S['velo_izq'][0],S['velo_azul'][0][::-1]]).astype(np.int32)
cv2.fillPoly(vm,[poly],1); vm[:, :]=vm; vm=cv2.dilate(vm,np.ones((15,15),np.uint8))
mant=np.zeros((H,W),np.uint8); cv2.fillPoly(mant,[np.array([(0,640),(60,600),(130,565),(170,560),(170,1136),(0,1136)],np.int32)],1)
cv2.fillPoly(mant,[np.array([(639,575),(560,535),(500,470),(470,600),(639,1136)],np.int32)],1)
block=np.maximum(vm,cv2.dilate(mant,np.ones((15,15),np.uint8)))
C=np.array([300,470.0]); out=[]
for r in (300,360):
    angs=np.radians(np.arange(-179,0,0.25)); P=C+r*np.stack([np.cos(angs),np.sin(angs)],1)
    ok=(P[:,0]>=0)&(P[:,0]<W)&(P[:,1]>=0)
    v=np.full(len(angs),255.0); v[ok]=map_coordinates(L,[P[ok,1],P[ok,0]],order=1)
    bl=np.zeros(len(angs),bool); bl[ok]=block[P[ok,1].astype(int),P[ok,0].astype(int)]>0; v[bl]=255
    pk,_=find_peaks(-v,prominence=18,distance=10)
    out.append(set(np.round(np.degrees(angs[pk])).astype(int)))
angles=sorted(out[0]|out[1]); merged=[]
for a in angles:
    if not merged or a-merged[-1]>3: merged.append(a)
lines=[]
for a in merged:
    d=np.array([np.cos(np.radians(a)),np.sin(np.radians(a))]); pts=[C+d*r for r in np.arange(150,800,2)]
    pts=[p for p in pts if 0<=p[0]<W and 0<=p[1]<H]
    seg=[p for p in pts if block[int(p[1]),int(p[0])]==0]
    if len(seg)<15: continue
    # el tramo fuera del velo, cortado donde se aclara mucho (fin de la raya)
    seg=np.array(seg,np.float32); lines.append(seg[::3])
F['rayos']=lines; np.save('F.npy',np.array(F,dtype=object)); print(len(lines),merged)
show(F,'final.jpg')
