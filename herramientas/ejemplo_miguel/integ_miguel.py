"""San Miguel Arcángel a lápiz: líneas del dibujo de líneas del usuario (ojos medidos a mano); sombreado de su imagen a lápiz."""
import json,os
src=open('integ_v.py').read().split('\nF={}')[0]; exec(src)          # solo la función integ()
H=491; h=round(400*H/900,1)
def prep(base,tag):
    os.makedirs(tag,exist_ok=True)
    if not os.path.islink(f'{tag}/out'): os.symlink(f'../{base}/out_{tag}',f'{tag}/out')
    os.system(f'cp {base}/{tag}_v.json {tag}/')
G=("Muy suave: un óvalo para la cabeza, con una línea por el centro de la cara y otra para los ojos. Una curva para los hombros y una línea larga "
   "por el centro del cuerpo. Dos líneas para las piernas, una línea larga para la espada y un óvalo para el escudo. Para cada ala, una curva arriba "
   "y otra abajo que se juntan en la punta. Abajo, un óvalo para el demonio, un círculo para su cabeza y una curva para la roca.")
L=[["Los ojos y las cejas","Empieza por la cara: sobre la línea de los ojos, dibuja los dos ojos con el párpado de arriba más marcado, el iris redondo y la pupila. Arriba, las cejas, que bajan hacia la nariz."],
 ["La nariz y la boca","Baja por el centro con la nariz: una línea larga de un lado y la punta con sus alitas. Debajo, la boca: el labio de arriba con su curva y una rayita para el de abajo."],
 ["La cara y el cabello","El contorno de la cara, de la oreja hasta la barbilla. A los lados, el cabello en rizos que sale debajo del casco."],
 ["El casco y la pluma","Encima de la cabeza, el casco redondo con su orilla y la banda adornada. Arriba, la pluma que se riza hacia atrás."],
 ["El cuello y el manto del pecho","El cuello, la orilla redonda de la túnica y el manto que cruza por el pecho, sujeto en el hombro con un broche redondo."],
 ["La armadura","La armadura: las placas del hombro, el peto con sus adornos y abajo las tiras de la falda, una junto a otra. Primero las orillas y al final los adornos."],
 ["El brazo y la espada","El brazo con su brazalete y la mano que agarra la espada. Luego la espada: el mango, la cruz y la hoja larga y recta que baja hasta la punta."],
 ["El escudo","El escudo en forma de punta: su orilla doble, la cruz grande en medio y al final los adornos de la orilla."],
 ["Las piernas y las sandalias","Las piernas: una derecha y la otra doblada, pisando al demonio. Las rodilleras redondas, las grebas con sus adornos y las sandalias con sus tiras."],
 ["La capa","La capa que cae detrás del brazo, con sus pliegues, y la parte que se asoma entre las piernas."],
 ["El ala de este lado","Ahora el ala de este lado: primero la orilla de arriba y las plumas grandes, fila por fila, y al final las rayitas de cada pluma."],
 ["El ala del otro lado","El ala del otro lado igual: la orilla, las filas de plumas y al final sus rayitas."],
 ["El demonio","Abajo, el demonio acostado: su cuerpo, la cabeza con sus cuernos, la mano y el ala de murciélago con sus puntas."],
 ["La roca","Por último, la roca donde está parado: su orilla y sus grietas."]]
T=[{'n':'San Miguel','d':'Ahora el sombreado a lápiz: empieza por lo más oscuro de San Miguel: la capa por dentro, entre los pliegues y debajo del escudo.','m':'Luego el tono medio de la armadura, del casco, de la piel y del escudo.','l':'Y lo más clarito: los brillos de la armadura y del escudo, casi sin apretar.'},
   {'n':'Las alas','d':'Las alas: primero lo más oscuro, entre las plumas y cerca del cuerpo.','m':'Luego el tono medio de cada pluma.','l':'Y lo más clarito: la orilla de arriba de las alas, con luz.'},
   {'n':'El demonio y la roca','d':'El demonio y la roca: primero lo más oscuro, la sombra debajo del demonio y las grietas.','m':'Luego el tono medio del demonio, de su ala y de la roca.','l':'Y lo más clarito: la luz sobre la roca.'},
   {'n':'El fondo','d':'El fondo: un gris suave en las orillas del dibujo.','m':'Luego un poco más claro hacia el centro.','l':'Y deja casi blanca la luz alrededor de San Miguel.'}]
FIN=[["Los últimos detalles","Repasa lo más oscuro: los ojos, la orilla de la capa y de las alas. Con la goma saca los brillos del casco, de la espada y del escudo."]]
prep('miguel','miguel_g')
o=dict(id='dmiguel_lapiz',k='miguel_g',lvl=5,cat='Personas',name='San Miguel Arcángel',time='2 horas',exact=True,h=h,guia=G,lines=L,tones=T,fin=FIN)
F=integ('miguel_g','miguel_g_v.json','miguel_g','dmiguel_lapiz',H,o,'g_partes9997.js','g_zvec9997.js','VEC9997',CW=900)
json.dump(F,open('files_miguel.json','w')); print('miguel_g ok',F)
