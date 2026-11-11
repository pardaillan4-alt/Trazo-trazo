/* Dibujos a partir de fotos: perezoso de peluche y velero */
(()=>{
const im=(id,t)=>[1,2,3,4,5,6,7,8].map(i=>`img/${id}_${t}_${i}.webp`);
add({id:'perezoso',lvl:2,cat:'Animales',name:'Perezoso de peluche',time:'45 min',sh:'Dibujo realista a partir de una foto',
 img:{lapiz:im('pere','lapiz')},
 steps:[
  {t:'Encaja las formas',x:'Empieza con un óvalo grande para la cabeza y otro todavía más grande para el cuerpo. Agrega un círculo para la patita de la izquierda y otro para el pie de abajo. Las manchas de los ojos son dos óvalos inclinados. Todo muy suave.'},
  {t:'La silueta',x:'Dibuja el contorno del peluche sobre las guías: la cabeza redonda, el bracito levantado, la panza y los pies. Como es de peluche, el borde es suave y peludito; hazlo con líneas cortas.'},
  {t:'Ojos, nariz y manchas',x:'Dibuja los ojos como bolitas dentro de las manchas y la nariz como otra bolita entre ellos. Marca el borde de la cara blanca y de las manchas oscuras.'},
  {t:'La primera capa',m:'base',x:'Con el lápiz acostado, sombrea suave todo el cuerpo y las manchas de los ojos. La cara se queda blanca. Haz trazos cortos y en distintas direcciones, como el pelo de un peluche.',chip:{lapiz:[['#B9B9C0','Lápiz HB']]}},
  {t:'Volumen',m:'mid',x:'Con un 2B, oscurece el cuerpo, sobre todo los lados y debajo de la cabeza. Así se ve redondito y suavecito.',chip:{lapiz:[['#8A8A96','Lápiz 2B']]}},
  {t:'Las manchas oscuras',m:'dark',x:'Con el 4B, rellena bien oscuras las manchas de los ojos y las sombras entre el brazo y la panza.',chip:{lapiz:[['#4A4A55','Lápiz 4B']]}},
  {t:'Ojos y pelitos',m:'detail',x:'Rellena los ojos y la nariz de negro y agrega pelitos sueltos en el borde del cuerpo y de la cabeza.',chip:{lapiz:[['#2E2E36','Punta fina']]}},
  {t:'Brillos',m:'light',x:'Con la goma en punta, deja un puntito de brillo en cada ojo y en la nariz, y limpia la cara blanca. ¡Listo!',chip:{lapiz:[['#FFFFFF','Goma moldeable']]}}
 ]});
add({id:'velero',lvl:1,cat:'Paisajes',name:'El velero al atardecer',time:'35 min',sh:'De una ilustración: formas limpias y color',
 img:{lapiz:im('velero','lapiz'),acuarela:im('velero','acuarela')},
 steps:[
  {t:'Horizonte y sol',x:'Traza la línea del horizonte un poco abajo de la mitad. Encima, un círculo grande para el sol, cortado por el horizonte. Marca el casco del barco, el mástil y las velas como triángulos.'},
  {t:'Barco, marinero y olas',x:'Sobre las guías, dibuja el casco redondeado, las dos velas y al marinero que se inclina hacia atrás jalando la cuerda. Arriba, las gaviotas como “v” abiertas; abajo, unas olitas.'},
  {t:'Los detalles',x:{lapiz:'Agrega las cuerdas, la cara y la ropa del marinero, y el borde de cada vela. Revisa que el mástil quede recto.',acuarela:'Agrega las cuerdas y los detalles del marinero. Dibuja muy suave: la acuarela es transparente y las líneas se notan.'}},
  {t:'Cielo y mar',m:'base',x:{lapiz:'Sombrea el cielo con trazos horizontales muy suaves, sin tocar el sol: el sol se queda blanco. Después el mar, un poco más oscuro.',acuarela:'Moja el papel y pinta el cielo con un crema muy diluido, rodeando el sol: el sol es el papel blanco. Luego el mar con un ocre claro.'},
   chip:{lapiz:[['#B9B9C0','Lápiz HB']],acuarela:[['#F6E6C6','Crema diluido'],['#EBCB8C','Ocre claro']]}},
  {t:'Velas y marinero',m:'mid',x:{lapiz:'Sombrea las velas: la amarilla clarita y la café más fuerte. También al marinero y la sombra bajo el barco.',acuarela:'Pinta la vela amarilla, la vela café y el casco con un primer tono claro.'},
   chip:{lapiz:[['#8A8A96','Lápiz 2B']],acuarela:[['#E2B42A','Amarillo'],['#7E4A2C','Café'],['#2F6A80','Azul petróleo']]}},
  {t:'Los oscuros',m:'dark',x:{lapiz:'El casco va muy oscuro, casi negro. Repasa la vela café y las olitas.',acuarela:'Con más pintura y menos agua, oscurece el casco y la vela café. Pinta la ropa del marinero.'},
   chip:{lapiz:[['#4A4A55','Lápiz 4B']],acuarela:[['#0E4A5E','Azul petróleo oscuro'],['#5E7A44','Verde']]}},
  {t:'Líneas finas',m:'detail',x:{lapiz:'Con la punta bien afilada: las cuerdas, las gaviotas y el borde de las velas.',acuarela:'Con un pincel fino: las cuerdas, las gaviotas y las olitas cafés.'},
   chip:{lapiz:[['#2E2E36','Punta fina']],acuarela:[['#2A2A2A','Pincel fino']]}},
  {t:'Luz',m:'light',x:{lapiz:'Con la goma, limpia el sol y abre unos brillos en el agua. ¡Listo!',acuarela:'Revisa los bordes, deja secar bien y ¡listo! Si quieres, pon brillitos blancos en el agua con témpera.'},
   chip:{lapiz:[['#FFFFFF','Goma moldeable']],acuarela:[['#FFFFFF','Blanco (témpera)']]}}
 ]});
})();
