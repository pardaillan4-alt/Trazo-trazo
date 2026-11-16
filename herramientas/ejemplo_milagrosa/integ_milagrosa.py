"""La Virgen Milagrosa sobre el mundo, a color y a lápiz: líneas del dibujo de líneas del usuario (sin la firma);
sombreado de su imagen a color y de la de lápiz."""
import json,os
src=open('integ_v.py').read().split('\nF={}')[0]; exec(src)          # solo la función integ()
H=900; h=400.0; OW=720
def prep(base,tag):
    os.makedirs(tag,exist_ok=True)
    if not os.path.islink(f'{tag}/out'): os.symlink(f'../{base}/out_{tag}',f'{tag}/out')
    os.system(f'cp {base}/{tag}_v.json {tag}/')
G=("Muy suave: un óvalo para la cara, con una línea por el centro y otra para los ojos. Alrededor de la cabeza, un círculo grande para la aureola. "
   "Una curva para los hombros, una línea larga por el centro del cuerpo y dos líneas inclinadas para los brazos abiertos. Abajo, un círculo grande para el mundo.")
L=[["Los ojos y las cejas","Sobre la línea de los ojos, dibuja los dos ojos: el párpado de arriba más marcado y el de abajo suave, el iris redondo con su pupila y el pliegue de arriba. Luego las cejas, finas y curvas."],
 ["La nariz y la boca","Baja por el centro con la nariz: una línea larga de un lado y la punta con sus alitas. Debajo, la boca pequeña con su sonrisa suave."],
 ["La cara, el velo y el cabello","El contorno de la cara hasta la barbilla. Alrededor, el cabello largo con raya en medio y, por fuera, el velo que cubre la cabeza y cae sobre los hombros."],
 ["El cuello, el pecho y el moño","El cuello y el escote redondo de la túnica, los pliegues del pecho y el cinto con su moño. Las dos cintas del moño caen largas por en medio."],
 ["Las manos","Al final de los brazos, las dos manos abiertas, de donde sale la luz. Primero la orilla y después los dedos."],
 ["El manto","El manto que baja desde los hombros, se abre con los brazos y cae a los lados en pliegues ondulados hasta abajo."],
 ["El vestido","El vestido largo: los pliegues rectos que bajan desde el cinto hasta los pies."],
 ["Los pies y la serpiente","Abajo, los pies descalzos sobre la serpiente que se enrolla. Dibuja su cuerpo en curvas, la cabeza con el ojo y la lengüita, y al final las escamas en rombitos."],
 ["El mundo","El mundo bajo sus pies: la orilla redonda sobre el círculo y, adentro, los continentes con su orilla ondulada."],
 ["Los rayos de luz","De cada mano salen los rayos de luz: líneas rectas que se abren hacia abajo, como un abanico."],
 ["La aureola","Alrededor de la cabeza, la aureola: un círculo sobre la guía y otros dos más grandes por fuera, muy suaves."],
 ["Las nubes","Por último, las nubes de los lados, con su orilla en curvitas, como algodón."]]
def T(lapiz):
    if lapiz:
        return [{'n':'La Virgen','d':'Ahora el sombreado a lápiz: empieza por lo más oscuro de la Virgen: los pliegues hondos del manto, el cabello y los ojos.','m':'Luego el tono medio del manto, del vestido y de la piel.','l':'Y lo más clarito: la luz del velo y del vestido. Deja blancos los brillos.'},
                {'n':'El mundo y la serpiente','d':'El mundo: primero lo más oscuro, la serpiente y la sombra de abajo.','m':'Luego el tono medio del mar y de los continentes.','l':'Y lo más clarito: las nubes del mundo.'},
                {'n':'Las nubes','d':'Las nubes: primero lo más oscuro, entre nube y nube.','m':'Luego el tono medio de las nubes.','l':'Y lo más clarito: las orillas de las nubes, con luz.'},
                {'n':'La luz','d':'La luz: primero las nubes que se ven detrás de los rayos.','m':'Luego un gris muy suave en los rayos y alrededor de la cabeza.','l':'Y deja casi blanco el brillo de la aureola.'}]
    return [{'n':'La Virgen','d':'Ahora el color: empieza por lo más oscuro de la Virgen: los pliegues hondos del manto azul, el cabello y los ojos.','m':'Luego el azul del manto y del moño, el crema del vestido y el color de la piel.','l':'Y lo más clarito: la luz del velo y del vestido. Deja blancos los brillos.'},
            {'n':'El mundo y la serpiente','d':'El mundo: primero lo más oscuro, la serpiente y las sombras de abajo.','m':'Luego el azul del mar y el verde de los continentes.','l':'Y lo más clarito: las nubes blancas del mundo.'},
            {'n':'Las nubes','d':'Las nubes: primero lo más oscuro, el café entre nube y nube.','m':'Luego el tono medio de las nubes, dorado y café.','l':'Y lo más clarito: las orillas de las nubes, donde les pega la luz.'},
            {'n':'La luz','d':'La luz: primero las nubes que se ven detrás de los rayos.','m':'Luego el amarillo de los rayos y alrededor de la cabeza.','l':'Y al final lo más claro: el brillo de la aureola, casi blanco.'}]
FIN={True:[["Los últimos detalles","Repasa lo más oscuro: los ojos, la boca, la orilla del manto y la serpiente. Con la goma saca la luz de los rayos y de la aureola."]],
     False:[["Los últimos detalles","Repasa lo más oscuro: los ojos, la boca, la orilla del manto y la serpiente. Deja muy brillante la luz de la aureola y de los rayos."]]}
F={}
for tag,did,nm,js,zs,vn,lap in [('milagrosa_c','dmilagrosa','La Virgen Milagrosa sobre el mundo','g_partes9995.js','g_zvec9995.js','VEC9995',False),
                                 ('milagrosa_g','dmilagrosa_lapiz','La Virgen Milagrosa sobre el mundo a lápiz','g_partes9996.js','g_zvec9996.js','VEC9996',True)]:
    prep('milagrosa',tag)
    o=dict(id=did,k=tag,lvl=5,cat='Personas',name=nm,time='2 horas',exact=True,h=h,guia=G,lines=L,tones=T(lap),fin=FIN[lap])
    F.update(integ(tag,f'{tag}_v.json',tag,did,OW,o,js,zs,vn,CW=OW)); print(tag,'ok')
json.dump(F,open('files_milagrosa.json','w')); print(F)
