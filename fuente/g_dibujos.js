/* Dibujos reales a mano (Pixabay) convertidos en pasos */
(()=>{
const im=k=>[1,2,3,4,5,6,7,8].map(i=>`img/d_${k}_lapiz_${i}.webp`);
const C={base:[['#B9B9C0','Lápiz HB']],mid:[['#8A8A96','Lápiz 2B']],dark:[['#4A4A55','Lápiz 4B']],detail:[['#2E2E36','Punta fina']],light:[['#FFFFFF','Goma moldeable']]};
const mk=(id,lvl,cat,name,time,sh,T)=>add({id,lvl,cat,name,time,sh,img:{lapiz:im(id==='dcaballo'?'caballo':id.slice(1))},
  steps:T.map((s,i)=>i<3?{t:s[0],x:s[1]}:{t:s[0],x:s[1],m:['base','mid','dark','detail','light'][i-3],chip:{lapiz:(s[2]||C[['base','mid','dark','detail','light'][i-3]])}})});
add({id:'dpajaro',lvl:3,cat:'Animales',name:'Pajarito en el cerezo',time:'90 min',sh:'Parte por parte, de oscuro a claro',
 img:{lapiz:Array.from({length:29},(_,i)=>`img/p5_pajaro_${i+1}.webp`)},
 steps:[
  {t:'Las guías',x:'Empieza con un círculo pequeño para la cabeza y un óvalo inclinado debajo para el cuerpo. Una línea corta marca la cola y una línea larga, la rama. Todo muy suave, casi sin apretar.'},
  {t:'Contorno de la cabeza',x:'Sobre el círculo, dibuja solo el borde de la cabeza: una curva redonda arriba que baja por la nuca. Nada adentro todavía. Deja abierto el lado del pico.'},
  {t:'El ojo',x:'Dentro de la cabeza, un poco hacia el pico, dibuja el contorno del ojo: un óvalo pequeño. Solo la orilla, sin rellenar.'},
  {t:'El pico',x:'En el hueco que dejaste, dibuja el pico: un triángulo corto y en punta, con una línea en medio que lo divide.'},
  {t:'Plumitas de la cabeza',x:'Ahora sí, adentro de la cabeza: unas rayitas cortas alrededor del ojo y en la coronilla. Son las plumitas.'},
  {t:'Contorno del cuerpo',x:'Desde la cabeza baja con una línea suave por el pecho, que es redondo y abultado, hasta abajo de la panza.'},
  {t:'Contorno del ala',x:'Del lado izquierdo, dibuja el borde del ala: larga, en forma de gota, que baja hacia la cola.'},
  {t:'Plumas del ala',x:'Dentro del ala, dibuja las plumas largas en filas, una junto a otra.'},
  {t:'La cola',x:'Debajo del ala sale la cola, larga y angosta, que termina en punta.'},
  {t:'Las patitas',x:'Dos patitas delgadas que bajan a la rama, con deditos que la abrazan como ganchitos.'},
  {t:'La rama',x:'Dibuja la rama: gruesa abajo y delgada arriba, con ramitas a los lados y algunos nudos.'},
  {t:'Las flores',x:'Alrededor, las flores del cerezo: cinco pétalos redondos alrededor de un centro.'},
  {t:'Cabeza: lo más oscuro',m:'dark',x:'Empezamos el sombreado por la cabeza y por lo más oscuro: el ojo bien negro, la línea que pasa junto al ojo y las plumitas oscuras de alrededor. Aprieta el lápiz.',chip:{lapiz:[['#4A4A55','Lápiz 4B']]}},
  {t:'Cabeza: tonos medios',m:'mid',x:'Ahora los tonos medios de la cabeza: la coronilla y la mejilla. Presión media, trazos cortitos hacia atrás.',chip:{lapiz:[['#8A8A96','Lápiz 2B']]}},
  {t:'Cabeza: lo más claro',m:'base',x:'Por último lo más clarito: la garganta y el borde de la cabeza. Casi sin apretar; deja que se vea el papel.',chip:{lapiz:[['#B9B9C0','Lápiz HB']]}},
  {t:'Cuerpo: lo más oscuro',m:'dark',x:'En el cuerpo, primero las sombras fuertes: debajo del ala y la parte de abajo de la panza.',chip:{lapiz:[['#4A4A55','Lápiz 4B']]}},
  {t:'Cuerpo: tonos medios',m:'mid',x:'Luego el tono medio en los costados del pecho, siguiendo la forma redonda.',chip:{lapiz:[['#8A8A96','Lápiz 2B']]}},
  {t:'Cuerpo: lo más claro',m:'base',x:'Y al final las plumitas casi blancas del pecho, con trazos muy suaves.',chip:{lapiz:[['#B9B9C0','Lápiz HB']]}},
  {t:'Ala y cola: lo más oscuro',m:'dark',x:'En el ala, primero las rayas oscuras de las plumas largas y la punta de la cola.',chip:{lapiz:[['#4A4A55','Lápiz 4B']]}},
  {t:'Ala y cola: tonos medios',m:'mid',x:'Después el tono medio entre las rayas, para que se vean las plumas una junto a otra.',chip:{lapiz:[['#8A8A96','Lápiz 2B']]}},
  {t:'Ala y cola: lo más claro',m:'base',x:'Por último los bordes claros de cada pluma: casi blancos, apenas tocando el papel.',chip:{lapiz:[['#B9B9C0','Lápiz HB']]}},
  {t:'Patitas: lo más oscuro',m:'dark',x:'Las patitas: primero lo oscuro, las uñas y la parte de abajo de los dedos.',chip:{lapiz:[['#4A4A55','Lápiz 4B']]}},
  {t:'Patitas: tonos medios',m:'mid',x:'Luego el tono medio en los dedos y las escamitas.',chip:{lapiz:[['#8A8A96','Lápiz 2B']]}},
  {t:'Patitas: lo más claro',m:'base',x:'Y lo claro en el lado donde les da la luz.',chip:{lapiz:[['#B9B9C0','Lápiz HB']]}},
  {t:'Rama: lo más oscuro',m:'dark',x:'La rama: primero las sombras fuertes, las grietas, los nudos y el lado de abajo.',chip:{lapiz:[['#4A4A55','Lápiz 4B']]}},
  {t:'Rama: tonos medios',m:'mid',x:'Después el tono medio a lo largo de la corteza.',chip:{lapiz:[['#8A8A96','Lápiz 2B']]}},
  {t:'Rama: lo más claro',m:'base',x:'Al final las partes claras donde pega la luz.',chip:{lapiz:[['#B9B9C0','Lápiz HB']]}},
  {t:'Flores: centros y sombras',m:'dark',x:'En las flores, primero lo más oscuro: los centritos con sus puntos y las sombras entre pétalos.',chip:{lapiz:[['#4A4A55','Lápiz 4B']]}},
  {t:'Flores: pétalos suaves',m:'base',x:'Termina con un gris muy suave en los pétalos y detrás de las flores, para que resalten blancas. ¡Listo, terminaste tu pajarito!',chip:{lapiz:[['#B9B9C0','Lápiz HB']]}}
 ]});
})();
