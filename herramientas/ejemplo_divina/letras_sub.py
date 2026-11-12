"""Orden de las letras: una letra a la vez, de izquierda a derecha.
Cada letra es el hueco blanco que encierra su contorno (las letras con hueco por dentro, como la o, cuentan una vez).
Escribe cfg['suborden']['Las letras'] con un polígono por letra (unidades de 900)."""
import cv2,numpy as np,json
c=json.load(open('cfg.json')); E=c['letras']['encerradas']; W=900
g=cv2.imread('gris_big.png',0); s=g.shape[1]/W
x0,y0,x1,y1=[int(round(v*s)) for v in E['caja']]; b=g[y0:y1,x0:x1]
wh=(b>E.get('umbral',200)).astype(np.uint8); n,lab,st,cen=cv2.connectedComponentsWithStats(wh,4); hh,ww=b.shape
ids=[i for i in range(1,n) if not(st[i,0]==0 or st[i,1]==0 or st[i,0]+st[i,2]>=ww or st[i,1]+st[i,3]>=hh) and E['area'][0]<=st[i,4]<=E['area'][1]]
# relleno de cada hueco (con lo que tiene adentro) para quitar los huecos de adentro de otra letra
fill={}
for i in ids:
    cs,_=cv2.findContours((lab==i).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); f=np.zeros_like(wh); cv2.drawContours(f,cs,-1,1,-1); fill[i]=f
dentro={i for i in ids for j in ids if i!=j and st[i,4]<st[j,4] and fill[j][lab==i].mean()>0.9}
d=int(round(4.5*s)); ke=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*d+1,2*d+1))
L=[]
for i in ids:
    if i in dentro: continue
    m=cv2.dilate(fill[i],ke); cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cc=max(cs,key=cv2.contourArea)
    cc=cv2.approxPolyDP(cc,1.0,True)[:,0,:].astype(np.float32)
    pol=((cc+[x0,y0])/s).round(1).tolist(); L.append((float(cen[i][0]+x0)/s,pol))
L.sort(key=lambda t:t[0])
c.setdefault('suborden',{})['Las letras']=[[f'letra {k+1}',p] for k,(_,p) in enumerate(L)]
json.dump(c,open('cfg.json','w'),ensure_ascii=False,indent=1)
print('letras',len(L),'(huecos de adentro quitados:',len(dentro),')')
im=cv2.cvtColor(g[y0:y1,x0:x1],cv2.COLOR_GRAY2BGR)
for k,(_,p) in enumerate(L):
    q=(np.array(p)*s-[x0,y0]).astype(np.int32); col=(int(60+190*(k%2)),int(200-150*(k%3==0)),int(40+200*(k%2==0)))
    cv2.polylines(im,[q],True,col,2); cv2.putText(im,str(k+1),tuple(q.min(0)+[0,-2]),0,0.5,(0,0,255),1)
cv2.imwrite('letras_sub.png',cv2.resize(im,None,fx=0.8,fy=0.8))
