from snap import *
S=np.load('S.npy',allow_pickle=True).item()
t=np.linspace(0,2*np.pi,60)
F={}
F['cara']=S['cara']
F['ceja']=[crm([(210,294),(222,286),(237,280),(252,277),(267,276),(281,278)]),crm([(130,322),(142,316),(155,314),(167,316),(175,320)])]
F['ojo']=[crm([(232,328),(243,322),(255,318),(268,313),(283,306)]),crm([(238,331),(248,334),(260,333),(272,326)]),
          crm([(143,362),(152,357),(165,354),(178,355),(188,360)]),crm([(148,366),(160,368),(172,367),(185,362)])]
F['nariz']=[crm([(185,355),(188,375),(193,392),(200,402)]),crm([(200,401),(205,410),(215,414),(228,410),(238,404),(245,405)])]
F['boca']=[crm([(215,443),(228,438),(242,433),(256,428),(270,423)]),crm([(218,440),(225,432),(236,426),(248,423),(260,421),(270,422)]),
           crm([(218,445),(228,452),(242,455),(256,450),(266,438),(270,425)])]
F['cuello']=[S['cuello'][0],snap([(348,458),(351,500),(354,545)],6),S['cuello'][2]]
F['cabello']=S['pelo_izq']+S['pelo_der']
F['velo']=S['velo_izq']+S['velo_izq_int']+S['velo_der_oro']+S['velo_azul']+S['manto_izq']+S['forro']
F['manos']=[snap([(304,700),(288,705),(268,722),(252,755),(242,795),(240,835),(246,872),(262,905),(285,935),(310,958),(338,975)],7),
            snap([(306,702),(328,722),(345,750),(358,790),(368,830),(375,870),(373,910),(362,945),(345,973)],7),
            snap([(296,712),(302,770),(312,830),(322,890),(332,945),(338,975)],5)]
F['punos']=S['punos']
B=np.load('bordes.npy',allow_pickle=True)
vm=np.zeros((H,W),np.uint8)
for p in S['velo_izq']: pass
poly=np.vstack([S['velo_izq'][0],S['velo_azul'][0][::-1]]).astype(np.int32)
cv2.fillPoly(vm,[poly],1); vm[575:,:]=1; vm=cv2.dilate(vm,np.ones((9,9),np.uint8))
F['rayos']=[p for p in B if vm[np.clip(np.round(p[:,1]).astype(int),0,H-1),np.clip(np.round(p[:,0]).astype(int),0,W-1)].mean()<0.2 and np.sum(np.hypot(*np.diff(p,axis=0).T))>50]
def star(c,r=11):
    a=np.linspace(0,2*np.pi,17); rr=np.where(np.arange(17)%2==0,r,r*0.35)
    return np.stack([c[0]+rr*np.sin(a),c[1]-rr*np.cos(a)],1).astype(np.float32)
F['estrellas']=[star(c) for c in [(395,195),(447,340),(527,488),(130,575),(590,605),(45,655),(120,758),(565,748),(50,840),(560,880),(20,1000),(570,1075)]]
np.save('F.npy',np.array(F,dtype=object)); print({k:len(v) for k,v in F.items()})
show(F,'final.jpg')
