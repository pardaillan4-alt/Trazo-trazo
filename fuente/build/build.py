"""Arma la app.
- vec/<id>.json: los trazos animados de cada dibujo (se cargan al abrirlo, así la app abre rápido)
- img/t_<id>.webp: miniaturas ligeras para la galería
- app.html: para el artifact (sin <!doctype>/<head>, el artifact los pone)
- index.html: documento completo para GitHub / Cloudflare (con viewport para celular)
Uso: python3 build/build.py   (desde la carpeta trazo2)"""
import os,re,json,glob,subprocess,sys
from PIL import Image
import numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__))+'/..')
# 1) trazos de cada dibujo y datos de miniaturas
r=subprocess.run(['node','build/export_vec.js','.','vec'],capture_output=True,text=True)
if r.returncode: print(r.stderr); sys.exit(1)
info=json.loads(r.stdout.strip().split('\n')[-1]); print('dibujos',info['n'],'con trazos',info['conDatos'],'MB',round(info['bytes']/1e6,2))
VECF=sorted(f[:-5] for f in os.listdir('vec') if f.endswith('.json'))
# 2) miniaturas (solo las que faltan o son más viejas que su hoja)
META={}
for t in json.load(open('build/miniaturas.json')):
    sp=t['sp']; src=sp['f'] if sp else t['src']
    name=f"img/t_{t['id']}{'' if t['tk']=='lapiz' else '_'+t['tk']}.webp"
    if (not os.path.exists(name)) or os.path.getmtime(name)<os.path.getmtime(src):
        im=Image.open(src).convert('RGB')
        if sp: im=im.crop((sp['x'],sp['y'],sp['x']+sp['w'],sp['y']+sp['h']))
        w,h=im.size; s=520/max(w,h)
        if s<1: im=im.resize((round(w*s),round(h*s)),Image.LANCZOS)
        im.save(name,'WEBP',quality=80,method=6)
    im=Image.open(name).convert('RGB'); a=np.asarray(im).astype(np.float32)/255
    mx,mn=a.max(2),a.min(2); sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0); tinta=mx<0.97
    col=float(sat[tinta].mean()) if tinta.any() else 0.0
    m=META.setdefault(t['id'],{}); m.setdefault('t',{})[t['tk']]=name
    if t['tk']=='lapiz': m['w'],m['h'],m['col']=im.size[0],im.size[1],round(col,3)
json.dump(META,open('build/meta.json','w'),ensure_ascii=False,indent=0)
# 3) archivos de datos sin los trazos (quedan las llaves; los trazos llegan de vec/)
def vacio(o):
    if isinstance(o,dict):
        if o and all(re.fullmatch(r'\d+',k) for k in o): return {}
        return {k:vacio(v) for k,v in o.items()}
    return o
parts=[]
for f in ['helpers.js','render.js','parts.js','audio.js']+sorted(glob.glob('g_*.js'))+['ui.js']:
    s=open(f).read()
    if f.startswith('g_zvec'):
        L=s.split('\n')
        for i,l in enumerate(L):
            m=re.match(r'^const (\w+)=(\{.*\});\s*$',l)
            if m: L[i]=f'const {m.group(1)}='+json.dumps(vacio(json.loads(m.group(2))),separators=(',',':'))+';'
        s='\n'.join(L)
    if f=='ui.js':
        parts.append('const VECF=new Set('+json.dumps(VECF)+');\nconst META='+json.dumps(META,separators=(',',':'))+';')
    parts.append(s)
js='\n'.join(parts)
open('all.js','w').write(js)
r=subprocess.run(['node','--check','all.js'],capture_output=True,text=True)
if r.returncode: print(r.stderr); sys.exit(1)
head=open('head2.html').read().replace('/*FUENTES*/',open('build/fuentes.css').read()); defs=open('defs.html').read(); body=open('body2.html').read()
app=head+defs+body+'<script>\n'+js+'\n</script>\n'
open('app.html','w').write(app)
# index.html: documento completo (GitHub / Cloudflare)
doc=('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
     '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
     '<meta name="theme-color" content="#EEF1F6" media="(prefers-color-scheme: light)">\n'
     '<meta name="theme-color" content="#11141B" media="(prefers-color-scheme: dark)">\n'
     '<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="mobile-web-app-capable" content="yes">\n'
     '<meta name="apple-mobile-web-app-title" content="Trazo a Trazo">\n'
     '<meta name="description" content="Aprende a dibujar paso a paso: guías, líneas y sombreado, con una voz que te explica.">\n'
     '<link rel="icon" href="img/icono.svg" type="image/svg+xml">\n<link rel="apple-touch-icon" href="img/icono-180.png">\n'
     '<link rel="manifest" href="manifest.webmanifest" crossorigin="use-credentials">\n'
     '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
     '</head>\n<body>\n'+app+'</body>\n</html>\n')
open('index.html','w').write(doc)
print('app.html',len(app.encode())//1024,'KB · index.html listo · vec',len(VECF),'· miniaturas',sum(len(m['t']) for m in META.values()))
