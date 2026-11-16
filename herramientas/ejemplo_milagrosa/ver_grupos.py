"""Acercamiento de las partes (G.npy): cada paso con su color, como grupos.jpg.  Uso: python3 ver_grupos.py x0 y0 x1 y1 f salida.jpg"""
import cv2,numpy as np,sys,json
x0,y0,x1,y1,f=[float(v) for v in sys.argv[1:6]]; out=sys.argv[6]
cfg=json.load(open('cfg.json')); G=np.load('G.npy',allow_pickle=True).item()
g=cv2.imread('gris_big.png',0); s=900/g.shape[1]
a=cv2.resize(g[int(y0/s):int(y1/s),int(x0/s):int(x1/s)],(int((x1-x0)*f),int((y1-y0)*f)),interpolation=cv2.INTER_AREA)
o=(cv2.cvtColor(a,cv2.COLOR_GRAY2BGR)*0.3+255*0.7).astype(np.uint8)
cols=[(40,80,240),(255,0,0),(200,0,200),(0,140,0),(0,120,255),(120,120,0),(150,150,150),(0,0,0),(255,128,0),(128,0,255),(0,200,200)]
for i,k in enumerate(cfg['pasos']):
    for p in G.get(k,[]):
        q=(p-[x0,y0])*f
        if q[:,0].max()<0 or q[:,1].max()<0 or q[:,0].min()>o.shape[1] or q[:,1].min()>o.shape[0]: continue
        cv2.polylines(o,[np.round(q*4).astype(np.int32)],False,cols[i%len(cols)],2,cv2.LINE_AA,shift=2)
for i,k in enumerate(cfg['pasos']): cv2.putText(o,k,(6,18+18*i),0,0.5,cols[i%len(cols)],1)
cv2.imwrite(out,o)
