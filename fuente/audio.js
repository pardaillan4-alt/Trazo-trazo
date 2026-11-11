/* Voz natural (síntesis del dispositivo) y música ambiental generada */
const SND={voice:true,music:true,vol:.5,rate:.94,vname:'',mood:'suave'};
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
function stopSpeak(){clearTimeout(speakTimer);speakId++;if(TTS)speechSynthesis.cancel();duck(false)}
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
  if(!TTS||(!SND.voice&&!force))return;
  stopSpeak();
  const my=speakId,parts=chunks(text),v=pickVoice();
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
