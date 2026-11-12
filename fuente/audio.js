/* Voz natural (síntesis del dispositivo) y música ambiental generada */
const SND={voice:true,music:true,vol:.5,rate:.94,vname:'',mood:'suave',motor:'disp',nv:'mx-f'};
try{Object.assign(SND,JSON.parse(localStorage.getItem('trazo-snd')||'{}'))}catch(e){}
const saveSnd=()=>{try{localStorage.setItem('trazo-snd',JSON.stringify(SND))}catch(e){}};

/* ---------- Voz ---------- */
const TTS='speechSynthesis' in window;
let VOICES=[];
const vscore=v=>{
  const l=(v.lang||'').toLowerCase().replace('_','-');let s=0;
  if(!l.startsWith('es'))return -1;
  if(/es-(mx|us|419)/.test(l))s+=4;else if(/es-(ar|co|cl|pe)/.test(l))s+=2;else s+=1;
  if(/natural|neural|online|premium|enhanced|siri/i.test(v.name))s+=6;
  if(/google/i.test(v.name))s+=3;
  if(/paulina|sabina|monica|mónica|helena|dalia|lupe|paloma|marisol|elena|sofia|sofía|camila|valentina/i.test(v.name))s+=2;
  if(!v.localService)s+=1;
  return s;
};
function loadVoices(){
  if(!TTS)return;
  VOICES=speechSynthesis.getVoices().filter(v=>vscore(v)>=0).sort((a,b)=>vscore(b)-vscore(a));
  if(window.fillVoiceList)fillVoiceList();
}
if(TTS){loadVoices();speechSynthesis.onvoiceschanged=loadVoices}
const pickVoice=()=>VOICES.find(v=>v.name===SND.vname)||VOICES[0]||null;
let speakTimer=0,speakId=0;
function stopSpeak(){clearTimeout(speakTimer);speakId++;if(TTS)speechSynthesis.cancel();nvCallar();duck(false)}
/* se habla por frases, con respiros y un ritmo que varía un poco, como una persona */
function chunks(text){
  const out=[];
  text.replace(/\s+/g,' ').trim().split(/(?<=[.!?¡¿:])\s+/).forEach(s=>{
    if(s.length<=150){out.push(s);return}
    s.split(/(?<=[,;])\s+/).reduce((acc,p)=>{
      if(acc.length&&(acc[acc.length-1]+' '+p).length<130)acc[acc.length-1]+=' '+p;else acc.push(p);return acc;
    },[]).forEach(x=>out.push(x));
  });
  return out.filter(Boolean);
}
function speak(text,force){
  if(!SND.voice&&!force)return;
  if(usaNV()){stopSpeak();nvHablar(text,speakId);return}
  if(!TTS)return;
  stopSpeak();
  hablarDisp(text,speakId);
}
function hablarDisp(text,my,desde){
  const parts=chunks(text).slice(desde||0),v=pickVoice();
  speakTimer=setTimeout(()=>{
    let i=0;
    const next=()=>{
      if(my!==speakId)return;
      if(i>=parts.length){duck(false);return}
      const t=parts[i],u=new SpeechSynthesisUtterance(t);
      if(v){u.voice=v;u.lang=v.lang}else u.lang='es-MX';
      const q=/\?$/.test(t),ex=/!$/.test(t);
      u.rate=Math.max(.6,Math.min(1.3,SND.rate*(.97+Math.random()*.06)*(i===0?.98:1)));
      u.pitch=1+(q?.06:0)+(ex?.04:0)+(Math.random()-.5)*.05;
      u.volume=1;
      u.onstart=()=>{if(my===speakId)duck(true)};
      u.onend=()=>{if(my!==speakId)return;i++;const gap=/[.!?]$/.test(t)?230+Math.random()*120:110;speakTimer=setTimeout(next,gap)};
      u.onerror=()=>{if(my===speakId)duck(false)};
      speechSynthesis.speak(u);
    };
    next();
  },90);
}

/* ---------- Voz natural (las voces de Atril) ----------
   Modelos VITS de Piper para español de México, generados en el dispositivo con sherpa-onnx y espeak-ng
   (WebAssembly, en trabajadores). Se descargan una vez y se guardan en este navegador (IndexedDB). */
const NV_DIR='voz/',NV_V='nv1';
const NV_CORE=[{f:'voz.wasm',n:13403088},{f:'fonetica.wasm',n:405867},{f:'espeak-es.wasm',n:697085}];
const NV_VOCES={
  'mx-f':{nom:'Mujer',nota:'Cálida y pausada, la más natural',parts:5,size:62949322},
  'mx-m':{nom:'Hombre',nota:'Grave y serena',parts:5,size:63149200},
  'mx-f-lite':{nom:'Mujer',nota:'Versión ligera',parts:2,size:18304617,lite:true},
  'mx-m-lite':{nom:'Hombre',nota:'Versión ligera',parts:2,size:18579723,lite:true}};
const NV_OK=typeof WebAssembly==='object'&&'Worker' in window&&'indexedDB' in window;
const NV={keys:null,pp:null,tts:null,voz:null,cargando:null,audio:null,dl:null,falla:false,sr:22050};
const IDB={p:null,
  db(){return this.p||(this.p=new Promise((res,rej)=>{let r;try{r=indexedDB.open('trazo-voz',1)}catch(e){rej(e);return}
    r.onupgradeneeded=()=>r.result.createObjectStore('b');r.onsuccess=()=>res(r.result);r.onerror=()=>rej(r.error)}))},
  async op(modo,fn){const db=await this.db();return new Promise((res,rej)=>{const t=db.transaction('b',modo),q=fn(t.objectStore('b'));
    t.oncomplete=()=>res(q&&q.result);t.onerror=t.onabort=()=>rej(t.error||new Error('no se pudo guardar'))})},
  get(k){return this.op('readonly',s=>s.get(k))},put(k,v){return this.op('readwrite',s=>s.put(v,k))},
  del(k){return this.op('readwrite',s=>s.delete(k))},keys(){return this.op('readonly',s=>s.getAllKeys())}};
async function nvKeys(){
  if(NV.keys)return NV.keys;
  let ks=[];try{ks=await IDB.keys()}catch(e){}
  NV.keys=new Set((ks||[]).filter(k=>typeof k==='string'&&k.startsWith(NV_V+':')).map(k=>k.slice(NV_V.length+1)));
  return NV.keys;
}
const nvTiene=k=>!!(NV.keys&&NV.keys.has(k));
const nvInstalada=id=>nvTiene('voz:'+id+':modelo')&&nvTiene('voz:'+id+':tokens')&&NV_CORE.every(c=>nvTiene('base:'+c.f));
const nvFalta=id=>(nvTiene('voz:'+id+':modelo')?0:NV_VOCES[id].size)+NV_CORE.reduce((a,c)=>a+(nvTiene('base:'+c.f)?0:c.n),0);
const usaNV=()=>NV_OK&&SND.motor==='nv'&&!NV.falla&&nvInstalada(SND.nv);
async function nvBajarArchivo(f,signal,onB){
  let r;try{r=await fetch(NV_DIR+f,{signal})}catch(e){if(e&&e.name==='AbortError')throw e;throw new Error('no hay conexión')}
  if(!r.ok)throw new Error('el archivo '+f+' no está disponible');
  if(!r.body||!r.body.getReader){const b=await r.blob();onB(b.size);return b}
  const rd=r.body.getReader(),ch=[];
  for(;;){const {done,value}=await rd.read();if(done)break;ch.push(value);onB(value.length)}
  return new Blob(ch);
}
async function nvDescargar(id,onProg){
  const v=NV_VOCES[id];await nvKeys();
  const jobs=[];
  for(const c of NV_CORE)if(!nvTiene('base:'+c.f))jobs.push({k:'base:'+c.f,fs:[c.f],n:c.n});
  if(!nvTiene('voz:'+id+':modelo'))jobs.push({k:'voz:'+id+':modelo',fs:Array.from({length:v.parts},(_,i)=>id+'.'+i+'.wasm'),n:v.size});
  if(!nvTiene('voz:'+id+':tokens'))jobs.push({k:'voz:'+id+':tokens',fs:[id+'.tokens.txt'],n:1000});
  const total=jobs.reduce((a,j)=>a+j.n,0)||1;let hecho=0;
  const ac=new AbortController();NV.dl={id,ac,frac:0};
  try{
    for(const j of jobs){
      const bl=[];
      for(const f of j.fs)bl.push(await nvBajarArchivo(f,ac.signal,d=>{hecho+=d;NV.dl.frac=Math.min(1,hecho/total);onProg&&onProg(NV.dl.frac)}));
      try{await IDB.put(NV_V+':'+j.k,new Blob(bl))}catch(e){throw new Error('no hay espacio suficiente en el navegador')}
      NV.keys.add(j.k);
    }
    try{navigator.storage&&navigator.storage.persist&&navigator.storage.persist()}catch(e){}
    NV.falla=false;return true;
  }finally{NV.dl=null}
}
const nvCancelar=()=>{if(NV.dl)NV.dl.ac.abort()};
async function nvBorrar(id){
  if(NV.voz===id)nvApagar();
  await nvKeys();
  for(const k of ['voz:'+id+':modelo','voz:'+id+':tokens']){try{await IDB.del(NV_V+':'+k)}catch(e){}NV.keys.delete(k)}
  if(!Object.keys(NV_VOCES).some(x=>nvTiene('voz:'+x+':modelo'))){
    for(const c of NV_CORE){try{await IDB.del(NV_V+':base:'+c.f)}catch(e){}NV.keys.delete('base:'+c.f)}
    if(NV.pp){NV.pp.kill();NV.pp=null}
  }
}
function nvTrabajador(f){
  const o={pend:new Map(),n:0,dead:false};
  o.ready=new Promise((res,rej)=>{o._res=res;o._rej=rej});o.ready.catch(()=>{});
  const falla=m=>{o.dead=true;o._rej(new Error(m));for(const[,cb]of o.pend)cb({error:m});o.pend.clear()};
  try{o.w=new Worker(NV_DIR+f)}catch(e){falla('el navegador no permite iniciar la voz');return o}
  o.w.onmessage=e=>{const m=e.data||{};
    if(m.type==='ready')o._res(m);else if(m.type==='error')falla(m.message||'error');
    else if(m.type!=='log'){const cb=o.pend.get(m.id);if(cb){o.pend.delete(m.id);cb(m)}}};
  o.w.onerror=e=>{try{e.preventDefault()}catch(x){}falla('el motor de voz se detuvo')};
  o.call=(msg,tr)=>new Promise(res=>{if(o.dead){res({error:'el motor de voz se detuvo'});return}const id=++o.n;o.pend.set(id,res);o.w.postMessage(Object.assign({id},msg),tr||[])});
  o.post=(msg,tr)=>o.w.postMessage(msg,tr||[]);
  o.kill=()=>{o.dead=true;try{o.w.terminate()}catch(e){}};
  return o;
}
const conTiempo=(p,ms,m)=>Promise.race([p,new Promise((_,rej)=>setTimeout(()=>rej(new Error(m)),ms))]);
async function nvBlob(k){const b=await IDB.get(NV_V+':'+k);if(!b){if(NV.keys)NV.keys.delete(k);throw new Error('faltan archivos de la voz; vuelve a descargarla')}return b}
async function nvIniciar(id){
  if(NV.tts&&NV.voz===id&&!NV.tts.dead)return true;
  if(NV.cargando&&NV.voz===id)return NV.cargando;
  nvApagar();NV.voz=id;
  const run=(async()=>{
    await nvKeys();if(!nvInstalada(id))throw new Error('la voz no está descargada');
    if(!NV.pp||NV.pp.dead){
      const [fw,es]=await Promise.all([nvBlob('base:fonetica.wasm'),nvBlob('base:espeak-es.wasm')]);
      const pp=nvTrabajador('fonetica.js'),a=await fw.arrayBuffer(),b=await es.arrayBuffer();
      if(!pp.dead)pp.post({type:'init',wasm:a,data:b},[a,b]);
      await conTiempo(pp.ready,45000,'la voz tardó demasiado en cargar');NV.pp=pp;
    }
    const [vw,mo,tk]=await Promise.all([nvBlob('base:voz.wasm'),nvBlob('voz:'+id+':modelo'),nvBlob('voz:'+id+':tokens')]);
    const w=nvTrabajador('voz.js'),wasm=await vw.arrayBuffer(),mb=await mo.arrayBuffer();
    if(!w.dead)w.post({type:'init',wasm,model:mb,tokens:await tk.text()},[wasm,mb]);
    const info=await conTiempo(w.ready,90000,'la voz tardó demasiado en cargar');
    NV.sr=info.sampleRate||22050;
    if(NV.voz!==id){w.kill();return false}
    NV.tts=w;return true;
  })();
  NV.cargando=run;
  try{return await run}finally{if(NV.cargando===run)NV.cargando=null}
}
function nvApagar(){if(NV.tts){NV.tts.kill();NV.tts=null}NV.voz=null}
function wavBlob(i16,sr){
  const buf=new ArrayBuffer(44),v=new DataView(buf),n=i16.length*2,w=(o,s)=>{for(let i=0;i<s.length;i++)v.setUint8(o+i,s.charCodeAt(i))};
  w(0,'RIFF');v.setUint32(4,36+n,true);w(8,'WAVE');w(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);
  v.setUint32(24,sr,true);v.setUint32(28,sr*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);w(36,'data');v.setUint32(40,n,true);
  return new Blob([buf,i16.buffer],{type:'audio/wav'});
}
// recorta los silencios del modelo, iguala el volumen y deja la pausa natural después de la frase
function nvPost(s,sr,pausa){
  const thr=.008;let a=0,b=s.length-1;
  while(a<b&&Math.abs(s[a])<thr)a++;while(b>a&&Math.abs(s[b])<thr)b--;
  a=Math.max(0,a-Math.round(sr*.025));b=Math.min(s.length-1,b+Math.round(sr*.07));
  const body=s.subarray(a,b+1);let sum=0,n=0,pk=0;
  for(let i=0;i<body.length;i++){const x=Math.abs(body[i]);if(x>pk)pk=x;if(x>.02){sum+=x*x;n++}}
  const rms=n?Math.sqrt(sum/n):.12;let g=Math.max(.6,Math.min(3,.15/rms));if(pk*g>.93)g=.93/pk;
  const lead=Math.round(sr*.015),pad=Math.round(sr*Math.max(0,pausa)/1000),out=new Int16Array(lead+body.length+pad),fade=Math.max(1,Math.min(Math.round(sr*.006),body.length>>2));
  for(let i=0;i<body.length;i++){let v=body[i]*g;if(i<fade)v*=i/fade;else if(i>body.length-fade)v*=(body.length-i)/fade;out[lead+i]=Math.max(-1,Math.min(1,v))*32767}
  return URL.createObjectURL(wavBlob(out,sr));
}
const NV_CACHE=new Map();
async function nvClip(t,pausa){
  const k=NV.voz+'|'+SND.rate+'|'+pausa+'|'+t;
  if(NV_CACHE.has(k))return NV_CACHE.get(k);
  const p=(async()=>{
    const ph=await NV.pp.call({type:'ph',text:t,voice:'es-419'});if(ph.error)throw new Error(ph.error);
    const cps=(ph.sentences&&ph.sentences[0])||[];if(!cps.length)return null;
    const r=await NV.tts.call({type:'gen',codepoints:cps,speed:Math.max(.6,Math.min(1.4,SND.rate))});if(r.error)throw new Error(r.error);
    return nvPost(r.samples,r.sampleRate||NV.sr,pausa);
  })();
  NV_CACHE.set(k,p);p.catch(()=>NV_CACHE.delete(k));
  if(NV_CACHE.size>40){const k0=NV_CACHE.keys().next().value;const v0=NV_CACHE.get(k0);NV_CACHE.delete(k0);v0.then(u=>u&&URL.revokeObjectURL(u),()=>{})}
  return p;
}
function nvAudio(){if(!NV.audio){const a=new Audio();a.preload='auto';a.setAttribute('playsinline','');NV.audio=a}return NV.audio}
function nvCallar(){const a=NV.audio;if(a){a.onended=null;a.onerror=null;try{a.pause()}catch(e){}}}
// lee frase por frase; mientras suena una, ya se prepara la siguiente
async function nvHablar(text,my){
  const parts=chunks(text);if(!parts.length)return;
  const pausa=i=>i>=parts.length-1?0:/[.!?]$/.test(parts[i])?260:120;
  let i=0;
  try{
    await nvIniciar(SND.nv);if(my!==speakId)return;
    const a=nvAudio();
    const sig=async()=>{
      if(my!==speakId)return;
      if(i>=parts.length){duck(false);return}
      const url=await nvClip(parts[i],pausa(i));if(my!==speakId)return;
      if(i+1<parts.length)nvClip(parts[i+1],pausa(i+1)).catch(()=>{});
      i++;if(!url){sig();return}
      a.onended=()=>{if(my===speakId)sig()};a.onerror=()=>{if(my===speakId)sig()};
      a.src=url;a.volume=1;duck(true);
      try{await a.play()}catch(e){if(my===speakId)duck(false)}
    };
    await sig();
  }catch(e){
    if(my!==speakId)return;
    console.warn('Voz natural',e);NV.falla=true;nvApagar();
    if(window.avisoVoz)avisoVoz('No se pudo usar la voz natural en este dispositivo. Sigo con la voz del dispositivo.');
    if(TTS)hablarDisp(text,my,Math.max(0,i-1));
  }
}

if(NV_OK)nvKeys();

/* ---------- Música ---------- */
let AC=null,master,duckG,verb,musicOn=false,timer=0,nextChord=0,nextNote=0,chordI=0;
const NOTE=m=>440*Math.pow(2,(m-69)/12);
const MOODS={
  suave:{chords:[[48,55,64,71],[45,52,60,67],[41,48,57,64],[43,50,59,66]],scale:[72,74,76,79,81,84],len:7,pad:'sine',pl:'triangle',dens:.55,pv:.5},
  bosque:{chords:[[38,45,53,60],[36,43,50,57],[41,48,55,62],[38,45,52,60]],scale:[62,65,67,69,72,74],len:9,pad:'triangle',pl:'sine',dens:.4,pv:.55},
  piano:{chords:[[48,55,60,64],[43,50,59,62],[45,52,60,64],[41,48,57,60]],scale:[60,64,67,72,76,79],len:6,pad:'sine',pl:'triangle',dens:.8,pv:.8}
};
function initAudio(){
  if(AC)return true;
  const C=window.AudioContext||window.webkitAudioContext;
  if(!C)return false;
  try{
    AC=new C();
    master=AC.createGain();master.gain.value=SND.vol*.55;
    duckG=AC.createGain();duckG.gain.value=1;
    verb=AC.createConvolver();
    const n=AC.sampleRate*3,buf=AC.createBuffer(2,n,AC.sampleRate);
    for(let c=0;c<2;c++){const d=buf.getChannelData(c);for(let i=0;i<n;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/n,2.6)}
    verb.buffer=buf;
    const wet=AC.createGain();wet.gain.value=.55;
    verb.connect(wet);wet.connect(duckG);
    master.connect(duckG);master.connect(verb);
    duckG.connect(AC.destination);
  }catch(e){AC=null;return false}
  return true;
}
function tone(m,t,dur,type,vol,att){
  const o=AC.createOscillator(),g=AC.createGain(),f=AC.createBiquadFilter();
  o.type=type;o.frequency.value=NOTE(m);o.detune.value=(Math.random()-.5)*8;
  f.type='lowpass';f.frequency.value=type==='sine'?1800:1300;
  g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(vol,t+att);
  g.gain.exponentialRampToValueAtTime(.0001,t+dur);
  o.connect(f);f.connect(g);g.connect(master);
  o.start(t);o.stop(t+dur+.1);
}
function tick(){
  if(!AC||!musicOn)return;
  const M=MOODS[SND.mood]||MOODS.suave,now=AC.currentTime;
  while(nextChord<now+1.5){
    const ch=M.chords[chordI++%M.chords.length];
    ch.forEach((m,i)=>tone(m,nextChord+i*.12,M.len+2,M.pad,.05,2.2));
    nextChord+=M.len;
  }
  while(nextNote<now+1.2){
    if(Math.random()<M.dens){
      const sc=M.scale,m=sc[(Math.random()*sc.length)|0];
      tone(m,nextNote,2.6,M.pl,.085*M.pv,.015);
    }
    nextNote+=.55+Math.random()*.9;
  }
}
function startMusic(){
  if(!SND.music||!initAudio())return;
  if(AC.state==='suspended')AC.resume();
  if(musicOn)return;
  musicOn=true;chordI=0;
  nextChord=nextNote=AC.currentTime+.2;
  tick();timer=setInterval(tick,300);
  master.gain.cancelScheduledValues(0);
  master.gain.setValueAtTime(0,AC.currentTime);
  master.gain.linearRampToValueAtTime(SND.vol*.55,AC.currentTime+2);
}
function stopMusic(){
  if(!AC||!musicOn)return;
  musicOn=false;clearInterval(timer);
  master.gain.cancelScheduledValues(0);
  master.gain.setTargetAtTime(0,AC.currentTime,.4);
}
function setVol(v){SND.vol=v;if(AC&&musicOn)master.gain.setTargetAtTime(v*.55,AC.currentTime,.1)}
function duck(on){if(AC)duckG.gain.setTargetAtTime(on?.3:1,AC.currentTime,.25)}
/* los navegadores solo dejan sonar tras un toque: arranca con el primero */
['pointerdown','keydown'].forEach(ev=>addEventListener(ev,function f(){
  if(SND.music)startMusic();
  removeEventListener(ev,f);
},{once:false}));
