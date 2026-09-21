'use strict';
// Pixal3D surface with a Blender-authored rig and seated performance. One simulation pose is shared by all passes.
const BRIAR_DRAGON_PERCH=BRIAR_DRAGON_MODEL.perch;
const BRIAR_DRAGON_CYCLE=120;
function briarDragonEase(x){x=clamp(x,0,1);return x*x*(3-2*x);}
function briarCreateDragon(scene){
 const dragon={time:0,parts:[],bones:new Float32Array(BRIAR_DRAGON_MODEL.bones.length*16),palette:new Float32Array(24*16),global:[],model:I,fire:0,flames:[],jetOrigins:new Float32Array(17*3),jetDirections:new Float32Array(17*3),behavior:'perched'};scene.dragon=dragon;
 // Publish ownership before allocation so the normal failed-room path cleans up.
 const source=BRIAR_DRAGON_MODEL,input=safariSkinDecode(source.vertexData,Float32Array),indices=safariSkinDecode(source.indexData,Uint32Array);
 for(const part of source.draws){
  if(part.bones.length>24)throw new Error('Dragon draw exceeds native bone palette.');
  const ids=new Map(),vertices=[],elements=[];
  for(const triangle of part.triangles)for(let k=0;k<3;k++){
   const id=indices[triangle*3+k];if(!ids.has(id)){
    ids.set(id,vertices.length/19);const row=Array.from(input.slice(id*19,(id+1)*19));
    for(let j=0;j<4;j++)row[8+j]=row[12+j]>0?part.bones.indexOf(row[8+j]):0;
    vertices.push(...row);
   }elements.push(ids.get(id));
  }
  dragon.parts.push({bones:part.bones,mesh:safariSkinMesh({vertices:vertices.length/19,vertexData:new Float32Array(vertices),indexData:new Uint32Array(elements),texture:source.texture},101,dragon.parts[0]?.mesh)});
 }
 briarUpdateDragon(scene,0);
}
function briarUpdateDragon(scene,dt){
 const d=scene.dragon;if(!d)return;
 if(!reduceMotion)d.time=(d.time+Math.max(0,dt))%BRIAR_DRAGON_CYCLE;
 const t=reduceMotion?0:d.time,source=BRIAR_DRAGON_MODEL;
 // Give the room a quiet opening, then one complete fire performance every
 // two minutes. The existing flame shader keeps its authored 7–17s clock.
 d.fireTime=t-20;
 const active=!reduceMotion&&d.fireTime>=0&&d.fireTime<source.actionDuration;
 const localTime=active?d.fireTime:t%source.actionDuration;
 const frames=active?source.actions.ritual:source.actions.watch,sample=localTime*source.actionSampleRate,fi=Math.floor(sample),fraction=sample-fi,global=[];
 d.fire=reduceMotion?0:briarDragonEase((d.fireTime-7)/.7)*(1-briarDragonEase((d.fireTime-12)/1.3));
 d.behavior=!active?'resting':d.fireTime<4.3?'watching':d.fireTime<7?'inhaling':d.fireTime<13.3?'breathing fire':d.fireTime<19?'settling':'resting';
 for(let i=0;i<source.bones.length;i++){
  const bone=source.bones[i],pose=safariSkinTRS(frames[fi][i],frames[Math.min(frames.length-1,fi+1)][i],fraction);
  const matrix=bone.parent===null?pose:mm(global[bone.parent],pose);
  global.push(matrix);d.bones.set(mm(matrix,bone.inverseBind),i*16);
 }
 d.global=global;d.model=mm(trans(...BRIAR_DRAGON_PERCH),ry(-PI/2));
 const head=source.bones.findIndex(b=>b.name==='head'),skin=mm(global[head],source.bones[head].inverseBind),mouth=transform(source.mouth,skin),tip=transform(add(source.mouth,[1,0,0]),skin);
 d.mouth=transform(mouth,d.model);d.direction=norm(sub(transform(tip,d.model),d.mouth));
 if(d.fireTime>7&&d.fireTime<17){
  // Sample the authored head pose at each particle's birth. A moving muzzle
  // must not drag previously emitted fire around with the present head pose.
  const chain=[];for(let i=head;i!==null;i=source.bones[i].parent)chain.unshift(i);
  for(let i=0;i<17;i++){
   const sample=clamp(d.fireTime-i/6,0,source.actionDuration)*source.actionSampleRate,fi=Math.floor(sample),fraction=sample-fi;let pose=I;
   for(const id of chain)pose=mm(pose,safariSkinTRS(source.actions.ritual[fi][id],source.actions.ritual[Math.min(source.actions.ritual.length-1,fi+1)][id],fraction));
   const matrix=mm(d.model,mm(pose,source.bones[head].inverseBind)),origin=transform(source.mouth,matrix),tip=transform(add(source.mouth,[1,0,0]),matrix);
   d.jetOrigins.set(origin,i*3);d.jetDirections.set(norm(sub(tip,origin)),i*3);
  }
 }
}
function briarDrawDragon(scene,p){
 const d=scene.dragon;if(!d)return;
 if(p===mainProgram){gl.activeTexture(gl.TEXTURE6);gl.bindTexture(gl.TEXTURE_2D,d.parts[0].mesh.skinTexture);gl.uniform1i(uniform(p,'uWildlifeCoat'),6);gl.activeTexture(gl.TEXTURE2);}
 for(const part of d.parts){
  for(let i=0;i<part.bones.length;i++)d.palette.set(d.bones.subarray(part.bones[i]*16,part.bones[i]*16+16),i*16);
  um(p,'uWildlifeBones[0]',d.palette);draw(part.mesh,d.model,p);
 }
}

// A scoped line light follows the simulated jet. Every room resets the uniform,
// including the map; it never leaks fire illumination into another exhibit.
function briarSetFireLight(scene,p,model=I){
 if(p!==mainProgram)return;const d=scene?.dragon,intensity=d?.fire||0;
 const start=intensity?transform(d.mouth,model):[0,0,0],end=intensity?transform(add(d.mouth,mul(d.direction,8)),model):start;
 gl.uniform4f(uniform(p,'uDragonLight'),...start,intensity*(12+Math.sin((d?.time||0)*31)*1.5));uv3(p,'uDragonLightEnd',end);uf(p,'uDragonLightScale',Math.hypot(model[0],model[1],model[2]));
}
const BRIAR_FIRE_VS=`#version 300 es
precision highp float;
uniform mat4 uVP,uRoom;uniform vec3 uEye,uJetOrigins[17],uJetDirections[17];uniform float uTime;
out vec2 vUV;out float vAge,vKind,vSeed,vStrength;
float hash(float n){return fract(sin(n*127.1+311.7)*43758.5453);}
void main(){
 int id=gl_InstanceID;float k=float(id);vKind=id<28?0.:id<140?1.:2.;
 float seed=hash(k+7.);vSeed=seed;float age=fract(uTime*(vKind==0.?.36:vKind==1.?1.10:.63)+seed);
 float lifetime=vKind==0.?2.6:vKind==1.?.91:1.6;
 float birth=uTime-age*lifetime;
 // Particles retain their travel after ignition stops instead of blinking off.
 vStrength=smoothstep(7.,7.35,birth)*(1.-smoothstep(12.,13.25,birth));vAge=age;
 float speed=vKind==0.?7.5:vKind==1.?17.:15.;float dist=age*speed*lifetime;
 float history=min(age*lifetime*6.,16.);int hi=int(floor(history)),hj=min(hi+1,16);
 vec3 origin=mix(uJetOrigins[hi],uJetOrigins[hj],fract(history));
 vec3 axis=normalize(mix(uJetDirections[hi],uJetDirections[hj],fract(history))),side=normalize(cross(axis,vec3(0.,1.,0.))),up=normalize(cross(side,axis));
 float spread=(.08+age*age*(vKind==0.?2.5:vKind==1.?2.3:3.4));
 float angle=hash(k*17.+2.)*6.283185+age*(vKind==0.?2.:5.);
 vec3 center=origin+axis*(.15+dist)+side*(sin(angle)*spread)+up*(cos(angle*1.3)*spread);
 center.y+=vKind==0.?age*age*3.8:vKind==2.?age*age*.8:age*age*.9;
 if(vKind==0.)center+=axis*5.;
 vec3 world=(uRoom*vec4(center,1.)).xyz;float roomScale=length(uRoom[0].xyz);
 vec3 forward=normalize(uEye-world),right=normalize(cross(vec3(0.,1.,0.),forward)),rise=cross(forward,right);
 vec2 corners[6]=vec2[6](vec2(-1,-1),vec2(1,-1),vec2(1,1),vec2(-1,-1),vec2(1,1),vec2(-1,1));
 vec2 q=corners[gl_VertexID];vUV=q;
 float size=vKind==0.?(1.1+age*1.8):vKind==1.?(.22+age*1.12):(.016+seed*.026);
 float turn=seed*6.283185+age;mat2 rotation=mat2(cos(turn),sin(turn),-sin(turn),cos(turn));vec2 offset=rotation*q*size*roomScale;
 if(vKind==2.)offset.y*=2.8;
 gl_Position=uVP*vec4(world+right*offset.x+rise*offset.y,1.);
}`;
const BRIAR_FIRE_FS=`#version 300 es
precision highp float;
in vec2 vUV;in float vAge,vKind,vSeed,vStrength;uniform float uTime;out vec4 frag;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
float fbm(vec2 p){return .57*noise(p)+.28*noise(p*2.03+8.)+.15*noise(p*4.11-3.);}
void main(){
 if(vStrength<.001)discard;
 vec2 q=vUV;float radius=length(q);float n=fbm(q*3.2+vec2(vSeed*21.,-uTime*2.4));
 float body=1.-radius+n*.48-.20;float alpha=smoothstep(.02,.40,body);
 float tail=1.-smoothstep(.65,1.,vAge);alpha*=tail*vStrength;
 if(vKind<.5){alpha*=.12*smoothstep(0.,.16,vAge);vec3 smoke=mix(vec3(.033,.026,.022),vec3(.10,.074,.045),n);frag=vec4(smoke*alpha,alpha);}
 else if(vKind<1.5){
  float tongues=fbm(q*7.+vec2(n*4.,-uTime*4.+vSeed*12.));alpha*=smoothstep(.09,.33,body+tongues*.5-.1);alpha*=.26;
  float heat=clamp((1.-vAge)*.72+body*.55+(tongues-.5)*.30,0.,1.);
  vec3 color=mix(vec3(1.4,.055,.004),vec3(4.8,.58,.025),smoothstep(.12,.55,heat));
  color=mix(color,vec3(8.,4.8,1.2),smoothstep(.58,.95,heat));frag=vec4(color*alpha,alpha);
 }else{alpha=(1.-smoothstep(.1,1.,radius))*tail*vStrength;frag=vec4(vec3(5.,1.05,.10)*alpha,alpha*.4);}
 if(frag.a<.001)discard;
}`;
let briarFireProgram=null;
function briarDrawFire(){
 const draws=[];
 if(typeof shopMap!=='undefined'&&shopMap.active){for(const entry of SHOP_HOUSE_LAYOUT.rooms){const d=roomScenes.get(entry.key)?.dragon;if(d&&d.fireTime>7&&d.fireTime<17)draws.push([d,entry.model]);}}
 else {const d=hobby.scene?.dragon;if(d&&d.fireTime>7&&d.fireTime<17)draws.push([d,I]);}
 if(!draws.length||reduceMotion)return;
 briarFireProgram??=program(BRIAR_FIRE_VS,BRIAR_FIRE_FS);const p=briarFireProgram;
 gl.useProgram(p);gl.bindVertexArray(null);gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);gl.disable(gl.CULL_FACE);
 um(p,'uVP',VP);uv3(p,'uEye',cameraPos);
 for(const [d,model]of draws){um(p,'uRoom',model);gl.uniform3fv(uniform(p,'uJetOrigins[0]'),d.jetOrigins);gl.uniform3fv(uniform(p,'uJetDirections[0]'),d.jetDirections);uf(p,'uTime',d.fireTime);gl.drawArraysInstanced(gl.TRIANGLES,0,6,188);}
 gl.depthMask(true);gl.disable(gl.BLEND);gl.disable(gl.CULL_FACE);gl.useProgram(mainProgram);gl.activeTexture(gl.TEXTURE2);
}
