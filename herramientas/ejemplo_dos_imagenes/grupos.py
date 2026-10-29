import cv2,numpy as np
src=open('../gua2/gen.py').read(); exec(src[:src.index("dog=cv2.GaussianBlur")])
ps=list(np.load('trazos.npy',allow_pickle=True)); starm=cv2.dilate(np.load('starm.npy'),np.ones((5,5),np.uint8))
def box(x0,y0,x1,y1,pad=6): m=np.zeros((H,W),np.uint8); m[y0-pad:y1+pad,x0-pad:x1+pad]=1; return m
ojos=box(117,295,202,380)|box(188,262,298,345); nb=box(184,360,263,425,4)|box(204,411,283,463,4)
cuello2=np.zeros((H,W),np.uint8); cv2.fillPoly(cuello2,[np.array([(215,500),(250,480),(340,450),(430,470),(450,560),(360,700),(260,700),(210,570)],np.int32)],1)
broche=np.zeros((H,W),np.uint8); cv2.ellipse(broche,(322,630),(35,70),0,0,360,1,-1)
D=lambda m,k=9:cv2.dilate(m.astype(np.uint8),np.ones((k,k),np.uint8))
order=[('estrellas',starm),('ojos y cejas',ojos),('nariz y boca',nb),('cuello y broche',(cuello2&(1-D(cara,5)))|broche),('manos',D(manos,7)),
       ('contorno de la cara',D(cara,23)),('tunica',D(tunica|punos,3)),('cabello',D(pelo,3)),('velo y manto',D(manto,3)),('rayos',np.ones((H,W),np.uint8))]
G={}
for p in ps:
    x=np.clip(np.round(p[:,0]).astype(int),0,W-1); y=np.clip(np.round(p[:,1]).astype(int),0,H-1)
    for k,m in order:
        if m[y,x].mean()>0.5: G.setdefault(k,[]).append(p); break
np.save('G.npy',np.array(G,dtype=object)); print({k:len(v) for k,v in G.items()})
cols=[(0,160,255),(255,0,0),(200,0,200),(0,128,128),(0,150,0),(40,80,240),(0,0,180),(60,60,60),(200,120,0),(150,150,150)]
w_=np.full((H,W,3),250,np.uint8)
for i,(k,_) in enumerate(order):
    for p in G.get(k,[]): cv2.polylines(w_,[np.round(p*4).astype(np.int32)],False,cols[i],2,cv2.LINE_AA,shift=2)
cv2.imwrite('grupos.jpg',w_)
