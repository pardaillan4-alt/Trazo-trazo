import cv2,numpy as np,sys,json; sys.path.insert(0,'..')
from facelib import crm
exec(open('mano.py').read().split("# 2) masas oscuras")[0].split("OUT={}")[0])   # im, L, pm, dk
R=np.load('perro_mano.npy',allow_pickle=True).item()
b=cv2.GaussianBlur(L,(0,0),3); m=(b<240).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((31,31),np.uint8))
n_,lab_,st_,_=cv2.connectedComponentsWithStats(m); m=(lab_==1+np.argmax(st_[1:,4])).astype(np.uint8)
t=np.linspace(0,2*np.pi,90)
# ojo medido sobre la imagen
up=crm([(512,168),(518,159),(526,152.5),(536,150),(546,150.5),(554,154),(559,162),(560,170)]); lo=crm([(512,168),(518,179),(527,187),(538,191),(549,189),(556,182),(560,170)])
R['ojo']=[up,lo]
poly=np.vstack([up,lo[::-1]]).astype(np.float32); ic=np.array([539,170.0]); ir=14.5
circ=ic+ir*np.stack([np.cos(t),np.sin(t)],1); ins=np.array([cv2.pointPolygonTest(poly,tuple(map(float,p)),True)>-0.3 for p in circ])
k=np.argmin(ins); ins=np.roll(ins,-k); circ=np.roll(circ,-k,0); seg=[]; i=0
while i<len(circ):
    if ins[i]:
        j=i
        while j<len(circ) and ins[j]: j+=1
        if j-i>4: seg.append(circ[i:j])
        i=j
    else: i+=1
R['iris']=seg if not ins.all() else [circ]
R['pupila']=[np.array([536,161.5])+2.8*np.stack([np.cos(t),np.sin(t)],1)]    # el brillito
# nariz medida
R['nariz']=[crm([(722,262),(733,249),(750,245.5),(767,248),(781,255),(790,268),(790,282),(785,297),(777,309),(764,316),(750,314),(738,305),(728,292),(722,278),(722,262)])]
R['orificio']=[crm([(726,268),(733,282),(743,292),(755,297),(767,296),(773,290)])]
# línea de la boca (orilla del labio de arriba)
R['boca']=[crm([(757,363),(747,377),(730,387),(707,394),(680,399),(653,403)])]
# puntitos de los bigotes: manchitas oscuras y redondas en el hocico claro
hoc=pm('hocico')*(1-pm('nariz',12)); Lb=cv2.GaussianBlur(L,(0,0),1.2); bgb=cv2.GaussianBlur(L,(0,0),5)
spot=((bgb-Lb)>40)&(hoc>0)&(bgb>165)
n,lab,st,cen=cv2.connectedComponentsWithStats(spot.astype(np.uint8))
dots=[]
for j in range(1,n):
    a=st[j,4]; w_,h_=st[j,2],st[j,3]
    if 5<=a<=60 and max(w_,h_)<=12 and cen[j][1]>300: dots.append((cen[j],max(1.6,np.sqrt(a/np.pi))))
R['bigotes']=[c+r*np.stack([np.cos(t),np.sin(t)],1)[::6] for c,r in dots]
print('puntitos',len(dots))
# pelo de la cabeza y la frente: pocos trazos que siguen el pelo
exec(open("mano.py").read().split("pocos y limpios")[1].split("# oreja medida")[0].replace("sys.path.insert(0,'..'); from facelib import crm",""))
ear=np.zeros(L.shape,np.uint8); cv2.fillPoly(ear,[np.round(R['oreja'][0]).astype(np.int32)],1)
cab=pm('cabeza')*(1-cv2.dilate(ear,np.ones((15,15),np.uint8)))*(1-pm('ojo',16))*cv2.erode(m,np.ones((21,21),np.uint8))
R['pelo_cabeza']=fur(cab,12,40,92,30)
R['pelo_hocico']=fur(hoc*(1-pm('nariz',20))*cv2.erode(m,np.ones((21,21),np.uint8)),8,34,90,26)
np.save('perro_final.npy',np.array(R,dtype=object)); print({k:len(v) for k,v in R.items()})
o=im.copy(); w=np.full_like(im,250)
for t_ in (o,w):
    for k,ps in R.items():
        for p in ps: cv2.polylines(t_,[np.round(p*4).astype(np.int32)],k not in('pelo_oreja',),(150,150,150) if 'pelo' in k else (40,80,240),2 if 'bigotes' not in k else 1,cv2.LINE_AA,shift=2) if k in('bigotes',) else cv2.polylines(t_,[np.round(p*4).astype(np.int32)],False,(150,150,150) if 'pelo' in k else (40,80,240),2,cv2.LINE_AA,shift=2)
cv2.imwrite('final_cmp.jpg',np.hstack([im,o,w]))
a=im[120:440,480:820]; f=3
za=cv2.resize(a,None,fx=f,fy=f); zo=cv2.resize(o[120:440,480:820],None,fx=f,fy=f); cv2.imwrite('final_cara.jpg',np.hstack([za,zo]))
# --- la oreja del fondo y la quijada, medidas: la quijada pasa por encima de la oreja y no se juntan ---
R['oreja_fondo']=[crm([(548,450),(556,443),(566,439),(577,438),(589,440),(602,445),(615,451),(627,460),(634,474),(636,490),(632,502),(620,503),(605,499),(590,493),(576,485),(564,474),(554,462),(548,450)],12)]
R['sil_barbilla']=[crm([(646,446),(632,439),(615,437),(600,434),(580,428),(560,424),(540,422),(520,426)])]
cu=[c for c in R['sil_cuello'] if abs(c[-1][0]-525)<4 and abs(c[-1][1]-473)<4]
if cu:
    c=cu[0]; low=c[c[:,1]>515]
    R['sil_cuello']=[x for x in R['sil_cuello'] if x is not c]+[np.vstack([low,crm([tuple(low[-1]),(505,505),(508,492),(514,479),(524,467),(536,457),(548,451)])])]
np.save('perro_final.npy',np.array(R,dtype=object))
