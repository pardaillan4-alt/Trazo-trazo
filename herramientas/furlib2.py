"""Motor de trazos de lápiz (pelo / plumas) que siguen la dirección de la textura."""
import cv2,numpy as np
SS=2
class Fur:
    def __init__(s,L,fg,prior=None,coh_s=9,seed=3):
        H,W=L.shape; s.H,s.W=H,W
        s.rng=np.random.default_rng(seed); s.fg=fg.astype(np.float32)
        g=cv2.GaussianBlur(L,(0,0),1.5)
        gx=cv2.Sobel(g,cv2.CV_32F,1,0,3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,3)
        Jxx=cv2.GaussianBlur(gx*gx,(0,0),coh_s);Jyy=cv2.GaussianBlur(gy*gy,(0,0),coh_s);Jxy=cv2.GaussianBlur(gx*gy,(0,0),coh_s)
        th=0.5*np.arctan2(2*Jxy,Jxx-Jyy)+np.pi/2
        coh=np.sqrt((Jxx-Jyy)**2+4*Jxy**2)/(Jxx+Jyy+1e-3)
        ux,uy=np.cos(th),np.sin(th)
        if prior is None: pdx,pdy=np.full((H,W),0.25,np.float32),np.ones((H,W),np.float32)
        else: pdx,pdy=prior
        pn=np.hypot(pdx,pdy)+1e-6; pdx=pdx/pn; pdy=pdy/pn
        w=np.clip((coh-0.12)*3,0,1)
        sg=np.sign(ux*pdx+uy*pdy+1e-6); ux*=sg; uy*=sg
        fx=w*ux+(1-w)*pdx; fy=w*uy+(1-w)*pdy; fn=np.hypot(fx,fy)+1e-6
        s.fx=cv2.GaussianBlur(fx/fn,(0,0),2); s.fy=cv2.GaussianBlur(fy/fn,(0,0),2)
        s.C=np.zeros((H,W),np.float32)
    def trace(s,x,y,Lmax,stopT,T):
        fx,fy,fg=s.fx,s.fy,s.fg
        pts=[(x,y)];dx0,dy0=fx[int(y),int(x)],fy[int(y),int(x)]
        for _ in range(int(Lmax/1.5)):
            ix,iy=int(x),int(y); dx,dy=fx[iy,ix],fy[iy,ix]
            if dx*dx0+dy*dy0<0: dx,dy=-dx,-dy
            dx,dy=0.72*dx0+0.28*dx,0.72*dy0+0.28*dy; nn=np.hypot(dx,dy)+1e-6; dx/=nn; dy/=nn
            x+=dx*1.5;y+=dy*1.5;dx0,dy0=dx,dy
            if not(1<x<s.W-2 and 1<y<s.H-2) or fg[int(y),int(x)]<0.5 or T[int(y),int(x)]<stopT: break
            pts.append((x,y))
        return np.array(pts)
    def layer(s,strokes,alpha):
        lay=np.zeros((s.H*SS,s.W*SS),np.float32)
        for p,a in zip(strokes,alpha):
            q=(p*SS*8).astype(np.int32); n=len(q); h=max(2,n*2//3); a=float(a)
            cv2.polylines(lay,[q[:h]],False,a,2,cv2.LINE_AA,shift=3)
            cv2.polylines(lay,[q[h-1:]],False,a*0.7,1,cv2.LINE_AA,shift=3)
        return cv2.resize(lay,(s.W,s.H),interpolation=cv2.INTER_AREA)
    def run(s,region,target,nmax,Lr=(8,18),batch=300,alpha=0.34,stopf=0.7):
        E0=None
        for it in range(0,nmax,batch):
            E=np.clip(target-s.C,0,None)*region
            if E0 is None: E0=E.sum()+1e-6
            p=E.ravel()**2; ps=p.sum()
            if ps<1e-4 or E.sum()<0.12*E0: break
            idx=s.rng.choice(s.H*s.W,batch,p=p/ps)
            ys,xs=np.divmod(idx,s.W); xs=xs+s.rng.random(batch); ys=ys+s.rng.random(batch)
            S=[];A=[]
            for x,y in zip(xs,ys):
                tv=target[int(y),int(x)]; ev=E[int(y),int(x)]
                pt=s.trace(x,y,s.rng.uniform(*Lr),tv*stopf,target)
                if len(pt)<3: continue
                S.append(pt);A.append(min(alpha,ev*0.8+0.02))
            s.C=1-(1-s.C)*(1-np.clip(s.layer(S,A),0,1))
    def streams(s,diff,spacing=9,Lmax=70,sc=0.5):
        FX,FY=s.fx,s.fy
        m=cv2.dilate((diff>0.02).astype(np.uint8),np.ones((5,5),np.uint8))
        cov=np.zeros((s.H,s.W),np.uint8); paths=[]
        ys,xs=np.nonzero(m[::spacing,::spacing]); ys=ys*spacing+spacing//2; xs=xs*spacing+spacing//2
        for y,x in zip(ys,xs):
            if y>=s.H or x>=s.W or not m[y,x] or cov[y,x]: continue
            pts=[(x,y)]; cx,cy=float(x),float(y); d0=(FX[y,x],FY[y,x])
            for _ in range(int(Lmax/2)):
                dx,dy=FX[int(cy),int(cx)],FY[int(cy),int(cx)]
                if dx*d0[0]+dy*d0[1]<0: dx,dy=-dx,-dy
                cx+=dx*2;cy+=dy*2;d0=(dx,dy)
                if not(0<cx<s.W-1 and 0<cy<s.H-1) or not m[int(cy),int(cx)]: break
                pts.append((cx,cy))
            pts=np.array(pts)
            cv2.polylines(cov,[pts.astype(np.int32)],False,1,int(spacing*1.1))
            paths.append(pts if len(pts)>=2 else np.array([[x-2,y-2],[x+2,y+2]],np.float32))
        paths.sort(key=lambda p:(int(p[0,1]//60),p[0,0] if int(p[0,1]//60)%2==0 else -p[0,0]))
        out=[]
        for p in paths:
            q=np.round(cv2.approxPolyDP(p.reshape(-1,1,2).astype(np.float32),1.2,False).reshape(-1,2)*sc)
            if len(q)<2: q=p[[0,-1]]*sc
            d='M'+f'{q[0,0]:.0f} {q[0,1]:.0f}'+'L'+' '.join(f'{x:.0f} {y:.0f}' for x,y in q[1:])
            out.append([d,round(float(np.sum(np.hypot(*np.diff(q,axis=0).T)))+0.6,1)])
        return out
