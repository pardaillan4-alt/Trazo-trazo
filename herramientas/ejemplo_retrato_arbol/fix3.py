import cv2,numpy as np,sys; sys.path.insert(0,'..')
from facelib import crm
im=cv2.imread('sq.png'); R=np.load('rostro_final.npy',allow_pickle=True).item()
inbox=lambda c,x0,y0,x1,y1:(np.asarray(c)[:,0].mean()>x0)&(np.asarray(c)[:,0].mean()<x1)&(np.asarray(c)[:,1].mean()>y0)&(np.asarray(c)[:,1].mean()<y1)
# ---- boca medida columna por columna ----
R['boca']=[crm([(529,546),(536,549),(545,551),(555,551),(565,552),(575,552),(585,552),(595,553),(605,554),(615,554),(622,553),(627,552)]),
 crm([(529,546),(535,541),(542,537),(549,533),(555,531),(561,532),(566,536),(569,537),(572,535),(576,533),(582,534),(590,538),(602,543),(612,546),(620,549),(627,552)]),
 crm([(529,546),(535,553),(540,559),(547,569),(556,577),(567,581),(577,582),(590,579),(602,572),(614,565),(622,558),(627,552)])]
# ---- ojo izquierdo medido columna por columna ----
for k in ['ojo','iris','pupila']: R[k]=[c for c in R[k] if not inbox(c,455,335,560,420)]
up=crm([(475,388),(483,380),(492,377),(505,377),(518,379),(528,384),(535,391),(541,399)])
lo=crm([(475,388),(485,389),(493,391),(498,398),(504,404),(512,408),(524,407),(533,404),(541,399)])
R['ojo']+=[up,lo]
t=np.linspace(0,2*np.pi,120); polyE=np.vstack([up,lo[::-1]]).astype(np.float32)
def clip(c):
    ins=np.array([cv2.pointPolygonTest(polyE,tuple(map(float,p)),True)>-0.3 for p in c]); out=[]
    if ins.all(): return [c]
    k=np.argmin(ins); ins=np.roll(ins,-k); c=np.roll(c,-k,0); i=0
    while i<len(c):
        if ins[i]:
            j=i
            while j<len(c) and ins[j]: j+=1
            if j-i>4: out.append(c[i:j])
            i=j
        else: i+=1
    return out
R['iris']+=clip(np.array([520,392])+12*np.stack([np.cos(t),np.sin(t)],1))
R['pupila']+=clip(np.array([521,393])+5*np.stack([np.cos(t),np.sin(t)],1))
np.save('rostro_final.npy',np.array(R,dtype=object))
for nm,(x0,y0,x1,y1,f) in {'z_ojoA2.jpg':(465,355,555,420,9),'z_boca2.jpg':(515,520,640,600,8)}.items():
    z=cv2.resize(im[y0:y1,x0:x1],None,fx=f,fy=f,interpolation=cv2.INTER_CUBIC); o=z.copy()
    for k,ps in R.items():
        for p in ps: cv2.polylines(o,[np.round((np.asarray(p)-[x0,y0])*f*4).astype(np.int32)],False,(40,40,230),2,cv2.LINE_AA,shift=2)
    cv2.imwrite(nm,np.vstack([z,o]))
