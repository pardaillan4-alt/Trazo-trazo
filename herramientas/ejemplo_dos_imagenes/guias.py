import cv2,numpy as np
lm=np.load('lm.npy')
def oval(c,a,b,ang=0,t0=0,t1=2*np.pi):
    ca,sa=np.cos(np.radians(ang)),np.sin(np.radians(ang)); t=np.linspace(t0,t1,90)
    return np.stack([c[0]+a*np.cos(t)*ca-b*np.sin(t)*sa,c[1]+a*np.cos(t)*sa+b*np.sin(t)*ca],1)
def ext(a,b,k1,k2): a=np.array(a,float); b=np.array(b,float); d=b-a; return np.array([a-d*k1,b+d*k2])
eye_dir=lm[263]-lm[33]
def par(p,k=0.6): p=np.array(p,float); return np.array([p-eye_dir*k,p+eye_dir*k])
G1=[oval((432,187),82,107,18)]                                # 1) óvalo de la cara
G2=[ext(lm[10],lm[152],0.15,0.1), ext(lm[33],lm[263],0.35,0.35)]   # 2) línea del centro y línea de los ojos
G3=[par(lm[2],0.45), par((lm[61]+lm[291])/2,0.5)]               # 3) base de la nariz y boca
G4=[oval((452,185),178,178,0,np.pi*0.98,np.pi*2.02), np.array([(170,514),(260,415),(350,378),(470,370),(570,368),(690,395),(790,514)])]
np.save('guias.npy',np.array({'g1':G1,'g2':G2,'g3':G3,'g4':G4},dtype=object))
l=cv2.cvtColor(cv2.imread('lineas.png',0),cv2.COLOR_GRAY2BGR); o=(l*0.45+140).astype(np.uint8)
for G,c in ((G1,(255,0,0)),(G2,(0,150,0)),(G3,(200,0,200)),(G4,(0,120,255))):
    for p in G: cv2.polylines(o,[np.round(p*4).astype(np.int32)],False,c,2,cv2.LINE_AA,shift=2)
cv2.imwrite('guias.jpg',o)
