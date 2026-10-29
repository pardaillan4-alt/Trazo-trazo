import cv2,numpy as np,sys,json; sys.path.insert(0,'..')
from tonal import *
from skimage.morphology import skeletonize
from scipy.ndimage import gaussian_filter1d as g1
im=cv2.imread('sq.png'); L=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32); H,W=L.shape
P={k:v for k,v in json.load(open('../foto/dib/perro.json'))['parts']}
def pm(name,grow=0):
    m=np.zeros((H,W),np.uint8)
    for sh in P[name]:
        if sh[0]=='p': cv2.fillPoly(m,[np.array(sh[1],np.int32)],1)
        if sh[0]=='e': cv2.ellipse(m,(sh[1],sh[2]),(sh[3],sh[4]),sh[5],0,360,1,-1)
    return cv2.dilate(m,np.ones((grow*2+1,)*2,np.uint8)) if grow else m
bg=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((11,11),np.uint8)),(0,0),6); raw=bg-cv2.GaussianBlur(L,(0,0),0.8)
dk=np.clip((raw-np.percentile(raw,50))/(np.percentile(raw,99.5)-np.percentile(raw,50)),0,1)
OUT={}
DIL={k:pm(k,25) for k in ['nariz','hocico','barbilla','oreja','cabeza','cuello','pecho']}
# 1) silueta (sin el borde de la hoja ni los huequitos blancos de abajo)
b=cv2.GaussianBlur(L,(0,0),3); m=(b<240).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((31,31),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(m); m=(lab==1+np.argmax(st[1:,4])).astype(np.uint8)
cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); sil=smooth_closed(max(cs,key=cv2.contourArea)[:,0,:],5)
keep=(sil[:,0]>3)&(sil[:,0]<W-4)&(sil[:,1]>3)&(sil[:,1]<H-4)
for seg in open_part(sil,keep):
    # repartir por partes
    lab_=[]
    for p in seg:
        x,y=int(np.clip(p[0],0,W-1)),int(np.clip(p[1],0,H-1)); best='pecho'
        for k in ['nariz','hocico','barbilla','oreja','cabeza','cuello','pecho']:
            if DIL[k][y,x]: best=k; break
        lab_.append(best)
    lab_=np.array(lab_); i=0
    while i<len(seg):
        j=i
        while j<len(seg) and lab_[j]==lab_[i]: j+=1
        if j-i>10: OUT.setdefault('sil_'+lab_[i],[]).append(seg[max(0,i-1):j+1])
        i=j
# 2) masas oscuras: oreja, manchas del pecho, el labio colgante y la nariz
inside=cv2.erode(m,np.ones((9,9),np.uint8))
D=masses(L,5,120,1500,4,within=inside)
eye_m=pm('ojo',14)
for c in D:
    cx,cy=c.mean(0).astype(int)
    if eye_m[cy,cx]: continue                                   # el ojo va aparte
    a=cv2.contourArea(c.astype(np.float32))
    k='oreja' if a>20000 else ('nariz' if pm('nariz',10)[cy,cx] else ('manchas' if cy>480 else 'sombras'))
    if k=='sombras':
        # solo si es una forma oscura clara (el labio que cuelga), no una sombra difusa
        mm=np.zeros((H,W),np.uint8); cv2.fillPoly(mm,[np.round(c).astype(np.int32)],1)
        if np.median(L[mm>0])>95: continue
        if not pm('barbilla',30)[cy,cx]: continue
        k='labio'
    OUT.setdefault(k,[]).append(np.vstack([c,c[:1]]))
# 3) el ojo: almendra y pupila del trazo real
e=[s for s in P['ojo']][0]; ex,ey=e[1],e[2]
win=L[ey-30:ey+30,ex-40:ex+40]; d_=cv2.GaussianBlur(win,(0,0),1.5)
pts=(np.argwhere(d_<np.percentile(d_,12))[:,::-1]+np.array([ex-40,ey-30])).astype(np.float32).reshape(-1,1,2)
(cx,cy),(ma,mi),ang=cv2.fitEllipse(pts); 
t=np.linspace(0,2*np.pi,90); ca,sa=np.cos(np.radians(ang)),np.sin(np.radians(ang))
A,B=ma/2*1.05,mi/2*1.05
alm=np.stack([cx+A*np.cos(t)*ca-B*np.sin(t)*sa,cy+A*np.cos(t)*sa+B*np.sin(t)*ca],1)
OUT['ojo']=[alm]
pk=(np.argwhere(d_<np.percentile(d_,3))[:,::-1]+np.array([ex-40,ey-30])).astype(np.float32); pc=pk.mean(0); pr=max(3,np.sqrt(len(pk)/np.pi))
OUT['pupila']=[pc+pr*np.stack([np.cos(t),np.sin(t)],1)]
# 4) líneas fuertes del hocico (boca) y de los pliegues: el trazo más oscuro, como línea limpia
def strong_lines(region,q,minlen,sig=3):
    mm=region>0; thr=np.percentile(dk[mm],q); ink=((dk>thr)&mm).astype(np.uint8)
    ink=cv2.morphologyEx(ink,cv2.MORPH_OPEN,np.ones((2,2),np.uint8)); sk=skeletonize(ink>0)
    n_,lab=cv2.connectedComponents(sk.astype(np.uint8),connectivity=8); out=[]
    for i in range(1,n_):
        yy,xx=np.nonzero(lab==i)
        if len(xx)<minlen: continue
        p=np.stack([xx,yy],1).astype(np.float32); c0=p.mean(0); u,s_,vt=np.linalg.svd(p-c0); p=p[np.argsort((p-c0)@vt[0])]
        if s_[1]>0.35*s_[0]: continue                                 # no es una línea (es mancha)
        p=np.stack([g1(p[:,0],sig,mode='nearest'),g1(p[:,1],sig,mode='nearest')],1); out.append(p[::2])
    return out
hoc=pm('hocico')*(1-pm('nariz',8))
OUT['boca']=sorted(strong_lines(hoc,97,30),key=len)[-1:]
# 5) pelo: trazos largos siguiendo el pelo (oreja y cuello), pocos y limpios
g=cv2.GaussianBlur(L,(0,0),1.0); gx=cv2.Sobel(g,cv2.CV_32F,1,0,3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,3)
Jxx,Jyy,Jxy=[cv2.GaussianBlur(a_,(0,0),4) for a_ in (gx*gx,gy*gy,gx*gy)]
th=0.5*np.arctan2(2*Jxy,Jxx-Jyy)+np.pi/2; DX,DY=np.cos(th),np.sin(th)
def fur(region,n,length,thr_q=85,space=14):
    mm=region>0; thr=np.percentile(dk[mm],thr_q); ink=(dk>thr)&mm; cov=np.zeros((H,W),np.uint8); out=[]
    ys,xs=np.nonzero(ink); rng=np.random.default_rng(3)
    for k in rng.permutation(len(xs)):
        y,x=ys[k],xs[k]
        if cov[y,x]: continue
        pts=[(float(x),float(y))]
        for sgn in (1,-1):
            cx_,cy_=float(x),float(y); d0=np.array([DX[y,x],DY[y,x]])*sgn; seg=[]
            for _ in range(length//2):
                ix,iy=int(cx_),int(cy_)
                if not(0<=ix<W and 0<=iy<H) or not mm[iy,ix]: break
                d=np.array([DX[iy,ix],DY[iy,ix]]); d=d if d@d0>0 else -d; d0=0.85*d0+0.15*d; d0/=np.linalg.norm(d0)
                cx_+=d0[0]*1.5; cy_+=d0[1]*1.5; seg.append((cx_,cy_))
            pts=(seg[::-1]+pts) if sgn==-1 else pts+seg
        p=np.array(pts,np.float32)
        if len(p)<length*0.4: cov[y,x]=1; continue
        p=np.stack([g1(p[:,0],2,mode='nearest'),g1(p[:,1],2,mode='nearest')],1)
        cv2.polylines(cov,[np.round(p).astype(np.int32)],False,1,space); out.append(p[::2])
        if len(out)>=n: break
    return out
sys.path.insert(0,'..'); from facelib import crm
# oreja medida sobre la imagen: su borde real (el borde claro de abajo y la línea fina de la derecha), no el borde de la sombra
OUT['oreja']=[crm([(395,100),(365,108),(320,130),(280,165),(250,205),(232,250),(226,290),(230,300),(265,330),(305,360),(350,385),(395,405),(435,420),(480,425),(515,412),(519,395),(520,360),(515,315),(500,270),(480,220),(450,165),(420,110),(395,100)],12)]
ear=np.zeros((H,W),np.uint8); cv2.fillPoly(ear,[np.round(OUT['oreja'][0]).astype(np.int32)],1)
# la oreja del fondo: forma completa, y la silueta no se repite encima de ella
if 'labio' in OUT:
    OUT['oreja_fondo']=OUT.pop('labio'); fm=np.zeros((H,W),np.uint8)
    for c in OUT['oreja_fondo']: cv2.fillPoly(fm,[np.round(c).astype(np.int32)],1)
    fm=cv2.dilate(fm,np.ones((25,25),np.uint8))
    for k in [k for k in OUT if k.startswith('sil_')]:
        new=[]
        for c in OUT[k]:
            ok=np.array([not fm[int(min(max(p[1],0),H-1)),int(min(max(p[0],0),W-1))] for p in c]); i=0
            while i<len(c):
                if ok[i]:
                    j=i
                    while j<len(c) and ok[j]: j+=1
                    if j-i>8: new.append(c[i:j])
                    i=j
                else: i+=1
        OUT[k]=new
OUT['pelo_oreja']=fur(cv2.erode(ear,np.ones((15,15),np.uint8)),22,60,80,22)
OUT['pelo_cuello']=fur(pm('cuello')*(1-ear)*cv2.erode(m,np.ones((21,21),np.uint8)),14,50,93,30)
np.save('perro_mano.npy',np.array(OUT,dtype=object)); print({k:len(v) for k,v in OUT.items()})
o=im.copy(); w=np.full_like(im,250); col={'pelo_oreja':(150,150,150),'pelo_cuello':(150,150,150)}
for t_ in (o,w):
    for k,ps in OUT.items():
        for p in ps: cv2.polylines(t_,[np.round(p*4).astype(np.int32)],False,col.get(k,(40,80,240)),2,cv2.LINE_AA,shift=2)
cv2.imwrite('mano_cmp.jpg',np.hstack([im,o,w]))
