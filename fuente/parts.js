/* Partes reutilizables: ojos, reflejo en el agua, etc. */
const rev=a=>a.slice().reverse();
const MXC=pts=>rev(MX(pts));          /* espejo que conserva el sentido de giro */
/* contorno de un ojo almendrado; flip=1: la esquina interna queda a la derecha */
const eyePts=(cx,cy,r,flip=1)=>{
  const m=(dx,dy)=>[cx+flip*dx*r,cy+dy*r];
  return [m(-1.15,.08),m(-.45,-.78),m(.45,-.82),m(1.1,.12),m(.4,.75),m(-.4,.72)];
};
/* capas de un ojo: base (iris), mid (sombra del párpado), dark (pupila y borde), light (brillos) */
const eyeT=(cx,cy,r,flip,col,pw=.46,ph=.6)=>{
  const pts=eyePts(cx,cy,r,flip),sil=S(pts),ix=cx+flip*.04*r;
  return{
    base:[{p:pts,k:'soft',v:.04,c:'#F4F1E8',b:1.5,nohl:1},{e:[ix,cy+.02*r,.8*r,.8*r],clip:sil,k:'soft',v:.4,c:col,b:1.5,nohl:1}],
    mid:[{e:[cx,cy-.6*r,1.15*r,.5*r],clip:sil,k:'soft',v:.55,c:mix(col,'#2a2a1a',.55),b:2.5,nohl:1}],
    dark:[
      {k:'line',d:[S([pts[0],pts[1],pts[2],pts[3]],false)],w:1.9,o:.9,c:'#1d1a17'},
      {k:'line',d:[E(ix,cy+.02*r,.8*r)],w:1.2,o:.7,c:mix(col,'#1d1a17',.65)},
      {e:[ix,cy+.02*r,pw*r,ph*r],clip:sil,k:'solid',v:1,c:'#14110e',nohl:1}
    ],
    light:[
      {e:[ix-.3*r,cy-.3*r,.2*r],clip:sil,k:'solid',v:1,lt:1,c:'#fffdf5',nohl:1},
      {e:[ix+.28*r,cy+.3*r,.09*r],clip:sil,k:'solid',v:.9,lt:1,c:'#fffdf5',nohl:1}
    ]
  };
};
/* trazos horizontales de reflejo o hierba, repartidos al azar dentro de una banda */
const band=(x0,y0,x1,y1)=>[[x0,y0],[x1,y0],[x1,y1],[x0,y1]];
/* pino: polígono con ramas en pisos */
const pine=(x,yb,h,w)=>{
  const n=4,y0=yb-h,R=[],L=[];
  for(let i=1;i<=n;i++){
    const yy=y0+h*.9*i/n,ww=w*i/n/2;
    R.push([x+ww*.5,yy-h*.07],[x+ww,yy]);
    L.unshift([x-ww,yy],[x-ww*.5,yy-h*.07]);
  }
  return [[x,y0]].concat(R,[[x+3,yb],[x-3,yb]],L);
};
/* línea poligonal abierta (picos de montaña) */
const poly=(pts)=>P(pts,false);
