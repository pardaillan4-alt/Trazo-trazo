/* Interfaz: inicio (portada y galería), estudio de dibujo, ajustes y festejo */
const LV=[
 {n:1,t:'Primeros trazos',d:'Formas sencillas y mucho color. Para soltar la mano.'},
 {n:2,t:'Tomando forma',d:'Más detalle en el pelo, las plumas y las hojas.'},
 {n:3,t:'Con carácter',d:'Miradas con brillo, texturas y sombras que dan volumen.'},
 {n:4,t:'Más realismo',d:'Proporciones y luz más cuidadas, como en un dibujo de lápiz.'},
 {n:5,t:'Maestros',d:'Dibujos largos y detallados. Para tener paciencia y disfrutar.'}
];
const CATS=['Animales','Personas','Paisajes','Juguetes'];
const NUEVOS=new Set(['ddivina','dsagrado_lapiz','dballena5','ddelfin5','dgatito5','dperrito5','djirafa']);
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const app=$('#app'),EST=$('#estudio'),CAPAS=$('#capas');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const sinAcento=s=>s.normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
const RM=()=>typeof matchMedia!=='undefined'&&matchMedia('(prefers-reduced-motion: reduce)').matches;
const sv=(p,extra='')=>`<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${extra}>${p}</svg>`;
const TACHA='<path class="tachado" d="M3.5 3.5l17 17"/>';
const IC={
 back:sv('<path d="M15 5l-7 7 7 7"/>',' stroke-width="2.4"'),
 voz:sv('<circle cx="9" cy="8" r="3.4"/><path d="M3 20c.4-3.6 2.8-5.8 6-5.8s5.6 2.2 6 5.8"/><path d="M16.5 5.8a4 4 0 0 1 0 5.4M19.3 3.4a7.5 7.5 0 0 1 0 10.2"/>'+TACHA),
 mus:sv('<path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>'+TACHA),
 aju:sv('<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>'),
 mat:sv('<path d="M15.5 4.5l4 4L9 19l-5 1 1-5z"/><path d="M13.5 6.5l4 4"/>'),
 enfoque:sv('<path d="M4 14v6h6M20 10V4h-6M4 20l7-7M20 4l-7 7"/>'),
 full:sv('<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',' stroke-width="2.2"'),
 close:sv('<path d="M6 6l12 12M18 6L6 18"/>',' stroke-width="2.4"'),
 prev:sv('<path d="M15 5l-7 7 7 7"/>',' stroke-width="2.6"'),
 next:sv('<path d="M9 5l7 7-7 7"/>',' stroke-width="2.6"'),
 zin:sv('<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L20 20M10.5 7.5v6M7.5 10.5h6"/>',' stroke-width="2.3"'),
 zout:sv('<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L20 20M7.5 10.5h6"/>',' stroke-width="2.3"'),
 zfit:sv('<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',' stroke-width="2.2"'),
 pause:'<svg class="ic" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="5" width="4" height="14" rx="1.2"/><rect x="14" y="5" width="4" height="14" rx="1.2"/></svg>',
 play:'<svg class="ic" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13a1 1 0 0 0 1.5.9l10-6.5a1 1 0 0 0 0-1.7l-10-6.5A1 1 0 0 0 8 5.5z"/></svg>',
 replay:sv('<path d="M4 12a8 8 0 1 0 2.5-5.8"/><path d="M4 4v5h5"/>',' stroke-width="2.2"'),
 txt:sv('<path d="M6 9l6 6 6-6"/>',' stroke-width="2.4"'),
 check:sv('<path d="M5 12.5l4.2 4.2L19 7"/>',' stroke-width="2.8"'),
 reloj:sv('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>'),
 pasos:sv('<path d="M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01"/>',' stroke-width="2.2"'),
 buscar:sv('<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4 4"/>',' stroke-width="2.2"'),
 oir:sv('<path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7M18.5 5.5a9 9 0 0 1 0 13"/>'),
 menu:'<svg class="ic" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="5.5" cy="12" r="1.9"/><circle cx="12" cy="12" r="1.9"/><circle cx="18.5" cy="12" r="1.9"/></svg>'
};
const FS_OK=!!(document.fullscreenEnabled||document.webkitFullscreenEnabled);

/* ---------- estado guardado en este navegador ---------- */
const KEY='trazo-a-trazo2';
const st={view:'home',id:null,tech:'lapiz',k:1,fin:false,cat:'Todos',q:'',min:false,done:{},last:null,ver:{},t0:0,tema:'auto'};
try{
  const s=JSON.parse(localStorage.getItem(KEY)||'{}');
  if(s.done&&typeof s.done==='object')st.done=s.done;
  if(s.last&&s.last.id)st.last=s.last;
  if(s.ver&&typeof s.ver==='object')st.ver=s.ver;
  if(['auto','light','dark'].includes(s.tema))st.tema=s.tema;
}catch(e){}
try{const v=+localStorage.getItem('trazo-spd');if(v)SPEED=v}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify({done:st.done,last:st.last,ver:st.ver,tema:st.tema}))}catch(e){}};
function aplicarTema(){
  const r=document.documentElement;
  if(st.tema==='auto'){if(r.dataset.temaApp){r.removeAttribute('data-theme');delete r.dataset.temaApp}}
  else{r.setAttribute('data-theme',st.tema);r.dataset.temaApp='1'}
}

/* ---------- dibujos y sus versiones (a color, a lápiz, acuarela) ---------- */
const byId=id=>D.find(d=>d.id===id);
const cur=()=>byId(st.id);
const MEDIO={color:'A color',lapiz:'A lápiz',acuarela:'Acuarela'};
const VLAB={color:'Color',lapiz:'Lápiz',acuarela:'Acuarela'};
const medioDe=(id,tk)=>tk==='acuarela'?'acuarela':((META[id]||{}).col||0)>=.15?'color':'lapiz';
const thumb=(id,tk)=>{const m=META[id];return m&&m.t?(m.t[tk]||m.t.lapiz):''};
const GRUPOS=[],GDE={};
D.forEach(d=>{
  if(/_lapiz$/.test(d.id)&&byId(d.id.replace(/_lapiz$/,'')))return;
  const g={key:d.id,base:d,name:d.name,vers:[]},par=byId(d.id+'_lapiz');
  if(par)g.vers.push({id:d.id,tk:'lapiz',m:medioDe(d.id,'lapiz')},{id:par.id,tk:'lapiz',m:medioDe(par.id,'lapiz')});
  else Object.keys(d.img||{lapiz:1}).forEach(tk=>g.vers.push({id:d.id,tk,m:medioDe(d.id,tk)}));
  GRUPOS.push(g);g.vers.forEach(v=>GDE[v.id]=g);
});
const isDone=v=>(st.done[v.id]||[]).includes(v.tk);
const grupoHecho=g=>g.vers.some(isDone);
const versionActual=()=>{const g=GDE[st.id];return g?g.vers.find(v=>v.id===st.id&&v.tk===effT(cur()))||g.vers.find(v=>v.id===st.id):null};

/* trazos animados de cada dibujo: se cargan al abrirlo */
const VCARGA={};
function ensureVec(d){
  if(!d||d._vec||typeof VECF==='undefined'||!VECF.has(d.id))return Promise.resolve();
  return VCARGA[d.id]||(VCARGA[d.id]=fetch('vec/'+d.id+'.json').then(r=>{if(!r.ok)throw new Error(r.status);return r.json()})
    .then(j=>{d.vec=j.vec||{};d.svec=j.svec||{};d._vec=1}).catch(()=>{d._vec=1}));
}

/* ---------- aviso corto ---------- */
let avisoT=0;
function aviso(t){const a=$('#aviso');a.textContent=t;a.classList.add('ver');clearTimeout(avisoT);avisoT=setTimeout(()=>a.classList.remove('ver'),1800)}

/* ---------- inicio ---------- */
const medidor=n=>`<span class="medidor" role="img" aria-label="Dificultad ${n} de 5">${[1,2,3,4,5].map(i=>`<i class="${i<=n?'on':''}"></i>`).join('')}</span>`;
function portadaHTML(){
  const L=st.last&&!st.last.fin&&byId(st.last.id)?st.last:null;
  let cta;
  if(L){
    const d=byId(L.id),g=GDE[d.id]||{name:d.name},n=d.steps.length,pc=Math.round(100*(L.k-1)/n),v=(g.vers||[]).length>1?' '+MEDIO[medioDe(d.id,L.tk||'lapiz')].toLowerCase():'';
    cta=`<div class="seguir"><img src="${thumb(d.id,L.tk||'lapiz')}" alt=""><div style="min-width:0"><b>${esc(g.name)}</b><small>Vas en el paso ${L.k} de ${n}${esc(v)}</small><div class="barrita"><i style="width:${pc}%"></i></div></div><button class="btn" data-a="seguir">Continuar</button></div>
      <div class="acciones"><button class="btn sec" data-a="ir-galeria">Elegir otro dibujo</button></div>`;
  }else{
    cta=`<div class="acciones"><button class="btn" data-a="open" data-id="dabeja">Empezar con la abejita</button><button class="btn sec" data-a="ir-galeria">Ver todos los dibujos</button></div>`;
  }
  const dm=byId('ddelfin5');
  return `<section class="portada" aria-labelledby="tit">
    <div>
      <h1 id="tit">Aprende a dibujar trazo a trazo</h1>
      <p class="lede">Unas guías suaves acomodan el dibujo. La línea roja te enseña dónde va cada trazo, y luego sombreas o coloreas por partes. Una voz te explica cada paso.</p>
      ${cta}
    </div>
    ${dm?`<figure class="demo" id="demo">
      <span class="nota" aria-hidden="true"><span>la línea roja es tu siguiente trazo</span><svg viewBox="0 0 58 46" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M52 4C38 5 24 14 15 36"/><path d="M9 28l6 9 8-6"/></svg></span>
      <div class="demo-hoja"><svg class="cv" id="demoCv" viewBox="0 0 400 ${dm.h||400}" role="img" aria-label="Ejemplo: guías suaves y líneas rojas que se van dibujando"></svg>
        <img id="demoFin" src="${thumb('ddelfin5','lapiz')}" alt="La ballena y el delfín, terminado"></div>
      <figcaption id="demoCap"><span class="demo-fase">Ejemplo</span><b>La ballena y el delfín</b></figcaption>
    </figure>`:''}
  </section>
  <ol class="como" aria-label="Cómo funciona">
    <li><svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="22" cy="24" r="14" fill="none" stroke="var(--guia)" stroke-width="2" stroke-dasharray="4 4"/><path d="M8 24h28M22 10v28" stroke="var(--guia)" stroke-width="2" stroke-linecap="round" opacity=".55"/></svg>
      <div><h3>Guías</h3><p>Círculos y líneas muy suaves para que todo quede en su lugar.</p></div></li>
    <li><svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="22" cy="24" r="14" fill="none" stroke="var(--borde)" stroke-width="2"/><path d="M7 33c6-16 16-22 32-21" fill="none" stroke="var(--linea-roja)" stroke-width="3.4" stroke-linecap="round"/></svg>
      <div><h3>Líneas</h3><p>La línea roja te enseña el trazo que sigue. Tú lo copias en tu hoja.</p></div></li>
    <li><svg viewBox="0 0 48 48" aria-hidden="true"><path d="M10 36l14-24M16 38l14-24M22 40l14-24M28 40l10-17" stroke="var(--grafito-2)" stroke-width="2.2" stroke-linecap="round"/><circle cx="34" cy="14" r="7" fill="var(--amarillo)"/></svg>
      <div><h3>Sombreado o color</h3><p>Parte por parte, de lo más oscuro a lo más claro.</p></div></li>
  </ol>`;
}
const cuenta=c=>GRUPOS.filter(g=>c==='Todos'||g.base.cat===c).length;
function galeriaHTML(){
  return `<section class="galeria" id="galeria" aria-labelledby="galTit">
    <div class="gal-cab"><h2 id="galTit">Dibujos<small>${GRUPOS.length} para elegir</small></h2>
      <label class="buscar"><span class="solo-lectores">Buscar un dibujo</span>${IC.buscar}<input id="q" type="search" placeholder="Busca: gato, Virgen, ballena…" value="${esc(st.q)}" autocomplete="off" enterkeyhint="search"></label></div>
    <div class="filtros" role="group" aria-label="Tipo de dibujo">${['Todos',...CATS].filter(c=>cuenta(c)).map(c=>`<button class="chip" data-a="cat" data-c="${c}" aria-pressed="${c===st.cat}">${c}<small>${cuenta(c)}</small></button>`).join('')}</div>
    <div id="niveles"></div>
  </section>
  <footer class="pie"><span>Trazo a Trazo</span><span>Dibuja en papel, con lápiz y goma, siguiendo cada paso.</span></footer>`;
}
function obraHTML(g){
  const i=Math.min(st.ver[g.key]||0,g.vers.length-1),v=g.vers[i],d=byId(v.id),M=META[v.id]||{},t=thumb(v.id,v.tk);
  return `<article class="obra" data-g="${g.key}">
    <button class="abrir" data-a="open" data-id="${v.id}" data-tk="${v.tk}" aria-label="Abrir ${esc(g.name)}${g.vers.length>1?', '+MEDIO[v.m].toLowerCase():''}">
      <span class="hojita">${t?`<img src="${t}" alt="" loading="lazy" decoding="async"${M.w?` width="${M.w}" height="${M.h}"`:''}>`:''}${grupoHecho(g)?`<span class="sello hecho">${IC.check}Terminado</span>`:''}${NUEVOS.has(g.key)?'<span class="sello nuevo">Nuevo</span>':''}</span>
      <span class="obra-tit">${esc(g.name)}</span>
      <span class="obra-meta"><span>${IC.pasos}${d.steps.length} pasos</span><span>${IC.reloj}${esc(d.time)}</span></span>
    </button>
    ${g.vers.length>1?`<div class="versiones" role="group" aria-label="Versión">${g.vers.map((x,j)=>`<button data-a="ver" data-g="${g.key}" data-i="${j}" aria-pressed="${j===i}"><span class="punto-medio ${x.m}"></span>${VLAB[x.m]}</button>`).join('')}</div>`
      :`<span class="medio"><span class="punto-medio ${v.m}"></span>${MEDIO[v.m]}</span>`}
  </article>`;
}
function pintarObras(){
  const q=sinAcento(st.q.trim()),cont=$('#niveles');if(!cont)return;
  const gs=GRUPOS.filter(g=>(st.cat==='Todos'||g.base.cat===st.cat)&&(!q||sinAcento(g.name+' '+g.base.cat).includes(q)));
  let h='';
  LV.forEach(l=>{
    const xs=gs.filter(g=>g.base.lvl===l.n);if(!xs.length)return;
    h+=`<section class="nivel" aria-labelledby="nv${l.n}"><div class="nivel-cab">${medidor(l.n)}<h3 id="nv${l.n}"><span>Nivel ${l.n}</span> ${l.t}</h3><p>${l.d}</p></div>
      <div class="obras">${xs.map(obraHTML).join('')}</div></section>`;
  });
  cont.innerHTML=h||`<div class="vacio"><b>No hay dibujos con “${esc(st.q)}”</b>Prueba con otra palabra o elige “Todos”.</div>`;
}
function actualizarAvance(){
  const a=$('#avance');if(!a)return;
  const n=GRUPOS.filter(grupoHecho).length,T=GRUPOS.length;
  if(!n){a.hidden=true;return}
  const C=2*Math.PI*11,p=n/T;
  a.hidden=false;a.innerHTML=`<svg class="anillo" viewBox="0 0 26 26" aria-hidden="true"><circle class="a-f" cx="13" cy="13" r="11"/><circle class="a-v" cx="13" cy="13" r="11" stroke-dasharray="${(C*p).toFixed(1)} ${C.toFixed(1)}"/></svg><span class="txt">${n} de ${T} terminados</span><span class="txt-c">${n}/${T}</span>`;
  a.setAttribute('aria-label',`${n} de ${T} dibujos terminados`);
}
function home(){
  st.view='home';
  app.innerHTML=portadaHTML()+galeriaHTML();
  pintarObras();actualizarAvance();demoIniciar();
}

/* ---------- demostración de la portada: guías, líneas rojas y el dibujo terminado ---------- */
const DEMO={on:false,timer:0,vis:true,io:null};
function demoParar(){DEMO.on=false;clearTimeout(DEMO.timer);if(DEMO.io){DEMO.io.disconnect();DEMO.io=null}}
function demoIniciar(){
  demoParar();
  const d=byId('ddelfin5'),fig=$('#demo');if(!d||!fig||RM())return;
  DEMO.on=true;DEMO.vis=true;
  if('IntersectionObserver' in window){DEMO.io=new IntersectionObserver(es=>{DEMO.vis=es[0].isIntersecting});DEMO.io.observe(fig)}
  ensureVec(d).then(()=>{if(DEMO.on)DEMO.timer=setTimeout(()=>demoPaso(1),1400)});
}
function demoPaso(k){
  clearTimeout(DEMO.timer);if(!DEMO.on)return;
  const d=byId('ddelfin5'),cv=$('#demoCv'),fin=$('#demoFin'),cap=$('#demoCap');if(!cv||!fin)return;
  if(!DEMO.vis||document.hidden||st.view!=='home'){DEMO.timer=setTimeout(()=>demoPaso(k),900);return}
  if(k>3){
    fin.classList.remove('fuera');
    cap.innerHTML=`<span class="demo-fase">Paso ${d.steps.length}</span><b>Terminado, con color</b>`;
    DEMO.timer=setTimeout(()=>demoPaso(1),4200);return;
  }
  const html=scene(d,'lapiz',k,false,false);cv.innerHTML=html;fin.classList.add('fuera');
  cap.innerHTML=`<span class="demo-fase">Paso ${k}</span><b>${esc(d.steps[k-1].t)}</b>`;
  let t=0;html.replace(/animation:dr ([\d.]+)s linear ([\d.]+)s/g,(m,a,b)=>{t=Math.max(t,+a+ +b);return m});
  DEMO.timer=setTimeout(()=>demoPaso(k+1),k===1?2600:(t+1.6)*1000);
}

/* ---------- estudio ---------- */
const effT=d=>d&&d.img&&!d.img[st.tech]?'lapiz':st.tech;
function fasePaso(d,i){const s=d.steps[i-1];if(!s)return 'tono';if(!s.m&&!s.T)return i===1?'guias':'lineas';if(/^para terminar/i.test(s.t))return 'final';return 'tono'}
function faseLab(f,medio){return f==='guias'?'Guías':f==='lineas'?'Líneas':f==='final'?'Final':medio==='lapiz'?'Sombreado':'Color'}
function stepInfo(d,k){
  const T=TECH[effT(d)],s=d.steps[k-1];
  if(d.img){const tone=!!s.m,x=typeof s.x==='string'?s.x:(s.x[effT(d)]||s.x.lapiz);return{tone,t:tone&&!s.t.includes(':')&&T.pre[s.m]&&T.pre[s.m].toLowerCase()!==s.t.toLowerCase()?`${T.pre[s.m]}: ${s.t}`:s.t,x,s}}
  const tone=!!s.T;
  return tone?{tone,t:`${T.pre[s.m]}: ${s.t}`,x:s.x+' '+T.how[s.m],s}:{tone,t:s.t,x:s.x,s};
}
const PRES={dark:3,mid:2,detail:2,base:1,light:1};
function chipsPaso(d,si,f,medio){
  if(!si.tone)return '';
  const s=si.s,tk=effT(d);let a='';
  if(medio==='color'&&f!=='final')a=`<span class="mat"><i class="color"></i>Lápices de colores</span>`;
  else if(s.chip){const ch=s.chip[tk]||s.chip.lapiz||[];a=ch.map(([c,n])=>`<span class="mat"><i style="background:${c}"></i>${esc(n)}</span>`).join('')}
  else if(TECH[tk].chip&&TECH[tk].chip[s.m])a=`<span class="mat"><i style="background:#8A8A96"></i>${TECH[tk].chip[s.m]}</span>`;
  const p=PRES[s.m]||1,pt=['','Presión suave','Presión media','Presión fuerte'][p];
  return a+`<span class="mat presion"><i aria-hidden="true">${[1,2,3].map(j=>`<b class="${j<=p?'on':''}" style="height:${4+j*3}px"></b>`).join('')}</i>${pt}</span>`;
}
const INTRO=['Muy bien.','Perfecto.','Vamos con calma.','Listo.','Sigamos.','Qué bien va quedando.','Sin prisa.'];
function spoken(){
  const d=cur(),g=GDE[d.id]||{name:d.name};
  if(st.fin){const o=otraVersion();return `¡Lo lograste! Mira qué bonito quedó tu dibujo.${o?` Si quieres, ahora puedes hacerlo ${MEDIO[o.m].toLowerCase()}.`:''}`}
  const si=stepInfo(d,st.k),tot=d.steps.length;
  const head=st.k===1?`Hola, vamos a dibujar ${g.name.charAt(0).toLowerCase()+g.name.slice(1)}. Empezamos con el primer paso: ${si.t.toLowerCase()}.`
    :st.k===tot?`Último paso: ${si.t.toLowerCase()}.`
    :`${INTRO[(st.k*3+d.name.length)%INTRO.length]} Paso ${st.k}: ${si.t.replace(': ',', ').toLowerCase()}.`;
  return `${head} ${si.x}`;
}
const say=()=>speak(spoken());
let PAUSED=false,ENFOQUE=false;
function otraVersion(){const g=GDE[st.id],v=versionActual();if(!g||g.vers.length<2||!v)return null;return g.vers.find(x=>x!==v&&!isDone(x))||g.vers.find(x=>x!==v)}
function estudioHTML(){
  const d=cur(),g=GDE[d.id]||{name:d.name};
  return `<div class="estudio" role="region" aria-label="Estudio de dibujo">
  <div class="e-top">
    <button class="ib" data-a="cerrar" aria-label="Volver a los dibujos">${IC.back}</button>
    <div class="e-tit"><b>${esc(g.name)}</b><span id="eSub"></span></div>
    <div id="verTop"></div>
    <div class="e-acc">
      <button class="ib" data-a="voz" data-sync="voz" aria-pressed="true" aria-label="Voz que explica los pasos">${IC.voz}</button>
      <button class="ib" data-a="mus" data-sync="mus" aria-pressed="true" aria-label="Música de fondo">${IC.mus}</button>
      <button class="ib ancho" data-a="materiales" aria-label="Materiales">${IC.mat}</button>
      <button class="ib ancho" data-a="enfoque" aria-label="Modo enfoque: solo el dibujo">${IC.enfoque}</button>
      <button class="ib ancho" data-a="ajustes" aria-label="Ajustes">${IC.aju}</button>
      ${FS_OK?`<button class="ib ancho" data-a="full" aria-label="Pantalla completa">${IC.full}</button>`:''}
      <button class="ib angosto" data-a="opciones" aria-label="Más opciones">${IC.menu}</button>
    </div>
  </div>
  <div class="e-lienzo"><div class="hoja-ctl"><div class="papel" id="zpaper"><div class="zoomer" id="zoomer"><svg id="cv" class="cv" viewBox="0 0 400 400" role="img" aria-label="Dibujo paso a paso"></svg></div>
    <div class="zbtns" role="group" aria-label="Acercar"><button class="cb" data-a="zin" aria-label="Acercar">${IC.zin}</button><button class="cb" data-a="zout" aria-label="Alejar">${IC.zout}</button><button class="cb" data-a="zfit" id="bFit" hidden aria-label="Ver todo el dibujo">${IC.zfit}</button></div>
    <div class="enfoque-top"><span id="enfPaso"></span><button class="cb" data-a="enfoque" aria-label="Salir del modo enfoque">${IC.close}</button></div>
    <div class="enfoque-nav"><button class="cb grande" data-a="prev" aria-label="Paso anterior">${IC.prev}</button><button class="cb grande" data-a="oir" aria-label="Escuchar otra vez">${IC.oir}</button><button class="cb grande ir" data-a="next" aria-label="Siguiente paso">${IC.next}</button></div></div>
    <div class="ctl" role="group" aria-label="Animación">
      <button class="cb" data-a="pause" id="bPause" aria-label="Pausa">${IC.pause}</button>
      <button class="cb" data-a="replay" aria-label="Repetir el paso">${IC.replay}</button>
      <span class="vel" role="group" aria-label="Velocidad del trazo">${velBtns()}</span>
    </div></div></div>
  <div class="e-panel">
    <section class="paso${st.min?' min':''}" id="paso" aria-live="polite"></section>
    <div class="mapa-caja"><div class="mapa" id="mapa" role="group" aria-label="Pasos"></div><div class="mapa-fases" id="mapaFases"></div></div>
    <div class="lista"><h3>Todos los pasos</h3><ol class="pasos-lista" id="listaPasos"></ol></div>
    <div class="e-nav"><button class="btn sec" id="bPrev" data-a="prev">Atrás</button><button class="btn sec oir" data-a="oir" aria-label="Escuchar el paso">${IC.oir}<span>Escuchar</span></button><button class="btn" id="bNext" data-a="next">Siguiente</button></div>
  </div>
  </div>`;
}
const velBtns=()=>[['0.5','Lento'],['1','Normal'],['2','Rápido']].map(([v,n])=>`<button data-a="vel" data-v="${v}" aria-pressed="${+v===SPEED}">${n}</button>`).join('');
let scrollInicio=0;
function open(id,tk,k){
  const d=byId(id);if(!d)return;
  if(st.view==='home')scrollInicio=window.scrollY;
  st.id=id;st.tech=tk&&d.img&&d.img[tk]?tk:'lapiz';st.k=Math.max(1,Math.min(k||1,d.steps.length));st.fin=false;st.view='studio';st.t0=Date.now();
  demoParar();cerrarCapa(true);
  document.body.classList.add('en-estudio');
  EST.innerHTML=estudioHTML();
  syncSonido();Z.s=1;Z.x=0;Z.y=0;zBind();
  ensureVec(d);pantallaEncendida(true);
  upd();say();
  const h=slug(id);if(location.hash.slice(1)!==h){HIST=true;location.hash=h}
}
/* la pantalla no se apaga mientras se dibuja (si el navegador lo permite) */
let WL=null;
async function pantallaEncendida(on){
  try{
    if(on&&'wakeLock' in navigator&&!WL&&document.visibilityState==='visible'){WL=await navigator.wakeLock.request('screen');WL.addEventListener('release',()=>{WL=null})}
    else if(!on&&WL){const w=WL;WL=null;await w.release()}
  }catch(e){WL=null}
}
function cerrarEstudio(){
  if(st.view!=='studio')return;
  pantallaEncendida(false);
  stopSpeak();stopShade();setPaused(false);ENFOQUE=false;exitFull();
  st.view='home';EST.innerHTML='';document.body.classList.remove('en-estudio');
  const f=$('.festejo');if(f)f.remove();
  home();window.scrollTo(0,scrollInicio);
}
function salir(){
  const conHash=location.hash.startsWith('#dibujo-');
  cerrarEstudio();
  if(!conHash)return;
  if(HIST){HIST=false;IGN=Date.now()+800;history.back()}
  else{try{history.replaceState(null,'',location.pathname+location.search)}catch(e){}}
}
function exitFull(){try{if(document.fullscreenElement)document.exitFullscreen();else if(document.webkitFullscreenElement)document.webkitExitFullscreen()}catch(e){}}
function toggleFull(){
  try{
    if(document.fullscreenElement||document.webkitFullscreenElement)exitFull();
    else{const el=document.documentElement,r=(el.requestFullscreen||el.webkitRequestFullscreen).call(el);if(r&&r.catch)r.catch(()=>{})}
  }catch(e){}
}
/* zoom propio del dibujo: los botones nunca se mueven ni se salen de la pantalla */
const Z={s:1,x:0,y:0};
function zApply(){
  const p=$('#zpaper'),z=$('#zoomer');if(!p||!z)return;
  const W=p.clientWidth,H=p.clientHeight;
  Z.s=Math.max(1,Math.min(5,Z.s));
  Z.x=Math.min(0,Math.max(W-W*Z.s,Z.x));Z.y=Math.min(0,Math.max(H-H*Z.s,Z.y));
  z.style.transform=`translate(${Z.x}px,${Z.y}px) scale(${Z.s})`;
  const f=$('#bFit');if(f)f.hidden=Z.s<=1.01;
}
function zTo(ns,cx,cy){const p=$('#zpaper');if(!p)return;const W=p.clientWidth,H=p.clientHeight;if(cx==null){cx=W/2;cy=H/2}
  ns=Math.max(1,Math.min(5,ns));Z.x=cx-(cx-Z.x)*ns/Z.s;Z.y=cy-(cy-Z.y)*ns/Z.s;Z.s=ns;zApply()}
function zReset(){Z.s=1;Z.x=0;Z.y=0;zApply()}
function zBind(){
  const p=$('#zpaper');if(!p)return;const pts=new Map();let g=null,lastTap=0;
  const rel=e=>{const r=p.getBoundingClientRect();return[e.clientX-r.left,e.clientY-r.top]};
  p.addEventListener('pointerdown',e=>{if(e.target.closest('button'))return;p.setPointerCapture(e.pointerId);pts.set(e.pointerId,rel(e));g=null;
    if(pts.size===1){const t=Date.now();if(t-lastTap<300){Z.s>1.01?zReset():zTo(2.5,...rel(e))}lastTap=t}});
  p.addEventListener('pointermove',e=>{if(!pts.has(e.pointerId))return;const prev=pts.get(e.pointerId),c=rel(e);pts.set(e.pointerId,c);
    if(pts.size>=2){const [a,b]=[...pts.values()],dd=Math.hypot(a[0]-b[0],a[1]-b[1]),m=[(a[0]+b[0])/2,(a[1]+b[1])/2];
      if(g){zTo(Z.s*dd/g.d,m[0],m[1]);Z.x+=m[0]-g.c[0];Z.y+=m[1]-g.c[1];zApply()}g={d:dd,c:m}}
    else if(Z.s>1.01){Z.x+=c[0]-prev[0];Z.y+=c[1]-prev[1];zApply()}});
  const up=e=>{pts.delete(e.pointerId);g=null};
  p.addEventListener('pointerup',up);p.addEventListener('pointercancel',up);
  p.addEventListener('wheel',e=>{e.preventDefault();zTo(Z.s*(e.deltaY<0?1.15:1/1.15),...rel(e))},{passive:false});
}
function setEnfoque(on){
  ENFOQUE=on;const f=$('.estudio');if(!f)return;
  f.classList.toggle('enfoque',on);
  if(on){
    if(HAY_VOZ&&!SND.voice){SND.voice=true;saveSnd();syncSonido()}
    if(FS_OK&&!(document.fullscreenElement||document.webkitFullscreenElement))toggleFull();
    say();
  }else exitFull();
  syncEnfoque();setTimeout(zApply,60);
}
function syncEnfoque(){const s=$('#enfPaso');if(!s)return;const d=cur();s.textContent=st.fin?'¡Terminado!':`Paso ${st.k} de ${d.steps.length}`}
function setPaused(p){
  PAUSED=p;const cv=$('#cv'),b=$('#bPause');if(!cv)return;
  cv.classList.toggle('paused',p);
  try{p?cv.pauseAnimations():cv.unpauseAnimations()}catch(e){}
  if(TTS){try{p?speechSynthesis.pause():speechSynthesis.resume()}catch(e){}}
  if(NV.audio&&NV.audio.src){try{p?NV.audio.pause():(NV.audio.onended&&NV.audio.play().catch(()=>{}))}catch(e){}}
  if(b){b.innerHTML=p?IC.play:IC.pause;b.setAttribute('aria-label',p?'Continuar':'Pausa');b.classList.toggle('on',p)}
}
function renderLienzo(){
  const d=cur(),tk=effT(d),cv=$('#cv');if(!cv)return;
  stopShade();PENDING_SHADE=null;
  cv.innerHTML=scene(d,tk,st.k,st.fin,false);
  runShade($('#zoomer'));
  if(d.img&&!st.fin){const nx=d.img[tk][st.k];if(nx){const im=new Image(),sp=sprOf(nx);im.src=sp?sp.f:nx}}
}
function replay(){setPaused(false);renderLienzo()}
function upd(speakIt){
  if(PAUSED)setPaused(false);
  const d=cur(),tk=effT(d),tot=d.steps.length,k=st.k,g=GDE[d.id],v=versionActual(),medio=v?v.m:medioDe(d.id,tk);
  {const PH=d.img&&d.h||400;$('#cv').setAttribute('viewBox',`0 0 400 ${PH}`);$('.estudio').style.setProperty('--ar',400/PH)}
  if(!d._vec&&typeof VECF!=='undefined'&&VECF.has(d.id)&&!st.fin&&k>1){
    stopShade();$('#cv').innerHTML='';
    const z=$('#zoomer'),c=document.createElement('div');c.className='cargando';c.innerHTML='<div><i></i>Cargando el dibujo…</div>';z.appendChild(c);
    ensureVec(d).then(()=>{c.remove();if(st.view==='studio'&&st.id===d.id&&st.k===k)renderLienzo()});
  }else renderLienzo();
  let h;
  const verBtns=g&&g.vers.length>1?g.vers.map((x,j)=>`<button data-a="cambiar-version" data-i="${j}" aria-pressed="${x===v}"><span class="punto-medio ${x.m}"></span>${VLAB[x.m]}</button>`).join(''):'';
  const verHTML=verBtns?`<div class="versiones ver-paso" role="group" aria-label="Versión">${verBtns}</div>`:'';
  $('#verTop').innerHTML=verBtns?`<div class="versiones ver-top" role="group" aria-label="Versión">${verBtns}</div>`:'';
  const ocultar=`<button class="ocultar" data-a="txt" aria-expanded="${!st.min}" aria-label="Mostrar u ocultar la explicación">${IC.txt}</button>`;
  if(st.fin){
    h=`${verHTML}<div class="paso-cab"><span class="fase final"><i></i>Terminado</span><span class="paso-n">${tot} pasos</span>${ocultar}</div>
       <h2>¡Quedó muy bien!</h2><p>Terminaste ${esc((g?g.name:d.name).toLowerCase())}. Puedes volver a ver cualquier paso tocándolo abajo.</p>`;
  }else{
    const si=stepInfo(d,k),f=fasePaso(d,k);
    const na=d.img&&!d.img[st.tech]?`<p class="na">Este dibujo está en ${Object.keys(d.img).map(t=>TECH[t].n.toLowerCase()).join(' y ')}. Te lo muestro en lápiz.</p>`:'';
    h=na+verHTML+`<div class="paso-cab"><span class="fase ${f}${medio==='color'||medio==='acuarela'?' color':''}"><i></i>${faseLab(f,medio)}</span><span class="paso-n">Paso ${k} de ${tot}</span>${ocultar}</div>
       <h2>${esc(si.t)}</h2><p>${esc(si.x)}</p>${si.tone?`<div class="mats">${chipsPaso(d,si,f,medio)}</div>`:''}`;
  }
  $('#paso').innerHTML=h;
  $('#eSub').textContent=st.fin?'Terminado':`Paso ${k} de ${tot}${g&&g.vers.length>1?', '+MEDIO[medio].toLowerCase():''}`;
  /* mapa de pasos y lista */
  let mp='',fz=[],ls='',lastF='';
  for(let i=1;i<=tot;i++){
    const f=fasePaso(d,i),now=!st.fin&&i===k,dn=st.fin||i<k,t=stepInfo(d,i).t;
    mp+=`<button class="${f}${dn?' hecho':''}${now?' ahora':''}" data-a="go" data-k="${i}" aria-label="Paso ${i}: ${esc(t)}"${now?' aria-current="step"':''}></button>`;
    if(f!==lastF){fz.push([f,0]);ls+=`<li class="grupo">${faseLab(f,medio)}</li>`;lastF=f}
    fz[fz.length-1][1]++;
    ls+=`<li><button class="pl${dn?' hecho':''}${now?' ahora':''}" data-a="go" data-k="${i}"${now?' aria-current="step"':''}><span class="n">${i}</span><span class="t">${esc(t)}</span><span class="ok">${IC.check}</span></button></li>`;
  }
  $('#mapa').innerHTML=mp;
  $('#mapaFases').innerHTML=fz.map(([f,n])=>`<span style="flex:${n} 1 0">${n>=2?faseLab(f,medio):''}</span>`).join('')+`<button class="ver-todos" data-a="lista">${IC.pasos}Todos los pasos</button>`;
  const lp=$('#listaPasos');lp.innerHTML=ls;
  const ah=lp.querySelector('.ahora');if(ah)ah.scrollIntoView({block:'nearest'});
  const pv=$('#bPrev'),nx=$('#bNext');
  if(st.fin){pv.textContent='Ver los pasos';pv.disabled=false;nx.textContent='Otro dibujo';nx.dataset.a='cerrar'}
  else{pv.textContent='Atrás';pv.disabled=k===1;nx.textContent=k===tot?'¡Terminé!':'Siguiente';nx.dataset.a='next'}
  syncEnfoque();ajustarLista();
  if(!st.fin){st.last={id:d.id,tk:st.tech,k};save()}
  if(speakIt)say();
}
/* la lista de pasos se muestra solo si cabe; si no, queda el enlace "Todos los pasos" */
function ajustarLista(){
  const l=$('.lista'),e=$('.estudio');if(!l||!e)return;
  l.classList.remove('oculta');const chica=l.clientHeight<120;l.classList.toggle('oculta',chica);e.classList.toggle('sin-lista',chica);
}
function next(){
  const d=cur();if(st.fin)return;
  if(st.k<d.steps.length){st.k++;upd(true);return}
  st.fin=true;const a=st.done[d.id]=st.done[d.id]||[];if(!a.includes(effT(d)))a.push(effT(d));
  st.last=null;save();upd(true);festejo();
}
function prev(){
  const d=cur();
  if(st.fin){st.fin=false;st.k=d.steps.length}else if(st.k>1)st.k--;
  upd(true);
}
function cambiarVersion(i){
  const g=GDE[st.id];if(!g||!g.vers[i])return;const v=g.vers[i],k=st.k,fin=st.fin,d=byId(v.id);
  st.ver[g.key]=i;
  if(v.id!==st.id){st.id=v.id;ensureVec(d);try{history.replaceState(null,'','#'+slug(v.id))}catch(e){}}
  st.tech=v.tk;st.k=Math.min(k,d.steps.length);st.fin=fin;save();upd();
  aviso(`Versión ${MEDIO[v.m].toLowerCase()}`);
}

/* ---------- festejo al terminar ---------- */
function festejo(){
  const d=cur(),g=GDE[d.id]||{name:d.name},v=versionActual(),o=otraVersion(),min=Math.round((Date.now()-st.t0)/60000);
  const f=document.createElement('div');f.className='festejo';f.setAttribute('role','dialog');f.setAttribute('aria-modal','true');f.setAttribute('aria-labelledby','fTit');
  f.innerHTML=`<canvas aria-hidden="true"></canvas><div class="f-caja">
    <div class="f-hoja"><img src="${thumb(d.id,effT(d))}" alt="${esc(g.name)}, terminado"></div>
    <p class="f-mano" aria-hidden="true">¡Muy bien!</p>
    <h2 id="fTit">¡Terminaste ${esc(g.name.charAt(0).toLowerCase()+g.name.slice(1))}!</h2>
    <p>Hiciste los ${d.steps.length} pasos${min>=2?` en unos ${min} minutos`:''}.</p>
    <div class="f-acc">${o?`<button class="btn" data-a="otra-version">Hacerlo ${MEDIO[o.m].toLowerCase()}</button>`:''}<button class="btn${o?' sec':''}" data-a="cerrar-festejo">Ver mi dibujo</button><button class="btn sec" data-a="festejo-inicio">Elegir otro dibujo</button></div>
  </div>`;
  document.body.appendChild(f);
  setTimeout(()=>{const b=f.querySelector('.f-acc .btn');if(b)b.focus()},50);
  if(!RM())confeti(f.querySelector('canvas'));
}
function confeti(cv){
  const dpr=Math.min(2,devicePixelRatio||1),W=innerWidth,H=innerHeight;cv.width=W*dpr;cv.height=H*dpr;
  const c=cv.getContext('2d');if(!c)return;c.scale(dpr,dpr);
  const col=['#F25F3F','#FFC23A','#2F63E0','#3BB273','#B05BD8','#1F2330'],P=[];
  for(let i=0;i<120;i++)P.push({x:W/2+(Math.random()-.5)*W*.3,y:H*.35,vx:(Math.random()-.5)*11,vy:-Math.random()*12-4,r:Math.random()*Math.PI,vr:(Math.random()-.5)*.3,w:5+Math.random()*7,h:3+Math.random()*4,c:col[i%col.length]});
  const t0=performance.now();
  const fr=t=>{
    if(!cv.isConnected)return;const e=(t-t0)/1000;c.clearRect(0,0,W,H);
    P.forEach(p=>{p.vy+=.32;p.vx*=.99;p.x+=p.vx;p.y+=p.vy;p.r+=p.vr;c.save();c.translate(p.x,p.y);c.rotate(p.r);c.globalAlpha=Math.max(0,1-e/3.2);c.fillStyle=p.c;c.fillRect(-p.w/2,-p.h/2,p.w,p.h);c.restore()});
    if(e<3.3)requestAnimationFrame(fr);else c.clearRect(0,0,W,H);
  };
  requestAnimationFrame(fr);
}

/* ---------- hojas: ajustes, materiales, opciones, lista de pasos ---------- */
let abridor=null;
function abrirCapa(html,der){
  cerrarCapa(true);abridor=document.activeElement;
  CAPAS.innerHTML=`<div class="capa${der?' der':''}" data-a="cerrar-capa">${html}</div>`;
  const b=CAPAS.querySelector('.panel-hoja button, .panel-hoja select, .panel-hoja input');if(b)b.focus();
}
function cerrarCapa(silencio){if(!CAPAS.innerHTML)return;CAPAS.innerHTML='';if(!silencio&&abridor&&abridor.isConnected)abridor.focus();abridor=null}
const cabHoja=(t,id)=>`<div class="ph-cab"><h2 id="${id}">${t}</h2><button class="ib" data-a="cerrar-capa" aria-label="Cerrar">${IC.close}</button></div>`;
function ajustesHTML(){
  return `<div class="panel-hoja" role="dialog" aria-modal="true" aria-labelledby="ajT">${cabHoja('Ajustes','ajT')}
    <section class="grupo-aj"><div class="fila"><h3>Voz que explica</h3><button class="interruptor" role="switch" data-a="voz" data-sync="voz" aria-checked="${SND.voice}" aria-label="Voz que explica"${HAY_VOZ?'':' disabled'}></button></div>
      ${NV_OK?`<div class="segm" role="group" aria-label="Tipo de voz"><button data-a="motor" data-m="disp" aria-pressed="${SND.motor!=='nv'}">Del dispositivo</button><button data-a="motor" data-m="nv" aria-pressed="${SND.motor==='nv'}">Voz natural</button></div>`:''}
      <div id="vDisp"${SND.motor==='nv'&&NV_OK?' hidden':''}><label class="nota-aj" for="vSel">Voz</label><select class="campo" id="vSel"></select>
        <p class="nota-aj">${TTS?'La voz viene de tu dispositivo. Las que dicen “Natural”, “Online” o “Google” suenan más humanas; en iPhone, las “Mejoradas”.':'Este navegador no tiene voz integrada. Puedes descargar la voz natural.'}</p></div>
      <div id="vNat"${SND.motor==='nv'&&NV_OK?'':' hidden'}></div>
      <label class="nota-aj" for="vRate">Velocidad de la voz</label><input class="campo" type="range" id="vRate" min=".7" max="1.2" step=".02" value="${SND.rate}">
      <button class="btn sec" data-a="probar-voz"${HAY_VOZ?'':' disabled'}>${IC.oir}Escuchar un ejemplo</button></section>
    <section class="grupo-aj"><div class="fila"><h3>Música</h3><button class="interruptor" role="switch" data-a="mus" data-sync="mus" aria-checked="${SND.music}" aria-label="Música de fondo"></button></div>
      <div class="segm" role="group" aria-label="Tipo de música">${[['suave','Suave'],['bosque','Bosque'],['piano','Piano']].map(([m,n])=>`<button data-a="mood" data-m="${m}" aria-pressed="${SND.mood===m}">${n}</button>`).join('')}</div>
      <label class="nota-aj" for="vVol">Volumen de la música</label><input class="campo" type="range" id="vVol" min="0" max="1" step=".05" value="${SND.vol}"></section>
    <section class="grupo-aj"><h3>Velocidad del trazo</h3><div class="segm" role="group" aria-label="Velocidad del trazo">${velBtns()}</div></section>
    <section class="grupo-aj"><h3>Apariencia</h3><div class="segm" role="group" aria-label="Apariencia">${[['auto','Automática'],['light','Clara'],['dark','Oscura']].map(([t,n])=>`<button data-a="tema" data-t="${t}" aria-pressed="${st.tema===t}">${n}</button>`).join('')}</div></section>
  </div>`;
}
const HAY_VOZ=TTS||NV_OK;
const MB=n=>Math.round(n/1e6)+' MB';
// las cuatro voces naturales: se descargan una vez y quedan en este navegador
function pintarNV(){
  const box=$('#vNat');if(!box)return;
  const fila=id=>{const v=NV_VOCES[id],ok=nvInstalada(id),bajando=NV.dl&&NV.dl.id===id,usa=SND.nv===id&&ok;
    let acc;
    if(bajando)acc=`<div class="nv-barra"><i style="width:${Math.round(NV.dl.frac*100)}%"></i></div><button class="btn sec chico" data-a="nv-cancelar">Cancelar</button>`;
    else if(ok)acc=`<button class="btn chico${usa?'':' sec'}" data-a="nv-usar" data-v="${id}" aria-pressed="${usa}">${usa?'En uso':'Usar'}</button><button class="btn sec chico" data-a="nv-borrar" data-v="${id}" aria-label="Borrar la voz ${v.nom}${v.lite?' ligera':''}">Borrar</button>`;
    else acc=`<button class="btn sec chico" data-a="nv-bajar" data-v="${id}"${NV.dl?' disabled':''}>Descargar · ${MB(nvFalta(id))}</button>`;
    return `<div class="nv-fila${usa?' usa':''}"><div class="nv-av">${v.nom[0]}</div><div class="nv-t"><b>${v.nom}${v.lite?' · ligera':''}</b><span>${v.nota} · México</span></div><div class="nv-acc">${acc}</div></div>`};
  box.innerHTML=`<div class="nv-lista">${Object.keys(NV_VOCES).map(fila).join('')}</div>
    <p class="nota-aj">${NV.falla?'La voz natural no funcionó en este dispositivo; por ahora se usa la del dispositivo. ':''}Son las mismas voces de Atril. Se descargan una sola vez, se guardan en este navegador y funcionan sin internet. La ligera pesa menos y suena casi igual.</p>`;
}
window.avisoVoz=t=>{aviso(t);pintarNV()};
async function nvAccion(a,id){
  if(a==='nv-bajar'){
    const t0=Date.now();let pt=0;
    try{pintarNV();await nvDescargar(id,()=>{if(Date.now()-pt>250){pt=Date.now();pintarNV()}});SND.nv=id;SND.motor='nv';saveSnd();pintarNV();aviso('Voz lista');speak('Hola, vamos a dibujar juntos.',true)}
    catch(e){pintarNV();if(!(e&&e.name==='AbortError'))aviso('No se pudo descargar: '+(e.message||e))}
  }else if(a==='nv-cancelar'){nvCancelar()}
  else if(a==='nv-usar'){SND.nv=id;SND.motor='nv';NV.falla=false;saveSnd();pintarNV();speak('Hola, vamos a dibujar juntos.',true)}
  else if(a==='nv-borrar'){await nvBorrar(id);if(SND.nv===id){const o=Object.keys(NV_VOCES).find(nvInstalada);if(o)SND.nv=o}saveSnd();pintarNV();aviso('Voz borrada')}
}
function abrirAjustes(){
  abrirCapa(ajustesHTML(),true);fillVoiceList();if(NV_OK)nvKeys().then(pintarNV);
  const vS=$('#vSel'),vR=$('#vRate'),vV=$('#vVol');
  vS.onchange=()=>{SND.vname=vS.value;saveSnd();speak('Hola, vamos a dibujar juntos.',true)};
  vR.oninput=()=>{SND.rate=+vR.value;saveSnd()};
  vV.oninput=()=>{setVol(+vV.value);saveSnd()};
}
window.fillVoiceList=()=>{
  const vS=$('#vSel');if(!vS)return;
  if(!VOICES.length){vS.innerHTML='<option>Voz del dispositivo</option>';return}
  const c=pickVoice();
  vS.innerHTML=VOICES.map(v=>`<option value="${esc(v.name)}"${c&&v.name===c.name?' selected':''}>${esc(v.name)} (${esc(v.lang)})</option>`).join('');
};
const MAT_COLOR={n:'Lápices de colores',sub:'Se dibuja con lápiz suave y se colorea por capas, de lo oscuro a lo claro.',
  mat:['Lápiz HB para las guías y las líneas','Lápices de colores (o crayones de cera)','Goma suave','Hojas blancas, mejor si son gruesas','Sacapuntas'],
  proc:['Dibuja las guías muy suaves para poder borrarlas.','Colorea primero lo más oscuro de cada parte y luego lo claro.','Pinta en la misma dirección y sin apretar al principio.','Para los brillos, deja el papel blanco o usa la goma.']};
function materialesHTML(){
  const d=cur(),v=versionActual(),medio=v?v.m:medioDe(d.id,effT(d)),T=medio==='color'?MAT_COLOR:TECH[effT(d)];
  return `<div class="panel-hoja" role="dialog" aria-modal="true" aria-labelledby="matT">${cabHoja('Materiales','matT')}
    <p class="medio" style="font-size:var(--t-s)"><span class="punto-medio ${medio}"></span>${MEDIO[medio]}. ${esc(T.sub)}</p>
    <section class="grupo-aj"><h3>Vas a necesitar</h3><ul class="lista-mat">${T.mat.map(m=>`<li>${esc(m)}</li>`).join('')}</ul></section>
    <section class="grupo-aj"><h3>Así se trabaja</h3><ol class="consejos">${T.proc.map(m=>`<li>${esc(m)}</li>`).join('')}</ol></section>
  </div>`;
}
function opcionesHTML(){
  const fila=(a,ic,t)=>`<button class="pl" data-a="${a}" style="grid-template-columns:28px minmax(0,1fr)"><span>${ic}</span><span class="t" style="font-size:var(--t-m)">${t}</span></button>`;
  return `<div class="panel-hoja" role="dialog" aria-modal="true" aria-labelledby="opT">${cabHoja('Opciones','opT')}
    <div style="display:grid;gap:4px">${fila('materiales',IC.mat,'Materiales')}${fila('enfoque',IC.enfoque,'Modo enfoque: solo el dibujo')}${fila('lista',IC.pasos,'Todos los pasos')}${fila('ajustes',IC.aju,'Ajustes')}${FS_OK?fila('full',IC.full,'Pantalla completa'):''}</div></div>`;
}
function listaHTML(){
  return `<div class="panel-hoja" role="dialog" aria-modal="true" aria-labelledby="lsT">${cabHoja('Todos los pasos','lsT')}<ol class="pasos-lista">${$('#listaPasos').innerHTML}</ol></div>`;
}

/* ---------- sonido ---------- */
function syncSonido(){
  $$('[data-sync="voz"]').forEach(b=>{b.hasAttribute('role')?b.setAttribute('aria-checked',String(SND.voice)):b.setAttribute('aria-pressed',String(SND.voice));if(!HAY_VOZ)b.disabled=true});
  $$('[data-sync="mus"]').forEach(b=>b.hasAttribute('role')?b.setAttribute('aria-checked',String(SND.music)):b.setAttribute('aria-pressed',String(SND.music)));
}
function toggleVoz(){if(!HAY_VOZ)return;SND.voice=!SND.voice;if(!SND.voice)stopSpeak();else if(st.view==='studio')say();saveSnd();syncSonido();aviso(SND.voice?'Voz encendida':'Voz apagada')}
function toggleMus(){SND.music=!SND.music;if(SND.music)startMusic();else stopMusic();saveSnd();syncSonido();aviso(SND.music?'Música encendida':'Música apagada')}

/* ---------- direcciones (#dibujo-…): el botón atrás del celular regresa a la galería ---------- */
let HIST=false,IGN=0;
const slug=id=>'dibujo-'+id.replace(/_/g,'-');
function ruta(){
  const h=decodeURIComponent(location.hash.slice(1));
  if(h.startsWith('dibujo-')){const d=D.find(x=>slug(x.id)===h);if(d&&(st.view!=='studio'||st.id!==d.id))open(d.id,(st.last&&st.last.id===d.id&&st.last.tk)||'lapiz')}
  else if(st.view==='studio'&&Date.now()>IGN){HIST=false;cerrarEstudio()}
}
addEventListener('hashchange',ruta);

/* ---------- clics ---------- */
document.addEventListener('click',e=>{
  const b=e.target.closest('[data-a]');if(!b||b.disabled)return;
  const a=b.dataset.a;
  if(a==='cerrar-capa'){if(e.target===b||b.tagName==='BUTTON')cerrarCapa();return}
  if(a==='home'){e.preventDefault();if(st.view==='studio')salir();else window.scrollTo({top:0,behavior:RM()?'auto':'smooth'});return}
  if(a==='open'){open(b.dataset.id,b.dataset.tk);return}
  if(a==='seguir'&&st.last){open(st.last.id,st.last.tk,st.last.k);return}
  if(a==='ir-galeria'){const g=$('#galeria');if(g)g.scrollIntoView({behavior:RM()?'auto':'smooth',block:'start'});return}
  if(a==='cat'){st.cat=b.dataset.c;$$('.chip').forEach(c=>c.setAttribute('aria-pressed',String(c.dataset.c===st.cat)));pintarObras();return}
  if(a==='ver'){const g=GRUPOS.find(x=>x.key===b.dataset.g);if(!g)return;st.ver[g.key]=+b.dataset.i;save();const art=b.closest('.obra');if(art)art.outerHTML=obraHTML(g);return}
  if(a==='voz'){toggleVoz();return}
  if(a==='mus'){toggleMus();return}
  if(a==='ajustes'){abrirAjustes();return}
  if(a==='motor'){SND.motor=b.dataset.m;NV.falla=false;saveSnd();$$('[data-a="motor"]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.m===SND.motor)));const d=$('#vDisp'),n=$('#vNat');if(d)d.hidden=SND.motor==='nv';if(n)n.hidden=SND.motor!=='nv';pintarNV();if(SND.motor==='disp'||nvInstalada(SND.nv))speak('Hola, vamos a dibujar juntos.',true);return}
  if(a.startsWith('nv-')){nvAccion(a,b.dataset.v);return}
  if(a==='probar-voz'){speak('Hola, vamos a dibujar juntos. Primero, traza un óvalo suave, casi sin apretar el lápiz.',true);return}
  if(a==='mood'){SND.mood=b.dataset.m;SND.music=true;stopMusic();setTimeout(startMusic,450);saveSnd();syncSonido();$$('[data-a="mood"]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.m===SND.mood)));return}
  if(a==='tema'){st.tema=b.dataset.t;save();aplicarTema();$$('[data-a="tema"]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.t===st.tema)));return}
  if(a==='vel'){SPEED=+b.dataset.v;try{localStorage.setItem('trazo-spd',String(SPEED))}catch(err){}$$('[data-a="vel"]').forEach(x=>x.setAttribute('aria-pressed',String(+x.dataset.v===SPEED)));if(st.view==='studio')replay();return}
  if(st.view!=='studio')return;
  if(a==='cerrar'){salir()}
  else if(a==='next')next();
  else if(a==='prev')prev();
  else if(a==='oir')speak(spoken(),true);
  else if(a==='go'){st.k=+b.dataset.k;st.fin=false;cerrarCapa(true);upd(true)}
  else if(a==='txt'){st.min=!st.min;const p=$('#paso');p.classList.toggle('min',st.min);b.setAttribute('aria-expanded',String(!st.min))}
  else if(a==='materiales')abrirCapa(materialesHTML(),true);
  else if(a==='opciones')abrirCapa(opcionesHTML(),false);
  else if(a==='lista')abrirCapa(listaHTML(),false);
  else if(a==='enfoque'){cerrarCapa(true);setEnfoque(!ENFOQUE)}
  else if(a==='full'){cerrarCapa(true);toggleFull()}
  else if(a==='zin')zTo(Z.s*1.5);
  else if(a==='zout')zTo(Z.s/1.5);
  else if(a==='zfit')zReset();
  else if(a==='pause')setPaused(!PAUSED);
  else if(a==='replay')replay();
  else if(a==='cambiar-version')cambiarVersion(+b.dataset.i);
  else if(a==='cerrar-festejo'){const f=$('.festejo');if(f)f.remove()}
  else if(a==='festejo-inicio'){const f=$('.festejo');if(f)f.remove();salir()}
  else if(a==='otra-version'){const o=otraVersion(),f=$('.festejo');if(f)f.remove();if(o){const g=GDE[st.id];cambiarVersion(g.vers.indexOf(o));st.k=1;st.fin=false;st.t0=Date.now();upd(true)}}
});
document.addEventListener('input',e=>{if(e.target.id==='q'){st.q=e.target.value;pintarObras()}});
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){
    if(CAPAS.innerHTML){cerrarCapa();return}
    const f=$('.festejo');if(f){f.remove();return}
    if(ENFOQUE){setEnfoque(false);return}
  }
  if(st.view!=='studio'||CAPAS.innerHTML||$('.festejo')||e.altKey||e.ctrlKey||e.metaKey||/INPUT|SELECT|TEXTAREA/.test(e.target.tagName))return;
  if(e.key===' '&&!/BUTTON/.test(e.target.tagName)){e.preventDefault();setPaused(!PAUSED);return}
  if(e.key==='ArrowRight')next();else if(e.key==='ArrowLeft')prev();
});
addEventListener('resize',()=>{if(st.view==='studio'){zApply();ajustarLista()}});
addEventListener('scroll',()=>{const b=$('#barra');if(b)b.classList.toggle('con-borde',scrollY>4)},{passive:true});
document.addEventListener('visibilitychange',()=>{
  if(document.hidden&&st.view==='studio'&&!PAUSED)stopSpeak();
  if(!document.hidden&&st.view==='studio')pantallaEncendida(true);
});

/* botones de ícono: el nombre también como globo de ayuda al pasar el ratón */
new MutationObserver(()=>{$$('.ib[aria-label]:not([title]),.cb[aria-label]:not([title])').forEach(b=>b.title=b.getAttribute('aria-label'))}).observe(document.body,{childList:true,subtree:true});
/* ---------- arranque ---------- */
aplicarTema();
$('#bVoz').innerHTML=IC.voz;$('#bMus').innerHTML=IC.mus;$('#bAju').innerHTML=IC.aju;
syncSonido();
home();
if(location.hash.startsWith('#dibujo-'))ruta();
