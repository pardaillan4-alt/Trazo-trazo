"""Sagrado Corazón de Jesús a lápiz: líneas del dibujo de líneas del usuario y sombreado de su imagen gris."""
import json,os
src=open('integ_v.py').read().split('\nF={}')[0]; exec(src)          # solo la función integ()
H=1068; h=round(400*H/900,3)
def prep(base,tag):
    os.makedirs(tag,exist_ok=True)
    if not os.path.islink(f'{tag}/out'): os.symlink(f'../{base}/out_{tag}',f'{tag}/out')
    os.system(f'cp {base}/{tag}_v.json {tag}/')
G="Muy suave: un óvalo para la cabeza, una línea por el centro de la cara y otra a la altura de los ojos. Luego una curva para los hombros, una línea por el centro del cuerpo, dos líneas para los lados del manto y un óvalo para el corazón."
L=[["Los ojos y las cejas","Sobre la línea de los ojos, dibuja los dos ojos con el iris redondo y la pupila, el pliegue de arriba y las cejas con rayitas que siguen el pelo."],
 ["La nariz","Baja por el centro con la nariz: una línea larga por un lado, la punta redondita y las alas a los lados."],
 ["El bigote, la boca y la barba","Debajo de la nariz, el bigote y la boca. Luego la barba con muchas rayitas que siguen el pelo, hasta la barbilla."],
 ["El cabello","El cabello largo que cae a los lados, con raya en medio. Dibuja los mechones ondulados hasta los hombros y los rizos de las puntas."],
 ["El cuello y el escote","El cuello y el escote redondo de la túnica, con su orilla doble."],
 ["Las manos","La mano levantada, con dos dedos hacia arriba, y la otra mano que señala el corazón. Primero la orilla y luego los nudillos y las uñas."],
 ["El corazón","En medio del pecho, el corazón con la corona de espinas, las llamas de arriba y la cruz."],
 ["Los rayos de luz","Alrededor del corazón, las líneas rectas de la luz, como un sol."],
 ["El manto de este lado","Del lado izquierdo, el manto que cae desde el hombro, con la manga ancha y sus pliegues."],
 ["El manto del otro lado","Del lado derecho, el manto con la otra manga y sus pliegues."],
 ["La túnica y el manto de abajo","Por último la túnica de en medio y el manto que cruza por abajo de lado a lado, con sus pliegues."]]
T=[{'n':'Cabello y barba','d':'Ahora el sombreado a lápiz: empieza por lo más oscuro del cabello y de la barba, entre los mechones.','m':'Luego el tono medio de todo el cabello y la barba, siguiendo la dirección del pelo.','l':'Y lo más clarito: los brillos del cabello, casi sin apretar.'},
   {'n':'Cara y manos','d':'La cara y las manos: primero lo más oscuro, los ojos, las fosas de la nariz y la boca.','m':'Luego las sombras suaves: a los lados de la nariz, bajo las cejas y entre los dedos.','l':'Y un tono muy clarito en toda la piel. Deja blancos los brillos de la frente y la nariz.'},
   {'n':'Corazón','d':'El corazón: primero lo más oscuro, el corazón y la corona de espinas.','m':'Luego el tono medio de las llamas y de la cruz.','l':'Y lo más claro: el brillo del corazón y la luz de las llamas.'},
   {'n':'Ropa','d':'La ropa: primero los pliegues más hondos del manto.','m':'Luego el tono medio de todo el manto.','l':'Y por último la túnica, muy clarita, con la luz que sale del corazón.'}]
F_=[["Los últimos detalles","Repasa lo más oscuro: las pupilas, la línea de la boca, el contorno del corazón y la corona de espinas. Con la goma saca los brillos de los ojos y la luz alrededor del corazón."]]
prep('sagrado5','sagrado5g')
o=dict(id='dsagrado_lapiz',k='sagrado5g',lvl=5,cat='Personas',name='Sagrado Corazón de Jesús',time='2 horas',exact=True,h=h,guia=G,lines=L,tones=T,fin=F_)
files=integ('sagrado5g','sagrado5g_v.json','sagrado5g','dsagrado_lapiz',854,o,'g_partes994.js','g_zvec994.js','VEC994',CW=720)
json.dump(files,open('files_sagrado.json','w')); print('sagrado5g ok',files)
