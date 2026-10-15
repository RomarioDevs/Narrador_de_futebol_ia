// Short commentary grounded in the current snapshot, with no simulated play-by-play.
class RadioCommentary {
 constructor(){this.reported=new Map();}
 pair(s,key,max=Infinity){
  const values=s.stats?.[key];
  if(!Array.isArray(values)||values.length!==2)return null;
  if(values.some(v=>v==null||v===''||!Number.isFinite(Number(v))||Number(v)<0||Number(v)>max))return null;
  return values.map(Number);
 }
 number(value){return Number(value).toLocaleString('pt-BR',{maximumFractionDigits:1});}
 candidates(s){
  const result=[],home=s.home.name,away=s.away.name;
  const shots=this.pair(s,'shots'),on=this.pair(s,'shots_on'),possession=this.pair(s,'possession',100);
  const add=(key,values,text,source={name:s.source||'Dados da partida'})=>result.push({key,id:key,signature:JSON.stringify(values),text,source});
  if(shots){
   const validOn=on&&on.every((v,i)=>v<=shots[i]);
   let text=`Nas finalizações, ${home} tem ${this.number(shots[0])} e ${away}, ${this.number(shots[1])}.`;
   if(validOn)text+=` No gol, são ${this.number(on[0])} a ${this.number(on[1])}.`;
   add('shots',[shots,validOn?on:null],text);
  }else if(on)add('shots',[null,on],`Finalizações no gol: ${home}, ${this.number(on[0])}. ${away}, ${this.number(on[1])}.`);
  if(possession&&Math.abs(possession[0]+possession[1]-100)<=1){
   let text=`Na posse de bola, ${home} tem ${this.number(possession[0])} por cento e ${away}, ${this.number(possession[1])} por cento.`;
   if(shots){
    const leader=possession[0]>=55?0:possession[1]>=55?1:null;
    if(leader!==null&&shots[leader]<shots[1-leader])text+=` Apesar de mais posse, ${leader===0?home:away} soma menos finalizações.`;
   }
   add('possession',[possession,shots],text);
  }
  for(const [key,label] of [['corners','Escanteios'],['fouls','Faltas cometidas'],['offsides','Impedimentos']]){
   const values=this.pair(s,key);
   if(values)add(key,values,`${label} na partida: ${home}, ${this.number(values[0])}. ${away}, ${this.number(values[1])}.`);
  }
  const accuracy=this.pair(s,'pass_accuracy',100);
  if(accuracy)add('accuracy',accuracy,`Precisão de passe: ${home}, ${this.number(accuracy[0])} por cento. ${away}, ${this.number(accuracy[1])} por cento.`);
  if(s.phase==='pre')for(const side of ['home','away']){
   const rows=(s.recent_form?.[side]||[]).filter(row=>['V','E','D'].includes(row.result)).slice(0,5);
   if(rows.length){
    const counts={V:0,E:0,D:0};rows.forEach(row=>counts[row.result]++);
    const latest=rows[0];
    const recent=latest?.opponent?` O resultado mais recente foi ${latest.result} contra ${latest.opponent}${latest.score?`, por ${latest.score}`:''}${latest.competition?`, em ${latest.competition}`:''}.`:'';
    add(`form:${side}`,rows.map(row=>[row.result,row.opponent,row.score,row.date]),`Nos últimos ${rows.length} resultados informados para ${s[side].name}: ${counts.V} vitórias, ${counts.E} empates e ${counts.D} derrotas.${recent}`,{name:s.data_sources?.recent_form||s.source||'ESPN'});
   }
  }
  const top=(s.youtube_chat?.top_players||[]).filter(item=>item?.name&&Number(item.count)>0).slice(0,3);
  if(top.length)add('chat-top',top.map(item=>[item.name,item.count]),`No chat da transmissão, os nomes mais comentados são ${top.map(item=>`${item.name}, com ${item.count} menções`).join('; ')}.`);
  const players=[...['home','away'].flatMap(side=>[...(s.lineups?.[side]?.starters||[]),...(s.lineups?.[side]?.bench||[])])];
  players.filter(player=>player?.name&&player.match_stats&&Object.keys(player.match_stats).length).slice(0,3).forEach(player=>{
   const stats=player.match_stats, parts=[];
   if(stats.totalGoals!=null)parts.push(`${stats.totalGoals} gol(s)`);
   if(stats.goalAssists!=null)parts.push(`${stats.goalAssists} assistência(s)`);
   if(stats.shots!=null)parts.push(`${stats.shots} finalização(ões)`);
   if(parts.length)add('player:'+player.id,parts,`${player.name} aparece nas estatísticas da partida com ${parts.join(', ')}.`);
  });
  if(s.news_context?.include_in_voice===true)for(const fact of (s.news_context.facts||[]).slice(0,3))if(fact?.text)add('news:'+fact.id,[fact.id],fact.text,fact.source||{name:'Notícia'});
  return result;
 }
 reset(s){this.reported=new Map(this.candidates(s).map(c=>[c.key,c.signature]));}
 next(s){
  const candidate=this.candidates(s).find(c=>this.reported.get(c.key)!==c.signature);
  if(!candidate)return '';
  this.reported.set(candidate.key,candidate.signature);
  return {...candidate,text:candidate.text};
 }
 score(s){
  if([s.home.score,s.away.score].some(v=>v==null||v===''||!Number.isFinite(Number(v))))return 'Placar não informado.';
  return `No placar, ${s.home.name}, ${s.home.score}. ${s.away.name}, ${s.away.score}.`;
 }
 clock(s){
  const value=String(s.clock_display??s.minute??'').replace(/['′\s]/g,'').match(/^(\d+)(?:\+(\d+))?$/);
  return value?`${value[1]} minutos${value[2]?`, mais ${value[2]} de acréscimo`:''}`:'';
 }
 snapshot(s){
  const intro=`Você acompanha ${s.home.name} e ${s.away.name}${s.competition?' pela '+s.competition:''}.`;
  if(s.phase==='pre'){
   const ranks=['home','away'].map(side=>{
    const r=s.standings?.[side];
    return r?.rank&&r.points!=null?`${s[side].name}: posição ${r.rank}, com ${r.points} pontos.`:'';
   }).filter(Boolean).join(' ');
   return `${intro} Pré-jogo.${ranks?' Na classificação informada pela fonte: '+ranks:''}`;
  }
  const moment=s.phase==='post'?'Partida encerrada.':s.status==='INTERVALO'?'Intervalo.':s.source==='manual'?'Dados do controle manual.':this.clock(s)?`Na última atualização, ${this.clock(s)}.`:'Na última informação recebida.';
  const numbers=this.candidates(s).slice(0,2).map(c=>c.text).join(' ');
  this.reset(s);
  return `${intro} ${moment} ${this.score(s)}${numbers?' '+numbers:''}`;
 }
 stage(s){
  const phase=s.phase==='post'?'post':s.status==='INTERVALO'?'half':s.phase==='pre'?'pre':'live';
  const intro={pre:`Começa nossa cobertura de ${s.home.name} e ${s.away.name}${s.competition?' pela '+s.competition:''}.`,half:'Intervalo da partida. Vamos ao balanço do primeiro tempo.',post:'Partida encerrada. Vamos ao balanço final.',live:'Vamos ao panorama da partida.'}[phase];
  const parts=[intro+(phase==='pre'?'':` ${this.score(s)}`)];
  if(phase==='pre'){
   if(s.venue)parts.push(`O palco informado para o jogo é ${s.venue}.`);
   for(const side of ['home','away']){
    const coach=s.lineups?.[side]?.coach;
    const name=typeof coach==='string'?coach:coach?.name;
    if(name)parts.push(`${s[side].name} tem no comando ${name}.`);
    const form=(s.recent_form?.[side]||[]).filter(row=>['V','E','D'].includes(row.result)).slice(0,5);
    if(form.length){
     const counts={V:0,E:0,D:0};form.forEach(row=>counts[row.result]++);
     const latest=form[0];
     parts.push(`Nos últimos ${form.length} resultados informados, ${s[side].name} teve ${counts.V} vitórias, ${counts.E} empates e ${counts.D} derrotas.${latest?.opponent?` O mais recente foi ${latest.result} contra ${latest.opponent}${latest.score?`, por ${latest.score}`:''}.`:''}`);
    }
    const table=s.standings?.[side];
    if(table?.rank&&table.points!=null)parts.push(`Na tabela informada do campeonato, ${s[side].name} ocupa a posição ${table.rank}, com ${table.points} pontos.`);
   }
  }else parts.push(...this.candidates(s).slice(0,3).map(c=>c.text));
  if(phase==='post')parts.push('Obrigado pela companhia nesta transmissão. Até a próxima partida!');
  return parts;
 }
 fresh(s){
  if(s.phase!=='in'||s.status==='INTERVALO'||s.source==='manual')return false;
  const received=Date.parse(s.updated_at);
  return Number.isFinite(received)&&Date.now()-received>=-5000&&Date.now()-received<=90000;
 }
}
