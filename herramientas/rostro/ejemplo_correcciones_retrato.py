# Correcciones de la revisión (retrato del árbol). Lo demás sale del método automático.
import numpy as np,sys; sys.path.insert(0,'..')
from facelib import crm
R=np.load('rostro.npy',allow_pickle=True).item(); lm=np.load('lm.npy')
def curl(a,b,outer,k=0.25,n=10):
    a=np.array(a,np.float32); b=np.array(b,np.float32); d=b-a; L=np.linalg.norm(d); nn=np.array([d[1],-d[0]])/L; nn*=np.sign(nn[0]*outer+1e-9)
    ts=np.linspace(0,1,n); return a+np.outer(ts,d)+np.outer(k*L*ts**2,nn)
# ojo izquierdo (de la imagen): párpado de arriba hasta la esquina real (no al mechón de pelo)
upA=crm([(480,386),(481,378),(490,374),(500,373.5),(510,374.5),(520,378),(530,385),(538,393),(542,398)])
loA=[c for c in R['ojo'] if c[:,0].mean()<560 and c[:,1].mean()>395][0]
loA=crm([(480,386),(486,389),(493,393),(500,401),(510,407),(522,409),(533,405),(542,398)])
R['ojo']=[c for c in R['ojo'] if c[:,0].mean()>560]+[upA,loA]
# pestañas: medidas sobre la imagen
R['pestanas']=[curl((482,377),(474,371),-1),curl((480,381),(471,378),-1),curl((480,385),(472,387),-1),curl((501,374),(502,366),-1,0.15),
  curl((631,384),(629,376),1),curl((637,383),(636,376),1),curl((646,383),(646,377),1),curl((656,384),(657,377),1),curl((665,387),(668,380),1),curl((674,390),(679,384),1),
  curl((625,408),(623,413),1,0.1),curl((636,409),(635,414),1,0.1),curl((646,409),(646,414),1,0.1),curl((656,408),(658,413),1,0.1),curl((666,406),(669,411),1,0.1)]
# cejas: fuera los trazos que son mechones del cabello (más allá del final de la ceja)
xmax=680
R['ceja']=[h for h in R['ceja'] if h[:,0].mean()<xmax]
R['parpado']=[c for c in R.get('parpado',[]) if np.ptp(c[:,0])>20 and c[:,1].mean()<385 and c[:,0].mean()>560]
np.save('rostro_final.npy',np.array(R,dtype=object)); print({k:len(v) for k,v in R.items()})
