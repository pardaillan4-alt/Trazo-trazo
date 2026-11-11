/* Ayudas para armar formas: todo en un lienzo de 400 x 400 */
const f=n=>Math.round(n*10)/10;
const D=[];
const add=o=>D.push(o);
/* elipse (o círculo) con rotación opcional */
const E=(x,y,rx,ry=rx,a=0)=>{
  const t=a*Math.PI/180,dx=rx*Math.cos(t),dy=rx*Math.sin(t);
  return `M${f(x-dx)} ${f(y-dy)}A${rx} ${ry} ${a} 1 0 ${f(x+dx)} ${f(y+dy)}A${rx} ${ry} ${a} 1 0 ${f(x-dx)} ${f(y-dy)}Z`;
};
/* polígono, cerrado o abierto */
const P=(pts,close=true)=>'M'+pts.map(q=>f(q[0])+' '+f(q[1])).join('L')+(close?'Z':'');
/* rectángulo redondeado */
const RR=(x,y,w,h,r)=>`M${x+r} ${y}H${x+w-r}A${r} ${r} 0 0 1 ${x+w} ${y+r}V${y+h-r}A${r} ${r} 0 0 1 ${x+w-r} ${y+h}H${x+r}A${r} ${r} 0 0 1 ${x} ${y+h-r}V${y+r}A${r} ${r} 0 0 1 ${x+r} ${y}Z`;
/* curva suave que pasa por los puntos */
const S=(p,closed=true)=>{
  const n=p.length;
  const g=i=>closed?p[((i%n)+n)%n]:p[Math.max(0,Math.min(n-1,i))];
  let d='M'+f(p[0][0])+' '+f(p[0][1]);
  const m=closed?n:n-1;
  for(let i=0;i<m;i++){
    const a=g(i-1),b=g(i),c=g(i+1),e=g(i+2);
    d+=`C${f(b[0]+(c[0]-a[0])/6)} ${f(b[1]+(c[1]-a[1])/6)} ${f(c[0]-(e[0]-b[0])/6)} ${f(c[1]-(e[1]-b[1])/6)} ${f(c[0])} ${f(c[1])}`;
  }
  return d+(closed?'Z':'');
};
/* reflejo horizontal de una lista de puntos */
const MX=pts=>pts.map(q=>[400-q[0],q[1]]);
/* rayos alrededor de un centro */
const rays=(cx,cy,n,r1,r2,hw,close)=>{
  let d='';
  for(let i=0;i<n;i++){
    const t=i*2*Math.PI/n-Math.PI/2,a=t-hw,b=t+hw;
    d+=P([[cx+r1*Math.cos(a),cy+r1*Math.sin(a)],[cx+r2*Math.cos(t),cy+r2*Math.sin(t)],[cx+r1*Math.cos(b),cy+r1*Math.sin(b)]],close);
  }
  return d;
};
/* estrella de cuatro puntas */
const star=(x,y,r)=>P([[x,y-r],[x+r*.3,y-r*.3],[x+r,y],[x+r*.3,y+r*.3],[x,y+r],[x-r*.3,y+r*.3],[x-r,y],[x-r*.3,y-r*.3]]);
/* ola: n tramos de 40 de ancho */
const wave=(x,y,n)=>`M${x} ${y}q20 -16 40 0`+'t40 0'.repeat(n-1);
/* nube festoneada alrededor de una elipse */
const puff=(cx,cy,rx,ry,n,r)=>{
  const pt=k=>{const t=2*Math.PI*k/n-Math.PI/2;return [cx+rx*Math.cos(t),cy+ry*Math.sin(t)]};
  const p0=pt(0);let d=`M${f(p0[0])} ${f(p0[1])}`;
  for(let k=1;k<=n;k++){const q=pt(k%n);d+=`A${r} ${r} 0 0 1 ${f(q[0])} ${f(q[1])}`}
  return d+'Z';
};
