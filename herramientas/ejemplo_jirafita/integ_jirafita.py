"""La jirafita (a color y a lápiz) y el perezoso en la selva (a lápiz): líneas de la imagen de líneas
(la gris de la jirafa y la de líneas del perezoso); sombreado de la imagen a color y de la gris."""
import json,os
src=open('integ_v.py').read().split('\nF={}')[0]; exec(src)          # solo la función integ()
H=502; h=round(400*H/900,1)
def prep(base,tag):
    os.makedirs(tag,exist_ok=True)
    if not os.path.islink(f'{tag}/out'): os.symlink(f'../{base}/out_{tag}',f'{tag}/out')
    os.system(f'cp {base}/{tag}_v.json {tag}/')

G_JIR=("Muy suave: un círculo para la cabeza, con una línea para los ojos. Una curva para el cuello largo, "
       "un óvalo para el cuerpo y cuatro líneas para las patas. Luego una línea larga para el horizonte.")
L_JIR=[["Los ojos","Empieza por la cara: los dos ojos grandes sobre su línea, con la pupila negra y su brillo blanco, y las pestañas rizadas."],
 ["La nariz y la sonrisa","Abajo, las dos fosas de la nariz y la sonrisa que sube hacia un lado."],
 ["La cabeza, las orejas y los cuernos","El contorno de la cabeza, las dos orejas grandes, los cuernitos con su punta peludita y el mechón de pelo de en medio."],
 ["El cuello y la crin","Baja con las dos líneas del cuello largo y, por atrás, la crin con rayitas que siguen el pelo."],
 ["El cuerpo, las patas y la cola","El cuerpo sobre el óvalo, las cuatro patas sobre sus líneas con las pezuñas, y la cola con su pompón."],
 ["Las manchas","Ahora las manchas: formas redondas y chuecas por toda la jirafa, más chiquitas en la cara y en las patas."],
 ["Las mariposas","Las mariposas que vuelan alrededor, con sus alas y sus antenitas."],
 ["Los árboles grandes","A los lados, los dos árboles grandes: primero el tronco y las ramas, y arriba las hojas con su orilla en curvitas."],
 ["Las acacias","Atrás, las acacias: árboles de copa plana, con su tronco delgado y sus ramitas."],
 ["Las nubes y las colinas","Las nubes en el cielo y las colinas suaves en el horizonte."],
 ["Los arbustos y la cerca","A la izquierda los arbustos redondos, y a la derecha la cerca de madera con sus postes."],
 ["Las flores, las piedras y el pasto","Por último, las flores, las piedras y las hojitas de pasto del suelo."]]
def T_JIR(lapiz):
    if lapiz:
        return [{'n':'La jirafa','d':'Ahora el sombreado a lápiz: empieza por lo más oscuro de la jirafa: los cuernos, la crin y las pezuñas.','m':'Luego el gris de las manchas y las sombras del cuello y de las patas.','l':'Y lo más clarito en toda la piel. Deja blancos los brillos.'},
                {'n':'Los árboles','d':'Los árboles: primero lo más oscuro, entre las ramas y debajo de las hojas.','m':'Luego el tono medio de los troncos y de las hojas.','l':'Y lo más claro: la luz sobre las hojas.'},
                {'n':'El suelo','d':'El suelo: primero lo más oscuro, las sombras de los arbustos y de la cerca.','m':'Luego el tono medio del pasto, las flores y las piedras.','l':'Y lo más clarito: el camino de tierra.'},
                {'n':'El fondo','d':'El fondo: primero las colinas.','m':'Luego un gris muy suave en el campo.','l':'Y deja casi blanco el cielo, con sus nubes.'}]
    return [{'n':'La jirafa','d':'Ahora el color: empieza por lo más oscuro de la jirafa: los cuernos, la crin y las pezuñas.','m':'Luego el café de las manchas y el amarillo de la piel.','l':'Y lo más clarito: la panza, el hocico y los brillos.'},
            {'n':'Los árboles','d':'Los árboles: primero lo más oscuro, entre las ramas y debajo de las hojas.','m':'Luego el café de los troncos y el verde de las hojas.','l':'Y lo más claro: la luz sobre las hojas.'},
            {'n':'El suelo','d':'El suelo: primero lo más oscuro, las sombras de los arbustos y de la cerca.','m':'Luego el verde del pasto y los colores de las flores y de las mariposas.','l':'Y lo más clarito: el camino de tierra.'},
            {'n':'El fondo','d':'El fondo: primero las colinas.','m':'Luego el amarillo del campo y el azul del cielo.','l':'Y al final la luz del sol y las nubes blancas.'}]
F_JIR={True:[["Los últimos detalles","Repasa lo más oscuro: los ojos, la sonrisa y la orilla de la jirafa. Con la goma saca el brillo de los ojos."]],
       False:[["Los últimos detalles","Repasa lo más oscuro: los ojos, la sonrisa y la orilla de la jirafa. Deja muy blanco el brillo de los ojos."]]}

G_PER=("Muy suave: un círculo para la cabeza, con una línea para los ojos. Un óvalo grande para el cuerpo y otro abajo para la pata. "
       "Dos curvas para los brazos y dos líneas inclinadas para el tronco.")
L_PER=[["Los ojos","Empieza por la cara: los dos ojitos redondos sobre su línea, con la pupila negra, su brillo y el párpado alrededor."],
 ["La nariz y la sonrisa","En medio, la nariz redonda con sus dos fosas, y abajo la sonrisa larga."],
 ["La cabeza","El contorno de la cabeza y la máscara que sale de los ojos. Luego el pelo de la cara, rayita por rayita."],
 ["Los brazos y las garras","Los brazos que abrazan el tronco, el de arriba y el de en medio, con sus garras largas y curvas. Primero la orilla y después el pelo."],
 ["El cuerpo","El cuerpo peludo sobre el óvalo grande, con rayitas largas que siguen el pelo hacia abajo."],
 ["La pata y las garras de abajo","Abajo, la pata doblada con sus garras sobre el tronco, y el otro pie que se asoma detrás."],
 ["El tronco","El tronco inclinado: sus dos orillas sobre las líneas, y luego el musgo y las rayitas de la corteza."],
 ["Las hojas grandes de la izquierda","A la izquierda, las hojas grandes de la selva: la orilla de cada hoja y luego sus nervaduras."],
 ["Las plantas de la derecha","A la derecha, los helechos, las plantas y las lianas que cuelgan."],
 ["El fondo de la selva","Por último el fondo: las lianas, los árboles de atrás y las hojitas pequeñas."]]
T_PER=[{'n':'El perezoso','d':'Ahora el sombreado a lápiz: primero lo más oscuro del perezoso: la máscara de los ojos, la nariz y entre el pelo.','m':'Luego el tono medio de todo el pelo, siguiendo las rayitas.','l':'Y lo más clarito: la cara y los brillos del pelo.'},
       {'n':'El tronco','d':'El tronco: primero las sombras más oscuras, debajo del perezoso.','m':'Luego el tono medio de la corteza y del musgo.','l':'Y lo claro, donde le pega la luz.'},
       {'n':'Las plantas','d':'Las plantas: primero lo más oscuro, entre las hojas.','m':'Luego el tono medio de las hojas y de los helechos.','l':'Y lo más clarito: las orillas con luz.'},
       {'n':'El fondo','d':'El fondo de la selva: primero lo más oscuro de los árboles de atrás.','m':'Luego un tono medio en las lianas y las hojitas.','l':'Y al final la luz que entra por arriba, muy suave.'}]
F_PER=[["Los últimos detalles","Repasa lo más oscuro: los ojos, la nariz, la sonrisa y la máscara. Con la goma saca el brillo de los ojos y de las garras."]]

F={}
for base,tag,did,nm,lvl,tm,G,Ls,T,Fi,js,zs,vn in [
  ('jirafita','jirafita_c','djirafita','La jirafita',3,'60 min',G_JIR,L_JIR,T_JIR(False),F_JIR[False],'g_partes999.js','g_zvec999.js','VEC999'),
  ('jirafita','jirafita_g','djirafita_lapiz','La jirafita a lápiz',3,'60 min',G_JIR,L_JIR,T_JIR(True),F_JIR[True],'g_partes9991.js','g_zvec9991.js','VEC9991'),
  ('perezoso3','perezoso3g','dperezoso3_lapiz','El perezoso en la selva',5,'2 horas',G_PER,L_PER,T_PER,F_PER,'g_partes9992.js','g_zvec9992.js','VEC9992')]:
    prep(base,tag)
    o=dict(id=did,k=tag,lvl=lvl,cat='Animales',name=nm,time=tm,exact=True,h=h,guia=G,lines=Ls,tones=T,fin=Fi)
    F.update(integ(tag,f'{tag}_v.json',tag,did,H,o,js,zs,vn,CW=900)); print(tag,'ok')
json.dump(F,open('files_jirafita.json','w')); print(F)
