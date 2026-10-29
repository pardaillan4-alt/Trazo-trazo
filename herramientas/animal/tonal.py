"""Método 'a mano' para dibujos sin cara humana: contornos de las masas de tono, suavizados como trazo de artista."""
import cv2,numpy as np
from scipy.ndimage import gaussian_filter1d as g1
def smooth_closed(c,sig):
    c=c.astype(np.float32); return np.stack([g1(c[:,0],sig,mode='wrap'),g1(c[:,1],sig,mode='wrap')],1)
def contours(mask,min_area,sig):
    cs,_=cv2.findContours(mask.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    return [smooth_closed(c[:,0,:],sig) for c in cs if cv2.contourArea(c)>=min_area]
def masses(L,sig_blur,thr,min_area,sig,within=None,close=7):
    b=cv2.GaussianBlur(L,(0,0),sig_blur); m=(b<thr).astype(np.uint8)
    if within is not None: m&=within
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((close,close),np.uint8)); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    return contours(m,min_area,sig)
def silhouette(L,thr=238,sig=5):
    b=cv2.GaussianBlur(L,(0,0),3); m=(b<thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); m=(lab==k).astype(np.uint8)
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)[:,0,:]
    return smooth_closed(c,sig),m
def open_part(c,keep):
    """Corta una curva cerrada: deja solo los tramos donde keep es verdadero (p.ej. quita el borde de la hoja)."""
    out=[]; n=len(c); k=np.argmin(keep) if not keep.all() else 0; c=np.roll(c,-k,0); keep=np.roll(keep,-k); i=0
    while i<n:
        if keep[i]:
            j=i
            while j<n and keep[j]: j+=1
            if j-i>8: out.append(c[i:j])
            i=j
        else: i+=1
    return out
