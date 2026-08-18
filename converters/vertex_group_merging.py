import bpy

def merge_normal(mesh, original_mesh, rig, context, merge_targets, clear_targets):
        for source_group, (target_group, source_scale, total_scale) in merge_targets.items():
            if (source_group in original_mesh.vertex_groups and 
                target_group in mesh.vertex_groups):
                
                for vert in mesh.data.vertices:
                    available_groups = [v_group_elem.group for v_group_elem in vert.groups]
                    source_weight = 0.0
                    target_weight = 0.0
                    
                    if original_mesh.vertex_groups[source_group].index in available_groups:
                        source_weight = original_mesh.vertex_groups[source_group].weight(vert.index)
                    if mesh.vertex_groups[target_group].index in available_groups:
                        target_weight = mesh.vertex_groups[target_group].weight(vert.index)
                    
                    # Only add to vertex group if weight is > 0
                    total_weight = (source_weight * source_scale + target_weight) * total_scale
                    if total_weight > 0:
                        mesh.vertex_groups[target_group].add([vert.index], total_weight, 'REPLACE')
                    
                    if source_group in clear_targets:
                        mesh.vertex_groups[source_group].add([vert.index], 0, 'REPLACE')
                        
                        
def merge_interpolation_from_head(mesh, original_mesh, rig, context, merge_targets, clear_targets):
    mesh_matrix = mesh.matrix_world
    rig_matrix = rig.matrix_world
                    
    for source_group, (target_group, source_scale, total_scale, reference_distance) in merge_targets.items():
        if (source_group in original_mesh.vertex_groups and 
            target_group in mesh.vertex_groups):
            
            for vert in original_mesh.data.vertices:
                available_groups = [v_group_elem.group for v_group_elem in vert.groups]
                source_weight = 0.0
                target_weight = 0.0
                
                if original_mesh.vertex_groups[source_group].index in available_groups:
                    source_weight = original_mesh.vertex_groups[source_group].weight(vert.index)
                if mesh.vertex_groups[target_group].index in available_groups:
                    target_weight = mesh.vertex_groups[target_group].weight(vert.index)
                
                interpolation_scale = 1.0
                
                bone = rig.data.bones.get(target_group)
                if bone:
                    vertex_position = mesh_matrix @ vert.co
                    #bone_tail_position = rig_matrix @ bone.tail_local
                    bone_head_position = rig_matrix @ bone.head_local
                    
                    distance = (vertex_position - bone_head_position).length
                    factor = distance / (reference_distance)
                    if factor < 0.0:
                        factor = 0.0
                    elif factor > 1.0:
                        factor = 1.0
                        
                    interpolation_scale = 1.0 - factor     
                                        
                # Only add to vertex group if weight is > 0
                total_weight = max(source_weight * source_scale, target_weight) * total_scale * interpolation_scale
                #if total_weight > 0:
                mesh.vertex_groups[target_group].add([vert.index], total_weight, 'REPLACE')
                
                if source_group in clear_targets:
                    mesh.vertex_groups[source_group].add([vert.index], 0, 'REPLACE')
                    
                    
def merge_interpolation_from_tail(mesh, original_mesh, rig, context, merge_targets, clear_targets):
    mesh_matrix = mesh.matrix_world
    rig_matrix = rig.matrix_world
                    
    for source_group, (target_group, source_scale, total_scale, reference_distance) in merge_targets.items():
        if (source_group in original_mesh.vertex_groups and 
            target_group in mesh.vertex_groups):
            
            for vert in original_mesh.data.vertices:
                available_groups = [v_group_elem.group for v_group_elem in vert.groups]
                source_weight = 0.0
                target_weight = 0.0
                
                if original_mesh.vertex_groups[source_group].index in available_groups:
                    source_weight = original_mesh.vertex_groups[source_group].weight(vert.index)
                if mesh.vertex_groups[target_group].index in available_groups:
                    target_weight = mesh.vertex_groups[target_group].weight(vert.index)
                
                interpolation_scale = 1.0
                
                bone = rig.data.bones.get(target_group)
                if bone:
                    vertex_position = mesh_matrix @ vert.co
                    bone_tail_position = rig_matrix @ bone.tail_local
                    
                    distance = (vertex_position - bone_tail_position).length
                    factor = distance / (reference_distance)
                    if factor < 0.0:
                        factor = 0.0
                    elif factor > 1.0:
                        factor = 1.0
                        
                    interpolation_scale = 1.0 - factor     
                                        
                # Only add to vertex group if weight is > 0
                total_weight = max(source_weight * source_scale, target_weight) * total_scale * interpolation_scale
                #if total_weight > 0:
                mesh.vertex_groups[target_group].add([vert.index], total_weight, 'REPLACE')
                
                if source_group in clear_targets:
                    mesh.vertex_groups[source_group].add([vert.index], 0, 'REPLACE')