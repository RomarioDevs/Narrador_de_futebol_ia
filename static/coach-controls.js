let coachDraftKey='',coachPhotoDraft='',coachDirty=false;
function renderCoachControls(s,force=false){
 const select=$('coachSide');if(!select)return;
 for(const side of ['home','away'])select.querySelector(`[value="${side}"]`).textContent=s[side]?.name||side;
 const side=select.value,key=JSON.stringify([side,s[side]?.source_name||s[side]?.name]);
 if(!force&&key===coachDraftKey&&coachDirty)return;
 coachDraftKey=key;coachDirty=false;
 const manual=s.coach_overrides?.[side];
 $('coachName').value=manual?.name||'';coachPhotoDraft=manual?.photo||'';
 const automatic=(s.ge?.ready?s.ge.coaches?.[side]:null)||s.coaches?.[side]||s.catalog_coaches?.[side];
 $('coachAutomatic').textContent=automatic?.name?`Automático: ${automatic.name} · ${automatic.source||'fonte da partida'}`:'Técnico ainda não informado pelas fontes.';
 $('coachManualStatus').textContent=manual?'Cadastro manual ativo para este time.':'Usando os dados disponíveis nas fontes.';
 updateCoachPhoto();
}
function updateCoachPhoto(){const img=$('coachPhotoPreview');img.hidden=!coachPhotoDraft;if(coachPhotoDraft)img.src=coachPhotoDraft;else img.removeAttribute('src')}
$('coachSide').onchange=()=>renderCoachControls(S,true);
$('coachName').oninput=()=>{coachDirty=true};
$('coachPhotoUpload').onchange=async event=>{
 const file=event.target.files[0],key=coachDraftKey;event.target.value='';if(!file)return;
 try{
  if(!['image/png','image/jpeg','image/webp'].includes(file.type)||file.size>5*1024*1024)throw new Error('Use PNG, JPG ou WebP de até 5 MB.');
  const bitmap=await createImageBitmap(file);bitmap.close();
  const response=await fetch('/api/appearance/upload',{method:'POST',headers:{'Content-Type':file.type},body:file});
  const result=await response.json();if(!response.ok)throw new Error(result.detail||'Falha no envio da foto.');
  if(key!==coachDraftKey)return;
  coachPhotoDraft=result.url;coachDirty=true;updateCoachPhoto();notice('Foto preparada. Clique em Salvar técnico.');
 }catch(error){notice(error.message,true)}
};
$('coachRemovePhoto').onclick=()=>{coachPhotoDraft='';coachDirty=true;updateCoachPhoto()};
$('saveCoach').onclick=async()=>{
 if(!S)return;const side=$('coachSide').value;
 try{await post('/api/coaches/manual',{side,team:S[side].source_name||S[side].name,name:$('coachName').value,photo:coachPhotoDraft});coachDirty=false;await load();renderCoachControls(S,true);notice('Técnico salvo para este time.')}catch(error){notice(error.message,true)}
};
$('resetCoach').onclick=async()=>{
 if(!S)return;const side=$('coachSide').value;
 try{await post('/api/coaches/manual',{side,team:S[side].source_name||S[side].name,reset:true});coachDirty=false;await load();renderCoachControls(S,true);notice('Dados automáticos restaurados.')}catch(error){notice(error.message,true)}
};
