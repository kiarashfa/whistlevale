"""Read-only review of the packed source; never saves geometry or animation."""
import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'evidence/briarwatch-dragon/studio';OUT.mkdir(parents=True,exist_ok=True)
rig=next(o for o in bpy.data.objects if o.get('dragon_rig'));scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
cam=scene.camera;cam.data.type='ORTHO';rig.animation_data.action=bpy.data.actions['Perched fire ritual']
for name,t,loc,target,size in [('rest',0,(12,-18,8),(-.9,0,3),14),('intake',6.6,(12,-18,8),(-.9,0,3),14),('exhale',9,(12,-18,8),(-.9,0,3),14),('front-exhale',9,(20,0,6),(0,1,3),12),('recovery',16,(12,-18,8),(-.9,0,3),14)]:
 scene.frame_set(1+round(t*24));cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size;scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
