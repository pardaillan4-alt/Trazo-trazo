#!/bin/sh
# Arma la app (app.html, index.html, vec/ y miniaturas)
cd "$(dirname "$0")" && exec python3 build/build.py
