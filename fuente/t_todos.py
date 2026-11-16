"""Regresión: abre todos los dibujos y recorre todos sus pasos; reporta errores de la página y dibujos que fallan."""
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1100,'height':900})
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('console',lambda m:errs.append(m.text) if m.type=='error' and 'fonts.g' not in m.text else None)
        malos=[]; pg.on('response',lambda r:malos.append((r.status,r.url)) if r.status>=400 else None)
        await pg.goto('http://127.0.0.1:8765/index.html'); await pg.wait_for_timeout(900)
        await pg.evaluate("SND.voice=false;SND.music=false")
        ids=await pg.evaluate("D.map(d=>d.id)"); fallos=[]
        for i in ids:
            try:
                await pg.evaluate(f"open('{i}',null,1)"); await pg.wait_for_timeout(250)
                n=await pg.evaluate("cur().steps.length")
                if not n: fallos.append((i,'sin pasos')); continue
                for k in range(1,n+1):
                    await pg.evaluate(f"open('{i}',null,{k})"); await pg.wait_for_timeout(35)
                await pg.wait_for_timeout(300)
                ok=await pg.evaluate("!!document.querySelector('#cv svg, #cv canvas, #cv img')")
                if not ok: fallos.append((i,'sin dibujo'))
            except Exception as e: fallos.append((i,str(e)[:120]))
        await b.close()
    print('dibujos',len(ids),'errores',errs[:10],'fallos',fallos,'404',malos[:10])
asyncio.run(main())
