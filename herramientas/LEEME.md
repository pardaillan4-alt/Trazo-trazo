# Método "a mano" de Trazo a Trazo

- `rostro/`: caras de personas (detector de puntos de la cara + ajuste al trazo real + revisión). `python3 rostro/correr.py carpeta` (la carpeta debe tener `sq.png`).
- `animal/tonal.py`: dibujos sin cara humana: silueta y masas de tono, suavizadas como trazo de artista.
- `ejemplo_sabueso/`: el dibujo modelo completo (líneas a mano, detalles medidos, pasos y sombreado).
- `integ_v.py`: arma las hojas de imágenes y los archivos de pasos para la app.
- `continuo.py`: trazo continuo. Une los pedazos de una misma línea y ordena los trazos de cada paso: primero la orilla de cada figura, de corrido, y luego los detalles de adentro, para que la mano no brinque. `integ_v.py` lo aplica solo a los dibujos `exact`.
