// Saca los trazos animados de cada dibujo a vec/<id>.json (se cargan al abrir el dibujo)
const vm=require('vm'),fs=require('fs'),path=require('path');
const dir=process.argv[2], out=process.argv[3];   // argv[4]: dónde guardar la lista de miniaturas
const files=['helpers.js','render.js','parts.js',...fs.readdirSync(dir).filter(f=>/^g_.*\.js$/.test(f)).sort()];
const noop=()=>{};
const ctx={console,setTimeout,clearTimeout,setInterval,clearInterval};
ctx.window=ctx;ctx.addEventListener=noop;ctx.matchMedia=()=>({matches:false,addEventListener:noop});
ctx.document={querySelector:()=>null,querySelectorAll:()=>[],addEventListener:noop,createElement:()=>({getContext:()=>null,style:{}}),documentElement:{style:{}}};
ctx.localStorage={getItem:()=>null,setItem:noop};
vm.createContext(ctx);
const src=files.map(f=>fs.readFileSync(path.join(dir,f),'utf8')).join('\n;\n')+'\n;globalThis.__D=D;';
vm.runInContext(src,ctx,{filename:'datos.js'});
fs.mkdirSync(out,{recursive:true});
const ids=[];let tot=0;
for(const d of ctx.__D){
  const v=d.vec&&Object.keys(d.vec).length?d.vec:null, s=d.svec&&Object.keys(d.svec).length?d.svec:null;
  if(!v&&!s)continue;
  const txt=JSON.stringify({vec:v||{},svec:s||{}});
  fs.writeFileSync(path.join(out,d.id+'.json'),txt);ids.push(d.id);tot+=txt.length;
}
// miniaturas: la última imagen de cada dibujo (y de cada técnica) y dónde está dentro de su hoja
const sprOf=vm.runInContext('sprOf',ctx),th=[];
for(const d of ctx.__D){
  for(const [tk,arr] of Object.entries(d.img||{})){
    const src=arr[arr.length-1],sp=sprOf(src);
    th.push({id:d.id,tk,src,sp,h:d.h||400});
  }
}
fs.writeFileSync(process.argv[4]||path.join(out,'..','miniaturas.json'),JSON.stringify(th));
console.log(JSON.stringify({n:ctx.__D.length,conDatos:ids.length,bytes:tot,miniaturas:th.length}));
