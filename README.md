# Trazo a Trazo

App para que niños aprendan a dibujar en papel, paso a paso: primero unas guías suaves, luego la línea roja que enseña cada trazo y al final el sombreado o el color, por partes. Una voz explica cada paso y hay música de fondo.

- 36 dibujos en 5 niveles, varios a color y a lápiz.
- Funciona en computadora, tableta y celular, en modo claro u oscuro. En el celular se puede agregar a la pantalla de inicio como app.
- Abre `index.html` en el navegador o publícala (Cloudflare Pages / GitHub Pages).

`fuente/` tiene el código de la app y cómo armarla. `herramientas/` tiene el método para crear dibujos nuevos.

## Voz natural

En Ajustes se puede elegir la voz del dispositivo o la voz natural: las mismas cuatro voces de Atril (mujer y hombre de México, normal y ligera). Son modelos Piper que se generan dentro del navegador con sherpa-onnx y espeak-ng (carpeta `voz/`). Se descargan una vez y se guardan en el navegador. Licencias: modelos Piper «claude» (Apache 2.0) y «ald» (Unlicense), sherpa-onnx (Apache 2.0), espeak-ng (GPL 3.0).
