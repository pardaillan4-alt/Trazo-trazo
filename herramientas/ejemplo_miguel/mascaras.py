"""Máscaras del sombreado (escala 900), hechas con el dibujo de líneas: cada hueco blanco encerrado por las líneas
se reparte según la zona de cfg.json donde cae (San Miguel, alas, demonio y roca); lo que se conecta con la orilla
de arriba o de los lados es el fondo. Las líneas van con el hueco más cercano.
Escribe m_angel.png, m_alas.png, m_demonio.png y mascaras_chk.jpg."""
import cv2,numpy as np,json
cfg=json.load(open('cfg.json')); H=cfg['H']; W=900
g=cv2.imread('gris_big.png',0); BH,BW=g.shape
GR={'angel':["Los ojos y las cejas","La nariz y la boca","La cara y el cabello","El casco y la pluma","El cuello y el manto del pecho","La armadura",
             "El brazo y la espada","El escudo","Las piernas y las sandalias","La capa"],
    'alas':["El ala de este lado","El ala del otro lado"],'demonio':["El demonio"]}
def mk(sh,h,w,s):
    m=np.zeros((h,w),np.uint8); cv2.fillPoly(m,[np.round(np.array(sh[1])*s).astype(np.int32)],1); return m
s=BW/W
# zona de cada pixel, por la prioridad de cfg['orden']; lo que no cae en ninguna es la roca
lab=np.full((BH,BW),3,np.uint8)                 # 0 ángel, 1 alas, 2 demonio, 3 roca
lab[:int(400*s)]=0                               # arriba, lo que no cae en ninguna zona es del ángel (la roca está abajo)
for zn in reversed(cfg['orden']):
    gi=[i for i,(k,v) in enumerate(GR.items()) if zn in v][0]
    for sh in cfg['zonas'][zn]: lab[mk(sh,BH,BW,s)>0]=gi
ink=(g<200).astype(np.uint8); ink[-1,:]=1        # abajo se cierra la roca
wh=(1-cv2.dilate(ink,np.ones((3,3),np.uint8))).astype(np.uint8)
n,cc,st,_=cv2.connectedComponentsWithStats(wh,4)
borde=set(np.unique(np.r_[cc[0,:],cc[:,0],cc[:,-1]]).tolist())-{0}
cls=np.full(n,-1,int)
for i in range(1,n):
    if i in borde:                               # fondo, salvo las puntas de las plumas que tocan la orilla de arriba
        cls[i]=4
        if st[i,4]<30000:
            cnt=np.bincount(lab[cc==i],minlength=4)
            if cnt[1]>0.8*cnt.sum(): cls[i]=1
        continue
    cls[i]=int(np.bincount(lab[cc==i],minlength=4).argmax()) if st[i,4]<400000 else 4
C=cls[cc]; C[cc==0]=-1
# las líneas (y el borde de 1 px) van con la clase del hueco más cercano
dist=[];
for k in range(5):
    m=(C==k).astype(np.uint8)
    dist.append(cv2.distanceTransform(1-m,cv2.DIST_L2,3) if m.any() else np.full((BH,BW),1e9,np.float32))
F=np.argmin(np.stack(dist),0)
# la capa de la imagen a lápiz es más grande que la del dibujo de líneas (se abre hacia la izquierda): lo oscuro
# de esa capa, pegado a San Miguel y debajo del ala, también es del ángel (si no, aparecería con el fondo)
gs=cv2.GaussianBlur(cv2.cvtColor(cv2.resize(cv2.imread('gris_src.jpg'),(BW,BH)),cv2.COLOR_BGR2GRAY),(0,0),2)
cap=np.zeros((BH,BW),np.uint8); cv2.fillPoly(cap,[np.round(np.array([(250,262),(345,240),(375,205),(400,200),(415,425),(250,425)])*s).astype(np.int32)],1)
osc=((gs<175)&(cap>0)&(F==4)).astype(np.uint8)
osc=cv2.morphologyEx(osc,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
n2,c2,st2,_=cv2.connectedComponentsWithStats(osc,8); junto=cv2.dilate((F==0).astype(np.uint8),np.ones((9,9),np.uint8))
for i in range(1,n2):
    if st2[i,4]>2000 and (junto[c2==i]>0).any(): F[c2==i]=0
# la roca y el demonio van juntos en el sombreado
for nm,ks in (('angel',[0]),('alas',[1]),('demonio',[2,3])):
    m=np.isin(F,ks).astype(np.uint8)*255
    cv2.imwrite(f'm_{nm}.png',(cv2.resize(m,(W,H),interpolation=cv2.INTER_AREA)>127).astype(np.uint8)*255)
col=np.array([(60,60,230),(60,200,230),(200,80,60),(150,60,150),(235,235,235)],np.uint8)
v=col[F]; v=(v*0.55+cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)*0.45).astype(np.uint8)
cv2.imwrite('mascaras_chk.jpg',cv2.resize(v,(1600,873),interpolation=cv2.INTER_AREA))
print('huecos',n,'fondo',int((cls==4).sum()))
