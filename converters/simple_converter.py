import bpy

from . import renamer
from .. import utility

class SimpleConverter:
    
    def convert(deform_rig, rigify_rig, context):
        
        original_meshes = utility.get_meshes_attached_to_rig(rigify_rig)
        modified_meshes = utility.get_meshes_attached_to_rig(deform_rig)
        
        # Execute conversion
        for mesh, o_mesh in zip(modified_meshes, original_meshes):
            SimpleConverter._merge_vertex_groups(mesh, context)
        SimpleConverter._remove_bones(deform_rig, context)
        for mesh, o_mesh in zip(modified_meshes, original_meshes):
            SimpleConverter._clean_up_vertex_groups(mesh, deform_rig, context)
        renamer.Renamer.rename_bones(deform_rig)
        
    
    # Merge duplicate vertex groups on the mesh
    def _merge_vertex_groups(mesh, context):
        # What vertex groups shall be merged to which group
        merge_targets = {
            "DEF-upper_arm.L.001" : "DEF-upper_arm.L",
            "DEF-forearm.L.001"   : "DEF-forearm.L",
            "DEF-upper_arm.R.001" : "DEF-upper_arm.R",
            "DEF-forearm.R.001"   : "DEF-forearm.R",
            "DEF-thigh.L.001"     : "DEF-thigh.L",
            "DEF-shin.L.001"      : "DEF-shin.L",
            "DEF-thigh.R.001"     : "DEF-thigh.R",
            "DEF-shin.R.001"      : "DEF-shin.R",
            "DEF-breast.L"        : "DEF-spine.003",
            "DEF-breast.R"        : "DEF-spine.003",
            "DEF-pelvis.L"        : "DEF-spine",
            "DEF-pelvis.R"        : "DEF-spine",
            "DEF-spine.005"       : "DEF-spine.004"
        }
        
        for source_group, target_group in merge_targets.items():
            if (source_group in mesh.vertex_groups and 
                target_group in mesh.vertex_groups):
                
                for vert in mesh.data.vertices:
                    available_groups = [v_group_elem.group for v_group_elem in vert.groups]
                    source_weight = 0
                    target_weight = 0
                    
                    if mesh.vertex_groups[source_group].index in available_groups:
                        source_weight = mesh.vertex_groups[source_group].weight(vert.index)
                    if mesh.vertex_groups[target_group].index in available_groups:
                        target_weight = mesh.vertex_groups[target_group].weight(vert.index)
                    
                    # Only add to vertex group if weight is > 0
                    total_weight = source_weight + target_weight
                    if total_weight > 0:
                        mesh.vertex_groups[target_group].add([vert.index], total_weight, 'REPLACE')
                    
                    mesh.vertex_groups[source_group].add([vert.index], 0, 'REPLACE')
                    
    
    # Remove unnecessary bones from the deform rig                          
    def _remove_bones(rig, context):
        # Store original active object and mode
        original_active = bpy.context.view_layer.objects.active
        
        # Switch to edit mode
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')
        
        # BoneToRemove - (NewParentBone, NewChildBone)
        bone_removal_targets = {
            "DEF-upper_arm.L.001" : ("DEF-upper_arm.L" , "DEF-forearm.L"),
            "DEF-forearm.L.001"   : ("DEF-forearm.L"   , "DEF-hand.L"),
            "DEF-upper_arm.R.001" : ("DEF-upper_arm.R" , "DEF-forearm.R"),
            "DEF-forearm.R.001"   : ("DEF-forearm.R"   , "DEF-hand.R"),
            "DEF-thigh.L.001"     : ("DEF-thigh.L"     , "DEF-shin.L"),
            "DEF-shin.L.001"      : ("DEF-shin.L"      , "DEF-foot.L"),
            "DEF-thigh.R.001"     : ("DEF-thigh.R"     , "DEF-shin.R"),
            "DEF-shin.R.001"      : ("DEF-shin.R"      , "DEF-foot.R"),
            "DEF-breast.L"        : ("", ""),
            "DEF-breast.R"        : ("", ""),
            "DEF-pelvis.L"        : ("", ""),
            "DEF-pelvis.R"        : ("", ""),
            "pelvis"              : ("", ""),
            "DEF-spine.005"       : ("DEF-spine.004", "DEF-spine.006")
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