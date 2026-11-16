"""Prueba de un dibujo: todos los pasos sin errores (hoja todos.jpg) y el orden de los trazos de cada paso de líneas
(capturas al 20, 45, 70 y 100 % de la animación, recortadas a la parte que se dibuja: orden_0.jpg, orden_1.jpg).
Uso: python3 t_pasos.py ID NL   (NL = número del último paso de líneas; necesita el servidor en el puerto 8765)"""
import asyncio,os,sys
from playwright.async_api import async_playwright
from PIL import Image,ImageDraw
ID=sys.argv[1]; NL=int(sys.argv[2]); OUT='cap_'+ID; os.makedirs(OUT,exist_ok=True)
FR=(0.2,0.45,0.7,1.0)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':1000})
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('console',lambda m:errs.append(m.text) if m.type=='error' and 'fonts.g' not in m.text else None)
        await pg.goto('http://127.0.0.1:8765/index.html'); await pg.wait_for_timeout(900)
        await pg.evaluate(f"SND.voice=false;SND.music=false;open('{ID}',null,1)"); await pg.wait_for_timeout(1500)
        n=await pg.evaluate("cur().steps.length"); print('pasos',n)
        fins=[]
        for k in range(1,n+1):
            await pg.evaluate(f"open('{ID}',null,{k})"); await pg.wait_for_timeout(700)
            await pg.evaluate("document.getAnimations().forEach(a=>{try{a.finish()}catch(e){}})"); await pg.wait_for_timeout(400)
            await pg.evaluate("document.getAnimations().forEach(a=>{try{a.finish()}catch(e){}})"); await pg.wait_for_timeout(300)
            el=await pg.query_selector('#cv'); await el.screenshot(path=f'{OUT}/f{k}.png'); fins.append(f'{OUT}/f{k}.png')
        filas=[]
        for k in range(2,NL+1):
            await pg.evaluate(f"open('{ID}',null,{k})"); await pg.wait_for_timeout(500)
            T=await pg.evaluate("(()=>{const A=document.getAnimations();A.forEach(a=>a.pause());return A.length?Math.max(...A.map(a=>a.effect.getComputedTiming().endTime)):0})()")
            if not T: continue
            bb=await pg.evaluate("""(()=>{const g=document.querySelector('#cv g.draw');if(!g)return null;const r=g.getBoundingClientRect();return {x:Math.max(0,r.x-14),y:Math.max(0,r.y-14),width:r.width+28,height:r.height+28}})()""")
            if not bb: continue
            fila=[]
            for f in FR:
                await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.currentTime={f*T}}})"); await pg.wait_for_timeout(120)
                pth=f'{OUT}/o{k}_{int(f*100)}.png'; await pg.screenshot(path=pth,clip=bb); fila.append(pth)
            filas.append((k,fila,T))
        await b.close()
    print('errores',errs)
    ims=[Image.open(f).convert('RGB') for f in fins]; w=260; ims=[i.resize((w,round(i.height*w/i.width))) for i in ims]; h=max(i.height for i in ims)
    cols=7; rows=(len(ims)+cols-1)//cols
    S=Image.new('RGB',(cols*w+(cols+1)*6,rows*h+(rows+1)*6),(225,228,235))
    for j,im in enumerate(ims): S.paste(im,(6+(j%cols)*(w+6),6+(j//cols)*(h+6)))
    S.save(f'{OUT}/todos.jpg',quality=86)
    mitad=(len(filas)+1)//2
    for parte,(a,c) in enumerate([(0,mitad),(mitad,len(filas))]):
        rows=[]
        for k,fila,T in filas[a:c]:
            ims=[Image.open(x).convert('RGB') for x in fila]; hh=300; ims=[i.resize((max(1,round(i.width*hh/i.height)),hh)) for i in ims]
            R=Image.new('RGB',(sum(i.width for i in ims)+6*5,hh+26),(255,255,255)); d=ImageDraw.Draw(R); d.text((6,4),f'paso {k}  ({T/1000:.1f} s)',fill=(0,0,0)); x=6
            for i in ims: R.paste(i,(x,24)); x+=i.width+6
            rows.append(R)
        if not rows: continue
        W=max(r.width for r in rows); S=Image.new('RGB',(W,sum(r.height+6 for r in rows)),(225,228,235)); y=0
        for r in rows: S.paste(r,(0,y)); y+=r.height+6
        S.save(f'{OUT}/orden_{parte}.jpg',quality=84)
asyncio.run(main())
