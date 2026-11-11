"""Comparación de cerca: referencia | líneas encima | solo líneas.  python3 cmp.py carpeta out.jpg x0,y0,x1,y1[,f] ..."""
import cv2,numpy as np,sys
d=sys.argv[1]; out=sys.argv[2]
g=cv2.imread(f'{d}/gris_big.png',0); s=900/g.shape[1]
ps=list(np.load(f'{d}/trazos_hd.npy',allow_pickle=True)); W=np.load(f'{d}/wid_hd.npy')
rows=[]
for box in sys.argv[3:]:
    v=[float(x) for x in box.split(',')]; x0,y0,x1,y1=v[:4]; f=v[4] if len(v)>4 else 4
    ref=cv2.resize(g[int(y0/s):int(y1/s),int(x0/s):int(x1/s)],(int((x1-x0)*f),int((y1-y0)*f)),interpolation=cv2.INTER_AREA)
    ref=cv2.cvtColor(ref,cv2.COLOR_GRAY2BGR); enc=(ref*0.55+255*0.45).astype(np.uint8); sol=np.full_like(ref,255)
    for p,w in zip(ps,W):
        q=(p-[x0,y0])*f
        if (q[:,0].max()<0) or (q[:,1].max()<0) or q[:,0].min()>ref.shape[1] or q[:,1].min()>ref.shape[0]: continue
        th=max(1,int(round(w*900/400*f*0.8)))
        for im in (enc,sol): cv2.polylines(im,[np.round(q*4).astype(np.int32)],False,(40,80,240),th,cv2.LINE_AA,shift=2)
    sep=np.full((ref.shape[0],8,3),255,np.uint8); rows.append(np.hstack([ref,sep,enc,sep,sol]))
w=max(r.shape[1] for r in rows); rows=[np.hstack([r,np.full((r.shape[0],w-r.shape[1],3),255,np.uint8)]) for r in rows]
cv2.imwrite(out,np.vstack([np.vstack([r,np.full((8,w,3),255,np.uint8)]) for r in rows]))
