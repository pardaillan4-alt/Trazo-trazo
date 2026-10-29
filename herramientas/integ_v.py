import json,sys
from PIL import Image
def integ(d,vf,k,did,ch,o,js,zs,vn,CW=600):
    APP='trazo2/'
    v=json.load(open(f'{d}/{vf}')); nl,n=v['nl'],v['n']
    assert 1+len(o['lines'])+sum(t.get('b',3) for t in o['tones'])+len(o['fin'])==n,n
    names=[(f'img/p6_{k}_{i}.webp',f'{d}/out/{i}.png') for i in range(1,nl+1)]+[(f'img/p6g_{k}_{i}.webp',f'{d}/out/{i}g.png') for i in range(1,nl)]+[(f'img/p6h_{k}_{nl}.webp',f'{d}/out/{nl}h.png')]+[(f'img/p6_{k}_{i}.webp',f'{d}/out/{i}.png') for i in range(nl+1,n+1)]
    mp={}; files={}
    for s in range(0,len(names),12):
        sh=Image.new('RGB',(4*CW,ch*3),(250,249,246))
        for j,(nm,src) in enumerate(names[s:s+12]): sh.paste(Image.open(src).convert('RGB'),((j%4)*CW,(j//4)*ch)); mp[nm]=f'img/s_{k}_{s//12}.webp#{j}@{CW}x{ch}x4x3'
        fn=f'img/s_{k}_{s//12}.webp'; sh.save(APP+fn,'WEBP',quality=84); files[fn]=fn
    open(APP+js,'w').write("PD("+json.dumps(o,ensure_ascii=False)+");\n")
    open(APP+zs,'w').write(f"const {vn}="+json.dumps({'v':v['vec'],'s':v['svec'],'nl':nl},separators=(',',':'))+";\nObject.assign(SPRMAP,"+json.dumps(mp)+");\n(()=>{const d=D.find(x=>x.id==='"+did+"');if(!d)return;const v="+vn+",k='"+k+"';d.vec=v.v;d.svec=v.s;d.vbase=i=>`img/p6g_${k}_${i}.webp`;d.sbase={[v.nl]:`img/p6h_${k}_${v.nl}.webp`}})();\n")
    return files
F={}
F.update(integ('guadalupe','gua_v.json','guadalupe','dguadalupe',720,dict(id='dguadalupe',k='guadalupe',h=480,lvl=5,cat='Personas',name='Virgen de Guadalupe',time='2 horas',
 guia='Con el método Loomis: una pelota para la cabeza, arriba y un poco a la izquierda. La Virgen inclina la cabeza hacia un lado, con mucha ternura.',
 lines=[["La línea de los ojos y el lado","Como la cabeza está inclinada, la línea de los ojos baja hacia la izquierda. A la izquierda, un óvalo para el lado de la cabeza."],
  ["El centro, la mandíbula y el manto","Baja la línea del centro, también inclinada. Marca la nariz y la barbilla y une la mandíbula. Alrededor, un arco grande para el manto, y una línea para las manos."],
  ["La nariz","Como en Loomis, empieza por la nariz: delgada y un poco de lado."],
  ["La boca","La boca pequeña y cerrada, con una sonrisa muy suave."],
  ["El contorno de la cara","El borde de la cara, ovalada, dentro del manto."],
  ["Los ojos","Los ojos mirando hacia abajo, casi cerrados, con los párpados grandes, y las cejas finas."],
  ["Las manos","Las manos juntas, rezando, en medio del pecho."],
  ["La túnica","La túnica con su cuello, las flores bordadas y las mangas."],
  ["El manto","El manto que cubre la cabeza y cae a los lados, con sus estrellas."],
  ["Los rayos","Por último, los rayos de sol que salen detrás de ella."]],
 tones=[{'n':'Cara','b':2,'d':'Ahora el sombreado: primero lo oscuro de la cara, los párpados, la nariz y la boca.','l':'Luego las sombras suaves junto al manto.'},
  {'n':'Manos','b':2,'d':'Las manos: las sombras entre los dedos.','l':'Y un tono suave en la piel.'},
  {'n':'Túnica','d':'La túnica: primero los pliegues oscuros.','m':'Luego el tono medio de la tela y las flores.','l':'Y difumina las partes de luz.'},
  {'n':'Manto','d':'El manto es oscuro: primero la orilla y los pliegues.','m':'Luego el tono medio, dejando las estrellas blancas.','l':'Y difumina suave.'},
  {'n':'Rayos','b':2,'d':'Los rayos: un tono entre rayo y rayo.','l':'Y deja los rayos claros, como luz.'}],
 fin=[["Repasa las líneas","Por último, repasa la cara, las manos y la orilla del manto para que se vean firmes.",["#4A4A55","Lápiz 4B"]]]),'g_partes13.js','g_zvec16.js','VEC19'))
F.update(integ('medalla','med_v.json','medalla','dmedalla',800,dict(id='dmedalla',k='medalla',h=533.333,lvl=5,cat='Personas',name='Virgen de la Medalla Milagrosa',time='3 horas',
 guia='Esta vez es una figura de cuerpo entero. Con el método Loomis, empieza por una pelota pequeña arriba para la cabeza. El cuerpo mide como ocho cabezas.',
 lines=[["La línea de los ojos y el lado","Cruza la pelota con la línea de los ojos y un óvalo delgado a la derecha."],
  ["El cuerpo y las medallas","Baja una línea larga por el centro del cuerpo. Marca los hombros, la cintura, los brazos abiertos hacia las manos y la orilla del manto abajo. A los lados, dos óvalos para las medallas."],
  ["La nariz","Empieza la cara por la nariz, pequeña, porque mira hacia arriba."],
  ["La boca","La boca, pequeña y tranquila."],
  ["El contorno de la cara","El borde de la cara, con el velo alrededor."],
  ["Los ojos","Los ojos miran al cielo, y las cejas encima."],
  ["La aureola","Alrededor de la cabeza, el círculo de la aureola."],
  ["El manto","El manto que cae de la cabeza y se abre con los brazos, con sus pliegues grandes."],
  ["La túnica","La túnica larga con el cinturón y los pliegues que bajan hasta los pies."],
  ["Las manos","Las manos abiertas, con las palmas hacia arriba."],
  ["Las medallas","Las dos medallas: de un lado la Virgen, del otro la M con la cruz, los dos corazones y las estrellas."],
  ["Las palomas","Las palomas que vuelan alrededor."],
  ["Las nubes","Por último, las nubes debajo de sus pies."]],
 tones=[{'n':'Cara','b':2,'d':'Ahora el sombreado: primero los ojos, la nariz y la boca.','l':'Luego un tono suave junto al velo.'},
  {'n':'Manto','d':'El manto: primero lo más oscuro dentro de los pliegues.','m':'Luego el tono medio de la tela.','l':'Y difumina las partes de luz.'},
  {'n':'Túnica','b':2,'d':'La túnica es clara: solo las sombras de los pliegues.','l':'Y un tono muy suave.'},
  {'n':'Manos','b':2,'d':'Las manos: las sombras entre los dedos.','l':'Y un tono suave.'},
  {'n':'Medallas','b':2,'d':'Las medallas: repasa la M, la cruz y los corazones.','l':'Y un tono suave en la figura de la Virgen.'},
  {'n':'Palomas','b':2,'d':'Las palomas: las sombras debajo de las alas.','l':'Y deja las plumas blancas.'},
  {'n':'Nubes','b':2,'d':'Las nubes: un tono suave abajo.','l':'Y difumina para que se vean esponjosas.'}],
 fin=[["Repasa las líneas","Por último, repasa la cara, las manos y las orillas del manto.",["#4A4A55","Lápiz 4B"]]]),'g_partes14.js','g_zvec17.js','VEC20'))
print(json.dumps(F))
