import cv2,numpy as np,sys; sys.path.insert(0,'..')
from facelib import crm,resamp
from scipy.ndimage import map_coordinates,gaussian_filter1d as g1
im=cv2.imread('sq.png'); H,W=im.shape[:2]
sm=cv2.bilateralFilter(im,15,60,15); sm=cv2.GaussianBlur(sm,(0,0),2.5)
lab=cv2.cvtColor(sm,cv2.COLOR_BGR2LAB).astype(np.float32)
GM=sum(np.hypot(cv2.Sobel(lab[:,:,c],cv2.CV_32F,1,0,3),cv2.Sobel(lab[:,:,c],cv2.CV_32F,0,1,3))*w for c,w in ((0,1.0),(1,1.6),(2,1.6)))
GM=GM/np.percentile(GM,99)
def snap(pts,R=8,lam=0.6,step=0.5):
    c=resamp(crm(pts,8),1.0); t=np.gradient(c,axis=0); t/=np.linalg.norm(t,axis=1,keepdims=True)+1e-6; n=np.stack([-t[:,1],t[:,0]],1)
    offs=np.arange(-R,R+1e-6,step)
    E=np.stack([map_coordinates(GM,[c[:,1]+n[:,1]*o,c[:,0]+n[:,0]*o],order=1,mode='nearest') for o in offs],1)
    E=np.clip(E,0,1.5)-0.01*np.abs(offs)[None,:]; N,K=E.shape
    pen=lam*((offs[:,None]-offs[None,:])/step)**2; cost=-E[0].copy(); bk=np.zeros((N,K),int)
    for i in range(1,N):
        tot=cost[:,None]+pen; bk[i]=np.argmin(tot,0); cost=tot[bk[i],np.arange(K)]-E[i]
    k=int(np.argmin(cost)); path=[k]
    for i in range(N-1,0,-1): k=bk[i][k]; path.append(k)
    o=g1(offs[np.array(path[::-1])],2,mode='nearest'); return (c+n*o[:,None]).astype(np.float32)
def show(D,name,box=None,f=1.0,raw=None):
    x0,y0,x1,y1=box or (0,0,W,H)
    z=cv2.resize(im[y0:y1,x0:x1],None,fx=f,fy=f,interpolation=cv2.INTER_CUBIC); o=z.copy()
    for k,ps in D.items():
        for p in ps: cv2.polylines(o,[np.round((np.asarray(p)-[x0,y0])*f*4).astype(np.int32)],False,(255,255,255),2,cv2.LINE_AA,shift=2)
    if raw:
        for k,ps in raw.items():
            for p in ps: cv2.polylines(o,[np.round((np.asarray(p,np.float32)-[x0,y0])*f*4).astype(np.int32)],False,(0,0,255),1,cv2.LINE_AA,shift=2)
    cv2.imwrite(name,np.hstack([z,o]))
