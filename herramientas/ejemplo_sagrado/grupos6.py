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
RAYOS=cfg.get('rayos') or []
if isinstance(RAYOS,dict): RAYOS=[RAYOS]          # puede haber varios grupos de rayos (la luz del corazón y los rayos grandes)
for R_ in RAYOS: R_['_m']=mk(['p',R_['zona']])
LET=cfg.get('letras')      # letras con contorno: trazos dentro de la franja de las letras que son cerrados o muy curvos
if LET: LET['_m']=mk(['p',LET['zona']])
if LET and LET.get('encerradas'):
    # letras con contorno y relleno blanco: su interior es un hueco blanco encerrado por el contorno (los rayos y la ropa
    # se detienen en la orilla de la letra). Un trazo es de las letras si va pegado a esos huecos.
    E=LET['encerradas']; gb=cv2.imread('gris_big.png',0); sb=gb.shape[1]/W
    x0,y0,x1,y1=[int(round(v*sb)) for v in E['caja']]; bb=gb[y0:y1,x0:x1]
    wh=(bb>E.get('umbral',200)).astype(np.uint8); n_,lab_,st_,_=cv2.connectedComponentsWithStats(wh,4); hh,ww=bb.shape
    ok=np.zeros(n_,bool)
    for i_ in range(1,n_):
        x_,y_,w_,h_,a_=st_[i_]
        ok[i_]=not(x_==0 or y_==0 or x_+w_>=ww or y_+h_>=hh) and E['area'][0]<=a_<=E['area'][1]
    hueco=np.zeros(gb.shape,np.uint8); hueco[y0:y1,x0:x1]=ok[lab_].astype(np.uint8)
    d_=int(E.get('dil',6)); hueco=cv2.dilate(hueco,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*d_+1,2*d_+1)))
    LET['_h']=cv2.resize(hueco,(W,H),interpolation=cv2.INTER_NEAREST); print('letras: huecos',int(ok.sum()))
def giro(q):
    d=np.diff(q,axis=0); d=d[np.hypot(*d.T)>1e-6]
    if len(d)<2: return 0.0
    a=np.arctan2(d[:,1],d[:,0]); da=np.diff(a); da=(da+np.pi)%(2*np.pi)-np.pi; return float(np.abs(da).sum())
if LET and '_h' in LET:
    # un trazo que sigue un rato la orilla de una letra y luego se va por un rayo o por la ropa se parte ahí
    nps=[];nwd=[];npart=0
    for p,w in zip(ps,WD):
        q=remuestrea(p,1.0); xq=np.clip(np.round(q[:,0]).astype(int),0,W-1); yq=np.clip(np.round(q[:,1]).astype(int),0,H-1)
        inl=LET['_h'][yq,xq]>0; fr=float(inl.mean())
        if 0.08<fr<0.999 and len(q)>=12:
            piezas=tramos(q,[bool(v) for v in inl],LET.get('tramo',6))
            if len(piezas)>1 and any((not v) and len(pc)>=LET.get('fuera_min',12) for v,pc in piezas):
                npart+=1
                for _,piece in piezas:
                    if len(piece)>=2: nps.append(cv2.approxPolyDP(piece.reshape(-1,1,2).astype(np.float32),0.2,False).reshape(-1,2)); nwd.append(w)
                continue
        nps.append(p); nwd.append(w)
    ps,WD=nps,nwd; print('letras: trazos partidos en la orilla',npart)
G={};GW={}
for p,w in zip(ps,WD):
    q0=remuestrea(p,1.0)      # las fracciones dentro de una zona se miden a lo largo del trazo, no solo en sus vértices
    x=np.clip(np.round(q0[:,0]).astype(int),0,W-1); y=np.clip(np.round(q0[:,1]).astype(int),0,H-1)
    k=None
    if B:
        ext=max(np.ptp(p[:,0]),np.ptp(p[:,1])); L=float(np.sum(np.hypot(*np.diff(p,axis=0).T)))
        cerr=np.linalg.norm(p[0]-p[-1])<max(1.5,0.12*L)
        if cerr and ext<=B['max'] and L>4 and AG[y,x].mean()>0.7 and FUERA[y,x].mean()<0.3: k=B['paso']
    if k is None and LET and '_h' in LET:
        if LET['_h'][y,x].mean()>=LET.get('pegado',0.8): k=LET['paso']
    elif k is None and LET and LET['_m'][y,x].mean()>=LET.get('dentro',0.85):
        q1=remuestrea(p,1.0); cerr=len(q1)>3 and np.linalg.norm(q1[0]-q1[-1])<LET.get('cierre',2.0)
        grueso=w>=LET.get('grosor_min',99) and p[:,1].max()<=LET.get('y_max',1e9)     # el contorno de las letras es más grueso que los rayos y la ropa
        if cerr or grueso or giro(remuestrea(p,2.0))>=LET.get('giro_min',3.0): k=LET['paso']
    sin_rayos=bool(cfg.get('antes_rayos')) and max(M[z][y,x].mean() for z in cfg['antes_rayos'])>0.6   # lo que está dentro de estas zonas no es rayo (la cruz, los dedos)
    for R_ in ([] if (k is not None or sin_rayos) else RAYOS):
        # rayos (o cuerdas): trazos rectos y largos que apuntan al centro
        L=float(np.sum(np.hypot(*np.diff(p,axis=0).T))); a,b=p[0],p[-1]; ch=float(np.hypot(*(b-a)))
        if L>=R_['min_L'] and ch/L>=R_['recta'] and R_['_m'][y,x].mean()>R_.get('dentro',0.8):
            u=(b-a)/ch; nrm=np.array([-u[1],u[0]])
            if 'desv' in R_ and float(np.max(np.abs((p-a)@nrm)))>max(R_.get('desv_abs',2.5),R_['desv']*L): continue   # se curva: es un pliegue, no un rayo
            mid=(a+b)/2     # la tolerancia crece con la distancia al centro (los rayos dibujados a mano no llegan exactos)
            if min(abs(float(np.dot(np.array(ap)-a,nrm)))-max(R_['tol'],R_.get('ang',0)*float(np.hypot(*(np.array(ap)-mid)))) for ap in R_['apices'])<=0: k=R_['paso']; break
    if k is not None:
        G.setdefault(k,[]).append(p); GW.setdefault(k,[]).append(float(w)); continue
    # cada punto toma su zona; los trazos largos que cruzan de una parte a otra se parten en la orilla de la zona
    q=remuestrea(p,1.0); xq=np.clip(np.round(q[:,0]).astype(int),0,W-1); yq=np.clip(np.round(q[:,1]).astype(int),0,H-1)
    labs=[next((nm for nm in cfg['orden'] if M[nm][b,a]),cfg['resto']) for a,b in zip(xq,yq)]
    for k,piece in tramos(q,labs,cfg.get('tramo_min',10)):
        if len(piece)>2: piece=cv2.approxPolyDP(piece.reshape(-1,1,2),0.2,False).reshape(-1,2)
        G.setdefault(k,[]).append(piece.astype(np.float32)); GW.setdefault(k,[]).append(float(w))
RS=cfg.get('rayos_sueltos')
if RS and G.get(RS['paso']):
    # pedacitos de rayo que quedaron sueltos (donde la luz los borra): si van sobre la línea de un rayo ya encontrado, son rayo
    if RS.get('fuera'): RS['_f']=mk(['p',RS['fuera']]); RS['_z']=mk(['p',RS['zona']])
    lin=[]
    for r in G[RS['paso']]:
        a_,b_=r[0],r[-1]; ch_=float(np.hypot(*(b_-a_)))
        if ch_>=RS.get('min_rayo',30): u_=(b_-a_)/ch_; lin.append((a_,u_,np.array([-u_[1],u_[0]])))
    mov=0
    for k_ in RS['de']:
        keep=[];keepw=[]
        for p,w in zip(G.get(k_,[]),GW.get(k_,[])):
            L_=float(np.sum(np.hypot(*np.diff(p,axis=0).T))); ok=False
            if 1.5<=L_<=RS.get('max_L',40):
                d_=p[-1]-p[0]; nd=float(np.hypot(*d_))
                for a_,u_,n_ in lin:
                    if float(np.max(np.abs((p-a_)@n_)))<=RS.get('dist',2.0) and (nd<2 or abs(float(np.dot(d_/nd,u_)))>=np.cos(np.radians(RS.get('ang',12)))): ok=True; break
            if not ok and RS.get('fuera'):      # o si quedó fuera de la figura, en la zona de los rayos
                xi=np.clip(np.round(p[:,0]).astype(int),0,W-1); yi=np.clip(np.round(p[:,1]).astype(int),0,H-1)
                ok=L_<=RS.get('max_L',40) and RS['_f'][yi,xi].max()==0 and RS['_z'][yi,xi].min()==1
            if ok: G[RS['paso']].append(p); GW[RS['paso']].append(w); mov+=1
            else: keep.append(p); keepw.append(w)
        G[k_]=keep; GW[k_]=keepw
    print('rayos sueltos',mov)
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
