"""Editable Blender control helpers, separate from generated-surface cleanup."""
import bpy,math
from mathutils import Vector,Matrix

def add_armature(name,spec):
 arm=bpy.data.armatures.new(name+' skeleton');rig=bpy.data.objects.new(name,arm);bpy.context.collection.objects.link(rig)
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 for name,record in spec.items():
  b=arm.edit_bones.new(name);b.head=record['head'];b.tail=record['tail'];b.use_deform=record.get('deform',True)
  if record.get('parent'):b.parent=arm.edit_bones[record['parent']]
 bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
 deform=arm.collections.new('Skin • anatomical deformation');control=arm.collections.new('Controls • animator handles')
 for b in arm.bones:
  (deform if b.use_deform else control).assign(b);b.color.palette='THEME03' if b.use_deform else 'THEME04'
  rig.pose.bones[b.name].rotation_mode='QUATERNION'
 return rig

def add_planted_leg(rig,prefix,target,pole):
 lower=rig.pose.bones[prefix+'.lower'];ik=lower.constraints.new('IK');ik.name='Two-joint planted leg';ik.target=rig;ik.subtarget=target;ik.pole_target=rig;ik.pole_subtarget=pole;ik.chain_count=2;ik.use_stretch=False;ik.iterations=128
 # Calibrate pole orientation against the inspected rest knee. The armature
 # stores the actual resulting constraint, so animator edits use Blender IK.
 knee=rig.data.bones[prefix+'.lower'].head_local.copy()
 def error(angle):
  ik.pole_angle=angle;bpy.context.view_layer.update();return (lower.head-knee).length
 angle=min((i*math.tau/72 for i in range(-36,37)),key=error)
 for step in (.02,.002,.0002,.00002):angle=min((angle+i*step for i in range(-5,6)),key=error)
 residual=error(angle);assert residual<.002,(prefix,'neutral IK moved the knee',residual)
 foot=rig.pose.bones[prefix+'.foot'];c=foot.constraints.new('COPY_TRANSFORMS');c.name='Planted sole orientation';c.target=rig;c.subtarget=target;c.target_space='POSE';c.owner_space='POSE'
 return residual

def key_pose(rig,frame,names=None):
 for name in names or [b.name for b in rig.data.bones]:
  p=rig.pose.bones[name];p.keyframe_insert(data_path='location',frame=frame,group=name);p.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=name)

def set_global_rotation(rig,name,axis,angle):
 p=rig.pose.bones[name];rest=rig.data.bones[name].matrix_local.to_3x3();local_axis=rest.inverted()@Vector(axis);p.rotation_quaternion=__import__('mathutils').Quaternion(local_axis,angle)

def set_global_translation(rig,name,offset):
 p=rig.pose.bones[name];p.location=rig.data.bones[name].matrix_local.to_3x3().inverted()@Vector(offset)

def ease(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)

def hermite(points,t):
 # C1-continuous timing with explicit animator-authored apex/recovery keys.
 if t<=points[0][0]:return points[0][1]
 for (a,x),(b,y) in zip(points,points[1:]):
  if t<=b:return x+(y-x)*ease(a,b,t)
 return points[-1][1]
