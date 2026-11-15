"""Hojas repetidas: la versión a color y la de lápiz de un dibujo comparten las hojas de las líneas, que salen idénticas.
Cada hoja repetida se cambia por la primera igual (por nombre), así la app y el artifact guardan una sola copia.
Escribe build/hojas_sin_uso.json con las hojas que ya nadie usa.  Uso: python3 build/dedup_hojas.py (desde trazo2)"""
import os,re,glob,hashlib,json
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/..')
F=sorted(glob.glob('g_zvec*.js')); refs=set()
for f in F: refs|=set(re.findall(r'img/s_[A-Za-z0-9_]+\.webp',open(f).read()))
h={}
for r in sorted(refs):
    if os.path.exists(r): h.setdefault(hashlib.md5(open(r,'rb').read()).hexdigest(),[]).append(r)
canon={r:v[0] for v in h.values() for r in v[1:]}
for f in F:
    s=open(f).read(); s2=s
    for r,c in canon.items(): s2=s2.replace('"'+r+'#','"'+c+'#')
    if s2!=s: open(f,'w').write(s2)
usadas=set()
for f in F: usadas|=set(re.findall(r'img/s_[A-Za-z0-9_]+\.webp',open(f).read()))
sin=sorted(refs-usadas); json.dump(sin,open('build/hojas_sin_uso.json','w'),indent=0)
print('hojas repetidas',len(canon),'· ya sin uso',len(sin))
