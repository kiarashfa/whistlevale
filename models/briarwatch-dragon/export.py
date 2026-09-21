"""Export a saved Pixal3D/Blender candidate; never rebuild or overwrite source."""
import bpy,json,math,hashlib,base64,struct
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
AXES=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE' and o.get('dragon_rig'))
def depth(b):return 0 if not b.parent else 1+depth(b.parent)
bones=sorted((b for b in rig.data.bones if b.use_deform),key=lambda b:(depth(b),b.name));ids={b.name:i for i,b in enumerate(bones)}
def parent(b):
 p=b.parent
 while p and p.name not in ids:p=p.parent
 return p
flatten=lambda m:[round(m[r][c],7) for c in range(4) for r in range(4)]
def trs(m):
 p,q,s=m.decompose();assert all(abs(x-1)<1e-4 for x in s),tuple(s)
 return [*[round(x,7) for x in p],round(q.x,7),round(q.y,7),round(q.z,7),round(q.w,7)]
records=[]
for b in bones:
 rest=AXES@rig.matrix_world@b.matrix_local@AXES.inverted();p=parent(b);par=AXES@rig.matrix_world@p.matrix_local@AXES.inverted() if p else Matrix.Identity(4)
 records.append(dict(name=b.name,parent=ids[p.name] if p else None,rest=trs(par.inverted()@rest),inverseBind=flatten(rest.inverted())))
vertices=[];indices=[];unique={};sole=[];texture=None;edges=set()
rig.data.pose_position='REST';bpy.context.view_layer.update()
for obj in sorted((o for o in bpy.data.objects if o.get('dragon_skin')),key=lambda o:o.name):
 assert all(m.type=='ARMATURE' for m in obj.modifiers)
 sole_ids=set(json.loads(obj.get('sole_indices','[]')));mesh=obj.data;mesh.calc_loop_triangles();matrix=AXES@obj.matrix_world;normals=matrix.to_3x3().inverted().transposed();mapping={}
 tint=mesh.color_attributes.get('Anatomical coat tint')
 for tri in mesh.loop_triangles:
  mat=mesh.materials[tri.material_index];bsdf=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');tex=next((n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and n.get('dragon_base_color')),None)
  if tex:
   assert texture is None or texture==tex;texture=tex
  color=(1,1,1) if tex else tuple(12.92*c if c<.0031308 else 1.055*c**(1/2.4)-.055 for c in mat.diffuse_color[:3])
  for li in tri.loops:
   loop=mesh.loops[li];v=mesh.vertices[loop.vertex_index];pos=matrix@v.co;normal=(normals@mesh.corner_normals[li].vector).normalized()
   weights=sorted([(ids[obj.vertex_groups[g.group].name],g.weight) for g in v.groups if obj.vertex_groups[g.group].name in ids and g.weight>1e-6],key=lambda q:-q[1])[:4];total=sum(w for _,w in weights);assert total>0
   weights=[(b,w/total) for b,w in weights]+[(0,0)]*(4-len(weights));uv=mesh.uv_layers.active.data[li].uv if tex else (-100,0)
   col=tuple(color[i]*(tint.data[v.index].color[i]**(1/2.2) if tint else 1) for i in range(3))
   row=tuple(round(x,6) for x in (*pos,*normal,*uv,*[b for b,w in weights],*[w for b,w in weights],*col));assert all(math.isfinite(x) for x in row)
   if row not in unique:
    unique[row]=len(vertices);vertices.append(row)
    if v.index in sole_ids:sole.append(len(vertices)-1)
   ix=unique[row];indices.append(ix);mapping[v.index]=ix
 for edge in mesh.edges:
  a,b=edge.vertices
  if a in mapping and b in mapping:
   ia,ib=mapping[a],mapping[b]
   names={bones[int(vertices[k][8+j])].name for k in (ia,ib) for j in range(4) if vertices[k][12+j]>.05}
   if len(names)>1 and not any(n=='jaw' for n in names):edges.add((ia,ib))
assert len(vertices)<16000,(len(vertices),'indexed vertex budget')
assert len(indices)<=60000,(len(indices),'expanded vertex budget')
# Greedy palettes preserve each face and its four influences without changing
# the renderer's 24-bone uniform limit. A connected skin may span several draws.
draws=[]
for t in range(len(indices)//3):
 used={int(vertices[indices[t*3+k]][8+j]) for k in range(3) for j in range(4) if vertices[indices[t*3+k]][12+j]>0}
 options=[(len(used-set(d['bones'])),i) for i,d in enumerate(draws) if len(used|set(d['bones']))<=24]
 if options:
  _,i=min(options);d=draws[i];d['bones']=sorted(set(d['bones'])|used);d['triangles'].append(t)
 else:draws.append(dict(bones=sorted(used),triangles=[t]))
assert len(draws)<=4,'partition locality unexpectedly fragmented'
assert texture and texture.packed_file
tex=texture.copy();tex.scale(2048,2048);tex.file_format='JPEG';tex.filepath_raw=str(ROOT/'evidence/briarwatch-dragon/dragon-coat-delivery.jpg');Path(tex.filepath_raw).parent.mkdir(parents=True,exist_ok=True);tex.save(quality=95);texturebytes=Path(tex.filepath_raw).read_bytes()
rig.data.pose_position='POSE';actions={};sample_rate=12
for key,name in [('watch','Quiet watch'),('ritual','Perched fire ritual')]:
 action=bpy.data.actions[name];rig.animation_data.action=action
 if len(action.slots):rig.animation_data.action_slot=action.slots[0]
 frames=[]
 for f in range(1,482,2):
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update();frame=[]
  for b in bones:
   pose=rig.pose.bones[b.name];world=AXES@rig.matrix_world@pose.matrix@AXES.inverted();par=parent(b);parworld=AXES@rig.matrix_world@rig.pose.bones[par.name].matrix@AXES.inverted() if par else Matrix.Identity(4);frame.append(trs(parworld.inverted()@world))
  frames.append(frame)
 actions[key]=frames
# Actual paired skin vertices on the separated lip, used by the native oracle.
lips={}
for i,row in enumerate(vertices):
 if row[0]<2.8 or row[1]<4.8 or row[6]<0:continue
 active=[bones[int(row[8+j])].name for j in range(4) if row[12+j]>.999]
 if len(active)==1 and active[0] in ('head','jaw'):lips.setdefault(tuple(row[:3]),{})[active[0]]=i
pairs=[(p,owners) for p,owners in lips.items() if len(owners)==2]
assert pairs,'Actual upper/lower lip pair missing'
_,lip=max(pairs,key=lambda item:item[0][0]);oralOpening=[lip['head'],lip['jaw']]
pack=lambda fmt,values:base64.b64encode(struct.pack('<'+fmt*len(values),*values)).decode()
model=dict(oralOpening=oralOpening,perch=json.loads(rig['perch']),assetId=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),draws=draws,attachments=[],deformationEdges=sorted(edges),source='Pixal3D generated surface; Blender authored anatomy, weighted armature and seated performance',format='whistlevale-skinned-v1',bones=records,vertices=len(vertices),vertexData=pack('f',[v for row in vertices for v in row]),indexData=pack('I',indices),texture='data:image/jpeg;base64,'+base64.b64encode(texturebytes).decode(),actions=actions,actionSampleRate=sample_rate,actionDuration=20,sole=sole,mouth=[json.loads(rig['mouth'])[k]*sign for k,sign in [(0,1),(2,1),(1,-1)]],bounds=[[min(v[i] for v in vertices),max(v[i] for v in vertices)] for i in range(3)])
script="'use strict';\n// Pixal3D dragon, rigged and animated in Blender for nickfromlater.\n// Exported from the packed editable source; do not edit these buffers.\nconst BRIAR_DRAGON_MODEL="+json.dumps(model,separators=(',',':'))+';\n'
(ROOT/'src/scenery/briarwatch-dragon-model.js').write_text(script)
report=dict(blender=bpy.app.version_string,bones=len(bones),drawPalettes=[len(d['bones']) for d in draws],vertices=len(vertices),expandedVertices=len(indices),soleVertices=len(sole),sourceBytes=len(script.encode()),textureBytes=len(texturebytes),textureSize=list(tex.size),authoringTextureSize=list(texture.size),blendSHA256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),scriptSHA256=hashlib.sha256(script.encode()).hexdigest(),bounds=model['bounds'])
(OUT/'export-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
