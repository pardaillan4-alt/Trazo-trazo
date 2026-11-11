"""Trazos de una zona con su número: python3 ver_idx.py carpeta out.jpg x0,y0,x1,y1,f"""
import cv2,numpy as np,sys
d,out,box=sys.argv[1],sys.argv[2],sys.argv[3]
g=cv2.imread(f'{d}/gris_big.png',0); s=900/g.shape[1]
ps=list(np.load(f'{d}/trazos_hd.npy',allow_pickle=True))
x0,y0,x1,y1,f=[float(v) for v in box.split(',')]
a=cv2.resize(g[int(y0/s):int(y1/s),int(x0/s):int(x1/s)],(int((x1-x0)*f),int((y1-y0)*f)),interpolation=cv2.INTER_CUBIC)
o=(cv2.cvtColor(a,cv2.COLOR_GRAY2BGR)*0.5+127).astype(np.uint8)
rng=np.random.default_rng(1)
for i,p in enumerate(ps):
    q=(p-[x0,y0])*f
    if q[:,0].max()<0 or q[:,1].max()<0 or q[:,0].min()>o.shape[1] or q[:,1].min()>o.shape[0]: continue
    c=tuple(int(v) for v in rng.integers(0,200,3))
    cv2.polylines(o,[np.round(q*4).astype(np.int32)],False,c,2,cv2.LINE_AA,shift=2)
    m=q[len(q)//2]; L=float(np.sum(np.hypot(*np.diff(p,axis=0).T)))
    cv2.putText(o,f'{i}',(int(m[0])+3,int(m[1])-3),0,0.45,c,1)
for x in np.arange(np.ceil(x0/5)*5,x1,5): X=int((x-x0)*f); cv2.putText(o,f'{x:g}',(X,10),0,0.35,(0,0,255),1)
for y in np.arange(np.ceil(y0/5)*5,y1,5): Y=int((y-y0)*f); cv2.putText(o,f'{y:g}',(0,Y),0,0.35,(0,0,255),1)
cv2.imwrite(out,o)
