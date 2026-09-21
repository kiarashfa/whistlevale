// Emission uses the active locomotive; already emitted puffs remain in world space.
import assert from 'node:assert/strict';
import {communityContext,read} from './community-lib.mjs';
const state=await communityContext();state.context.assert=assert;
const source=await read('src/hobby.js');
const start=source.indexOf('function drawHobbyParticles()'),end=source.indexOf('\nfunction houseOrbit',start);
state.run(`const hobby={room:'briarwatch'};let activeMatrix=I,activeForward=[0,0,1],family='tank',power='steam',drawn=null;
function hobbyHasNativeTrain(){return true;}function hobbyTrainMatrix(){return activeMatrix;}function hobbyTrainInfo(){return {f:activeForward};}
function collectionPower(){return power;}function collectionChoice(){return {id:'qa'};}const collectionById={get:()=>({family})};
${source.slice(start,end)}
// Deliberately opposite, distant Valley locomotive exposes route leakage.
trainModels=[mm(trans(-60,0,-30),ry(PI))];leadInfo={f:[0,0,-1]};
const oldDrawSteam=drawSteam;drawSteam=()=>{drawn=steam.map(s=>s.p.slice());};
for(const angle of[0,PI/2,PI,-PI/2]){
 steam.length=0;activeMatrix=mm(trans(17,6,23),ry(angle));activeForward=[Math.sin(angle),0,Math.cos(angle)];emitSteam();
 const expected=transform([0,1.668,1.03],activeMatrix),puff=steam[0];assert.ok(len(sub(puff.p,expected))<1e-6,'puff starts at active chimney at every heading');
 let exhaust=0;for(let i=0;i<40;i++){emitSteam();const v=steam.at(-1).v;exhaust+=v[0]*activeForward[0]+v[2]*activeForward[2];}assert.ok(exhaust/40<-.07,'exhaust trails actual heading despite turbulent spread');
 const born=puff.p.slice();activeMatrix=mm(trans(35,6,40),ry(angle+PI/2));drawHobbyParticles();
 assert.deepEqual(puff.p,born,'moving or turning the train cannot move an existing puff');assert.deepEqual(drawn[0],born,'draw uses world-space particles');
 const before=JSON.stringify(steam);drawHobbyParticles();assert.equal(JSON.stringify(steam),before,'multiple render passes never mutate simulation');
}
family='saddle';activeMatrix=I;steam.length=0;emitSteam(true);assert.deepEqual(steam[0].p,[-.091,1.562,-.47],'tank whistle has its own emitter');
drawSteam=oldDrawSteam;
`);
console.log('Steam: active chimney, four headings, whistle position, fixed world-space trail and immutable rendering pass.');
