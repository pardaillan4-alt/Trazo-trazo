"""Acercamiento con cuadrícula en coordenadas reales (escala 900) y los trazos encima.
Uso: python3 grid_zona.py x0 y0 x1 y1 f salida.jpg [paso_cuadricula]"""
import cv2,numpy as np,sys,os
x0,y0,x1,y1,f=[float(v) for v in sys.argv[1:6]]; out=sys.argv[6]; st=float(sys.argv[7]) if len(sys.argv)>7 else 10
g=cv2.imread('gris_big.png',0); s=900/g.shape[1]
a=cv2.resize(g[int(y0/s):int(y1/s),int(x0/s):int(x1/s)],(int((x1-x0)*f),int((y1-y0)*f)),interpolation=cv2.INTER_AREA)
o=(cv2.cvtColor(a,cv2.COLOR_GRAY2BGR)*0.55+255*0.45).astype(np.uint8)
for x in np.arange(np.ceil(x0/st)*st,x1,st):
    X=int((x-x0)*f); big=abs(x%50)<1e-6; cv2.line(o,(X,0),(X,o.shape[0]),(120,120,255) if big else (215,215,255),1)
    if big: cv2.putText(o,f'{x:g}',(X+2,14),0,0.45,(0,0,200),1)
for y in np.arange(np.ceil(y0/st)*st,y1,st):
    Y=int((y-y0)*f); big=abs(y%50)<1e-6; cv2.line(o,(0,Y),(o.shape[1],Y),(120,120,255) if big else (215,215,255),1)
    if big: cv2.putText(o,f'{y:g}',(2,Y-3),0,0.45,(0,0,200),1)
if os.path.exists('trazos_hd.npy'):
    for p in np.load('trazos_hd.npy',allow_pickle=True):
        q=(p-[x0,y0])*f
        if q[:,0].max()<0 or q[:,1].max()<0 or q[:,0].min()>o.shape[1] or q[:,1].min()>o.shape[0]: continue
        cv2.polylines(o,[np.round(q*4).astype(np.int32)],False,(40,110,240),2,cv2.LINE_AA,shift=2)
cv2.imwrite(out,o)
