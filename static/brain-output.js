// Optional API-backed planning. A canceled or slow plan cannot hold up the match narration.
function brainErrorMessage(detail,fallback){
 if(typeof detail==='string'&&detail.trim())return detail;
 if(Array.isArray(detail)){
  const messages=detail.map(item=>{
   if(typeof item==='string')return item;
   if(item&&typeof item==='object'){
    const location=Array.isArray(item.loc)?item.loc.filter(part=>part!=='body').join(' → '):'';
    const message=typeof item.msg==='string'?item.msg:'';
    return [location,message].filter(Boolean).join(': ');
   }
   return '';
  }).filter(Boolean);
  if(messages.length)return messages.join('; ');
 }
 if(detail&&typeof detail==='object'){
  for(const key of ['message','error','msg','detail'])if(typeof detail[key]==='string'&&detail[key].trim())return detail[key];
 }
 return fallback;
}
class BrainOutput {
 constructor(){this.enabled=true;this.status=null;this.message='Verificando a configuração da IA…';}
 async load(){
  try{
   const response=await fetch('/api/brain/status');
   if(!response.ok)throw new Error();
   this.status=await response.json();this.message=this.status.message;
  }catch{this.status=null;this.message='Não foi possível carregar a configuração da IA. Reinicie o programa.';}
 }
 async saveSettings(settings){
  const response=await fetch('/api/brain/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(settings)});
  const body=await response.json().catch(()=>({}));
  if(!response.ok)throw new Error(brainErrorMessage(body.detail,'Não foi possível salvar a configuração da IA.'));
  this.status=body;this.message=body.message;
  return body;
 }
 async listModels(settings){
  const response=await fetch('/api/brain/models',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(settings)});
  const body=await response.json().catch(()=>({}));
  if(!response.ok)throw new Error(brainErrorMessage(body.detail,'Não foi possível buscar os modelos.'));
  return Array.isArray(body.models)?body.models:[];
 }
 async prepare(){
  const response=await fetch('/api/brain/test',{method:'POST'});
  const body=await response.json().catch(()=>({}));
  if(!response.ok){this.message=brainErrorMessage(body.detail,'Não foi possível conectar à IA.');if(this.status)this.status={...this.status,ready:false,message:this.message};throw new Error(this.message);}
  this.status=body;this.message=body.message;
 }
 async compose(item,state,signal){
  if(!this.enabled||!this.status?.ready||item.kind!=='analysis')return item.text;
  const controller=new AbortController(),cancel=()=>controller.abort();
  signal.addEventListener('abort',cancel,{once:true});
  if(signal.aborted)controller.abort();
  const timeout=setTimeout(cancel,13000);
  const payload={text:item.text,kind:item.kind,profile:state?.narration?.commentaryProfile||'balanced'};
  if(item.panorama&&item.kind==='analysis'&&state?.phase!=='pre'){
   const radio=new RadioCommentary();
   payload.choices=radio.candidates(state).slice(0,8).map(fact=>fact.text);
   const moment=state.phase==='post'?'Partida encerrada.':state.status==='INTERVALO'?'Intervalo.':state.source==='manual'?'Dados do controle manual.':radio.clock(state)?`Na última atualização, ${radio.clock(state)}.`:'Na última informação recebida.';
   payload.anchor=moment+' '+radio.score(state);
  }
  try{
   const response=await fetch('/api/brain/compose',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:controller.signal});
   if(!response.ok)return item.text;
   const result=await response.json();
   return typeof result.text==='string'?result.text:item.text;
  }catch{return item.text;}
  finally{clearTimeout(timeout);signal.removeEventListener('abort',cancel);}
 }
}
