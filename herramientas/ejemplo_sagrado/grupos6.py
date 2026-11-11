"""Reparte los trazos en pasos (como grupos5) con zonas de cfg.json.
Además: 'burbujas' = trazos cerrados y chiquitos en el agua, fuera de los animales, van a su propio paso."""
import cv2,numpy as np,json
cfg=json.load(open('cfg.json')); H=cfg['H']; W=900
ps=list(np.load('trazos_hd.npy',allow_pickle=True)); WD=list(np.load('wid_hd.npy'))
def mk(sh):
    m=np.zeros((H,W),np.uint8)
    if sh[0]=='p': cv2.fillPoly(m,[np.array(sh[1],np.int32)],1)
    else: cv2.ellipse(m,tuple(sh[1]),tuple(sh[2]),0,0,360,1,-1)
    return m
M={k:np.clip(sum(mk(s) for s in v),0,1) for k,v in cfg['zonas'].items()}
B=cfg.get('burbujas')
if B: AG=mk(['p',B['agua']]); FUERA=np.clip(sum(M[k] for k in B['fuera_de']),0,1)
def remuestrea(p,step):
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(p,axis=0).T))]
    if d[-1]<step: return p.astype(np.float32)
    t=np.linspace(0,d[-1],max(2,int(np.ceil(d[-1]/step))+1)); return np.stack([np.interp(t,d,p[:,0]),np.interp(t,d,p[:,1])],1).astype(np.float32)
def tramos(q,labs,minlen):
    """corridas de la misma zona; las corridas cortitas se juntan con la vecina más larga"""
    R=[]; 
    for i,l in enumerate(labs):
        if R and R[-1][0]==l: R[-1][2]=i
        else: R.append([l,i,i])
    cerrado=len(q)>3 and np.linalg.norm(q[0]-q[-1])<1.5
    while len(R)>1:
        ln=[r[2]-r[1]+1 for r in R]; j=int(np.argmin(ln))
        if ln[j]>=minlen: break
        if j==0: R[1][1]=R[0][1]; R.pop(0)
        elif j==len(R)-1: R[-2][2]=R[-1][2]; R.pop()
        else:
            if ln[j-1]>=ln[j+1]: R[j-1][2]=R[j][2]
            else: R[j+1][1]=R[j][1]
            R.pop(j)
        R2=[]
        for r in R:
            if R2 and R2[-1][0]==r[0]: R2[-1][2]=r[2]
            else: R2.append(r)
        R=R2
    if cerrado and len(R)>1 and R[0][0]==R[-1][0]:
        a=R.pop(); return [(a[0],np.vstack([q[a[1]:a[2]+1],q[R[0][1]+1:R[0][2]+2]]))]+[(r[0],q[max(0,r[1]-1):r[2]+2]) for r in R[1:]]
    return [(r[0],q[max(0,r[1]-1):r[2]+2]) for r in R]
RZ=mk(['p',cfg['rayos']['zona']]) if cfg.get('rayos') else None
G={};GW={}
for p,w in zip(ps,WD):
    q0=remuestrea(p,1.0)      # las fracciones dentro de una zona se miden a lo largo del trazo, no solo en sus vértices
    x=np.clip(np.round(q0[:,0]).astype(int),0,W-1); y=np.clip(np.round(q0[:,1]).astype(int),0,H-1)
    k=None
    if B:
        ext=max(np.ptp(p[:,0]),np.ptp(p[:,1])); L=float(np.sum(np.hypot(*np.diff(p,axis=0).T)))
        cerr=np.linalg.norm(p[0]-p[-1])<max(1.5,0.12*L)
        if cerr and ext<=B['max'] and L>4 and AG[y,x].mean()>0.7 and FUERA[y,x].mean()<0.3: k=B['paso']
    R_=cfg.get('rayos')
    if k is None and R_ and cfg.get('antes_rayos'):      # lo que está dentro de estas zonas no es rayo (la cruz, los dedos)
        if max(M[z][y,x].mean() for z in cfg['antes_rayos'])>0.6: R_=None
    if k is None and R_:
        # cuerdas: trazos rectos y largos que apuntan a la punta del mástil (o a las puntas de la verga)
        L=float(np.sum(np.hypot(*np.diff(p,axis=0).T))); a,b=p[0],p[-1]; ch=float(np.hypot(*(b-a)))
        if L>=R_['min_L'] and ch/L>=R_['recta'] and RZ[y,x].mean()>R_.get('dentro',0.8):
            u=(b-a)/ch; nrm=np.array([-u[1],u[0]])
            mid=(a+b)/2     # la tolerancia crece con la distancia al centro (los rayos dibujados a mano no llegan exactos)
            if min(abs(float(np.dot(np.array(ap)-a,nrm)))-max(R_['tol'],R_.get('ang',0)*float(np.hypot(*(np.array(ap)-mid)))) for ap in R_['apices'])<=0: k=R_['paso']
    if k is not None:
        G.setdefault(k,[]).append(p); GW.setdefault(k,[]).append(float(w)); continue
    # cada punto toma su zona; los trazos largos que cruzan de una parte a otra se parten en la orilla de la zona
    q=remuestrea(p,1.0); xq=np.clip(np.round(q[:,0]).astype(int),0,W-1); yq=np.clip(np.round(q[:,1]).astype(int),0,H-1)
    labs=[next((nm for nm in cfg['orden'] if M[nm][b,a]),cfg['resto']) for a,b in zip(xq,yq)]
    for k,piece in tramos(q,labs,cfg.get('tramo_min',10)):
        if len(piece)>2: piece=cv2.approxPolyDP(piece.reshape(-1,1,2),0.2,False).reshape(-1,2)
        G.setdefault(k,[]).append(piece.astype(np.float32)); GW.setdefault(k,[]).append(float(w))
np.save('G.npy',np.array(G,dtype=object)); np.save('GW.npy',np.array(GW,dtype=object)); print({k:len(v) for k,v in G.items()})
cols=[(40,80,240),(255,0,0),(200,0,200),(0,140,0),(0,120,255),(120,120,0),(150,150,150),(0,0,0),(255,128,0),(128,0,255),(0,200,200)]
f=2; o=np.full((H*f,W*f,3),250,np.uint8)
for i,k in enumerate(cfg['pasos']):
    for p in G.get(k,[]): cv2.polylines(o,[np.round(p*f*4).astype(np.int32)],False,cols[i%len(cols)],2,cv2.LINE_AA,shift=2)
    cv2.putText(o,k,(10,40+40*i),0,1.1,cols[i%len(cols)],3)
for k,v in cfg['zonas'].items():
    for sh in v:
        if sh[0]=='p': cv2.polylines(o,[np.array(sh[1],np.int32)*f],True,(200,200,200),1)
cv2.imwrite('grupos.jpg',o)
