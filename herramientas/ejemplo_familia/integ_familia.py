"""Retrato en familia, a color y a lápiz: líneas del dibujo de líneas del usuario; sombreado de su imagen a color y de la gris."""
import json,os
src=open('integ_v.py').read().split('\nF={}')[0]; exec(src)
H=1200; h=round(400*H/900,3); CH=960
def prep(base,tag):
    os.makedirs(tag,exist_ok=True)
    if not os.path.islink(f'{tag}/out'): os.symlink(f'../{base}/out_{tag}',f'{tag}/out')
    os.system(f'cp {base}/{tag}_v.json {tag}/')
G=("Muy suave: tres óvalos para las caras. El más grande, a la derecha, para el papá; uno abajo a la izquierda para el niño de adelante "
   "y uno chiquito arriba para el niño de atrás. En cada óvalo, una línea para los ojos. Luego una curva para los hombros y dos líneas para la barda.")
L=[["Los ojos y las cejas del papá","Empieza por la cara del papá: los dos ojos sobre su línea, con la pupila negra, y las cejas con rayitas cortas."],
 ["La nariz y la boca del papá","La nariz con sus alas y, abajo, la boca con una sonrisa grande que deja ver los dientes."],
 ["La cabeza y el cabello del papá","El contorno de la cara hasta la barbilla, la oreja y el cabello ondulado, rizo por rizo."],
 ["Los ojos y las cejas del niño de adelante","Ahora el niño de adelante, con la cabeza un poco inclinada: sus ojos con la pupila y sus cejas."],
 ["La nariz y la boca del niño de adelante","Su nariz chiquita y su boca sonriente."],
 ["La cabeza y el cabello del niño de adelante","El contorno de su cara y el cabello lacio, con mechones que caen sobre la frente."],
 ["El niño de atrás","Arriba, el niño de atrás: sus ojos, su nariz, su sonrisa, la oreja, el cabello y el cuello de su camisa."],
 ["La camisa y el collar del papá","La camisa del papá con su cuello y sus pliegues, y el collar con el medallón."],
 ["La ropa del niño de adelante","La ropa del niño de adelante: la manga, la bufanda con sus puntitos y el brazo que lo abraza."],
 ["La barda","La barda de tubos detrás de ellos, con el brazo del niño que se apoya, y las hojitas que se ven entre los tubos."],
 ["El árbol","Arriba, el árbol: las ramas grandes y las hojas con sus orillas en picos."],
 ["Las hojas de abajo","Por último, las hojas de los arbustos a los lados de las cabezas."]]
def T(lapiz):
    pre='Ahora el sombreado a lápiz' if lapiz else 'Ahora el color'
    return [{'n':'El papá','d':pre+': empieza por el papá, con lo más oscuro del cabello, los ojos y la boca.','m':'Luego las sombras de la cara: a los lados de la nariz, bajo los ojos y en el cuello.','l':'Y un tono muy suave en toda la piel. Deja claritos los brillos de la frente y la nariz.'},
            {'n':'El niño de adelante','d':'El niño de adelante: primero lo más oscuro del cabello y de los ojos.','m':'Luego las sombras suaves de su cara, junto a la nariz y bajo el cabello.','l':'Y un tono clarito en toda su piel, con brillos en las mejillas.'},
            {'n':'El niño de atrás','d':'El niño de atrás: lo más oscuro de su cabello y sus ojos.','m':'Luego las sombras de su cara y de su camisa.','l':'Y lo más clarito de su piel.'},
            {'n':'La ropa','d':'La ropa: primero los pliegues más hondos de la camisa del papá.' if lapiz else 'La ropa: primero el azul oscuro de los pliegues de la camisa del papá.','m':'Luego el tono de toda la camisa, la bufanda y la manga.' if lapiz else 'Luego el azul de toda la camisa, y el color crema de la bufanda.','l':'Y lo más claro: los brillos de la tela y del medallón.'},
            {'n':'El fondo','d':'El fondo: primero lo más oscuro, entre las ramas y las hojas, y los tubos de la barda.' if lapiz else 'El fondo: primero lo más oscuro, entre las ramas y las hojas, y el rojo de la barda.','m':'Luego el tono medio de los árboles y los arbustos.' if lapiz else 'Luego el verde y el café de los árboles y los arbustos.','l':'Y al final el cielo y la luz que entra entre las hojas, muy suave.'}]
FIN=[["Los últimos detalles","Repasa lo más oscuro: las pupilas, el cabello y las sonrisas. Con la goma saca los brillos de los ojos, de los dientes y del medallón."]]
F={}
for tag,did,nm,js,zs,vn,lap in [('familia_c','dfamilia','Retrato en familia','g_partes997.js','g_zvec997.js','VEC997',False),
                                 ('familia_g','dfamilia_lapiz','Retrato en familia a lápiz','g_partes998.js','g_zvec998.js','VEC998',True)]:
    prep('familia',tag)
    o=dict(id=did,k=tag,lvl=5,cat='Personas',name=nm,time='2 horas',exact=True,h=h,guia=G,lines=L,tones=T(lap),fin=FIN)
    F.update(integ(tag,f'{tag}_v.json',tag,did,CH,o,js,zs,vn,CW=720)); print(tag,'ok')
