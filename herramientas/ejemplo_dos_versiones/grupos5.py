import cv2,numpy as np,sys,json
cfg=json.load(open('cfg.json')); H=cfg['H']; W=900
ps=list(np.load('trazos_hd.npy',allow_pickle=True)); WD=list(np.load('wid_hd.npy'))
def mk(sh):
    m=np.zeros((H,W),np.uint8)
    if sh[0]=='p': cv2.fillPoly(m,[np.array(sh[1],np.int32)],1)
    else: cv2.ellipse(m,tuple(sh[1]),tuple(sh[2]),0,0,360,1,-1)
    return m
M={k:np.clip(sum(mk(s) for s in v),0,1) for k,v in cfg['zonas'].items()}
G={};GW={}
for p,w in zip(ps,WD):
    x=np.clip(np.round(p[:,0]).astype(int),0,W-1); y=np.clip(np.round(p[:,1]).astype(int),0,H-1)
    L=float(np.sum(np.hypot(*np.diff(p,axis=0).T)))
    k=None
    for nm in cfg['orden']:
        if nm=='bigotes':
            if 'bigotes' in M and M['bigotes'][y,x].mean()>0.6 and w<0.7 and L>45: k=nm; break
            continue
        if M[nm][y,x].mean()>0.5: k=nm; break
    k=k or cfg['resto']
    G.setdefault(k,[]).append(p); GW.setdefault(k,[]).append(float(w))
np.save('G.npy',np.array(G,dtype=object)); np.save('GW.npy',np.array(GW,dtype=object)); print({k:len(v) for k,v in G.items()})
cols=[(40,80,240),(255,0,0),(200,0,200),(0,140,0),(0,120,255),(120,120,0),(150,150,150),(0,0,0),(255,128,0)]
o=np.full((H,W,3),250,np.uint8)
for i,k in enumerate(cfg['pasos']):
    for p in G.get(k,[]): cv2.polylines(o,[np.round(p*4).astype(np.int32)],False,cols[i%len(cols)],2,cv2.LINE_AA,shift=2)
    cv2.putText(o,k,(10,30+22*i),0,0.6,cols[i%len(cols)],2)
cv2.imwrite('grupos.jpg',o)
