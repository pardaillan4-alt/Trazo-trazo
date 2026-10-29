"""Uso: python3 correr.py carpeta_del_dibujo   (la carpeta debe tener sq.png)
Saca: lm.npy (puntos de la cara), rostro.npy (líneas), rostro_cmp.jpg (comparación) y z_*.jpg (acercamientos para revisar)."""
import cv2,numpy as np,sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from facelm import landmarks; from rostro import build3,compare
d=sys.argv[1]; im=cv2.imread(f'{d}/sq.png'); F=landmarks(f'{d}/sq.png')
if not F: sys.exit('No se encontró cara')
lm=max(F,key=lambda f:np.ptp(f[:,0])); np.save(f'{d}/lm.npy',lm)
R,rep,_=build3(im,lm); print('revisión (fracción sobre trazo real):',rep); print({k:len(v) for k,v in R.items()})
np.save(f'{d}/rostro.npy',np.array(R,dtype=object))
x0,y0=np.maximum(lm.min(0).astype(int)-12,0); x1,y1=lm.max(0).astype(int)+12; h=y1-y0
compare(im,R,(x0,y0+int(h*0.12),x1,y1-int(h*0.1)),max(2,int(700/(x1-x0))),f'{d}/rostro_cmp.jpg')
os.system(f'cd "{os.path.dirname(os.path.abspath(__file__))}" && python3 zoomr.py "{os.path.abspath(d)}"')
