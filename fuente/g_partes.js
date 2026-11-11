/* Dibujos reales construidos parte por parte; sombreado de oscuro a claro */
const GOMA=['gatofoto','dpulpo','djcolor','djardin','dsofa','drama','dcielo'];
const PD=(o)=>{
  if(!o.fin&&GOMA.includes(o.id))o.fin=[['Brillos con la goma','Por último, con la goma, saca los brillos: los ojos, la nariz y las partes donde da más la luz.']];
  const n=1+o.lines.length+o.tones.reduce((a,t)=>a+(t.b||3),0)+(o.fin||[]).length+(o.pre||[]).length;
  const steps=[{t:'Las guías',x:o.guia}];
  o.lines.forEach(([t,x])=>steps.push({t,x}));
  (o.pre||[]).forEach(([t,x,c])=>steps.push({t,x,m:'base',chip:{lapiz:[c||['#9A9AA4','Grafito en polvo']]}}));
  const L=Object.assign({dark:['#4A4A55','Lápiz 4B'],mid:['#8A8A96','Lápiz 2B'],base:['#B9B9C0','Lápiz HB']},o.lap||{});
  o.tones.forEach(t=>{
    const seq=(t.b===1)?[['base','todo',t.d]]:(t.b===2)?[['dark','lo más oscuro',t.d],['base','lo más claro',t.l]]:[['dark','lo más oscuro',t.d],['mid','tonos medios',t.m],['base','lo más claro',t.l]];
    seq.forEach(([m,lab,x])=>steps.push({t:`${t.n}: ${lab}`,m,x,chip:{lapiz:[L[m]]}}));
  });
  (o.fin||[]).forEach(([t,x,c])=>steps.push({t:'Para terminar: '+t.charAt(0).toLowerCase()+t.slice(1),x,m:'base',chip:{lapiz:[c||['#F2F2F2','Goma']]}}));
  steps[steps.length-1].x+=' ¡Listo, terminaste!';
  if(steps.length!==n)console.warn('pasos',o.id,steps.length,n);
  add({artist:o.artist,reveal:o.reveal,exact:o.exact,id:o.id,lvl:o.lvl,cat:o.cat,name:o.name,time:o.time,h:o.h,sh:'Parte por parte, de oscuro a claro',
    img:{lapiz:Array.from({length:n},(_,i)=>`img/p6_${o.k}_${i+1}.webp`)},steps});
};
PD({id:'dgatos',k:'gatos',lvl:4,cat:'Animales',name:'Gatitos abrazados',time:'80 min',
 guia:'Dos círculos para las cabezas: uno abajo a la izquierda para el gato grande y otro arriba a la derecha para el gatito. Un óvalo grande para los cuerpos y otro abajo para las patas.',
 lines:[["Cabeza del gato grande","Dibuja solo el borde de la cabeza del gato grande, con su oreja en punta. Nada adentro."],
  ["Sus ojos","Sus ojos están entrecerrados: dos rayitas curvas."],
  ["Su cara","La nariz, la boca y los bigotes del gato grande."],
  ["Cabeza del gatito","Arriba, el borde de la cabeza del gatito con sus dos orejas."],
  ["Su ojo","El ojo del gatito, redondo, y su nariz."],
  ["Detalles del gatito","Las rayitas de su frente y su boca."],
  ["La patita que abraza","La pata del gatito pasa por encima de la cabeza del gato grande."],
  ["Los cuerpos","Dibuja el borde de los dos cuerpos, uno junto al otro."],
  ["Las patas","Abajo, las patas estiradas del gato grande, con sus deditos."],
  ["La sombra","Unas líneas suaves marcan dónde va la sombra en el suelo."]],
 tones:[{n:'Gato grande',d:'Empieza por la cabeza del gato grande: primero lo oscuro, ojos, nariz y dentro de la oreja.',m:'Luego el tono medio de la cara.',l:'Y lo claro: su pelo es blanco, casi no lleva lápiz.'},
  {n:'Gatito',d:'La cabeza del gatito: primero el ojo y las rayas oscuras.',m:'Luego los tonos medios de su pelo.',l:'Y lo claro alrededor de la boca.'},
  {n:'Cuerpos',d:'Los cuerpos: primero las sombras fuertes donde se juntan.',m:'Luego el tono medio de las rayas del gatito.',l:'Y al final el pelo claro.'},
  {n:'Patas',d:'Las patas: primero la sombra entre los dedos.',m:'Luego el tono medio.',l:'Y lo claro de arriba.'},
  {n:'Sombra',b:2,d:'La sombra en el suelo, oscura junto a los gatos.',l:'Y se va aclarando hacia afuera.'}]});
PD({id:'dcaballo',k:'caballo',lvl:5,cat:'Animales',name:'Caballo al galope',time:'100 min',
 guia:'Un óvalo alargado para la cabeza, una línea para el cuello y un óvalo grande para el cuerpo. Las patas son líneas con un quiebre en cada rodilla.',
 lines:[["Contorno de la cabeza","Dibuja solo el borde de la cabeza, larga y de frente, con las orejas paradas."],
  ["Ojos y orejas","Adentro: los ojos a los lados y las líneas de las orejas."],
  ["El hocico","Abajo, el hocico con las fosas nasales y la boca."],
  ["El cuello","El cuello fuerte baja desde la cabeza hasta el pecho."],
  ["Contorno del cuerpo","El borde del pecho y del cuerpo."],
  ["Los músculos","Adentro, las líneas de los músculos del pecho y los hombros."],
  ["Patas de adelante","Las patas de adelante: una levantada y otra estirada, con sus cascos."],
  ["Patas de atrás","Las patas de atrás, con sus cascos."],
  ["La crin","La crin, con líneas sueltas que vuelan hacia atrás."],
  ["La cola","La cola, larga y en movimiento."]],
 tones:[{n:'Cabeza',d:'Empieza por la cabeza: primero lo oscuro, ojos, fosas nasales y orejas. Usa lápiz café o sepia.',m:'Luego el café medio a los lados de la cara.',l:'Y lo claro de la frente y la raya blanca.'},
  {n:'Cuello',d:'El cuello: primero la sombra junto a la crin.',m:'Luego el café medio.',l:'Y los brillos del músculo.'},
  {n:'Cuerpo',d:'El cuerpo: primero las sombras fuertes del pecho y la panza.',m:'Luego el café medio de los músculos.',l:'Y las luces de los músculos.'},
  {n:'Patas',d:'Las patas: primero lo oscuro, las de atrás casi negras.',m:'Luego los grises de las rodillas.',l:'Y los brillos de los cascos.'},
  {n:'Crin y cola',d:'La crin y la cola: primero los mechones oscuros.',m:'Luego los medios.',l:'Y los mechones claros que vuelan.'},
  {n:'Fondo',b:2,d:'Los trazos sueltos del fondo, primero los más marcados.',l:'Y una mancha muy suave alrededor para dar ambiente.'}]});
PD({id:'dnina',k:'nina',lvl:5,cat:'Personas',name:'Retrato de niña',time:'100 min',
 guia:'Un óvalo para la cara, más angosto abajo, y otro más grande para el cabello. La línea de los ojos va a la mitad de la cabeza; la nariz y la boca, más abajo.',
 lines:[["Contorno de la cara","Dibuja solo el borde de la cara: frente, mejillas y barbilla redondeada. Nada adentro todavía."],
  ["Los ojos","Sobre la línea de los ojos, dos almendras con el iris redondo."],
  ["Las cejas","Arriba de cada ojo, una ceja suave."],
  ["La nariz","La nariz se marca solo con la punta y las aletas."],
  ["La boca","La boca con una sonrisa suave."],
  ["Contorno del cabello","El borde de afuera del cabello, con ondas grandes."],
  ["Los mechones","Dentro del cabello, curvas en forma de S para los mechones."],
  ["Cuello y hombros","Abajo, el cuello y los hombros."]],
 tones:[{n:'Ojos y cejas',d:'Empieza por los ojos: primero lo más oscuro, la pupila y el borde.',m:'Luego el iris y las cejas en tono medio.',l:'Y una sombra muy suave alrededor.'},
  {n:'Cara',d:'En la cara: primero lo oscuro, las fosas nasales y la línea de los labios.',m:'Luego las sombras de las mejillas y bajo la nariz.',l:'Y la piel clara, casi sin apretar.'},
  {n:'Cabello',d:'El cabello: primero lo oscuro entre los mechones.',m:'Luego los medios.',l:'Y los mechones claros.'},
  {n:'Cuello',d:'El cuello: primero la sombra bajo la barbilla.',m:'Luego el tono medio.',l:'Y lo claro de los hombros.'},
  {n:'Fondo',d:'El fondo: primero lo oscuro junto al cabello, así resalta.',m:'Luego el tono medio.',l:'Y las rayitas suaves de afuera.'}]});
PD({id:'gatofoto',k:'gato',lvl:3,cat:'Animales',name:'Gato tricolor',time:'60 min',
 guia:'Un óvalo grande para la cabeza, una línea inclinada para los ojos y otra para la nariz. Dos triángulos marcan las orejas.',
 lines:[["Contorno de la cabeza","Dibuja solo el borde de la cabeza, con las mejillas esponjosas. Nada adentro todavía."],
  ["Las orejas","Arriba, el borde de las dos orejas grandes y en punta."],
  ["Los ojos","Los ojos, grandes y redondos: solo su contorno."],
  ["Nariz y boca","La nariz pequeña y la boca."],
  ["Las manchas","Marca el borde de las manchas oscuras de la frente y la mejilla."],
  ["El pecho","Abajo, el borde del pecho con el pelo largo."]],
 tones:[{n:'Cabeza',d:'Empieza por la cabeza: primero lo más oscuro, los ojos y las manchas oscuras.',m:'Luego los tonos medios de la frente y la mejilla.',l:'Y lo claro: el centro de la cara casi blanco.'},
  {n:'Orejas',d:'Las orejas: primero lo oscuro del borde.',m:'Luego el tono medio.',l:'Y los pelitos claros de adentro.'},
  {n:'Pecho',d:'El pecho: primero las sombras.',m:'Luego el tono medio.',l:'Y el pelo blanco.'}]});
