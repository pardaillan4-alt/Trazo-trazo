# Método "a mano" de Trazo a Trazo

- `rostro/`: caras de personas (detector de puntos de la cara + ajuste al trazo real + revisión). `python3 rostro/correr.py carpeta` (la carpeta debe tener `sq.png`).
- `animal/tonal.py`: dibujos sin cara humana: silueta y masas de tono, suavizadas como trazo de artista.
- `ejemplo_sabueso/`: el dibujo modelo completo (líneas a mano, detalles medidos, pasos y sombreado).
- `integ_v.py`: arma las hojas de imágenes y los archivos de pasos para la app.
- `continuo.py`: trazo continuo. Une los pedazos de una misma línea y ordena los trazos de cada paso figura por figura: de cada figura, primero su orilla de corrido y luego los detalles de adentro (los fuertes y luego los finos). La mano termina una figura antes de pasar a la que tiene más cerca (un ojo y luego el otro, una mano y luego la otra), así no regresa a lo que ya dejó. `integ_v.py` lo aplica solo a los dibujos `exact`. Las manchitas, burbujas, gotas y mechoncitos (y las figuras chicas que quedan dentro de una grande) son detalles de la figura grande más cercana, aunque estén pegados a la orilla. Una figura de tamaño parecido a la grande (el otro ojo, la otra mano) es figura aparte, no detalle. Dentro de cada figura, los puntitos (pupilas) van al final, cuando ya está lo que los rodea.
  - Pasos compuestos: si cada trazo trae un 4.º valor (grupo), los grupos se dibujan en ese orden, cada uno completo (`gen6.py` lo pone con `suborden` en `cfg.json`).
  - `procesar_paso5(..., por_figura=False)` da el orden anterior: todas las orillas primero y después todos los detalles.
- `ejemplo_mar/`: escenas completas con dos imágenes (ballena y barco hundido; ballena y delfín). Sirve también cuando el dibujo "de líneas" viene sombreado a lápiz:
  - `trazo_mix.py TH BHT`: líneas = lo oscuro + las líneas finas por contraste local (black-hat) que son largas o cerradas; deja fuera las rayitas de textura.
  - `detalles_*.py`: correcciones medidas a mano (ojos de caricatura dibujados con círculos; fuera las rayitas de sombra en la boca, las aletas y bajo la barbilla).
  - `grupos6.py`: reparte los trazos en pasos con las zonas de `cfg_*.json`; parte en la orilla de la zona los trazos que cruzan de una parte a otra; manda las burbujas sueltas a su propio paso y las cuerdas (rectas que apuntan a la punta del mástil) al paso del mástil.
  - `gen6.py`: guías medidas sobre el dibujo (óvalos ajustados a cada parte, curvas y rectas) y sombreado por regiones; la silueta de cada región no se sale por las rendijas del contorno.
  - `integ_mar.py`: integra las dos versiones (color y lápiz) de cada dibujo. `cmp.py`, `ver_idx.py` y `grid_trazos.py`: revisión de cerca.
- `ejemplo_sagrado/`: Sagrado Corazón a lápiz (dibujo de líneas + imagen gris). Tiene las versiones más nuevas de `gen6.py` y `grupos6.py` (sirven también con los `cfg` del mar):
  - `detalles.py`: las pupilas (manchas negras con brillo) se vuelven un círculo medido sobre la mancha real.
  - `grupos6.py`: los rayos de luz son rectas que apuntan al centro del corazón (`rayos`, con `ang`: la tolerancia crece con la distancia). `antes_rayos`: zonas que nunca son rayo (la cruz, los dedos).
  - `gen6.py`: `OW` (imágenes más chicas para dibujos altos); regiones con polígonos (`mas`, `menos`, `silueta`, `mas_silueta`), solo dentro del dibujo; `fondo_papel` (el blanco de la imagen toma el color del papel, para que al sombrear no aparezcan cuadros más blancos); `suborden` (las partes de un paso compuesto en orden: corazón, corona, llamas y cruz).
  - `integ_sagrado.py`: textos de los pasos y armado.
- `ejemplo_divina/`: Divina Misericordia, con tres imágenes: dibujo de líneas, imagen gris (versión a lápiz) e imagen a color (versión a color). Usa `gen6.py` y `grupos6.py` de `ejemplo_sagrado/` (la versión más nueva, sirve para los dos):
  - `detalles.py`: las pupilas son puntos rellenos medidos sobre la mancha real; se quitan las motitas sueltas de la franja donde la luz borra los rayos.
  - `cfg.json`: `rayos` puede ser una lista (la luz corta del corazón y los rayos grandes, cada uno con su paso); `desv` deja fuera los pliegues que se curvan. `rayos_sueltos`: los pedacitos de rayo que la luz dejó sueltos van con los rayos (si siguen la línea de un rayo o quedan fuera de la figura).
  - Letras con contorno: `letras.encerradas` las reconoce por el hueco blanco que encierra cada letra; los trazos que siguen la orilla de una letra y luego se van por un rayo se parten ahí. `letras_sub.py` hace un polígono por letra en `suborden`, para que se dibujen una por una, de izquierda a derecha.
  - Sombreado: `mas_color` agrega a una región lo que tiene su color (la piel de manos y pies), dentro de polígonos ajustados a cada mano y pie (`piel_pol.py`), sin huecos ni fondo colado. `d_blur` suaviza la oscuridad de una región (el fondo con textura se descubre en manchas y no en puntitos). `suave` desvanece la orilla de una región donde no tiene contorno (la túnica bajo la luz). Con fondo oscuro todo el cuadro es dibujo.
  - `integ_divina.py`: textos y armado de las dos versiones (`ddivina` y `ddivina_lapiz`).
- `vec.py` y `furlib2.py`: los usan todos los `gen*.py`; cópialos a la carpeta del dibujo.
- Para armar la app después de agregar un dibujo: ver `fuente/LEEME.md` (`sh assemble.sh` crea `index.html`, `app.html`, `vec/` y las miniaturas).

## Jirafita y perezoso (noviembre 2026)
- `ejemplo_jirafita/`: la jirafita no trae dibujo de líneas; las líneas salen de la imagen gris con
  `trazo_mix.py 80 45 4 60` (el 3.er valor separa el rayado de sombra pegado al contorno; el 4.o es el largo mínimo de las líneas finas).
  Las manchas se miden aparte con `manchas.py` y van completas a su paso con `"fijos": {"manchas.npy": "Las manchas"}` en `cfg.json`.
  Los ojos negros se rellenan con contornos hacia adentro (`detalles.py`).
- En las regiones del sombreado (`gen6.py`): `sin_cielo` deja el cielo para el final y `objeto` limita la región a los colores de esa parte
  (hojas verdes, troncos cafés, orillas), para que no se vean cuadros de cielo alrededor de los árboles y las mariposas.
- `ejemplo_perezoso/`: pupilas y fosas medidas a mano y rellenas (`detalles.py`); el tronco va en una zona que sigue su curva.
- `continuo.py`: dentro de cada paso, primero las líneas largas y fuertes, luego las medianas y al final los detalles finos (`niveles`).

## Leoncito (noviembre 2026)
- `ejemplo_leoncito/`: líneas del dibujo de líneas con `trazo_mix.py 140`; ojos y fosas de la nariz rellenos (`detalles.py`).
- `mascara_leon.py` hace la silueta exacta del león con el dibujo de líneas. Sirve dos veces:
  `"recorte"` en `cfg.json` (`grupos6.py`) para que las zonas del león no tomen el pasto de junto,
  y `"mascara": ["leon_mask.png", 2]` en la región del sombreado (`gen6.py`), para que no quede un halo de color alrededor.
- `fuente/build/dedup_hojas.py` (lo corre `build.py`): la versión a color y la de lápiz comparten las hojas de las líneas, que salen idénticas; se guarda una sola copia.

## Virgen Milagrosa (noviembre 2026)
- `ejemplo_milagrosa/`: líneas del dibujo de líneas con `trazo_mix.py 170`. `detalles.py` quita la firma «Corazón de Paúl»
  (máscara de las letras con huecos) y redibuja los ojos a mano (párpados, pliegue, iris recortado y pupila rellena).
- Zona tipo anillo en `grupos6.py`: `["a", [cx,cy], r_adentro, r_afuera]`. La aureola se escoge por forma (trazos que siguen
  un círculo alrededor de la cabeza) y va completa a su paso con `"fijos"`.
- Las imágenes del dibujo se guardan a 720 px (`"OW": 720`) para que pesen menos.
- `grid_zona.py` y `ver_grupos.py`: acercamientos con cuadrícula y con las partes de colores.
- `fuente/t_pasos.py ID NL` (orden de los trazos y hoja de pasos) y `fuente/t_todos.py` (todos los dibujos, sin errores).
- Espacio del artifact: `render.js` ya acepta un mapa `ASSET` (hojas en el almacén de imágenes del artifact,
  `build/assets_artifact.json`); solo se usa en `app.html`, GitHub sigue con `img/`.

## San Miguel Arcángel (noviembre 2026)
- `ejemplo_miguel/`: líneas del dibujo de líneas con `trazo_mix.py 205` (umbral claro, para que salgan las rayitas finas
  de las plumas y los adornos). `detalles.py` redibuja los ojos a mano.
- `mascaras.py`: máscaras del sombreado con los huecos blancos del dibujo de líneas, repartidos por zona (San Miguel, alas,
  demonio y roca); lo conectado con la orilla es el fondo. La capa de la imagen a lápiz es más grande que la del dibujo
  de líneas: lo oscuro pegado a San Miguel también va con él.
- Almacén de imágenes del artifact: el artifact ya casi no tiene espacio para archivos (límite 256 MB por versión, las voces
  ocupan la mayor parte). Desde San Miguel, las hojas de cada dibujo nuevo se suben al almacén (`Artifact` con `asset: true`),
  cada dirección `/_blob/<id>` se anota en `fuente/build/assets_artifact.json` y `build.py` las pone en `app.html`
  (mapa `ASSET` de `render.js`). GitHub (`index.html`) sigue usando `img/`. `fuente/t_assets.py` lo prueba en local.
