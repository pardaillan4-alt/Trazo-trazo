import json,os
src=open('integ_v.py').read().split('\nF={}')[0]; exec(src)          # solo la función integ()
H=502; h=round(400*H/900,1)
def prep(base,tag):
    os.makedirs(tag,exist_ok=True)
    if not os.path.islink(f'{tag}/out'): os.symlink(f'../{base}/out_{tag}',f'{tag}/out')
    os.system(f'cp {base}/{tag}_v.json {tag}/')
L_BARCO=[["La cabeza de la ballena","Sobre el óvalo, la cabeza larga de la ballena: la orilla de arriba con sus bolitas, la línea de la boca y el ojo pequeño."],
 ["El cuerpo y la cola","Sigue la orilla del lomo hasta la cola, con la aletita de arriba, y la cola abierta en dos puntas. Luego la orilla de la panza."],
 ["Las aletas","Las dos aletas: la larga, que baja hacia la derecha, y la de atrás, más cortita."],
 ["Las rayas de la garganta","Las rayas largas de la garganta, una junto a otra, siguiendo la curva de la panza."],
 ["El casco del barco","Ahora el barco hundido, inclinado sobre el óvalo de abajo: el casco con sus tablas, las ventanitas redondas y la orilla de arriba."],
 ["La cabina y la chimenea","Arriba del casco, la cabina con sus ventanas, la chimenea y las plantitas que crecen encima."],
 ["El mástil y las cuerdas","Sobre la línea recta, el mástil, el palo cruzado de arriba y las cuerdas que bajan, con las algas que cuelgan."],
 ["Los peces y las burbujas","Los pececitos que nadan alrededor y las burbujas que suben."],
 ["El fondo del mar","Por último el fondo del mar: las rocas, los corales y las algas."]]
G_BARCO="Muy suave: un óvalo largo e inclinado para el cuerpo de la ballena, una curva para la cola y una raya para la punta de la cola. A la izquierda, otro óvalo inclinado para el casco del barco y una línea recta para el mástil."
def T_BARCO(lapiz):
    a='Ahora el sombreado a lápiz' if lapiz else 'Ahora el color'
    return [{'n':'Ballena','d':f'{a}: primero lo más oscuro de la ballena, el lomo y la cola.','m':'Luego el tono medio de la piel y de las aletas.','l':'Y lo más clarito, la panza y los brillos de la luz.'},
            {'n':'Barco','d':'El barco: primero lo más oscuro, las ventanas y las sombras del casco.','m':'Luego el tono medio de la madera y de las algas.','l':'Y lo claro, donde le pega la luz.'},
            {'n':'Mar','d':'El mar: primero lo más oscuro, abajo y en las orillas.','m':'Luego el tono medio del agua, los corales y las algas.','l':'Y por último los rayos de luz que bajan desde arriba.'}]
F_BARCO=[["Los últimos detalles","Repasa lo más oscuro: el ojo de la ballena, las ventanas del barco y las sombras de abajo."]]
L_DELF=[["El cuerpo de la ballena","Sobre el óvalo grande, la orilla del cuerpo de la ballena: el lomo redondo con sus manchitas."],
 ["La cola","Al final de la curva, la cola en dos puntas, como una V."],
 ["La cara de la ballena","El ojo grande y brillante con su ceja, y la sonrisa que cruza la cara."],
 ["La panza y las aletas","La panza con sus rayas y las aletas: una adelante y otra chiquita abajo."],
 ["El chorro de agua","Arriba, el chorro de agua que sale de la cabeza, con sus gotitas."],
 ["El delfín","Sobre el círculo y la curva, el cuerpo del delfín que se dobla hacia abajo, con la aleta de arriba, la del lado y la cola."],
 ["La cara del delfín","El hocico largo, la boca abierta y sonriente, el ojo y la cejita."],
 ["Los peces y las burbujas","Los pececitos y las burbujas que flotan alrededor."],
 ["El fondo del mar","Por último el fondo: las olas de arriba, las algas, los corales, las estrellas de mar y las conchitas."]]
G_DELF="Muy suave: un óvalo grande para el cuerpo de la ballena, una curva para la cola y una raya para la punta de la cola. A la derecha, un círculo para la cabeza del delfín y una curva larga para su cuerpo, que se dobla hacia abajo."
def T_DELF(lapiz):
    a='Ahora el sombreado a lápiz' if lapiz else 'Ahora el color'
    return [{'n':'Ballena','d':f'{a}: primero lo más oscuro de la ballena, el lomo y la cola.','m':'Luego el tono medio de la piel y de las aletas.','l':'Y lo más clarito, la panza y los brillos.'},
            {'n':'Delfín','d':'El delfín: primero lo más oscuro del lomo y de las aletas.','m':'Luego el tono medio de la piel.','l':'Y deja clara la panza.'},
            {'n':'Mar','d':'El mar: primero lo más oscuro del fondo y de las algas.','m':'Luego el tono medio del agua, los corales y la arena.','l':'Y por último los rayos de luz que bajan desde arriba.'}]
F_DELF=[["Los últimos detalles","Repasa lo más oscuro: los ojos y las sonrisas, y deja los brillitos blancos."]]
F={}
for base,tag,did,nm,lvl,tm,G,Ls,T,Fi,js,zs,vn,lap in [
  ('ballena5','ballena5c','dballena5','La ballena y el barco hundido',5,'2 horas',G_BARCO,L_BARCO,T_BARCO,F_BARCO,'g_partes99.js','g_zvec99.js','VEC99',False),
  ('ballena5','ballena5g','dballena5_lapiz','La ballena y el barco hundido a lápiz',5,'2 horas',G_BARCO,L_BARCO,T_BARCO,F_BARCO,'g_partes991.js','g_zvec991.js','VEC991',True),
  ('delfin5','delfin5c','ddelfin5','La ballena y el delfín',3,'60 min',G_DELF,L_DELF,T_DELF,F_DELF,'g_partes992.js','g_zvec992.js','VEC992',False),
  ('delfin5','delfin5g','ddelfin5_lapiz','La ballena y el delfín a lápiz',3,'60 min',G_DELF,L_DELF,T_DELF,F_DELF,'g_partes993.js','g_zvec993.js','VEC993',True)]:
    prep(base,tag)
    o=dict(id=did,k=tag,lvl=lvl,cat='Animales',name=nm,time=tm,exact=True,h=h,guia=G,lines=Ls,tones=T(lap),fin=Fi)
    F.update(integ(tag,f'{tag}_v.json',tag,did,H,o,js,zs,vn,CW=900)); print(tag,'ok')
json.dump(F,open('files_mar.json','w'))
