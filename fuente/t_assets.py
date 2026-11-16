"""app.html con las hojas en el almacén (/_blob/...): que San Miguel pida sus hojas ahí y que se vean."""
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':900})
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        req=[]; pg.on('response',lambda r:req.append((r.status,r.url.split('8765')[-1])))
        await pg.goto('http://127.0.0.1:8765/app_test.html'); await pg.wait_for_timeout(900)
        await pg.evaluate("SND.voice=false;SND.music=false")
        n=await pg.evaluate("(open('dmiguel_lapiz',null,1),cur().steps.length)")
        for k in range(1,n+1):
            await pg.evaluate(f"open('dmiguel_lapiz',null,{k})"); await pg.wait_for_timeout(80)
        await pg.evaluate("open('dmiguel_lapiz',null,24)"); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getAnimations().forEach(a=>{try{a.finish()}catch(e){}})"); await pg.wait_for_timeout(1500)
        el=await pg.query_selector('#cv'); await el.screenshot(path='cap_assets_24.png')
        await b.close()
    print('pasos',n,'errores',errs)
    print('hojas pedidas',sorted(set(u for s,u in req if 's_miguel' in u or '_blob' in u)))
    print('fallas',[(s,u) for s,u in req if s>=400])
asyncio.run(main())
