import bpy

from . import renamer
from . import vertex_group_merging
from .. import utility

class AdvancedConverter:
    
    def convert(deform_rig, rigify_rig, context):
        original_meshes = utility.get_meshes_attached_to_rig(rigify_rig)
        modified_meshes = utility.get_meshes_attached_to_rig(deform_rig)
        
        # Execute conversion
        for mesh, original_mesh in zip(modified_meshes, original_meshes):
            AdvancedConverter._merge_vertex_groups(mesh, original_mesh, deform_rig, context)
            
        AdvancedConverter._remove_bones(deform_rig, context)
        AdvancedConverter._reparent_bones(deform_rig, context)
        
        for mesh, original_mesh in zip(modified_meshes, original_meshes):
            AdvancedConverter._clean_up_vertex_groups(mesh, deform_rig, context)
        renamer.Renamer.rename_bones(deform_rig)    
        
    # Merges verter group of bones that will be removed
    def _merge_vertex_groups(mesh, original_mesh, rig, context):
        
        # What vertex groups shall be merged to which group
        # Source - (Target, Source Scale, Total Scale)
        merge_targets = {            
            "DEF-pelvis.L"        : ("DEF-spine",           1.0, 1.0),
            "DEF-pelvis.R"        : ("DEF-spine",           1.0, 1.0),
            "DEF-spine.005"       : ("DEF-spine.004",       1.0, 1.0)
        }
        
        if not context.scene.rigify_to_unreal_keep_breasts:
            merge_targets += {
                "DEF-breast.L"        : ("DEF-spine.003",       1.0, 1.0),
                "DEF-breast.R"        : ("DEF-spine.003",       1.0, 1.0),
            }
        
        arm_interpolation_reference_distance = context.scene.rigify_to_unreal_twist_interpolation_arm_length
        leg_interpolation_reference_distance = context.scene.rigify_to_unreal_twist_interpolation_leg_length
        
        merge_with_interpolation_from_tail = {
            "DEF-upper_arm.L" : ("DEF-upper_arm.L.001",     1.0, 1.0,   arm_interpolation_reference_distance),
            "DEF-forearm.L"   : ("DEF-forearm.L.001",       1.0, 1.0,   arm_interpolation_reference_distance),
            "DEF-upper_arm.R" : ("DEF-upper_arm.R.001",     1.0, 1.0,   arm_interpolation_reference_distance),
            "DEF-forearm.R"   : ("DEF-forearm.R.001",       1.0, 1.0,   arm_interpolation_reference_distance),
            "DEF-thigh.L"     : ("DEF-thigh.L.001",         1.0, 1.0,   leg_interpolation_reference_distance),
            "DEF-shin.L"      : ("DEF-shin.L.001",          1.0, 1.0,   leg_interpolation_reference_distance),
            "DEF-thigh.R"     : ("DEF-thigh.R.001",         1.0, 1.0,   leg_interpolation_reference_distance),
            "DEF-shin.R"      : ("DEF-shin.R.001",          1.0, 1.0,   leg_interpolation_reference_distance),
        }
        
        merge_with_interpolation_from_head = {
            "DEF-upper_arm.L.001" : ("DEF-upper_arm.L",     1.0, 0.5,   arm_interpolation_reference_distance),
            "DEF-forearm.L.001"   : ("DEF-forearm.L",       1.0, 0.5,   arm_interpolation_reference_distance),
            "DEF-upper_arm.R.001" : ("DEF-upper_arm.R",     1.0, 0.5,   arm_interpolation_reference_distance),
            "DEF-forearm.R.001"   : ("DEF-forearm.R",       1.0, 0.5,   arm_interpolation_reference_distance),
            "DEF-thigh.L.001"     : ("DEF-thigh.L",         1.0, 0.5,   leg_interpolation_reference_distance),
            "DEF-shin.L.001"      : ("DEF-shin.L",          1.0, 0.5,   leg_interpolation_reference_distance),
            "DEF-thigh.R.001"     : ("DEF-thigh.R",         1.0, 0.5,   leg_interpolation_reference_distance),
            "DEF-shin.R.001"      : ("DEF-shin.R",          1.0, 0.5,   leg_interpolation_reference_distance),
        }
        
        clear_targets = [
            "DEF-breast.L",
            "DEF-breast.R",
            "DEF-pelvis.L",
            "DEF-pelvis.R",
            "DEF-spine.005"
        ]
        
        # Normal merging
        vertex_group_merging.merge_normal(mesh, original_mesh, rig, context, 
                                          merge_targets, clear_targets)
        
        # Merge with interpolation from head
        vertex_group_merging.merge_interpolation_from_head(mesh, original_mesh, rig, context, 
                                                           merge_with_interpolation_from_head, clear_targets)
        
        # Merge with interpolation from tail
        vertex_group_merging.merge_interpolation_from_tail(mesh, original_mesh, rig, context, 
                                                           merge_with_interpolation_from_tail, clear_targets)
    
               
        

    # Removes unnecessary bones from the deform rig
    def _remove_bones(rig, context):
        
        # Store original active object and mode
        original_active = bpy.context.view_layer.objects.active
        
        # Switch to edit mode
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')
        
        # BoneToRemove - (NewParentBone, NewChildBone)
        bone_removal_targets = {
            "DEF-pelvis.L"  : ("", ""),
            "DEF-pelvis.R"  : ("", ""),
            "pelvis"        : ("", ""),
            "DEF-spine.005" : ("DEF-spine.004", "DEF-spine.006")
        }
        
        if not context.scene.rigify_to_unreal_keep_breasts:
            bone_removal_targets += {
                "DEF-breast.L"  : ("", ""),
                "DEF-breast.R"  : ("", ""),
            }
        
        armature = rig.data
        
        for target, (new_parent, new_child) in bone_removal_targets.items():
            if target in armature.edit_bones:
                bpy.ops.armature.select_all(action='DESELECT')
                armature.edit_bones.remove(armature.edit_bones[target])
                
                if new_child in armature.edit_bones and new_parent in armature.edit_bones:
                    armature.edit_bones[new_parent].tail = armature.edit_bones[new_child].head
                    armature.edit_bones[new_child].parent = armature.edit_bones[new_parent]
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Restore original active object
        if original_active:
            bpy.context.view_layer.objects.active = original_active
    
    
    # Reparenting bones to fit the twist bone architecture
    def _reparent_bones(rig, context):
        
        # Store original active object and mode
        original_active = bpy.context.view_layer.objects.active
        
        # Switch to edit mode
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')
        
        armature = rig.data
        
        # Bone - NewParent
        bone_reparent_targets_keep_offset = {
            "DEF-forearm.L.001"     : "DEF-forearm.L",
            "DEF-upper_arm.L.001"   : "DEF-upper_arm.L",
            "DEF-forearm.R.001"     : "DEF-forearm.R",
            "DEF-upper_arm.R.001"   : "DEF-upper_arm.R",
            "DEF-shin.L.001"        : "DEF-shin.L",
            "DEF-thigh.L.001"       : "DEF-thigh.L",
            "DEF-shin.R.001"        : "DEF-shin.R",
            "DEF-thigh.R.001"       : "DEF-thigh.R",
        }
            
        for new_child, new_parent in bone_reparent_targets_keep_offset.items():     
            if new_child in armature.edit_bones and new_parent in armature.edit_bones:
                child_bone = armature.edit_bones[new_child]
                parent_bone = armature.edit_bones[new_parent]
                
                child_bone.parent = parent_bone
                child_bone.use_connect = False
        
        
        # Bone - NewParent
        bone_reparent_targets = {
            "DEF-forearm.L" : "DEF-upper_arm.L",
            "DEF-hand.L"    : "DEF-forearm.L",
            "DEF-forearm.R" : "DEF-upper_arm.R",
            "DEF-hand.R"    : "DEF-forearm.R",
            "DEF-shin.L"    : "DEF-thigh.L",
            "DEF-foot.L"    : "DEF-shin.L",
            "DEF-shin.R"    : "DEF-thigh.R",
            "DEF-foot.R"    : "DEF-shin.R",
        }
        
        for new_child, new_parent in bone_reparent_targets.items():
            if new_child in armature.edit_bones and new_parent in armature.edit_bones:
                armature.edit_bones[new_parent].tail = armature.edit_bones[new_child].head
                armature.edit_bones[new_child].parent = armature.edit_bones[new_parent]
                
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Restore original active object
        if original_active:
            bpy.context.view_layer.objects.active = original_active

    # Removes leftover vertex groups
    def _clean_up_vertex_groups(mesh, rig, context):
        
        mesh.select_set(True)
        context.view_layer.objects.active = mesh
                
        bone_names = [bone.name for bone in rig.data.bones]     
                
        groups_to_remove = []
        for vertex_group in mesh.vertex_groups:
            if vertex_group.name not in bone_names:
                groups_to_remove.append(vertex_group)
        
        for vertex_group in groups_to_remove:
            mesh.vertex_groups.remove(vertex_group)