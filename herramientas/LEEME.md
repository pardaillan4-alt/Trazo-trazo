# Método "a mano" de Trazo a Trazo

- `rostro/`: caras de personas (detector de puntos de la cara + ajuste al trazo real + revisión). `python3 rostro/correr.py carpeta` (la carpeta debe tener `sq.png`).
- `animal/tonal.py`: dibujos sin cara humana: silueta y masas de tono, suavizadas como trazo de artista.
- `ejemplo_sabueso/`: el dibujo modelo completo (líneas a mano, detalles medidos, pasos y sombreado).
- `integ_v.py`: arma las hojas de imágenes y los archivos de pasos para la app.
- `continuo.py`: trazo continuo. Une los pedazos de una misma línea y ordena los trazos de cada paso: primero la orilla de cada figura, de corrido, y luego los detalles de adentro, para que la mano no brinque. `integ_v.py` lo aplica solo a los dibujos `exact`. Las manchitas, burbujas, gotas y mechoncitos (y las figuras chicas que quedan dentro de una grande) se dejan para el final, aunque estén pegados a la orilla.
- `ejemplo_mar/`: escenas completas con dos imágenes (ballena y barco hundido; ballena y delfín). Sirve también cuando el dibujo "de líneas" viene sombreado a lápiz:
  - `trazo_mix.py TH BHT`: líneas = lo oscuro + las líneas finas por contraste local (black-hat) que son largas o cerradas; deja fuera las rayitas de textura.
  - `detalles_*.py`: correcciones medidas a mano (ojos de caricatura dibujados con círculos; fuera las rayitas de sombra en la boca, las aletas y bajo la barbilla).
  - `grupos6.py`: reparte los trazos en pasos con las zonas de `cfg_*.json`; parte en la orilla de la zona los trazos que cruzan de una parte a otra; manda las burbujas sueltas a su propio paso y las cuerdas (rectas que apuntan a la punta del mástil) al paso del mástil.
  - `gen6.py`: guías medidas sobre el dibujo (óvalos ajustados a cada parte, curvas y rectas) y sombreado por regiones; la silueta de cada región no se sale por las rendijas del contorno.
  - `integ_mar.py`: integra las dos versiones (color y lápiz) de cada dibujo. `cmp.py`, `ver_idx.py` y `grid_trazos.py`: revisión de cerca.
- Para armar la app después de agregar un dibujo: ver `fuente/LEEME.md` (`sh assemble.sh` crea `index.html`, `app.html`, `vec/` y las miniaturas).
