/* Motor de dibujo: contornos, sombreado, pelo, hojas y luz */
const rng=s=>{let a=s>>>0;return()=>{a=(a+0x6D2B79F5)|0;let t=Math.imul(a^(a>>>15),1|a);t=(t+Math.imul(t^(t>>>7),61|t))^t;return((t^(t>>>14))>>>0)/4294967296}};
const hash=str=>{let h=2166136261;for(let i=0;i<str.length;i++){h^=str.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0};
const hx=c=>[parseInt(c.slice(1,3),16),parseInt(c.slice(3,5),16),parseInt(c.slice(5,7),16)];
const mix=(a,b,t)=>{const x=hx(a),y=hx(b);return '#'+x.map((v,i)=>Math.round(v+(y[i]-v)*t).toString(16).padStart(2,'0')).join('')};
const f2=n=>Math.round(n*100)/100;
const GR='#22222a';

/* Tipos de región: len = trazos (pelo, rayas, hojas, pasto); soft = cuánto relleno suave lleva */
const KIND={
  fur:{len:[7,16],w:.75,cv:.3,dens:80,op:[.14,.4],jit:15,soft:.55,b:4},
  hatch:{len:[24,44],w:1,cv:.1,dens:20,op:[.14,.3],jit:5,soft:.3,b:6},
  leaf:{len:[3,8],w:2.2,cv:.2,dens:60,op:[.25,.5],jit:180,soft:.5,b:4},
  grass:{len:[12,28],w:1,cv:.35,dens:35,op:[.2,.45],jit:14,soft:.2,b:3,dir:-90},
  blade:{len:[60,160],w:1,cv:.3,dens:3,op:[.25,.6],jit:12,soft:0,b:0,dir:-90},
  stripe:{len:[7,13],w:1,cv:.25,dens:120,op:[.3,.6],jit:14,soft:.9,b:1.8},
  soft:{soft:1,b:5},
  solid:{soft:1,b:0},
  light:{soft:1,b:4},
  line:{}
};
const BLS=[1.5,3,5,8,12,18];
const blurId=b=>{if(!b||b<.8)return null;let best=BLS[0];for(const v of BLS)if(Math.abs(v-b)<Math.abs(best-b))best=v;return 'bl'+String(best).replace('.','_')};

/* geometría de una región */
function norm(r){
  if(r._n)return r._n;
  let d,poly=null,ell=null,bb,area;
  if(r.p){poly=r.p;d=S(r.p)}else if(r.q){poly=r.q;d=P(r.q)}else if(r.e){ell=r.e;d=E(...r.e)}else d=r.d;
  if(poly){
    let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9,a=0;
    poly.forEach((p,i)=>{x0=Math.min(x0,p[0]);y0=Math.min(y0,p[1]);x1=Math.max(x1,p[0]);y1=Math.max(y1,p[1]);const q=poly[(i+1)%poly.length];a+=p[0]*q[1]-q[0]*p[1]});
    bb=[x0-4,y0-4,x1+4,y1+4];area=Math.abs(a)/2;
  }else if(ell){
    const m=Math.max(ell[2],ell[3]||ell[2]);
    bb=[ell[0]-m,ell[1]-m,ell[0]+m,ell[1]+m];area=Math.PI*ell[2]*(ell[3]||ell[2]);
  }else{bb=r.bb||[0,0,400,400];area=(bb[2]-bb[0])*(bb[3]-bb[1])*.5}
  return r._n={d,poly,ell,bb,area};
}
function inside(N,x,y){
  if(N.poly){
    const p=N.poly;let c=false;
    for(let i=0,j=p.length-1;i<p.length;j=i++){
      if(((p[i][1]>y)!==(p[j][1]>y))&&(x<(p[j][0]-p[i][0])*(y-p[i][1])/(p[j][1]-p[i][1])+p[i][0]))c=!c;
    }
    return c;
  }
  if(N.ell){
    const e=N.ell,rx=e[2],ry=e[3]||e[2],t=-(e[4]||0)*Math.PI/180,dx=x-e[0],dy=y-e[1];
    const u=dx*Math.cos(t)-dy*Math.sin(t),v=dx*Math.sin(t)+dy*Math.cos(t);
    return u*u/(rx*rx)+v*v/(ry*ry)<=1;
  }
  return true;
}
function angAt(dir,x,y){
  if(typeof dir==='number')return dir;
  if(typeof dir==='function')return dir(x,y);
  return Math.atan2(y-dir.c[1],x-dir.c[0])*180/Math.PI+(dir.a||0)+(dir.m==='tan'?90:0);
}
/* trazos: se generan una vez por región y se guardan */
/* un pelo o trazo que nace grueso y termina en punta, como el lápiz real */
const TAPER={fur:1,blade:1,grass:1,stripe:1};
const sliver=(x,y,dx,dy,cv,a,w)=>{
  const nx=-Math.sin(a),ny=Math.cos(a),h=w/2,cx=x+dx/2+nx*cv,cy=y+dy/2+ny*cv;
  return `M${f(x+nx*h)} ${f(y+ny*h)}Q${f(cx+nx*h*.55)} ${f(cy+ny*h*.55)} ${f(x+dx)} ${f(y+dy)}Q${f(cx-nx*h*.55)} ${f(cy-ny*h*.55)} ${f(x-nx*h)} ${f(y-ny*h)}Z`;
};
/* trazos: se generan una vez por región y se guardan; el pelo sale en mechones */
function strokes(r,seed,q,sw){
  sw=sw||1;
  const key=seed+'|'+q+'|'+sw;
  if(r._s&&r._s[key])return r._s[key];
  const o=Object.assign({},KIND[r.k],r),N=norm(r),tp=r.taper!=null?r.taper:TAPER[r.k];
  const cl=tp?(r.cl!=null?r.cl:(r.k==='fur'?3:1)):1;
  const n=Math.min(6000,Math.round(o.dens*(r.n||1)*N.area/1000*q/Math.max(1,cl*.7)*((r.form!=null?r.form:(r.k==='fur'&&r.nf&&!r.lt))?1.5:1)));
  const form=r.form!=null?r.form:(r.k==='fur'&&r.nf&&!r.lt);
  const fcx=(N.bb[0]+N.bb[2])/2,fcy=(N.bb[1]+N.bb[3])/2,frx=(N.bb[2]-N.bb[0])/2,fry=(N.bb[3]-N.bb[1])/2;
  const R=rng(seed),b=N.bb,out=['','',''],W=(r.w||KIND[r.k].w||1)*sw*(r.k==='fur'?1.05:1.7);
  for(let i=0;i<n;i++){
    let x,y,t=0,ok=false;
    if(o.k==='blade'){x=b[0]+R()*(b[2]-b[0]);y=b[3]-4-R()*10;ok=true}
    else while(t++<14){x=b[0]+R()*(b[2]-b[0]);y=b[1]+R()*(b[3]-b[1]);if(inside(N,x,y)){ok=true;break}}
    if(!ok)continue;
    let fp=1;
    if(form){
      const ux=(x-fcx)/frx,uy=(y-fcy)/fry,rr=Math.min(1,Math.sqrt(ux*ux+uy*uy));
      fp=Math.max(.12,Math.min(1,.25+.55*rr*rr+.35*(ux*.55+uy*.83)));
      if(R()>fp)continue;
    }
    const a=(angAt(o.dir!=null?o.dir:0,x,y)+(R()-.5)*2*o.jit)*Math.PI/180;
    const L=(o.len[0]+R()*(o.len[1]-o.len[0]))*(form?(.8+.4*fp):1);
    const dx=Math.cos(a)*L,dy=Math.sin(a)*L,cv=(R()-.5)*L*o.cv*2,bk=form?Math.min(2,Math.floor(fp*2.2+R()*.8)):Math.floor(R()*3);
    if(!tp){out[bk]+=`M${f(x)} ${f(y)}q${f(dx/2-Math.sin(a)*cv)} ${f(dy/2+Math.cos(a)*cv)} ${f(dx)} ${f(dy)}`;continue}
    const k=cl>1?cl-1+Math.floor(R()*2):1,nx=-Math.sin(a),ny=Math.cos(a);
    for(let j=0;j<k;j++){
      const off=(j-(k-1)/2)*W*1.8,lj=L*(.85+R()*.3),conv=.3;
      const x0=x+nx*off+Math.cos(a)*R()*2,y0=y+ny*off+Math.sin(a)*R()*2;
      const ex=Math.cos(a)*lj-nx*off*conv,ey=Math.sin(a)*lj-ny*off*conv;
      out[(bk+j)%3]+=sliver(x0,y0,ex,ey,cv*(.8+R()*.4),a,W*(.75+R()*.5));
    }
  }
  (r._s=r._s||{})[key]=out;
  return out;
}

/* Técnicas: papel, filtros, cómo se ve cada capa y qué se dice en cada paso */
const ORDER=['lapiz','acuarela','tempera','oleo','crayones'];
const isLt=r=>r.k==='light'||r.lt;
/* opacidad de pinturas opacas: las sombras y luces suaves se ven más transparentes */
const cfa=(r,hi)=>(r.k==='soft'||r.k==='light')?Math.min(hi,.14+.55*(r.v==null?.5:r.v)):hi;
const TECH={
 lapiz:{n:'Lápiz',sub:'Grafito. Se dibuja suave y se sombrea por capas, de claro a oscuro.',
  paper:'#FFFEFA',pf:'f-paper',po:1,ff:'f-pencil',phase:'Sombreado',
  line:{c:'#3a3a44',w:1.1,o:.55,f:'f-pencil'},
  tone:r=>{const v=r.v==null?.5:r.v,li=isLt(r),vc=Math.pow(v,1.15)*(1+.45*v);return{c:li?'#ffffff':GR,fa:Math.min(1,(li?.9:.62)*vc*(r.k==='solid'?1.7:1)),sc:li?'#ffffff':GR,so:li?1.2:.5+1.25*v,sw:1,bm:1}},
  pre:{base:'Primera capa',mid:'Medios tonos',dark:'Sombras fuertes',detail:'Detalles finos',light:'Luces'},
  how:{base:'Inclina el lápiz y sombrea suave y parejo, casi sin presionar. Es una capa muy clarita.',
   mid:'Presiona un poquito más y sigue la dirección del pelo o de la forma. Así va apareciendo el volumen.',
   dark:'Ahora van los oscuros. Aprieta más el lápiz, con trazos cortos. Las sombras le dan profundidad.',
   detail:'Con la punta bien afilada, haz trazos finitos en la dirección natural. Sin prisa.',
   light:'Levanta un poco de grafito con la goma o con un papel para crear luz. También puedes dejar el papel blanco.'},
  chip:{base:'Lápiz HB',mid:'Lápiz 2B',dark:'Lápiz 4B',detail:'Punta fina',light:'Goma moldeable'},
  mat:['Lápiz HB o del número 2','Lápiz 2B y 4B para las sombras (opcional)','Goma moldeable o goma suave','Hojas blancas','Sacapuntas'],
  proc:['Empieza con formas muy suaves, sin apretar.','Primero lo grande, después los detalles.','Sombrea por capas, de claro a oscuro.','Deja para el final las luces y los detalles finos.']},
 acuarela:{n:'Acuarela',sub:'Pintura de base agua, transparente. Entre más agua, más clarito.',
  paper:'#FBF8F0',pf:'f-cold',po:.5,ff:'f-wc',phase:'Color',
  line:{c:'#5a5766',w:1.1,o:.4,f:'f-wob'},
  tone:r=>{const v=r.v==null?.5:r.v,c=r.c||GR;return{c,fa:Math.min(1,(.2+.55*v)*(r.k==='solid'?1.6:1)),sc:mix(c,'#241a14',isLt(r)?0:.4),so:.9,sw:.9,bm:1.2}},
  pre:{base:'Color base',mid:'Tonos medios',dark:'Sombras',detail:'Detalles finos',light:'Luces'},
  how:{base:'Moja bien el pincel y suelta el color clarito con mucha agua. Déjalo secar un poco.',
   mid:'Con menos agua, agrega el tono medio sobre lo seco. Así se forman las capas transparentes.',
   dark:'Usa el color más oscuro y más espeso, solo en las sombras. Suaviza el borde con un pincel limpio y húmedo.',
   detail:'Pincel fino casi seco: líneas finitas para el pelo, las plumas o las hojas.',
   light:'Deja el papel blanco, o levanta color con una toalla de papel limpia y húmeda.'},
  chip:{},
  mat:['Acuarelas en pastilla o en tubo','Pincel redondo grueso (del 8 o 10) y uno fino (del 2)','Papel grueso para acuarela','Dos vasos con agua: uno para limpiar y otro para mezclar','Toalla de papel','Un plato blanco como paleta'],
  proc:['Haz el dibujo a lápiz muy suave.','Pinta primero los colores claros y deja los oscuros para el final.','Mucha agua y poquito color: así queda transparente.','Espera a que seque antes de pintar encima o al lado.','No uses goma al final: puede arrugar el papel.']},
 tempera:{n:'Témpera',sub:'Pintura de base agua que cubre bien. Ideal para empezar a pintar.',
  paper:'#FFFEFA',pf:'f-paper',po:1,ff:'f-tem',phase:'Color',
  line:{c:'#2a2535',w:1.4,o:.35,f:'f-wob'},
  tone:r=>{const c=r.c||GR;return{c,fa:cfa(r,.9),nsoft:1,sc:mix(c,isLt(r)?'#ffffff':'#1e1612',.16),so:.55,sw:1.15,bm:.5}},
  pre:{base:'Color base',mid:'Tonos medios',dark:'Sombras',detail:'Detalles finos',light:'Luces'},
  how:{base:'Cubre toda la zona con color parejo. Una segunda capa tapa los huequitos.',
   mid:'Mezcla un poco de oscuro en tu color y pinta las zonas de sombra suave.',
   dark:'Mezcla más color oscuro y pinta las sombras con el pincel plano, con pinceladas cortas.',
   detail:'Con el pincel más fino pinta líneas del pelo, las plumas o las hojas.',
   light:'Mezcla blanco con tu color y pinta las luces al final, con poca agua.'},
  chip:{},
  mat:['Témperas o pintura acrílica lavable','Pincel plano mediano y uno redondo fino','Cartulina o papel grueso','Vaso con agua y trapito','Plato o paleta para mezclar','Delantal o camisa vieja'],
  proc:['Dibuja a lápiz y pinta encima: la témpera cubre.','Empieza por lo más grande: fondo y cuerpo.','Deja secar cada color unos minutos.','Los detalles pequeños van al final, con el pincel fino.']},
 oleo:{n:'Óleo',sub:'Pintura espesa y cremosa que deja relieve. Se trabaja con un adulto.',
  paper:'#F3ECDD',pf:'f-cold',po:.5,ff:'f-oil',phase:'Color',
  line:{c:'#3a2a26',w:1.2,o:.22,f:'f-wob'},
  tone:r=>{const c=r.c||GR;return{c,fa:cfa(r,.94),nsoft:1,sc:mix(c,isLt(r)?'#ffffff':'#1a120e',.18),so:.55,sw:1.7,bm:.7}},
  pre:{base:'Color base',mid:'Tonos medios',dark:'Sombras',detail:'Detalles finos',light:'Luces'},
  how:{base:'Extiende una capa delgada de color por toda la zona, con un pincel de cerda.',
   mid:'Mezcla en tu paleta el tono medio y pinta encima con pinceladas cortas, siguiendo la forma.',
   dark:'Agrega los oscuros con pintura más espesa. Mezcla directo en el lienzo, sin lavar el pincel.',
   detail:'Con un pincel fino, marca pelo, plumas u hojas con pintura cremosa.',
   light:'Pon blanco mezclado en toques de pintura gruesa. Las luces van siempre al final.'},
  chip:{},
  mat:['Pinturas al óleo (mejor las “lavables con agua” para niños)','Pinceles de cerda planos y redondos','Lienzo, cartón entelado o papel para óleo','Espátula pequeña','Paleta para mezclar','Trapo, y aceite o aguarrás solo con un adulto y con ventana abierta'],
  proc:['Pide ayuda a un adulto: el óleo huele fuerte y mancha.','Marca las formas con pincel delgado y pintura diluida.','Cubre primero lo grande con capas delgadas.','Al final pon pintura gruesa en las luces.','Tarda días en secar: déjalo en un lugar seguro.']},
 crayones:{n:'Crayones',sub:'Cera de colores. Se presiona poco o mucho para cambiar el tono.',
  paper:'#FFFDF6',pf:'f-paper',po:1,ff:'f-wax',phase:'Color',
  line:{c:'#3a3350',w:1.6,o:.5,f:'f-wax'},
  tone:r=>{const c=r.c||GR;return{c,fa:cfa(r,.72),sc:mix(c,isLt(r)?'#ffffff':'#1e1612',.2),so:.8,sw:2.2,bm:.25}},
  pre:{base:'Color base',mid:'Tonos medios',dark:'Sombras',detail:'Detalles finos',light:'Luces'},
  how:{base:'Colorea suave con el lado del crayón, todo hacia el mismo lado.',
   mid:'Presiona más y agrega el tono medio encima, mezclando con el color de abajo.',
   dark:'Presiona fuerte con un crayón oscuro en las sombras. Es la capa final de oscuros.',
   detail:'Con la punta del crayón haz líneas cortitas para el pelo, las plumas o las hojas.',
   light:'Usa un crayón blanco o crema encima para dar brillo, o raspa suave con una uña.'},
  chip:{},
  mat:['Crayones de cera o pasteles grasos','Papel grueso o cartulina','Sacapuntas, si los crayones son delgados','Una hoja extra para apoyar la mano y no manchar'],
  proc:['Dibuja el contorno suave con lápiz.','Con la punta haces detalles; con el lado, llenas rápido.','Primera capa suave, segunda capa más fuerte.','Mezcla dos colores uno encima del otro para crear tonos nuevos.']}
};
const SKETCH={c:'#4a4a55',w:1.5,o:.88,f:'f-pencil'};

/* Una región de tono */
function reg(r,did,i,j,T,clip,q,sil){
  const st=T.tone(r);
  if(r.k==='line'){
    const g=`<g fill="none" stroke="${r.c||st.sc}" stroke-width="${f2((r.w||1)*(st.sw>1?1.25:1))}" stroke-linecap="round" opacity="${r.o==null?.8:r.o}">${r.d.map(p=>`<path d="${p}"/>`).join('')}</g>`;
    return r.clip?`<g clip-path="url(#${clip(r.clip)})">${g}</g>`:g;
  }
  const kd=KIND[r.k]||KIND.soft,N=norm(r);
  const b=(r.b!=null?r.b:kd.b)*st.bm;
  let s='';
  const fa=r.nf?0:Math.min(1,st.fa*(st.nsoft||kd.soft==null?1:kd.soft));
  if(fa>.01){
    const bid=blurId(b);
    s+=`<path d="${N.d}" fill="${st.c}" fill-opacity="${f2(fa)}"${bid?` filter="url(#${bid})"`:''}/>`;
  }
  if(kd.len){
    const sd=strokes(r,hash(did)+i*131+j*17,q,st.sw);
    const op=r.op||kd.op,w=(r.w||kd.w)*st.sw,ops=[op[0],(op[0]+op[1])/2,op[1]];
    const cg=r.k==='blade'?'':` clip-path="url(#${clip(N.d)})"`;
    const tp=r.taper!=null?r.taper:TAPER[r.k];
    if(tp)s+=`<g${cg} fill="${st.sc}" stroke="none">`+sd.map((p,u)=>p?`<path d="${p}" fill-opacity="${f2(Math.min(1,ops[u]*st.so*(r.k==='fur'?1.05:1.25)))}"/>`:'').join('')+'</g>';
    else s+=`<g${cg} fill="none" stroke="${st.sc}" stroke-width="${f2(w)}" stroke-linecap="round">`+
      sd.map((p,u)=>p?`<path d="${p}" stroke-opacity="${f2(Math.min(1,ops[u]*st.so))}" stroke-width="${f2(w*(.7+u*.3))}"/>`:'').join('')+'</g>';
  }
  if(r.rim){
    const w=r.rimw||16,bid=blurId(w*.5)||'bl8',ro=Math.min(.9,r.rim*(st.fa+.25));
    s+=`<g clip-path="url(#${clip(N.d)})"><path d="${N.d}" fill="none" stroke="${isLt(r)?'#fff':st.sc}" stroke-width="${w}" stroke-opacity="${f2(ro)}" filter="url(#${bid})"/></g>`;
  }
  let out;
  if(r.out&&sil)out=`<g mask="url(#${clip({out:sil})})">${s}</g>`;
  else{const cd=r.free?r.clip:(r.clip||sil);out=cd?`<g clip-path="url(#${clip(cd)})">${s}</g>`:s}
  if(r.edge){
    const es=edgeStrokes(r,hash(did)+i*977+j*31,q),op=[.18,.3,.45];
    out+=`<g fill="${st.sc}" stroke="none"${r.edge.inS&&sil?` clip-path="url(#${clip(sil)})"`:''}>`+es.map((p,u)=>p?`<path d="${p}" fill-opacity="${f2(Math.min(1,op[u]*st.so*1.3*(r.edge.o||1)))}"/>`:'').join('')+'</g>';
  }
  return out;
}
/* pelitos que salen del borde de una forma, para que el contorno no se vea duro */
function edgeStrokes(r,seed,q){
  const key='e'+seed+'|'+q;
  if(r._s&&r._s[key])return r._s[key];
  const N=norm(r),R=rng(seed),out=['','',''],E_=r.edge,Ln=E_.len||[7,15],sp=(E_.sp||3)/Math.max(.4,q);
  let pts=[];
  if(N.poly){
    const sm=N.poly,n=sm.length;
    for(let i=0;i<n;i++){
      const a=sm[(i+n-1)%n],b=sm[i],c=sm[(i+1)%n],d=sm[(i+2)%n];
      for(let t=0;t<1;t+=sp/Math.max(8,Math.hypot(c[0]-b[0],c[1]-b[1]))){
        const t2=t*t,t3=t2*t;
        const g=(k)=>.5*((2*b[k])+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t2+(-a[k]+3*b[k]-3*c[k]+d[k])*t3);
        pts.push([g(0),g(1)]);
      }
    }
  }else if(N.ell){
    const e=N.ell,rx=e[2],ry=e[3]||e[2],ro=(e[4]||0)*Math.PI/180,m=Math.round(Math.PI*(rx+ry)/sp);
    for(let k=0;k<m;k++){const t=2*Math.PI*k/m,x=rx*Math.cos(t),y=ry*Math.sin(t);pts.push([e[0]+x*Math.cos(ro)-y*Math.sin(ro),e[1]+x*Math.sin(ro)+y*Math.cos(ro)])}
  }
  let cx=0,cy=0;pts.forEach(p=>{cx+=p[0];cy+=p[1]});cx/=pts.length;cy/=pts.length;
  const skip=E_.skip;
  pts.forEach(p=>{
    if(skip&&skip(p[0],p[1]))return;
    if(R()>(E_.p==null?.8:E_.p))return;
    const base=Math.atan2(p[1]-cy,p[0]-cx),a=base+(R()-.5)*.9+(E_.sw||0.12);
    const L=Ln[0]+R()*(Ln[1]-Ln[0]),x0=p[0]-Math.cos(base)*3,y0=p[1]-Math.sin(base)*3;
    const dx=Math.cos(a)*L,dy=Math.sin(a)*L,cv=(R()-.5)*L*.5;
    out[Math.floor(R()*3)]+=sliver(x0,y0,dx,dy,cv,a,1.5+R()*.7);
  });
  (r._s=r._s||{})[key]=out;
  return out;
}

let SCN=0;
let SPEED=1;
let PENDING_SHADE=null;
const SPRMAP={};  /* 'img/x.webp' -> 'img/hoja.webp#n' */
const sprOf=src=>{const m=/^(.*)#(\d+)(?:@(\d+)x(\d+)x(\d+)x(\d+))?$/.exec(SPRMAP[src]||'');if(!m)return null;const t=+m[2],w=+(m[3]||800),h=+(m[4]||800),c=+(m[5]||4),rw=+(m[6]||3);return{f:m[1],x:(t%c)*w,y:Math.floor(t/c)*h,w,h,W:c*w,H:rw*h}};  /* velocidad de las animaciones, la elige quien dibuja */
/* Escena: k = paso actual (1...), full = terminado, lite = miniatura */
function scene(d,tk,k,full,lite){
  if(d.img){
    const t2=d.img[tk]?tk:'lapiz',arr=d.img[t2],i=full?arr.length-1:Math.max(0,Math.min(arr.length-1,k-1));
    const PH=d.h||400,TH=lite?400:PH,oy=(TH-PH)/2;  /* hoja ancha: alto propio; en miniaturas va centrada */
    const img=src=>{const sp=sprOf(src);return sp?`<svg x="0" y="${oy}" width="400" height="${PH}" viewBox="${sp.x} ${sp.y} ${sp.w} ${sp.h}"><image href="${sp.f}" x="0" y="0" width="${sp.W}" height="${sp.H}"/></svg>`:`<image href="${src}" x="0" y="${oy}" width="400" height="${PH}" preserveAspectRatio="xMidYMid slice"/>`};
    if(full||lite||i===0)return `<rect width="400" height="${TH}" fill="#fbfaf7"/>${img(arr[i])}`;
    /* contorno: las líneas nuevas se trazan una por una, como a mano */
    const vk=d.vec&&d.vec[String(i+1)];
    const rm=typeof matchMedia!=='undefined'&&matchMedia('(prefers-reduced-motion: reduce)').matches;
    if(vk&&!rm){
      /* muchos trazos (cabello, hojas): se dibujan seguidos y más rápido, para que el paso no dure demasiado */
      /* detalles finos (ojos, nariz, boca, manos...): se respeta el dibujo, solo se quita el temblor */
      const st0=d.steps&&d.steps[i],tt=((st0&&st0.t)||'').toLowerCase();
      let bx0=1e9,by0=1e9,bx1=-1e9,by1=-1e9;for(const [dd] of vk){const n=dd.replace(/[MLQ]/g,' ').trim().split(/[\s,]+/).map(Number);for(let j=0;j+1<n.length;j+=2){bx0=Math.min(bx0,n[j]);bx1=Math.max(bx1,n[j]);by0=Math.min(by0,n[j+1]);by1=Math.max(by1,n[j+1])}}
      const fine=/ojo|nariz|boca|labio|cara|rostro|mano|dedo|oreja|pico|ceja|pesta|iris|pupila|garra|detalle|cera|m[aá]scara|parche|bigote|coraz[oó]n|medalla/.test(tt)||Math.max(bx1-bx0,by1-by0)<110;
      let vc=(d.reveal||d.exact)?vk.map(([dd,len,w])=>[smoothD(dd,true),len,w]):cleanStep(vk,fine);
      if(d.artist&&!d.reveal&&!d.exact)vc=vc.filter(([dd,len])=>len>=(fine?4:12)||vc.length<=6).map(([dd,len])=>[artistLine(dd,fine),len]);
      const nP=vc.length,many=nP>100,tot=vc.reduce((a,p)=>a+p[1],0),dur=many?Math.min(16,4.5+nP*0.008):4.5,sp=Math.max(40,tot/dur);
      const gap=many?0:0.04,mn=many?0.004:0.06;
      let t=0.25,paths='';
      for(const [dd,len,w] of vc){
        const du=Math.max(mn,len/sp)/SPEED;
        paths+=`<path d="${dd}" pathLength="1" style="animation:dr ${du.toFixed(3)}s linear ${t.toFixed(3)}s both${w&&d.exact?`;stroke-width:${Math.max(0.6,w*1.3).toFixed(2)}`:''}"/>`;
        t+=du+gap/SPEED;
      }
      if(d.reveal){  /* dibujo de líneas: la mano va descubriendo la tinta real del dibujo, en rojo */
        const mid='rv'+(++SCN);
        return `<defs><mask id="${mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="400" height="${TH}"><g class="draw" fill="none" stroke="#fff" stroke-width="${d.reveal}" stroke-linecap="round" stroke-linejoin="round">${paths}</g></mask></defs><rect width="400" height="${TH}" fill="#fbfaf7"/>${img(d.vbase?d.vbase(i):arr[i-1])}<g mask="url(#${mid})">${img(arr[i])}</g>`;
      }
      return `<rect width="400" height="${TH}" fill="#fbfaf7"/>${img(d.vbase?d.vbase(i):arr[i-1])}<g class="draw" fill="none" stroke="#F25F3F" stroke-width="${fine?0.9:1.3}" stroke-linecap="round" stroke-linejoin="round">${paths}</g>`;
    }
    /* sombreado: trazos de lápiz que van rellenando la zona nueva */
    const sk=d.svec&&d.svec[String(i+1)];
    if(sk&&sk.length&&!rm){
      const base=(d.sbase&&d.sbase[i])||arr[i-1];
      PENDING_SHADE={src:arr[i],paths:sk};
      return `<rect width="400" height="${TH}" fill="#fbfaf7"/>${img(base)}`;
    }
    /* el paso nuevo aparece como si se fuera dibujando, de arriba hacia abajo */
    const cid='wp'+(++SCN);
    return `<defs><clipPath id="${cid}"><rect x="0" y="0" width="400" height="0"><animate attributeName="height" from="0" to="${TH}" dur="${(1.6/SPEED).toFixed(2)}s" fill="freeze" calcMode="spline" keySplines=".4 0 .2 1" keyTimes="0;1"/></rect></clipPath></defs><rect width="400" height="${TH}" fill="#fbfaf7"/>${img(arr[i-1])}<g clip-path="url(#${cid})">${img(arr[i])}</g>`;
  }
  const T=TECH[tk],steps=d.steps,upto=full?steps.length:k;
  const id='s'+(++SCN);let cn=0,clips='';const cmap={};
  const clip=dd=>{
    if(dd&&dd.out){
      const a2=Array.isArray(dd.out)?dd.out:[dd.out],k2='out|'+a2.join('|');
      if(cmap[k2])return cmap[k2];
      const i2=id+'m'+(++cn);
      clips+=`<mask id="${i2}" maskUnits="userSpaceOnUse" x="0" y="0" width="400" height="400"><rect width="400" height="400" fill="#fff"/>${a2.map(p=>`<path d="${p}" fill="#000"/>`).join('')}</mask>`;
      return cmap[k2]=i2;
    }
    const arr=Array.isArray(dd)?dd:[dd],key=arr.join('|');
    if(cmap[key])return cmap[key];
    const i=id+'c'+(++cn);
    clips+=`<clipPath id="${i}">${arr.map(p=>`<path d="${p}"/>`).join('')}</clipPath>`;
    return cmap[key]=i;
  };
  const q=lite?.3:1;
  let body=`<rect width="400" height="400" fill="${T.paper}"/>`;
  let tg='';
  for(let i=0;i<upto;i++){
    const s=steps[i];if(!s.T)continue;
    const isNew=!full&&i===k-1;
    tg+=`<g${isNew?' class="pop"':''}>`+s.T.map((r,j)=>reg(r,d.id,i,j,T,clip,q,d.sil)).join('')+'</g>';
  }
  if(tg)body+=`<g filter="url(#${T.ff})">${tg}</g>`;
  const cur=full?null:steps[k-1];
  const contourPhase=!!cur&&!cur.T;
  const LS=contourPhase?SKETCH:T.line;
  let guides='',solid='',now='';
  for(let i=0;i<upto;i++){
    const s=steps[i],isCur=!full&&i===k-1,w=s.w||1;
    if(contourPhase&&s.G)guides+=`<g${isCur?' class="pop"':''} opacity="${isCur?1:.4}">`+s.G.map(p=>`<path d="${p}"/>`).join('')+'</g>';
    if(s.L){
      if(isCur&&contourPhase)now+=s.L.map((p,j)=>`<path d="${p}" pathLength="1" style="animation-duration:${(.9/SPEED).toFixed(2)}s;animation-delay:${(j*.14/SPEED).toFixed(2)}s"/>`).join('');
      else solid+=`<g stroke-width="${f2(LS.w*w)}">`+s.L.map(p=>`<path d="${p}"/>`).join('')+'</g>';
    }
  }
  if(guides)body+=`<g fill="none" stroke="#5B7CFF" stroke-width="1.5" stroke-dasharray="5 6" stroke-linecap="round">${guides}</g>`;
  if(solid)body+=`<g fill="none" stroke="${LS.c}" stroke-linecap="round" stroke-linejoin="round" opacity="${f2(contourPhase?LS.o:LS.o*(d.lo||1))}" filter="url(#${LS.f})">${solid}</g>`;
  if(now)body+=`<g class="draw" fill="none" stroke="#FF5A36" stroke-width="${f2(LS.w*(cur.w||1)+1.3)}" stroke-linecap="round" stroke-linejoin="round">${now}</g>`;
  if(cur&&cur.T){
    const hl=cur.T.filter(r=>r.k!=='line'&&!r.nohl).map(r=>`<path d="${norm(r).d}"/>`).join('');
    if(hl)body+=`<g class="hl" fill="none" stroke="#FF5A36" stroke-width="1.5" stroke-dasharray="5 5" stroke-linecap="round" opacity=".85">${hl}</g>`;
  }
  body+=`<rect width="400" height="400" fill="#fff" filter="url(#${T.pf})" opacity="${T.po}" style="mix-blend-mode:multiply;pointer-events:none"/>`;
  return `<defs>${clips}</defs>`+body;
}
const swatch=k=>{
  const T=TECH[k];let cp='';
  const cl=dd=>{cp=`<clipPath id="swc-${k}"><path d="${dd}"/></clipPath>`;return 'swc-'+k};
  const a=reg({e:[190,215,150],k:'fur',v:.8,c:'#D9822B',n:.6},'sw'+k,0,0,T,cl,1,null);
  const b=reg({e:[255,140,85],k:'soft',v:.6,c:'#FFD36B'},'sw'+k,0,1,T,cl,1,null);
  return `<svg viewBox="0 0 400 400" aria-hidden="true"><defs>${cp}</defs><rect width="400" height="400" fill="${T.paper}"/><g filter="url(#${T.ff})">${a}${b}</g></svg>`;
};

/* Sombreado animado en un lienzo (funciona igual en Safari, Chrome y Android):
   la imagen nueva se descubre siguiendo trazos de lápiz de ida y vuelta */
let SHADE=null;
function stopShade(){if(SHADE){cancelAnimationFrame(SHADE.raf);SHADE.cv.remove();SHADE=null}}
/* trazo limpio: quita el "temblor" de escalera de píxeles y dibuja curvas suaves, como una mano firme */
const SMC=new Map(),SMP=new Map(),CLN=new WeakMap();
function smoothD(d,fine){
  const ck=fine?'f'+d:d;const c=SMC.get(ck);if(c)return c;
  const n=d.replace(/[MLQ]/g,' ').trim().split(/[\s,]+/).map(Number);let P=[];
  for(let j=0;j+1<n.length;j+=2)P.push([n[j],n[j+1]]);
  if(P.length<3){SMC.set(ck,d);return d}
  /* 1) densificar para que el suavizado sea parejo */
  const D=[P[0]];for(let j=1;j<P.length;j++){const a=P[j-1],b=P[j],L=Math.hypot(b[0]-a[0],b[1]-a[1]),k=Math.max(1,Math.ceil(L/1.5));for(let t=1;t<=k;t++)D.push([a[0]+(b[0]-a[0])*t/k,a[1]+(b[1]-a[1])*t/k])}
  const closed=Math.hypot(D[0][0]-D[D.length-1][0],D[0][1]-D[D.length-1][1])<1.5&&D.length>8;
  /* 2) promedio móvil (3 pasadas), sin mover las puntas de una línea abierta */
  let S=D;const W=fine?1:Math.max(1,Math.min(5,Math.floor(D.length/9)));
  for(let it=0;it<(fine?1:3);it++){const m=S.length,o=[];for(let j=0;j<m;j++){if(!closed&&(j===0||j===m-1)){o.push(S[j]);continue}let x=0,y=0,c2=0;for(let q=-W;q<=W;q++){let k=j+q;if(closed)k=(k+m)%m;else if(k<0||k>=m)continue;x+=S[k][0];y+=S[k][1];c2++}o.push([x/c2,y/c2])}S=o}
  if(closed){  /* las figuras cerradas conservan su tamaño (el suavizado las encoge) */
    const cen=A=>A.reduce((a,p)=>[a[0]+p[0]/A.length,a[1]+p[1]/A.length],[0,0]),rad=(A,c)=>A.reduce((a,p)=>a+Math.hypot(p[0]-c[0],p[1]-c[1]),0)/A.length;
    const c0=cen(D),c1=cen(S),k=rad(D,c0)/(rad(S,c1)||1);S=S.map(p=>[c1[0]+(p[0]-c1[0])*k,c1[1]+(p[1]-c1[1])*k]);
  }
  /* 3) simplificar (Douglas-Peucker) y dibujar con curvas */
  const rdp=(a,b,eps,out)=>{let mx=0,mi=-1;const A=S[a],B=S[b],dx=B[0]-A[0],dy=B[1]-A[1],L=Math.hypot(dx,dy)||1;for(let j=a+1;j<b;j++){const dd=Math.abs(dy*S[j][0]-dx*S[j][1]+B[0]*A[1]-B[1]*A[0])/L;if(dd>mx){mx=dd;mi=j}}if(mx>eps){rdp(a,mi,eps,out);rdp(mi,b,eps,out)}else out.push(b)};
  const K=[0];rdp(0,S.length-1,fine?0.25:0.6,K);const Q=K.map(j=>S[j]);
  const f=v=>v.toFixed(1);let s=`M${f(Q[0][0])} ${f(Q[0][1])}`;
  if(Q.length===2)s+=`L${f(Q[1][0])} ${f(Q[1][1])}`;
  else{for(let j=1;j<Q.length-1;j++){const mxp=(Q[j][0]+Q[j+1][0])/2,myp=(Q[j][1]+Q[j+1][1])/2;s+=`Q${f(Q[j][0])} ${f(Q[j][1])} ${f(mxp)} ${f(myp)}`}const z=Q[Q.length-1];s+=`L${f(z[0])} ${f(z[1])}`}
  SMC.set(ck,s);if(!fine)SMP.set(d,Q);return s;
}
/* una sola línea: quita las líneas dobles o triples que corren juntas (los dos bordes de un trazo grueso)
   y las rayitas cortas sueltas. Se queda con la línea más larga y de las demás solo lo que no repite. */
function cleanStep(vk,fine){
  const c=CLN.get(vk);if(c)return c;
  if(fine){const res=vk.map(([d,len])=>[smoothD(d,true),len]);CLN.set(vk,res);return res}
  const GW=400,GH=800,G=new Uint8Array(GW*GH),R=2.4,busy=vk.length>6;
  const dens=pts=>{const S=[pts[0]];for(let j=1;j<pts.length;j++){const a=pts[j-1],b=pts[j],L=Math.hypot(b[0]-a[0],b[1]-a[1]),k=Math.max(1,Math.ceil(L));for(let t=1;t<=k;t++)S.push([a[0]+(b[0]-a[0])*t/k,a[1]+(b[1]-a[1])*t/k])}return S};
  const raw=vk.map(([d,len],i)=>{smoothD(d);let pts=SMP.get(d);
    if(!pts){const n=d.replace(/[MLQ]/g,' ').trim().split(/[\s,]+/).map(Number);pts=[];for(let j=0;j+1<n.length;j+=2)pts.push([n[j],n[j+1]])}
    return{i,d,S:dens(pts)}});
  /* unir tramos que siguen el mismo camino: así cada mechón o contorno es una sola línea */
  const used=new Uint8Array(raw.length),dir=(S,end)=>{const n=S.length,k=Math.min(5,n-1);const a=end?S[n-1]:S[0],b=end?S[n-1-k]:S[k];const L=Math.hypot(a[0]-b[0],a[1]-b[1])||1;return[(a[0]-b[0])/L,(a[1]-b[1])/L]};
  const order=raw.map((_,j)=>j).sort((p,q)=>raw[q].S.length-raw[p].S.length),items=[];
  for(const s0 of order){if(used[s0])continue;used[s0]=1;let C=raw[s0].S.slice(),mi=raw[s0].i,joined=false;
    for(const side of [1,0]){for(let guard=0;guard<60;guard++){const P=side?C[C.length-1]:C[0],D=dir(C,side);let best=-1,bd=3.2,flip=false;
      for(let j=0;j<raw.length;j++){if(used[j])continue;const S=raw[j].S;if(S.length<2)continue;
        for(const e of [0,1]){const Q=e?S[S.length-1]:S[0],dd=Math.hypot(Q[0]-P[0],Q[1]-P[1]);if(dd>=bd)continue;const In=dir(S,e);if(-(In[0]*D[0]+In[1]*D[1])<0.35)continue;best=j;bd=dd;flip=!!e}}
      if(best<0)break;used[best]=1;joined=true;mi=Math.min(mi,raw[best].i);let S=raw[best].S.slice();
      if(side){if(flip)S.reverse();C=C.concat(S)}else{if(!flip)S.reverse();C=S.concat(C)}}}
    let d=raw[s0].d;if(joined){d='M'+C[0][0].toFixed(1)+' '+C[0][1].toFixed(1);for(let j=1;j<C.length;j++)d+='L'+C[j][0].toFixed(1)+' '+C[j][1].toFixed(1);smoothD(d);C=dens(SMP.get(d)||C)}
    items.push({i:mi,d,len:C.length,S:C})}
  const cov=p=>{const x=Math.round(p[0]),y=Math.round(p[1]);return x>=0&&y>=0&&x<GW&&y<GH&&G[y*GW+x]};
  const mark=p=>{const cx=Math.round(p[0]),cy=Math.round(p[1]),r=Math.ceil(R);for(let dy=-r;dy<=r;dy++)for(let dx=-r;dx<=r;dx++){if(dx*dx+dy*dy>R*R)continue;const x=cx+dx,y=cy+dy;if(x>=0&&y>=0&&x<GW&&y<GH)G[y*GW+x]=1}};
  const out=[];
  for(const it of [...items].sort((a,b)=>b.len-a.len)){
    const S=it.S,minL=busy?6:2;
    if(busy&&it.len<minL)continue;
    const f=S.map(cov),nc=f.filter(v=>!v).length;
    const fr=nc/S.length;
    if(fr>0.7){out.push({i:it.i,o:0,d:smoothD(it.d),len:it.len});S.forEach(mark);continue}  /* casi no repite: la línea completa */
    if(fr<0.4)continue;  /* casi toda repite otra línea: fuera */
    /* repite en parte: solo los tramos nuevos (los huecos cortitos se unen para no cortar la línea) */
    const g=f.slice();for(let j=0;j<g.length;){if(!g[j]){j++;continue}let k=j;while(k<g.length&&g[k])k++;if(j>0&&k<g.length&&k-j<=5)for(let q=j;q<k;q++)g[q]=0;j=k}
    let run=[],o=0;const flush=()=>{if(run.length>=8){let s='M'+run[0][0].toFixed(1)+' '+run[0][1].toFixed(1);for(let j=2;j<run.length;j+=2)s+='L'+run[j][0].toFixed(1)+' '+run[j][1].toFixed(1);const z=run[run.length-1];s+='L'+z[0].toFixed(1)+' '+z[1].toFixed(1);out.push({i:it.i,o:o++,d:s,len:run.length});run.forEach(mark)}run=[]};
    S.forEach((p,j)=>{if(!g[j])run.push(p);else flush()});flush();
  }
  out.sort((a,b)=>a.i-b.i||a.o-b.o);
  const res=out.map(x=>[x.d,x.len]);CLN.set(vk,res);return res;
}
/* trazo de artista: cada línea se vuelve pocos trazos largos (recta o un solo arco), sin ondulaciones */
function artistLine(d,fine){
  const n=d.replace(/[MLQ]/g,' ').trim().split(/[\s,]+/).map(Number),P=[];for(let j=0;j+1<n.length;j+=2)P.push([n[j],n[j+1]]);
  if(P.length<3)return d;
  const eps=fine?0.9:2.2,K=[0];
  const rdp=(a,b)=>{let mx=0,mi=-1;const A=P[a],B=P[b],dx=B[0]-A[0],dy=B[1]-A[1],L=Math.hypot(dx,dy)||1;for(let j=a+1;j<b;j++){const dd=Math.abs(dy*P[j][0]-dx*P[j][1]+B[0]*A[1]-B[1]*A[0])/L;if(dd>mx){mx=dd;mi=j}}if(mx>eps){rdp(a,mi);rdp(mi,b)}else K.push(b)};
  rdp(0,P.length-1);const Q=K.map(j=>P[j]),f=v=>v.toFixed(1);
  let s=`M${f(Q[0][0])} ${f(Q[0][1])}`;
  if(Q.length===2)return s+`L${f(Q[1][0])} ${f(Q[1][1])}`;
  /* esquinas muy cerradas se respetan; las suaves se vuelven arco */
  for(let j=1;j<Q.length-1;j++){const a=Q[j-1],b=Q[j],c=Q[j+1],u=[b[0]-a[0],b[1]-a[1]],v=[c[0]-b[0],c[1]-b[1]],cs=(u[0]*v[0]+u[1]*v[1])/((Math.hypot(...u)*Math.hypot(...v))||1);
    if(cs<-0.2){s+=`L${f(b[0])} ${f(b[1])}`;continue}
    const m=[(b[0]+c[0])/2,(b[1]+c[1])/2];s+=`Q${f(b[0])} ${f(b[1])} ${f(m[0])} ${f(m[1])}`}
  const z=Q[Q.length-1];return s+`L${f(z[0])} ${f(z[1])}`;
}
function runShade(host){
  stopShade();
  const job=PENDING_SHADE;PENDING_SHADE=null;
  if(!job||!host)return;
  const cv=document.createElement('canvas');cv.className='shade';host.appendChild(cv);
  const r=host.querySelector('#cv').getBoundingClientRect();
  const dpr=Math.min(2,window.devicePixelRatio||1),W=Math.round(r.width*dpr),H=Math.round(r.height*dpr);
  cv.width=W;cv.height=H;
  Object.assign(cv.style,{position:'absolute',left:'0',top:'0',width:'100%',height:'100%',pointerEvents:'none'});
  const ctx=cv.getContext('2d'),mk=document.createElement('canvas');mk.width=W;mk.height=H;const mc=mk.getContext('2d');
  const k=W/400;mc.lineCap='round';mc.lineJoin='round';mc.lineWidth=5.4*k;mc.strokeStyle='#000';
  const P=job.paths.map(([d,len])=>{const n=d.replace(/[ML]/g,' ').trim().split(/[\s,]+/).map(Number),pts=[];for(let j=0;j+1<n.length;j+=2)pts.push([n[j]*k,n[j+1]*k]);return{pts,len}});
  const tot=P.reduce((a,p)=>a+p.len,0),speed=Math.max(120,tot/5.5);/* unidades por segundo a velocidad normal */
  const sp=sprOf(job.src),im=new Image();im.src=sp?sp.f:job.src;const dI=()=>sp?ctx.drawImage(im,sp.x,sp.y,sp.w,sp.h,0,0,W,H):ctx.drawImage(im,0,0,W,H);
  const st={cv,raf:0,t:0,last:0,pi:0,seg:0,done:false};SHADE=st;
  let drawnLen=0;
  const frame=now=>{
    if(SHADE!==st)return;
    if(!st.last)st.last=now;
    const dt=Math.min(.1,(now-st.last)/1000);st.last=now;
    if(!(typeof PAUSED!=='undefined'&&PAUSED)&&im.complete){
      let budget=dt*speed*SPEED*k;
      let guard=0;
      while(budget>0&&st.pi<P.length&&guard++<20000){
        const p=P[st.pi].pts;
        if(st.seg>=p.length-1){st.pi++;st.seg=0;st.part=0;continue}
        const a=p[st.seg],b=p[st.seg+1],L=Math.hypot(b[0]-a[0],b[1]-a[1]);
        if(!(L>0.5)){st.seg++;st.part=0;continue}  /* tramo sin largo: se salta (antes trababa la app) */
        const f=st.part||0,take=Math.min(L*(1-f),budget),nf=f+take/(L||1);
        mc.beginPath();mc.moveTo(a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f);mc.lineTo(a[0]+(b[0]-a[0])*nf,a[1]+(b[1]-a[1])*nf);mc.stroke();
        budget-=take;
        if(nf>=0.999){st.seg++;st.part=0}else st.part=nf;
      }
      ctx.globalCompositeOperation='source-over';ctx.clearRect(0,0,W,H);
      if(st.pi>=P.length){dI();st.done=true;return}
      dI();ctx.globalCompositeOperation='destination-in';ctx.drawImage(mk,0,0);
    }
    st.raf=requestAnimationFrame(frame);
  };
  st.raf=requestAnimationFrame(frame);
}
