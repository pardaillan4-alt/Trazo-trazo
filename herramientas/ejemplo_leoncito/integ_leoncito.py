"""El leoncito en la sabana, a color y a lápiz: líneas del dibujo de líneas del usuario; sombreado de su imagen a color y de la de lápiz."""
import json,os
src=open('integ_v.py').read().split('\nF={}')[0]; exec(src)          # solo la función integ()
H=502; h=round(400*H/900,1)
def prep(base,tag):
    os.makedirs(tag,exist_ok=True)
    if not os.path.islink(f'{tag}/out'): os.symlink(f'../{base}/out_{tag}',f'{tag}/out')
    os.system(f'cp {base}/{tag}_v.json {tag}/')
G=("Muy suave: un círculo grande para la melena y, adentro, otro más chico para la cara, con una línea por el centro y otra para los ojos. "
   "Abajo, un óvalo para el cuerpo y una curva para la cola. Luego una línea ondulada para las colinas.")
L=[["Los ojos","Empieza por la cara: los dos ojos grandes y redondos sobre su línea, con el iris negro y sus brillos blancos, las pestañitas y las cejas."],
 ["La nariz y la sonrisa","En medio, la nariz con sus dos fosas y, abajo, la boca que sonríe."],
 ["La cara y las orejas","El contorno de la cara, con los cachetes peluditos, y las dos orejas redondas a los lados."],
 ["La melena","Alrededor, la melena grande con sus picos de pelo. Primero la orilla de afuera y luego los mechones de adentro y del pecho."],
 ["El cuerpo, las patas y la cola","El cuerpo sentado sobre el óvalo, las patas de adelante con sus deditos y la cola con su pompón de pelo."],
 ["Las mariposas","Las mariposas que vuelan alrededor, con sus alas y sus antenitas."],
 ["Los árboles","Los árboles de la sabana: primero los troncos y las ramas, y arriba las copas planas con su orilla en curvitas."],
 ["Las colinas, el pasto y las piedras","Atrás, las colinas y el pasto alto. Luego las piedras grandes de los lados, las piedritas y la orilla del camino."],
 ["El camino, los arbustos y las flores","Por último, abajo: los arbustos redondos, las flores, las matitas de pasto y el resto del camino."]]
def T(lapiz):
    if lapiz:
        return [{'n':'El león','d':'Ahora el sombreado a lápiz: empieza por lo más oscuro del león: los ojos, la nariz y entre los mechones de la melena.','m':'Luego el tono medio de la melena, de la cola y de las sombras del cuerpo.','l':'Y lo más clarito en la cara y el pecho. Deja blancos los brillos de los ojos.'},
                {'n':'Los árboles','d':'Los árboles: primero lo más oscuro, debajo de las copas y en los troncos.','m':'Luego el tono medio de las hojas y de las ramas.','l':'Y lo más claro: la luz sobre las copas.'},
                {'n':'El suelo','d':'El suelo: primero lo más oscuro, las sombras de las piedras y del pasto.','m':'Luego el tono medio de las colinas, del pasto y de los arbustos.','l':'Y lo más clarito: el camino.'},
                {'n':'El cielo','d':'El cielo: un gris muy suave arriba.','m':'Luego las nubes y las mariposas.','l':'Y deja casi blanca la luz cerca de las colinas.'}]
    return [{'n':'El león','d':'Ahora el color: empieza por lo más oscuro del león: los ojos, la nariz y el café de la melena entre los mechones.','m':'Luego el café de la melena y de la cola, y el amarillo del cuerpo.','l':'Y lo más clarito: el color crema del hocico y del pecho. Deja blancos los brillos de los ojos.'},
            {'n':'Los árboles','d':'Los árboles: primero lo más oscuro, debajo de las copas y en los troncos.','m':'Luego el café de las ramas y el verde de las hojas.','l':'Y lo más claro: la luz sobre las copas.'},
            {'n':'El suelo','d':'El suelo: primero lo más oscuro, las piedras grises y las sombras del pasto.','m':'Luego el verde del pasto y de los arbustos, y los colores de las flores.','l':'Y lo más clarito: el camino de tierra.'},
            {'n':'El cielo','d':'El cielo: primero el azul de arriba.','m':'Luego las nubes y las mariposas naranjas.','l':'Y al final la luz amarilla cerca de las colinas.'}]
FIN={True:[["Los últimos detalles","Repasa lo más oscuro: los ojos, la nariz, la sonrisa y la orilla de la melena. Con la goma saca los brillos de los ojos."]],
     False:[["Los últimos detalles","Repasa lo más oscuro: los ojos, la nariz, la sonrisa y la orilla de la melena. Deja muy blancos los brillos de los ojos."]]}
F={}
for tag,did,nm,js,zs,vn,lap in [('leoncito_c','dleoncito','El leoncito en la sabana','g_partes9993.js','g_zvec9993.js','VEC9993',False),
                                 ('leoncito_g','dleoncito_lapiz','El leoncito en la sabana a lápiz','g_partes9994.js','g_zvec9994.js','VEC9994',True)]:
    prep('leoncito',tag)
    o=dict(id=did,k=tag,lvl=3,cat='Animales',name=nm,time='60 min',exact=True,h=h,guia=G,lines=L,tones=T(lap),fin=FIN[lap])
    F.update(integ(tag,f'{tag}_v.json',tag,did,H,o,js,zs,vn,CW=900)); print(tag,'ok')
json.dump(F,open('files_leoncito.json','w')); print(F)
