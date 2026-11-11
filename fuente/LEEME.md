# Fuentes de la app

- `head2.html` (estilos y colores, claro y oscuro), `body2.html` y `defs.html`: la página.
- `helpers.js`, `render.js`, `parts.js`, `audio.js`: el motor (dibujo de cada paso, trazo animado, voz y música).
- `g_partes*.js` y `g_zvec*.js`: los dibujos (pasos, textos, hojas de imágenes y trazos).
- `ui.js`: la interfaz (inicio, galería, estudio de dibujo, ajustes y festejo).
- `build/`: el armado. `fuentes.py` prepara las letras incrustadas (`fuentes.css`).

## Armar la app

```sh
cp -r fuente trabajo && cd trabajo && ln -s ../img img
sh assemble.sh
```

Eso deja:
- `index.html`: la app completa (va a la raíz del repo, Cloudflare la publica);
- `app.html`: la misma app para el artifact de claude.ai (sin `<head>`);
- `vec/<id>.json`: los trazos animados de cada dibujo, que se cargan al abrirlo;
- `img/t_<id>.webp`: las miniaturas de la galería.

Copia `index.html`, `vec/` y las miniaturas nuevas al repo. En el artifact se publican `app.html`, `vec/*.json`, `img/t_*.webp` y las hojas `img/s_*.webp` nuevas.
