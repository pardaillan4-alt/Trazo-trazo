import cv2,numpy as np,sys; sys.path.insert(0,'..')
from facelib import crm
from scipy.ndimage import gaussian_filter1d as g1
im=cv2.imread('sq.png'); L=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32); H,W=L.shape
X={}
# contorno de la cara medido sobre la imagen (lado derecho, mandíbula, barbilla) y el lado izquierdo junto al pelo
X['cara']=[crm([(475,160),(487,185),(493,215),(498,247),(506,282),(514,315),(527,343),(540,367),(548,392),(552,415),(550,437)]),
           crm([(250,152),(249,200),(246,245),(243,290),(243,330),(250,370),(262,405),(278,440),(296,472),(314,497),(332,520),(352,533),(380,538)])]
X['mandibula']=[crm([(550,437),(537,457),(520,473),(500,490),(480,500),(460,510),(440,522),(420,530),(400,535),(380,538)])]
X['cuello']=[crm([(332,530),(337,555),(341,582),(345,610),(347,632)]),crm([(379,551),(383,585),(388,620)]),
             crm([(297,701),(316,676),(345,655),(385,639),(447,617),(497,617),(541,632),(585,657),(622,695),(647,732)]),crm([(297,701),(291,745),(285,795)])]
# cabello: trazos largos que siguen cómo cae el pelo
bg=cv2.GaussianBlur(cv2.morphologyEx(L,cv2.MORPH_CLOSE,np.ones((11,11),np.uint8)),(0,0),6); raw=bg-cv2.GaussianBlur(L,(0,0),0.8)
dk=np.clip((raw-np.percentile(raw,50))/(np.percentile(raw,99.5)-np.percentile(raw,50)),0,1)
g=cv2.GaussianBlur(L,(0,0),1.0); gx=cv2.Sobel(g,cv2.CV_32F,1,0,3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,3)
Jxx,Jyy,Jxy=[cv2.GaussianBlur(a_,(0,0),5) for a_ in (gx*gx,gy*gy,gx*gy)]
th=0.5*np.arctan2(2*Jxy,Jxx-Jyy)+np.pi/2; DX,DY=np.cos(th),np.sin(th)
def poly(p): m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
def ell(c,a): m=np.zeros((H,W),np.uint8); cv2.ellipse(m,c,a,0,0,360,1,-1); return m
cara=poly([(245,190),(330,160),(450,165),(500,200),(512,290),(502,380),(470,470),(420,515),(360,542),(310,520),(290,470),(270,400),(250,330),(240,260)])
cue=poly([(290,525),(350,545),(420,518),(460,560),(560,600),(660,700),(690,800),(305,800),(300,690),(330,600)])
firma=poly([(175,705),(305,705),(305,800),(175,800)])
hair=((1-cv2.dilate(cara,np.ones((9,9),np.uint8)))*(1-cue)*(1-firma)).astype(np.uint8)
hair[:, :120]=0; hair[:,720:]=0
def fur(mm,n,length,q=85,space=16,step=1.5):
    thr=np.percentile(dk[mm>0],q); ink=(dk>thr)&(mm>0); cov=np.zeros((H,W),np.uint8); out=[]
    ys,xs=np.nonzero(ink); order=np.argsort(-dk[ys,xs])
    for k in order:
        y,x=ys[k],xs[k]
        if cov[y,x]: continue
        pts=[(float(x),float(y))]
        for sgn in (1,-1):
            cx_,cy_=float(x),float(y); d0=np.array([DX[y,x],DY[y,x]])*sgn; seg=[]; miss=0
            for _ in range(int(length/step)):
                ix,iy=int(cx_),int(cy_)
                if not(0<=ix<W and 0<=iy<H) or not mm[iy,ix]: break
                miss=0 if ink[iy,ix] else miss+1
                if miss>6: break
                d=np.array([DX[iy,ix],DY[iy,ix]]); d=d if d@d0>0 else -d; d0=0.85*d0+0.15*d; d0/=np.linalg.norm(d0)
                cx_+=d0[0]*step; cy_+=d0[1]*step; seg.append((cx_,cy_))
            pts=(seg[::-1]+pts) if sgn==-1 else pts+seg
        p=np.array(pts,np.float32)
        if len(p)*step<length*0.35: cov[y,x]=1; continue
        p=np.stack([g1(p[:,0],3,mode='nearest'),g1(p[:,1],3,mode='nearest')],1)
        cv2.polylines(cov,[np.round(p).astype(np.int32)],False,1,space); out.append(p[::2])
        if len(out)>=n: break
    return out
X['cabello']=fur(hair,70,160,82,14)
# fuera los mechones que van pegados encima del contorno de la cara (no se repite la línea)
cm=np.zeros((H,W),np.uint8)
for p in X['cara']+X['mandibula']: cv2.polylines(cm,[np.round(p).astype(np.int32)],False,1,9)
X['cabello']=[p for p in X['cabello'] if cm[np.clip(np.round(p[:,1]).astype(int),0,H-1),np.clip(np.round(p[:,0]).astype(int),0,W-1)].mean()<0.4]
np.save('resto_hand.npy',np.array(X,dtype=object)); print({k:len(v) for k,v in X.items()})
E=np.load('eyes_hand.npy',allow_pickle=True).item(); NB=np.load('nm_hand.npy',allow_pickle=True).item()
o=im.copy(); w=np.full_like(im,250)
for t in (o,w):
    for D_,c in ((X,(40,80,240)),(E,(40,80,240)),(NB,(40,80,240))):
        for k,ps in D_.items():
            for p in ps: cv2.polylines(t,[np.round(np.asarray(p)*4).astype(np.int32)],False,(160,120,60) if k=='cabello' else c,2,cv2.LINE_AA,shift=2)
cv2.imwrite('loomis_mano.jpg',np.hstack([im,o,w]))
