import bpy

# These funcitons and deform rig extraction logic 
# come from Game Rig Tools addon
# https://toshicg.gumroad.com/l/game_rig_tools

def get_deform(bone, bones):
    bone_name = bone.name.replace("ORG-", "DEF-")
    return bones.get(bone_name)

def find_first_def(bone, bones):
    if bone:
        if get_deform(bone, bones):
            if bone.parent:
                if bone.parent.use_deform:
                    return bone.parent

def find_deform(bone, bones):
    if "DEF-" not in bone.name:
        new_name = bone.name.replace("ORG-", "DEF-")
        return bones.get(new_name)

def get_root(bone):
    if bone.parent:
        return get_root(bone.parent)
    else:
        return bone


class DeformRigGenerator:
    
    def generate(rigify_rig, context):
        scene = context.scene
        
        # Renaming existing unreal rig (backing it up)
        if scene.rigify_to_unreal_converted_rig != None:
            old_deform_rig = scene.rigify_to_unreal_converted_rig
            
            if old_deform_rig != rigify_rig:
                old_deform_rig.name = "Armature_Old"
            
            scene.rigify_to_unreal_converted_rig = None
        
        # Copying rigify rig as a base for the deform rig
        deform_rig = rigify_rig.copy()
        deform_rig.data = rigify_rig.data.copy()
        
        deform_rig.name = "Armature"
        scene.collection.objects.link(deform_rig)
        scene.rigify_to_unreal_converted_rig = deform_rig

        # Selecting deform rig
        bpy.ops.object.select_all(action="DESELECT")
        deform_rig.select_set(True)
        context.view_layer.objects.active = deform_rig
        
        # Clearing old constraints
        bpy.ops.object.mode_set(mode="POSE")
        pose_bones = deform_rig.pose.bones
        
        for bone in pose_bones:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)
                
        # Entering edit mode
        bpy.ops.object.mode_set(mode="EDIT")
        
        edit_bones = deform_rig.data.edit_bones
        
        # Fixing hierarchy
        for bone in edit_bones:
            if bone.use_deform:
                if bone.parent:
                    if not bone.parent.use_deform:
                        recursive_parent = bone.parent_recursive

                        for f in recursive_parent:
                            if f.use_deform:
                                bone.parent = f
                                break
                            else:
                                b = find_deform(f, edit_bones)
                                if b:
                                    if not b.name == bone.name:
                                        if b.use_deform:
                                            bone.parent = b
                                            break
        
        # Removing non-deform bones
        for bone in edit_bones:
            if not bone.use_deform and bone.name != "root":
                edit_bones.remove(bone)
                
        # Disconnecting all the bones
        for bone in edit_bones:
            bone.use_connect = False
             
        bpy.ops.object.mode_set(mode="POSE")
        pose_bones = deform_rig.pose.bones
        
        # Removing custom shapes for all bones
        for bone in pose_bones:
            bone.custom_shape = None
        
        # Unlocking bones
        for bone in pose_bones:
            bone.lock_location[0] = False
            bone.lock_location[1] = False
            bone.lock_location[2] = False
            
            bone.lock_rotation[0] = False
            bone.lock_rotation[1] = False
            bone.lock_rotation[2] = False
            bone.lock_rotation_w = False
            
            bone.lock_scale[0] = False
            bone.lock_scale[1] = False
            bone.lock_scale[2] = False
                
        # Links resulting deform rig to the original rigify rig
        for bone in pose_bones:
            constraint = bone.constraints.new("COPY_TRANSFORMS")
            constraint.target = rigify_rig
            constraint.subtarget = rigify_rig.data.bones.get(bone.name).name
                
        # Returning to object mode
        bpy.ops.object.mode_set(mode="OBJECT")
        
        # Bone collection clean up
        while len(deform_rig.data.collections) > 0:
            deform_rig.data.collections.remove(deform_rig.data.collections[0])

        new_collection = deform_rig.data.collections.new("Deform")
        new_collection.is_visible = True
        
        for bone in deform_rig.data.bones:
            new_collection.assign(bone)