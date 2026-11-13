"""Trazo continuo: une los pedazos de una misma línea y ordena los trazos de cada paso
para que la mano siga de corrido (cada trazo empieza cerca de donde terminó el anterior),
primero los contornos y después los detalles. Trabaja directo sobre los trazos de la app (escala 400)."""
import re,json,numpy as np
def parse(d):
    n=[float(x) for x in re.findall(r'-?\d+\.?\d*',d)]; return np.array(n,np.float32).reshape(-1,2)
def to_d(p):
    if len(p)==1: p=np.vstack([p,p])
    return 'M'+f'{p[0,0]:.1f} {p[0,1]:.1f}'+'L'+' '.join(f'{x:.1f} {y:.1f}' for x,y in p[1:])
def plen(p): return float(np.sum(np.hypot(*np.diff(p,axis=0).T))) if len(p)>1 else 0.0
def closed(p): return len(p)>3 and float(np.linalg.norm(p[0]-p[-1]))<0.6
def tang(p,e,k=5):
    a=p[0] if e==0 else p[-1]
    for j in range(1,min(len(p),k+1)+0):
        b=p[j] if e==0 else p[-1-j]
        if np.linalg.norm(a-b)>1.2: break
    d=a-b; n=np.linalg.norm(d); return d/n if n>1e-6 else np.zeros(2,np.float32)
def unir(P,Wd,cerca=1.1,lejos=3.0,cosmin=0.5,wratio=2.0):
    """Junta pedazos cuyas puntas se tocan y siguen la misma dirección (o se tocan en una esquina)."""
    n=len(P); ends=[]
    for i,p in enumerate(P):
        if len(p)<2 or closed(p): continue
        ends.append((i,0,p[0],tang(p,0))); ends.append((i,1,p[-1],tang(p,1)))
    cand=[]
    if ends:
        pts=np.array([e[2] for e in ends])
        from scipy.spatial import cKDTree
        for a,b in cKDTree(pts).query_pairs(lejos):
            ia,ea,pa,ta=ends[a]; ib,eb,pb,tb=ends[b]
            if ia==ib: continue
            wa,wb=Wd[ia],Wd[ib]
            if wa and wb and max(wa,wb)/max(min(wa,wb),1e-3)>wratio: continue
            d=float(np.linalg.norm(pa-pb)); c=float(-(ta@tb))
            if not (d<=cerca or c>=cosmin): continue
            cand.append((d+1.5*(1-c),a,b))
    cand.sort(); used=set(); par=list(range(n)); link={}
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for _,a,b in cand:
        if a in used or b in used: continue
        ia,ea=ends[a][0],ends[a][1]; ib,eb=ends[b][0],ends[b][1]
        if f(ia)==f(ib): continue
        par[f(ia)]=f(ib); used|={a,b}; link[(ia,ea)]=(ib,eb); link[(ib,eb)]=(ia,ea)
    seen=set(); out=[]; ow=[]
    for i in range(n):
        if i in seen: continue
        cur=(i,0); vis={i}
        while cur in link:
            j,e=link[cur]
            if j in vis: break
            vis.add(j); cur=(j,1-e)
        j,e=cur; parts=[]; ws=0.0; ls=0.0; hasw=False
        while True:
            p=P[j] if e==0 else P[j][::-1]
            if parts and np.linalg.norm(p[0]-parts[-1][-1])<0.3: p=p[1:]
            if len(p): parts.append(p)
            seen.add(j); L=plen(P[j]); ls+=L
            if Wd[j]: ws+=Wd[j]*max(L,0.1); hasw=True
            nx=link.get((j,1-e))
            if nx is None or nx[0] in seen: break
            j,e=nx
        out.append(np.vstack(parts)); ow.append(round(ws/max(ls,0.1),2) if hasw else None)
    return out,ow
def ordenar(P,Wd,pen=None,wthr=None,Lmaj=26.0):
    """Primero los contornos (gruesos o largos), luego los detalles; cada trazo empieza junto a donde terminó el anterior."""
    L=[plen(p) for p in P]
    major=[i for i in range(len(P)) if L[i]>=Lmaj or (wthr is not None and Wd[i] is not None and Wd[i]>=wthr and L[i]>=4)]
    minor=[i for i in range(len(P)) if i not in set(major)]
    res=[]
    for grp in (major,minor):
        rem=set(grp)
        if not rem: continue
        if pen is None:   # empezar arriba a la izquierda, como empieza uno a dibujar
            best=None
            for i in rem:
                for q in (P[i][0],P[i][-1]):
                    s=q[1]+0.35*q[0]
                    if best is None or s<best: best=s; pen=q.copy()
        while rem:
            bi=None
            for i in rem:
                p=P[i]
                if closed(p):
                    dd=np.linalg.norm(p-pen,axis=1); k=int(np.argmin(dd)); dist=float(dd[k]); how=('loop',k)
                else:
                    d0=float(np.linalg.norm(p[0]-pen)); d1=float(np.linalg.norm(p[-1]-pen))
                    dist,how=(d0,('fwd',0)) if d0<=d1 else (d1,('rev',0))
                if bi is None or dist<bi[0]: bi=(dist,i,how)
            _,i,how=bi; p=P[i]
            if how[0]=='rev': p=p[::-1]
            elif how[0]=='loop':
                k=how[1]; p=np.vstack([p[k:-1],p[:k+1]]) if k>0 else p
            res.append((p,Wd[i])); rem.remove(i); pen=p[-1]
    return res
def saltos(P):
    """Distancia total que la mano viaja en el aire entre un trazo y el siguiente."""
    return float(sum(np.linalg.norm(P[k][0]-P[k-1][-1]) for k in range(1,len(P))))
def procesar_paso(vk,wthr):
    P=[parse(v[0]) for v in vk]; Wd=[(v[2] if len(v)>2 else None) for v in vk]
    keep=[k for k,p in enumerate(P) if len(p)>=1]; P=[P[k] for k in keep]; Wd=[Wd[k] for k in keep]
    antes=(len(P),saltos(P))
    J,JW=unir(P,Wd); R=ordenar(J,JW,wthr=wthr)
    out=[]
    for p,w in R:
        e=[to_d(p),round(plen(p),1)]
        if w is not None: e.append(w)
        out.append(e)
    despues=(len(R),saltos([p for p,_ in R]))
    return out,antes,despues
def umbral(vec):
    ws=[v[2] for vk in vec.values() for v in vk if len(v)>2]
    if not ws: return None
    return max(0.9,float(np.percentile(ws,80))*0.75)
def leer_zvec(path):
    L=open(path).read().split('\n'); a=L[0].index('=')+1; obj=json.loads(L[0][a:L[0].rindex(';')]); return L,obj
def escribir_zvec(path,L,obj):
    a=L[0].index('=')+1; L[0]=L[0][:a]+json.dumps(obj,separators=(',',':'),ensure_ascii=False)+';'; open(path,'w').write('\n'.join(L))

# ---------- orden "rodeando la figura" ----------
def _nn(items,pen):
    """items: lista de (p,w); orden por cercanía desde la pluma (con giro de los cerrados)."""
    rem=list(range(len(items))); res=[]
    while rem:
        bi=None
        for i in rem:
            p=items[i][0]
            if closed(p):
                dd=np.linalg.norm(p-pen,axis=1); k=int(np.argmin(dd)); cand=(float(dd[k]),i,('loop',k))
            else:
                d0=float(np.linalg.norm(p[0]-pen)); d1=float(np.linalg.norm(p[-1]-pen)); cand=(d0,i,('fwd',0)) if d0<=d1 else (d1,i,('rev',0))
            if bi is None or cand[0]<bi[0]: bi=cand
        _,i,how=bi; p,w=items[i]
        if how[0]=='rev': p=p[::-1]
        elif how[0]=='loop' and how[1]>0: p=np.vstack([p[how[1]:-1],p[:how[1]+1]])
        res.append((p,w)); rem.remove(i); pen=p[-1]
    return res,pen
def ordenar2(P,Wd,wthr=None,Lmaj=26.0,close_u=7.0,near_u=2.6,pen=None):
    import cv2
    from scipy.spatial import cKDTree
    if not P: return []
    S=2.0; allp=np.vstack(P); x0,y0=np.floor(allp.min(0))-12; x1,y1=np.ceil(allp.max(0))+12
    Wpx,Hpx=int((x1-x0)*S)+1,int((y1-y0)*S)+1
    m=np.zeros((Hpx,Wpx),np.uint8)
    for p in P: cv2.polylines(m,[np.round((p-[x0,y0])*S).astype(np.int32)],closed(p),1,3)
    k=int(close_u*S)|1; m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    comps=[]
    for c in cs:
        c=c[:,0,:].astype(np.float32)/S+[x0,y0]
        if len(c)<8: continue
        a=0.5*np.sum(c[:,0]*np.roll(c[:,1],-1)-np.roll(c[:,0],-1)*c[:,1])
        if a<0: c=c[::-1]                      # vuelta en el sentido del reloj (arriba hacia la derecha)
        mask=np.zeros((Hpx,Wpx),np.uint8); cv2.drawContours(mask,[np.round((c-[x0,y0])*S).astype(np.int32)],-1,1,-1)
        comps.append({'c':c,'mask':mask,'items':[]})
    if not comps: return _nn(list(zip(P,Wd)),P[0][0] if pen is None else pen)[0]
    for p,w in zip(P,Wd):
        q=np.round((p-[x0,y0])*S).astype(int); q[:,0]=np.clip(q[:,0],0,Wpx-1); q[:,1]=np.clip(q[:,1],0,Hpx-1)
        best=max(range(len(comps)),key=lambda j:comps[j]['mask'][q[:,1],q[:,0]].mean()); comps[best]['items'].append((p,w))
    def top_left(c): return c[int(np.argmin(c[:,1]+0.35*c[:,0]))]
    res=[]
    if pen is None:
        allc=np.vstack([cc['c'] for cc in comps]); pen=top_left(allc)
    pend=[cc for cc in comps if cc['items']]
    while pend:
        j_=min(range(len(pend)),key=lambda j:float(np.min(np.linalg.norm(pend[j]['c']-pen,axis=1)))); cc=pend.pop(j_)
        c=cc['c']; seg=np.hypot(*np.diff(np.vstack([c,c[:1]]),axis=0).T); s=np.r_[0,np.cumsum(seg)][:-1]; Lt=float(seg.sum())
        # punto de arranque: el de la orilla más cercano a la pluma (al principio, arriba a la izquierda)
        s0=s[int(np.argmin(np.linalg.norm(c-pen,axis=1)))]
        tree=cKDTree(c); borde=[]; dentro=[]
        for p,w in cc['items']:
            dd,ii=tree.query(p)
            if (dd<=near_u).mean()>=0.6 and plen(p)>=3:
                rel=(s[ii]-s0)%Lt
                if closed(p):
                    # un contorno cerrado completo: arranca junto al inicio y gira con el reloj
                    k=int(np.argmin(rel)); a=0.5*np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
                    q=p[:-1] if a>0 else p[:-1][::-1]
                    k=int(np.argmin(np.linalg.norm(q-c[int(np.argmin(np.abs(s-s0)))],axis=1))); q=np.vstack([q[k:],q[:k+1]]); borde.append((0.0,q,w)); continue
                # sentido: que avance con el reloj
                stp=((np.diff(s[ii])+Lt/2)%Lt)-Lt/2      # cuánto avanza cada tramo por la orilla
                if stp.sum()<0: p=p[::-1]; dd,ii=dd[::-1],ii[::-1]; rel=rel[::-1]
                # posición: dónde empieza, cuidando el cruce por el arranque
                adv=np.r_[0,np.cumsum(((np.diff(s[ii])+Lt/2)%Lt)-Lt/2)]
                key=float(rel[0]) if rel[0]+adv.max()<=Lt*1.02 or rel[0]<0.5*Lt else float(rel[0]-Lt)
                borde.append((key,p,w))
            else: dentro.append((p,w))
        borde.sort(key=lambda t:t[0])
        for _,p,w in borde: res.append((p,w)); pen=p[-1]
        # adentro: primero las líneas fuertes/largas, luego los detalles finos, siempre por cercanía
        Lm=lambda p:plen(p)
        big=[(p,w) for p,w in dentro if Lm(p)>=Lmaj or (wthr is not None and w is not None and w>=wthr and Lm(p)>=4)]
        small=[(p,w) for p,w in dentro if not (Lm(p)>=Lmaj or (wthr is not None and w is not None and w>=wthr and Lm(p)>=4))]
        r1,pen=_nn(big,pen); r2,pen=_nn(small,pen); res+=r1+r2
    return res
def procesar_paso2(vk,wthr):
    P=[parse(v[0]) for v in vk]; Wd=[(v[2] if len(v)>2 else None) for v in vk]
    keep=[k for k,p in enumerate(P) if len(p)>=1]; P=[P[k] for k in keep]; Wd=[Wd[k] for k in keep]
    antes=(len(P),saltos(P))
    J,JW=unir(P,Wd); R=ordenar2(J,JW,wthr=wthr)
    out=[]
    for p,w in R:
        e=[to_d(p),round(plen(p),1)]
        if w is not None: e.append(w)
        out.append(e)
    return out,antes,(len(R),saltos([p for p,_ in R]))

# ---------- orden que minimiza el viaje de la mano en el aire (vecino más cercano + mejoras 2-opt / mover trazos) ----------
def _mejorar(items,fix_first=True,max_pasadas=30):
    """items: lista de (p,w) ya orientados en orden. Mejora el orden para que la mano viaje menos en el aire."""
    n=len(items)
    if n<3: return items
    P=[p for p,_ in items]; W=[w for _,w in items]
    A=np.array([p[0] for p in P],np.float64); B=np.array([p[-1] for p in P],np.float64)
    order=list(range(n)); flip=[False]*n
    def S(k): return B[order[k]] if flip[order[k]] else A[order[k]]
    def E(k): return A[order[k]] if flip[order[k]] else B[order[k]]
    i0=1 if fix_first else 0
    for _ in range(max_pasadas):
        mejoro=False
        # 2-opt: invertir un tramo del recorrido
        Sx=np.array([S(k) for k in range(n)]); Ex=np.array([E(k) for k in range(n)])
        for i in range(i0,n):
            left=Ex[i-1] if i>0 else None
            # j >= i
            js=np.arange(i,n)
            nxt=np.vstack([Sx[js[:-1]+1],np.full((1,2),np.nan)]) if len(js)>0 else None
            old=np.zeros(len(js)); new=np.zeros(len(js))
            if left is not None:
                old+=np.linalg.norm(left-Sx[i]); new+=np.linalg.norm(Ex[js]-left,axis=1)
            has=~np.isnan(nxt[:,0])
            old[has]+=np.linalg.norm(Ex[js[has]]-nxt[has],axis=1); new[has]+=np.linalg.norm(Sx[i]-nxt[has],axis=1)
            d=new-old; k=int(np.argmin(d))
            if d[k]<-1e-6:
                j=int(js[k]); seg=order[i:j+1][::-1]; order[i:j+1]=seg
                for q in seg: flip[q]=not flip[q]
                Sx=np.array([S(t) for t in range(n)]); Ex=np.array([E(t) for t in range(n)]); mejoro=True
        # mover un trazo a otro lugar (con o sin voltearlo)
        for k in range(i0,n):
            Sx=np.array([S(t) for t in range(n)]); Ex=np.array([E(t) for t in range(n)])
            sk,ek=Sx[k],Ex[k]
            gain=(np.linalg.norm(Ex[k-1]-sk) if k>0 else 0)+(np.linalg.norm(ek-Sx[k+1]) if k<n-1 else 0)-(np.linalg.norm(Ex[k-1]-Sx[k+1]) if 0<k<n-1 else 0)
            # posiciones: insertar entre m y m+1 (m=-1 al principio no se permite si fix_first)
            ms=np.array([m for m in range(i0-1,n) if m!=k and m!=k-1 and m>=0],int)
            if len(ms)==0: continue
            prevE=Ex[ms]; nextS=np.array([Sx[m+1] if m+1<n else [np.nan,np.nan] for m in ms])
            has=~np.isnan(nextS[:,0])
            base=np.where(has,np.linalg.norm(prevE-np.nan_to_num(nextS),axis=1),0)
            c1=np.linalg.norm(prevE-sk,axis=1)+np.where(has,np.linalg.norm(ek-np.nan_to_num(nextS),axis=1),0)-base
            c2=np.linalg.norm(prevE-ek,axis=1)+np.where(has,np.linalg.norm(sk-np.nan_to_num(nextS),axis=1),0)-base
            c=np.minimum(c1,c2); t=int(np.argmin(c))
            if c[t]<gain-1e-6:
                m=int(ms[t]); q=order[k]; fl=c2[t]<c1[t]
                del order[k]; m2=m if m<k else m-1; order.insert(m2+1,q)
                if fl: flip[q]=not flip[q]
                mejoro=True
        if not mejoro: break
    out=[]
    for q in order:
        p=P[q][::-1] if flip[q] else P[q]; out.append((p,W[q]))
    # contornos cerrados: que empiecen en el punto más cercano a donde quedó la mano
    pen=None; res=[]
    for p,w in out:
        if pen is not None and closed(p):
            dd=np.linalg.norm(p-pen,axis=1); k=int(np.argmin(dd))
            if k>0: p=np.vstack([p[k:-1],p[:k+1]])
        res.append((p,w)); pen=p[-1]
    return res
def ordenar3(P,Wd,wthr=None,Lmaj=26.0,pen=None):
    L=[plen(p) for p in P]
    big=[i for i in range(len(P)) if L[i]>=Lmaj or (wthr is not None and Wd[i] is not None and Wd[i]>=wthr and L[i]>=4)]
    sb=set(big); small=[i for i in range(len(P)) if i not in sb]
    res=[]
    for grp in (big,small):
        if not grp: continue
        items=[(P[i],Wd[i]) for i in grp]
        if pen is None:
            best=None
            for p,_ in items:
                for q in (p[0],p[-1]):
                    s=q[1]+0.35*q[0]
                    if best is None or s<best: best=s; pen=q.copy()
        seq,_=_nn(items,pen)
        seq=_mejorar(seq,fix_first=True)
        res+=seq; pen=seq[-1][0][-1]
    return res
def procesar_paso3(vk,wthr):
    P=[parse(v[0]) for v in vk]; Wd=[(v[2] if len(v)>2 else None) for v in vk]
    keep=[k for k,p in enumerate(P) if len(p)>=1]; P=[P[k] for k in keep]; Wd=[Wd[k] for k in keep]
    antes=(len(P),saltos(P))
    J,JW=unir(P,Wd); R=ordenar3(J,JW,wthr=wthr)
    out=[]
    for p,w in R:
        e=[to_d(p),round(plen(p),1)]
        if w is not None: e.append(w)
        out.append(e)
    return out,antes,(len(R),saltos([p for p,_ in R]))

# ---------- versión final: rápida y probando varios órdenes ----------
def _mejorar(items,fix_first=True,max_pasadas=25):
    n=len(items)
    if n<3: return items
    P=[p for p,_ in items]; W=[w for _,w in items]
    A=np.array([p[0] for p in P],np.float64); B=np.array([p[-1] for p in P],np.float64)
    order=np.arange(n); flip=np.zeros(n,bool)
    def SE(o=None):
        o=order if o is None else o; f=flip[o][:,None]; return np.where(f,B[o],A[o]),np.where(f,A[o],B[o])
    nrm=lambda x:np.sqrt((x*x).sum(-1))
    i0=1 if fix_first else 0
    for _ in range(max_pasadas):
        mejoro=False; Sx,Ex=SE()
        for i in range(i0,n):                      # 2-opt: invertir el tramo i..j
            js=np.arange(i,n); nx=np.minimum(js+1,n-1); has=(js+1)<n
            old=np.where(has,nrm(Ex[js]-Sx[nx]),0.0); new=np.where(has,nrm(Sx[i]-Sx[nx]),0.0)
            if i>0: old=old+nrm(Ex[i-1]-Sx[i]); new=new+nrm(Ex[js]-Ex[i-1])
            d=new-old; k=int(np.argmin(d))
            if d[k]<-1e-6:
                j=i+k; seg=order[i:j+1][::-1].copy(); order[i:j+1]=seg; flip[seg]=~flip[seg]; Sx,Ex=SE(); mejoro=True
        for k in range(i0,n):                      # mover un trazo a otro lugar (y voltearlo si conviene)
            Sx,Ex=SE()
            g=0.0
            if k>0: g+=nrm(Ex[k-1]-Sx[k])
            if k<n-1: g+=nrm(Ex[k]-Sx[k+1])
            if 0<k<n-1: g-=nrm(Ex[k-1]-Sx[k+1])
            rest=np.delete(order,k); S2,E2=SE(rest); sk,ek=Sx[k],Ex[k]; m=len(rest)
            ts=np.arange(max(i0,1) if fix_first else 0,m+1)      # insertar antes de rest[t]
            prev=E2[ts-1]; hasn=ts<m; nxt=S2[np.minimum(ts,m-1)]
            base=np.where(hasn,nrm(prev-nxt),0.0)
            c1=nrm(prev-sk)+np.where(hasn,nrm(ek-nxt),0.0)-base
            c2=nrm(prev-ek)+np.where(hasn,nrm(sk-nxt),0.0)-base
            c=np.minimum(c1,c2); t=int(np.argmin(c))
            if c[t]<g-1e-6:
                q=order[k]; fl=c2[t]<c1[t]; order=np.insert(rest,ts[t],q)
                if fl: flip[q]=~flip[q]
                mejoro=True
        if not mejoro: break
    out=[]; pen=None
    for q in order:
        p=P[q][::-1] if flip[q] else P[q]
        if pen is not None and closed(p):
            dd=np.linalg.norm(p-pen,axis=1); kk=int(np.argmin(dd))
            if kk>0: p=np.vstack([p[kk:-1],p[:kk+1]])
        out.append((p,W[q])); pen=p[-1]
    return out
def _costo(seq): return saltos([p for p,_ in seq])
def _arranque(items):
    best=None
    for p,_ in items:
        for q in (p[0],p[-1]):
            s=q[1]+0.35*q[0]
            if best is None or s<best[0]: best=(s,q.copy())
    return best[1]
def ordenar4(P,Wd,wthr=None,Lmaj=26.0):
    L=[plen(p) for p in P]
    isbig=[L[i]>=Lmaj or (wthr is not None and Wd[i] is not None and Wd[i]>=wthr and L[i]>=4) for i in range(len(P))]
    big=[(P[i],Wd[i]) for i in range(len(P)) if isbig[i]]; small=[(P[i],Wd[i]) for i in range(len(P)) if not isbig[i]]
    res=[]; pen=None
    if big:
        cands=[]
        nn,_=_nn(big,_arranque(big)); cands.append(_mejorar(nn))
        try:
            ar=ordenar2([p for p,_ in big],[w for _,w in big],wthr=wthr,Lmaj=1e9); cands.append(_mejorar(ar))
        except Exception: pass
        best=min(cands,key=_costo); res+=best; pen=best[-1][0][-1]
    if small:
        nn,_=_nn(small,pen if pen is not None else _arranque(small)); res+=_mejorar(nn,fix_first=True)
    return res
def procesar_paso4(vk,wthr):
    P=[parse(v[0]) for v in vk]; Wd=[(v[2] if len(v)>2 else None) for v in vk]
    P,Wd=zip(*[(p,w) for p,w in zip(P,Wd) if len(p)>=1]) if P else ([],[])
    P=list(P); Wd=list(Wd); antes=(len(P),saltos(P))
    J,JW=unir(P,Wd); R=ordenar4(J,JW,wthr=wthr)
    out=[]
    for p,w in R:
        e=[to_d(p),round(plen(p),1)]
        if w is not None: e.append(w)
        out.append(e)
    return out,antes,(len(R),saltos([p for p,_ in R]))

# ---------- v5: figura por figura; en cada una primero la orilla y luego lo de adentro ----------
def _costo_desde(seq,pen):
    if not seq: return 0.0
    return float(np.linalg.norm(seq[0][0][0]-pen))+_costo(seq)
def ordenar5(P,Wd,wthr=None,close_u=7.0,near_u=2.6,chica_u=28.0,pegada_u=1e9,pen=None,por_figura=True):
    """por_figura: cada figura se termina (orilla y luego lo de adentro) antes de pasar a la siguiente,
    así la mano no regresa a una figura que ya dejó (un ojo y luego el otro, una mano y luego la otra).
    pen: dónde quedó la mano (para seguir desde el grupo anterior)."""
    import cv2
    from scipy.spatial import cKDTree
    if not P: return []
    S=2.0; allp=np.vstack(P); x0,y0=np.floor(allp.min(0))-12; x1,y1=np.ceil(allp.max(0))+12
    Wpx,Hpx=int((x1-x0)*S)+1,int((y1-y0)*S)+1
    m=np.zeros((Hpx,Wpx),np.uint8)
    for p in P: cv2.polylines(m,[np.round((p-[x0,y0])*S).astype(np.int32)],closed(p),1,3)
    k=int(close_u*S)|1; m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
    n_,lab=cv2.connectedComponents(m,connectivity=8)
    def chico(p):
        ext=float(max(np.ptp(p[:,0]),np.ptp(p[:,1]))); return (closed(p) and ext<14) or ext<6
    # la orilla se mide sin las gotitas y manchitas de alrededor (si no, la orilla rodea las gotas y no la figura)
    m2=np.zeros_like(m)
    for p in P:
        if not chico(p): cv2.polylines(m2,[np.round((p-[x0,y0])*S).astype(np.int32)],closed(p),1,3)
    m2=cv2.morphologyEx(m2,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
    comps={}
    for i,(p,w) in enumerate(zip(P,Wd)):
        q=np.round((p-[x0,y0])*S).astype(int); q[:,0]=np.clip(q[:,0],0,Wpx-1); q[:,1]=np.clip(q[:,1],0,Hpx-1)
        ls=lab[q[:,1],q[:,0]]; ls=ls[ls>0]; c=int(np.bincount(ls).argmax()) if len(ls) else 0
        comps.setdefault(c,[]).append((p,w))
    # figuritas (manchas, puntitos, burbujas pegadas a una figura): son detalles de la figura grande más cercana,
    # así la mano termina primero la orilla y no se detiene a medio camino a hacer un puntito
    tam={c:sum(plen(p) for p,_ in it if not chico(p)) for c,it in comps.items()}      # un montoncito de gotas no es figura grande
    def extension(c): pts=np.vstack([p for p,_ in comps[c]]); return float(np.ptp(pts,0).max())
    grandes=[c for c in comps if tam[c]>=chica_u and extension(c)>=20]          # un mechoncito o un pececito suelto no es figura grande
    extra={}
    if grandes:
        GP={c:np.vstack([p for p,_ in comps[c]]) for c in grandes}; GT={c:cKDTree(GP[c]) for c in grandes}
        for c in [c for c in comps if c not in grandes]:
            pts=np.vstack([p for p,_ in comps[c]])
            dmin,cb=min(((float(GT[g].query(pts)[0].min()),g) for g in grandes),key=lambda t:t[0])
            # solo si es mucho más chica que la grande (una gota, un mechoncito); una figura de tamaño parecido
            # (el otro ojo, la otra mano) es figura aparte y se termina antes de pasar a la siguiente
            if dmin<=pegada_u and tam[c]<0.35*tam[cb]: extra.setdefault(cb,[]).extend(comps.pop(c))
    # figuras metidas dentro de otra mucho más grande (mechones de la cara dentro de la cabeza, aletas dentro del cuerpo):
    # son detalles de la grande, se hacen cuando ya está toda la orilla
    orden=sorted([c for c in comps if c>0],key=lambda c:-tam[c]); fills={}
    for c in orden:
        if c not in grandes: continue
        mk=((lab==c)&(m2>0)).astype(np.uint8)
        if not mk.any(): continue
        cs,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); f=np.zeros_like(m); cv2.drawContours(f,cs,-1,1,-1); fills[c]=f
    for c in sorted([c for c in comps if c>0],key=lambda c:tam[c]):
        pts=np.vstack([p for p,_ in comps[c]]); q=np.round((pts-[x0,y0])*S).astype(int); q[:,0]=np.clip(q[:,0],0,Wpx-1); q[:,1]=np.clip(q[:,1],0,Hpx-1)
        for g in orden:
            if g==c or g not in fills or g not in comps or tam[g]<3*max(tam[c],1.0): continue
            if fills[g][q[:,1],q[:,0]].mean()>=0.8: extra.setdefault(g,[]).extend(comps.pop(c)+extra.pop(c,[])); break
    # orilla de cada figura
    info=[]
    for c,items in comps.items():
        mask=((lab==c)&(m2>0)).astype(np.uint8) if c>0 else np.zeros_like(m)
        if c>0 and not mask.any(): mask=(lab==c).astype(np.uint8)
        cs,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        if cs:
            cc=max(cs,key=cv2.contourArea)[:,0,:].astype(np.float32)/S+[x0,y0]; tree=cKDTree(cc)
            borde=[];dentro=[]
            for p,w in items:
                if chico(p): dentro.append((p,w)); continue      # manchita, burbuja o rayita pegada a la orilla: es detalle
                dd,_=tree.query(p); (borde if ((dd<=near_u).mean()>=0.6) else dentro).append((p,w))
        else: borde,dentro=list(items),[]
        if not borde: borde,dentro=dentro,[]
        info.append((borde,dentro+extra.get(c,[])))
    princ=[it for b,d in info for it in b if sum(plen(q) for q,_ in b)>=chica_u and float(np.ptp(np.vstack([q for q,_ in b]),0).max())>=20]       # se empieza por una orilla grande
    res=[]
    if pen is None: pen=_arranque(princ or [it for b,d in info for it in b+d])
    def pts_of(items): return np.vstack([np.vstack([p[0],p[-1]]) if not closed(p) else p for p,_ in items])
    def hacer_borde(borde):
        nonlocal pen,res
        cands=[]
        nn,_=_nn(borde,pen); cands.append(_mejorar(nn))
        if len(borde)>=3:
            try:
                ar=ordenar2([p for p,_ in borde],[w for _,w in borde],wthr=wthr,Lmaj=1e9,pen=pen); cands.append(_mejorar(ar))
            except Exception: pass
        best=min(cands,key=lambda s:_costo_desde(s,pen)); res+=best; pen=best[-1][0][-1]
    def hacer_dentro(dentro):      # primero líneas fuertes, luego detalles finos
        nonlocal pen,res
        L=[plen(p) for p,_ in dentro]
        isb=[(l>=26 or (wthr is not None and it[1] is not None and it[1]>=wthr)) for it,l in zip(dentro,L)]
        # los puntitos (pupilas, manchitas) al final, cuando ya está lo que los rodea
        for grp in ([it for it,b in zip(dentro,isb) if b],[it for it,b in zip(dentro,isb) if not b and not chico(it[0])],[it for it,b in zip(dentro,isb) if not b and chico(it[0])]):
            if not grp: continue
            nn,_=_nn(grp,pen); seq=_mejorar(nn); res+=seq; pen=seq[-1][0][-1]
    if por_figura:
        # figura por figura (la más cercana a la mano): su orilla de corrido y luego lo de adentro
        pend=[j for j in range(len(info)) if info[j][0] or info[j][1]]
        while pend:
            j=min(pend,key=lambda j:float(np.min(np.linalg.norm(pts_of(info[j][0] or info[j][1])-pen,axis=1)))); pend.remove(j)
            if info[j][0]: hacer_borde(info[j][0])
            if info[j][1]: hacer_dentro(info[j][1])
        return res
    # 1) todas las orillas, figura por figura (la más cercana primero)
    pend=[j for j in range(len(info)) if info[j][0]]
    while pend:
        j=min(pend,key=lambda j:float(np.min(np.linalg.norm(pts_of(info[j][0])-pen,axis=1)))); pend.remove(j); hacer_borde(info[j][0])
    # 2) después lo de adentro, figura por figura
    pend=[j for j in range(len(info)) if info[j][1]]
    while pend:
        j=min(pend,key=lambda j:float(np.min(np.linalg.norm(pts_of(info[j][1])-pen,axis=1)))); pend.remove(j); hacer_dentro(info[j][1])
    return res
def niveles(J,JW,min_n=25):
    """Reparte los trazos de un paso en tres niveles, como dibuja un artista:
    1) las líneas principales (contornos, tronco, orillas): las más largas y fuertes, hasta la mitad de la tinta del paso;
    2) las líneas medianas (ramas, mechones grandes, pliegues);
    3) los detalles finos (pelitos, arruguitas, puntitos, texturas).
    Los pasos con pocos trazos se dejan en un solo nivel."""
    if len(J)<min_n: return [(J,JW)]
    L=np.array([plen(p) for p in J]); ws=np.array([w if w is not None else np.nan for w in JW],float)
    wm=np.nanmedian(ws) if np.isfinite(ws).any() else 1.0
    fw=np.where(np.isfinite(ws),np.clip(ws/max(wm,1e-6),0.6,1.6),1.0)
    imp=L*fw; orden=np.argsort(-imp); tot=L.sum(); acc=0; nivel=np.zeros(len(J),int)
    for i in orden:
        nivel[i]=0 if acc<0.5*tot else (1 if acc<0.82*tot else 2); acc+=L[i]
    nivel[(L<6)&(nivel<2)]=2                              # lo muy cortito siempre es detalle
    out=[]
    for k in range(3):
        ix=[i for i in range(len(J)) if nivel[i]==k]
        if ix: out.append(([J[i] for i in ix],[JW[i] for i in ix]))
    return out
def procesar_paso5(vk,wthr,por_figura=True):
    """Un 4.o valor en cada trazo (grupo) da el orden de las partes de un paso compuesto
    (por ejemplo: corazón, corona, llamas y cruz): cada grupo se termina antes de empezar el siguiente."""
    P=[parse(v[0]) for v in vk]; Wd=[(v[2] if len(v)>2 else None) for v in vk]; Gr=[(v[3] if len(v)>3 else 0) for v in vk]
    trip=[(p,w,g) for p,w,g in zip(P,Wd,Gr) if len(p)>=1]; P=[t[0] for t in trip]; Wd=[t[1] for t in trip]; Gr=[t[2] for t in trip]
    antes=(len(P),saltos(P))
    R=[]; pen=None
    for g in sorted(set(Gr)):
        Pg=[p for p,gg in zip(P,Gr) if gg==g]; Wg=[w for w,gg in zip(Wd,Gr) if gg==g]
        J,JW=unir(Pg,Wg)
        for Jt,JWt in niveles(J,JW):      # primero lo importante (líneas largas y fuertes), al final los detalles finos
            Rg=ordenar5(Jt,JWt,wthr=wthr,pen=pen,por_figura=por_figura)
            if Rg: R+=Rg; pen=Rg[-1][0][-1]
    out=[]
    for p,w in R:
        e=[to_d(p),round(plen(p),1)]
        if w is not None: e.append(w)
        out.append(e)
    return out,antes,(len(R),saltos([p for p,_ in R]))
