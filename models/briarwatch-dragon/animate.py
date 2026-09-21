"""Author overlapping seated performance on the saved editable rig."""
import bpy,json,math,runpy,argparse,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent;globals().update({k:v for k,v in runpy.run_path(str(OUT/'rig-tools.py')).items() if not k.startswith('__')})
rig=next(o for o in bpy.data.objects if o.get('dragon_rig'));scene=bpy.context.scene;direction=json.loads((OUT/'animation-direction.json').read_text())['ritual']
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);output=Path(args.output).resolve();assert output!=Path(bpy.data.filepath).resolve(),'Write an animation candidate before replacing the saved source';output.parent.mkdir(parents=True,exist_ok=True)
rig.animation_data_create()
rig.animation_data.action=None
for name in ['Quiet watch','Perched fire ritual']:
 if name in bpy.data.actions:bpy.data.actions.remove(bpy.data.actions[name])
for action_name in ['Quiet watch','Perched fire ritual']:
 action=bpy.data.actions.new(action_name);action.use_fake_user=True;rig.animation_data.action=action
 for frame in range(1,482,2):
  t=(frame-1)/24;ritual=action_name=='Perched fire ritual';envelope=math.sin(math.pi*t/20)**2
  for p in rig.pose.bones:p.location=(0,0,0);p.rotation_quaternion=(1,0,0,0);p.scale=(1,1,1)
  quiet=.035*math.sin(math.tau*t/5)+.008*math.sin(math.tau*t/10)
  lift=hermite(direction['chest_lift'],t) if ritual else quiet
  set_global_translation(rig,'body',(0,0,lift*.65));set_global_translation(rig,'chest',(.018*envelope if ritual else 0,0,lift*.35))
  expansion=hermite(direction['rib_expansion'],t) if ritual else quiet*.75
  set_global_translation(rig,'rib.L',(0,-expansion,0));set_global_translation(rig,'rib.R',(0,expansion,0))
  gaze=hermite(direction['gaze_yaw'],t) if ritual else hermite([(0,0),(3,.03),(7,-.025),(10,-.015),(14,.04),(17,.016),(20,0)],t)
  neck=hermite(direction['neck_extend'],t) if ritual else .012*math.sin(math.tau*t/5-.35)*envelope
  for i,factor in [(1,.70),(2,.65),(3,.40)]:
   delayed=hermite(direction['neck_extend'],max(0,t-(i-1)*.14)) if ritual else neck
   set_global_rotation(rig,'neck.%02d'%i,(0,1,0),delayed*factor)
   p=rig.pose.bones['neck.%02d'%i];rest=rig.data.bones[p.name].matrix_local.to_3x3();p.rotation_quaternion=p.rotation_quaternion@__import__('mathutils').Quaternion(rest.inverted()@Vector((0,0,1)),gaze*[.2,.3,.3][i-1])
  set_global_rotation(rig,'head',(0,1,0),-neck*.38+.004*math.sin(t*2.8)*envelope)
  head=rig.pose.bones['head'];rest=rig.data.bones['head'].matrix_local.to_3x3();head.rotation_quaternion=head.rotation_quaternion@__import__('mathutils').Quaternion(rest.inverted()@Vector((0,0,1)),gaze*.2)
  jaw=hermite(direction['jaw_open_radians'],t) if ritual else .009*(1-math.cos(math.tau*t/5))*.5
  set_global_rotation(rig,'jaw',(0,1,0),jaw)
  brace=hermite(direction['wing_brace'],t) if ritual else .009*math.sin(math.tau*t/5-.7)*envelope
  for side,sgn in [('L',-1),('R',1)]:
   set_global_rotation(rig,'wing.'+side+'.root',(1,0,0),sgn*brace*.45)
   set_global_rotation(rig,'wing.'+side+'.arm',(0,0,1),sgn*brace*.65)
   set_global_rotation(rig,'wing.'+side+'.outer',(1,0,0),sgn*(-brace*.28+.007*math.sin(t*1.15+(0 if side=='L' else .6))*envelope))
  for i in range(3,6):set_global_rotation(rig,'tail.%02d'%i,(0,0,1),.012*math.sin(t*.63-i*.58)*envelope)
  bpy.context.view_layer.update();key_pose(rig,frame)
 # Sampled keys remain editable; no separate procedural clock is needed.
 for layer in action.layers:
  for strip in layer.strips:
   for slot in action.slots:
    bag=strip.channelbag(slot)
    if bag:
     for curve in bag.fcurves:
      for k in curve.keyframe_points:k.interpolation='LINEAR'
rig.animation_data.action=bpy.data.actions['Perched fire ritual'];scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(output))
