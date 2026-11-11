"""Pasos de una escena (como gen5) con regiones y guías de cfg.json.
cfg['regiones'] = [[nombre, [pasos cuya silueta forma la región] o null (= el resto), [bandas]], ...]
cfg['guias'] = [["elipse", [pasos]] | ["curva", [[x,y],...]] | ["linea", [[x,y],[x,y]]], ...]  (medidas sobre el dibujo)
Uso: python3 ../gen6.py imagen.png x TAG"""
import cv2,numpy as np,json,os,sys
sys.path.insert(0,'.')
from vec import to_svg
from furlib2 import Fur
SRC,OUT,TAG=sys.argv[1],sys.argv[2],sys.argv[3]
cfg=json.load(open('cfg.json')); H=cfg['H']; W=900
OW=cfg.get('OW',W); OH=round(H*OW/W)      # tamaño de las imágenes que se guardan (dibujos altos: más chicas, para que las hojas no pesen)
sq=cv2.resize(cv2.imread(SRC),(W,H),interpolation=cv2.INTER_AREA); O='out_'+TAG; os.system(f'rm -rf {O}'); os.makedirs(O)
orig=sq.astype(np.float32)/255; L=cv2.cvtColor(sq,cv2.COLOR_BGR2GRAY).astype(np.float32)
GL=np.load('G.npy',allow_pickle=True).item(); GWD=np.load('GW.npy',allow_pickle=True).item()
def silueta(steps,close=45,minA=150,grosor=3):
    m=np.zeros((H,W),np.uint8)
    for k in steps:
        for p in GL.get(k,[]): cv2.polylines(m,[np.round(p).astype(np.int32)],False,1,grosor)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(close,close)))
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); out=np.zeros((H,W),np.uint8)
    for c in cs:
        if cv2.contourArea(c)>=minA: cv2.drawContours(out,[c],-1,1,-1)
    return out
def silueta2(steps,k=21,grosor=3):
    """silueta sin rellenar los huecos de afuera: lo de afuera es lo que se conecta con la orilla de la imagen por pasos anchos
    (así una rendija en el contorno no deja salir el relleno, y el agua entre la cola y el lomo no cuenta como animal)"""
    m=np.zeros((H,W),np.uint8)
    for st in steps:
        for p in GL.get(st,[]): cv2.polylines(m,[np.round(p).astype(np.int32)],False,1,grosor)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); R=np.zeros((H,W),np.uint8)
    for c in cs: cv2.drawContours(R,[c],-1,1,-1)
    out=(1-R).astype(np.uint8); ke=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k))
    op=cv2.morphologyEx(out,cv2.MORPH_OPEN,ke); n,lab=cv2.connectedComponents(op)
    borde=set(np.unique(np.r_[lab[0,:],lab[-1,:],lab[:,0],lab[:,-1]]).tolist())-{0}
    fuera=np.isin(lab,list(borde)).astype(np.uint8)
    k3=np.ones((3,3),np.uint8)
    for _ in range(k//2+1): fuera=cv2.dilate(fuera,k3)&out          # crecer de regreso solo por el agua, sin brincar el contorno
    S=(1-fuera).astype(np.uint8)
    n2,l2,st2,_=cv2.connectedComponentsWithStats(S)
    for j in range(1,n2):
        if st2[j,4]<150: S[l2==j]=0
    return S
def crm(P,n=12):
    P=np.asarray(P,np.float32); P=np.vstack([P[:1],P,P[-1:]]); out=[]
    for i in range(1,len(P)-2):
        p0,p1,p2,p3=P[i-1],P[i],P[i+1],P[i+2]
        for t in np.linspace(0,1,n,endpoint=False):
            out.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3))
    out.append(P[-2]); return np.array(out,np.float32)
def ell(m):
    cs,_=cv2.findContours(m.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)
    (cx,cy),(a,b),ang=cv2.fitEllipse(c); t=np.linspace(0,2*np.pi,90); ca,sa=np.cos(np.radians(ang)),np.sin(np.radians(ang)); a/=2;b/=2
    return np.stack([cx+a*np.cos(t)*ca-b*np.sin(t)*sa,cy+a*np.cos(t)*sa+b*np.sin(t)*ca],1)
# regiones para el sombreado
POL=cfg.get('poligonos',{})
def pmask(names):
    m=np.zeros((H,W),np.uint8)
    for n in names:
        for poly in (POL[n] if n in POL else [sh[1] for sh in cfg['zonas'][n]]): cv2.fillPoly(m,[np.array(poly,np.int32)],1)
    return m
def figura():
    f=(cv2.GaussianBlur(L,(0,0),1.2)<246).astype(np.uint8)
    f=cv2.morphologyEx(f,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
    ff=np.pad(f,1); msk=np.zeros((H+4,W+4),np.uint8); cv2.floodFill(ff,msk,(0,0),2)
    return (ff[1:-1,1:-1]!=2).astype(np.uint8)
FIG=figura()
if cfg.get('fondo_papel'):      # el fondo blanco de la imagen se vuelve del color del papel, así no cambia al terminar
    FD=cv2.GaussianBlur(cv2.dilate(FIG.astype(np.float32),np.ones((7,7),np.uint8)),(0,0),2.5)[:,:,None]
    PAP=np.ones((H,W,3),np.float32)*np.array([0.965,0.975,0.98],np.float32)
    orig=orig*FD+PAP*(1-FD)
REG=[]; usado=np.zeros((H,W),np.uint8)
for nm,steps,bands,*op in cfg['regiones']:
    if isinstance(steps,dict):      # región por polígonos (zonas o polígonos propios), solo dentro del dibujo
        m=pmask(steps['mas'])&(1-pmask(steps.get('menos',[])))&FIG&(1-usado)
        if steps.get('silueta'):      # y dentro del contorno real de esas partes (sin cuadros alrededor)
            m&=cv2.dilate(silueta2(steps['silueta']),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
        if steps.get('mas_silueta'):  # partes que van completas aunque se salgan del polígono (por ejemplo, las manos)
            m|=cv2.dilate(silueta2(steps['mas_silueta']),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))&FIG&(1-usado)
        REG.append((nm,m.astype(np.uint8),bands)); usado|=m.astype(np.uint8); continue
    m=(1-usado) if steps is None else (silueta2(steps)&(1-usado))
    if len(op)>2 and op[2]:      # dentro de estas zonas, la silueta cerrada completa (aletas, casco con huecos en el contorno)
        zm=np.zeros((H,W),np.uint8)
        for zn in op[2]:
            for sh in cfg['zonas'][zn]: cv2.fillPoly(zm,[np.array(sh[1],np.int32)],1)
        m=(m|(silueta(steps,close=45)&zm))&(1-usado)
    if steps is not None: m=cv2.erode(m.astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))   # que no se asome el agua junto a la orilla
    if len(op)>1:      # partes delgadas (mástil, cuerdas): solo sus líneas, engrosadas, sin rellenar el agua de en medio
        ln=np.zeros((H,W),np.uint8)
        for k in op[1]:
            for p in GL.get(k,[]): cv2.polylines(ln,[np.round(p).astype(np.int32)],False,1,2)
        m=(m|ln)&(1-usado)
    REG.append((nm,m.astype(np.uint8),bands)); usado|=m.astype(np.uint8)
cv2.imwrite(f'regiones_{TAG}.jpg',np.hstack([cv2.cvtColor(m*255,cv2.COLOR_GRAY2BGR) for _,m,_ in REG]))
# guías medidas sobre el dibujo
G=[]
for gd in cfg['guias']:
    if gd[0]=='elipse':
        m=silueta(gd[1])
        if len(gd)>3: cl=np.zeros((H,W),np.uint8); cv2.fillPoly(cl,[np.array(gd[3],np.int32)],1); m=m&cl     # solo esta parte (sin la cola, por ejemplo)
        if len(gd)>2 and gd[2]: m=cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(gd[2],gd[2])))
        G.append(ell(m))
    elif gd[0]=='elipse_m':
        cx,cy,a,b,ang=gd[1]; t=np.linspace(0,2*np.pi,90); ca,sa=np.cos(np.radians(ang)),np.sin(np.radians(ang))
        G.append(np.stack([cx+a*np.cos(t)*ca-b*np.sin(t)*sa,cy+a*np.cos(t)*sa+b*np.sin(t)*ca],1))
    elif gd[0]=='curva': G.append(crm(gd[1]))
    else: G.append(np.array(gd[1],np.float32))
d=np.clip((250-cv2.GaussianBlur(L,(0,0),1.0))/250,0,1)
paper=np.ones((H,W,3),np.float32)*np.array([0.965,0.975,0.98],np.float32)
GR=np.array([0.20,0.19,0.19],np.float32); RED=np.array([0.25,0.37,0.95],np.float32); Zr=np.zeros((H,W),np.float32)
def save(img,name):
    o=(np.clip(img,0,1)*255).astype(np.uint8)
    if OW!=W: o=cv2.resize(o,(OW,OH),interpolation=cv2.INTER_AREA)
    cv2.imwrite(f'{O}/{name}.png',o)
def ssl(segs,th=3,val=.5):
    big=np.zeros((H*4,W*4),np.uint8)
    for q in segs: cv2.polylines(big,[(np.asarray(q)*4).astype(np.int32)],False,255,th,cv2.LINE_AA)
    return np.clip(cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255*1.4,0,1)*val
guide=ssl(G,3,.45); i=1; VEC={}; SV={}
lin=cv2.resize(cv2.imread('gris_big.png',0),(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)
# tinta de cada paso: solo la que queda junto a sus trazos (así no se cuela la textura)
TL=np.zeros((H*4,W*4),np.uint8)
STEPS=cfg['pasos']; dist=[]
for k in STEPS:
    r=np.full((H,W),255,np.uint8)
    for p in GL.get(k,[]): cv2.polylines(r,[np.round(p).astype(np.int32)],False,0,1)
    dist.append(cv2.distanceTransform(r,cv2.DIST_L2,3))
lab=np.argmin(np.stack(dist),0); near=np.min(np.stack(dist),0)<cfg.get('cerca',3)
INK=np.clip((cfg['th']-lin)/60,0,1)
# los trazos agregados o medidos a mano también se ven en la imagen del paso
for k in STEPS:
    for p,w in zip(GL.get(k,[]),GWD.get(k,[])): cv2.polylines(TL,[np.round(p*4*4).astype(np.int32)],False,255,max(2,int(round(w*900/400*4))),cv2.LINE_AA,shift=2)
TLs=cv2.resize(TL,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255
INK=np.maximum(INK*near,TLs*0.9)
# pasos compuestos: cfg['suborden'][paso] = [[nombre, polígono], ...] en el orden en que se dibujan las partes
# (cada trazo va con el polígono que más lo contiene; si empatan, el más chico)
SUBO={k:[(nm,np.array(pp,np.int32)) for nm,pp in v] for k,v in cfg.get('suborden',{}).items()}
SUBM={k:[cv2.fillPoly(np.zeros((H,W),np.uint8),[pp],1) for _,pp in v] for k,v in SUBO.items()}
def sub(k,q):
    if k not in SUBM: return []
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(q,axis=0).T))]; t=np.linspace(0,d[-1],max(2,int(d[-1])+1)) if d[-1]>0 else np.zeros(1)
    x=np.clip(np.round(np.interp(t,d,q[:,0])).astype(int),0,W-1); y=np.clip(np.round(np.interp(t,d,q[:,1])).astype(int),0,H-1)
    fr=[(float(m[y,x].mean()),-float(m.sum())) for m in SUBM[k]]; j=max(range(len(fr)),key=lambda j:fr[j])
    return [j if fr[j][0]>0 else len(fr)]
DONE=Zr.copy()
def base():
    o=paper*(1-guide[:,:,None])+GR*guide[:,:,None]; return o*(1-DONE[:,:,None])+GR*DONE[:,:,None]
F=Fur(L,(L<250).astype(np.uint8)); save(base(),'1'); save(base(),'1g')
for si,k in enumerate(STEPS):
    i+=1; segs=[np.asarray(q,np.float32) for q in GL.get(k,[])]
    VEC[i]=[v+[w]+sub(k,q) for v,w,q in zip(to_svg(segs,400/W),GWD.get(k,[]),segs)]
    m=INK*(lab==si); o=base(); save(o*(1-m[:,:,None])+RED*m[:,:,None],str(i)); DONE=np.maximum(DONE,m*0.85); save(base(),f'{i}g')
NL=i; guide=Zr.copy(); hbase=base(); save(hbase,f'{NL}h'); prev=hbase.copy(); acc=Zr.copy()
nz=cv2.GaussianBlur(np.random.default_rng(7).random((H,W)).astype(np.float32),(0,0),6); nz=(nz-nz.min())/(nz.max()-nz.min())
def show(src): a=acc[:,:,None]; return hbase*(1-a)+src*a
def tstep():
    global i,prev
    i+=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=10,sc=400/W); prev=img
for nm,m,bands in REG:
    reg=cv2.GaussianBlur(cv2.dilate(m.astype(np.float32),np.ones((3,3),np.uint8)),(0,0),2)
    soft=np.clip((reg-0.5+0.25*(nz-0.5))*3+0.5,0,1)
    for b in bands: acc=np.maximum(acc,soft*np.clip((d-b)/0.06,0,1) if b>0 else soft); tstep()
i+=1; acc[:]=1; img=show(orig); save(img,str(i)); SV[i]=F.streams(np.abs(img-prev).max(2),spacing=8,sc=400/W)
json.dump({'vec':{str(k):v for k,v in VEC.items()},'svec':{str(k):v for k,v in SV.items()},'nl':NL,'n':i},open(f'{TAG}_v.json','w'),separators=(',',':'))
ims=[cv2.resize(cv2.imread(f'{O}/{j}.png'),(300,int(300*H/W))) for j in range(1,i+1)]
while len(ims)%6: ims.append(np.full_like(ims[0],255))
cv2.imwrite(f'pasos_{TAG}.jpg',np.vstack([np.hstack(ims[r*6:(r+1)*6]) for r in range(len(ims)//6)])); print(TAG,'pasos',i,'lineas',NL)
