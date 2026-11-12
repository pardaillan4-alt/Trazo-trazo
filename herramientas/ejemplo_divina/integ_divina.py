"""Divina Misericordia, a color y a lápiz: líneas del dibujo de líneas del usuario; sombreado de su imagen a color y de la gris."""
import json,os
src=open('integ_v.py').read().split('\nF={}')[0]; exec(src)          # solo la función integ()
H=1464; h=round(400*H/900,3); CH=1171
def prep(base,tag):
    os.makedirs(tag,exist_ok=True)
    if not os.path.islink(f'{tag}/out'): os.symlink(f'../{base}/out_{tag}',f'{tag}/out')
    os.system(f'cp {base}/{tag}_v.json {tag}/')
G=("Muy suave: un óvalo para la cabeza, con una línea por el centro de la cara y otra para los ojos. "
   "Una curva para los hombros y una línea larga hasta los pies. Dos óvalos para las mangas y dos chiquitos para las manos. "
   "Un circulito en el pecho, de donde salen dos líneas para los rayos, y abajo una línea para las letras.")
L=[["Los ojos y las cejas","Sobre la línea de los ojos, dibuja los dos ojos con su iris redondo y la pupila, el pliegue de arriba y las cejas."],
 ["La nariz","Baja por el centro con la nariz: una línea larga por un lado, la punta y las alas a los lados."],
 ["La boca, el bigote y la barba","Debajo de la nariz, el bigote y la boca con una sonrisa suave. Luego las mejillas y la barba con rayitas que siguen el pelo, hasta la barbilla en dos puntas."],
 ["El cabello y la aureola","El cabello largo con raya en medio, que cae en ondas hasta los hombros. Alrededor de la cabeza, un círculo muy suave: la aureola."],
 ["El cuello","El cuello y el escote redondo de la túnica, con su orilla doble."],
 ["Las manos","La mano levantada que bendice, con su brazo. Luego la otra mano sobre el pecho, con los dedos que señalan el corazón."],
 ["La manga de este lado","La manga ancha que cuelga del brazo levantado, con sus pliegues hondos."],
 ["La manga del otro lado","Del otro lado, el hombro y la manga larga que cae, con sus pliegues."],
 ["La túnica","La túnica: los pliegues del pecho, el cinto en la cintura y los pliegues largos que bajan hasta los pies. En medio se pierden con la luz."],
 ["Los pies","Abajo, los pies descalzos que se asoman bajo la túnica, con sus deditos."],
 ["La luz del corazón","Del corazón, debajo de los dedos, salen rayitas cortas en todas direcciones, como una estrella."],
 ["Los rayos de luz","Ahora los rayos grandes: muchas líneas rectas que salen del corazón y se abren hacia abajo. Arriba se ven fuertes, en medio se pierden con la luz y abajo vuelven a aparecer."],
 ["Las letras","Abajo, con letra bonita: Jesús, en Ti confío. Dibuja la orilla de cada letra, una por una."],
 ["El piso","Por último el piso de piedras: rectángulos chuecos, uno junto a otro."]]
def T(lapiz):
    if lapiz:
        return [{'n':'Cabello y barba','d':'Ahora el sombreado a lápiz: primero lo más oscuro del cabello y de la barba, entre los mechones.','m':'Luego el tono medio de todo el cabello, siguiendo las ondas.','l':'Y lo más clarito: los brillos del cabello, casi sin apretar.'},
                {'n':'Cara y manos','d':'La piel: primero lo más oscuro, los ojos, debajo de la nariz y entre los dedos.','m':'Luego las sombras suaves de la cara, el cuello, las manos y los pies.','l':'Y un tono muy clarito en toda la piel. Deja blancos los brillos.'},
                {'n':'La túnica','d':'La túnica: primero los pliegues más hondos de las mangas y de abajo.','m':'Luego el tono medio de toda la túnica.','l':'Y lo más clarito: el pecho, donde brilla la luz.'},
                {'n':'La luz y el fondo','d':'Ahora el fondo: oscurece todo alrededor y el piso, y deja claritos los rayos de luz.','m':'Luego el tono medio de los rayos, más suave cerca de Jesús.','l':'Y al final lo más clarito: la luz alrededor de la cabeza, el brillo del corazón y las letras.'}]
    return [{'n':'Cabello y barba','d':'Ahora el color: primero el café más oscuro del cabello y de la barba, entre los mechones.','m':'Luego el café de todo el cabello, siguiendo las ondas.','l':'Y lo más clarito: los brillos dorados del cabello.'},
            {'n':'Cara y manos','d':'La piel: primero lo más oscuro, los ojos, debajo de la nariz y entre los dedos.','m':'Luego el color de la piel en la cara, el cuello, las manos y los pies.','l':'Y un tono muy clarito en toda la piel. Deja blancos los brillos.'},
            {'n':'La túnica','d':'La túnica: primero los pliegues más hondos de las mangas y de abajo.','m':'Luego el color crema de la túnica, y donde le pega la luz, rojo de un lado y azul del otro.','l':'Y lo más claro: el pecho, donde brilla la luz.'},
            {'n':'La luz y el fondo','d':'Ahora el fondo: azul muy oscuro alrededor y el piso, y deja claritos los rayos de luz.','m':'Luego los rayos: rojo de un lado y azul pálido del otro.','l':'Y al final lo más clarito: la luz alrededor de la cabeza, el brillo del corazón y las letras blancas.'}]
FIN={True:[["Los últimos detalles","Repasa lo más oscuro: las pupilas, la línea de la boca y la orilla de las letras. Con la goma saca el brillo del corazón y la luz de los rayos."]],
     False:[["Los últimos detalles","Repasa lo más oscuro: las pupilas, la línea de la boca y la orilla de las letras. Deja muy blanco el brillo del corazón."]]}
F={}
for tag,did,nm,js,zs,vn,lap in [('divina_c','ddivina','Divina Misericordia','g_partes995.js','g_zvec995.js','VEC995',False),
                                 ('divina_g','ddivina_lapiz','Divina Misericordia a lápiz','g_partes996.js','g_zvec996.js','VEC996',True)]:
    prep('divina',tag)
    o=dict(id=did,k=tag,lvl=5,cat='Personas',name=nm,time='2 horas',exact=True,h=h,guia=G,lines=L,tones=T(lap),fin=FIN[lap])
    F.update(integ(tag,f'{tag}_v.json',tag,did,CH,o,js,zs,vn,CW=720)); print(tag,'ok')
json.dump(F,open('files_divina.json','w')); print(F)
