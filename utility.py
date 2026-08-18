import bpy

# These functions were generated using DeepSeek cause I am too lazy to figure out this API

# Find all mesh objects that have an armature modifier targeting the rig
def get_meshes_attached_to_rig(rig):
    meshes = []
    
    # Also check if rig is parent of any meshes
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            # Check for armature modifier
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object == rig:
                    meshes.append(obj)
                    break
                
            # Check if parented to rig
            else:
                if obj.parent == rig: 
                    meshes.append(obj)
    
    return meshes


# Determine how the mesh is attached to the rig
def get_mesh_attachment_type(mesh_obj, rig_obj):
    # Check for armature modifier
    for modifier in mesh_obj.modifiers:
        if modifier.type == 'ARMATURE' and modifier.object == rig_obj:
            return {'type' : 'MODIFIER'}
    
    # Check if parented to a bone
    if mesh_obj.parent == rig_obj and mesh_obj.parent_bone:
        return {'type' : 'BONE_PARENT', 'parent_bone' : mesh_obj.parent_bone}
    
    # Check if parented to rig (whole object)
    if mesh_obj.parent == rig_obj:
        return {'type' : 'OBJECT_PARENT'}
    
    return {'type' : 'NONE'}