import bpy

# Importing converters
from .converters import simple_converter
from .converters import advanced_converter
from . import deform_rig_generator
from . import utility

# Execute the Rigify to Unreal conversion process based on selected mode
class RIGIFYTOUNREAL_OT_execute(bpy.types.Operator):
    bl_idname = "rigify_to_unreal.convert"
    bl_label = "Convert Rigify to Unreal"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        """Check if we're in object mode"""
        return context.mode == 'OBJECT'
    
    def execute(self, context):
        scene = context.scene
        rigify_rig_obj = scene.rigify_to_unreal_rigify_rig
        
        # Check if objects are selected
        
        if rigify_rig_obj is None:
            self.report({'ERROR'}, "No rigify rig selected!")
            return {'CANCELLED'}
        
        # Check if rig is actually an armature
        if rigify_rig_obj.type != 'ARMATURE':
            self.report({'ERROR'}, f"Object '{rigify_rig_obj.name}' is not an armature!")
            return {'CANCELLED'}
        
        
        # RIG GENERATION
        deform_rig_generator.DeformRigGenerator.generate(rigify_rig_obj, context=context)
        
        deform_rig_obj = scene.rigify_to_unreal_converted_rig
        
        if deform_rig_obj is None:
                    self.report({'ERROR'}, "No unreal rig selected!")
                    return {'CANCELLED'}
                
        if deform_rig_obj.type != 'ARMATURE':
            self.report({'ERROR'}, f"Object '{deform_rig_obj.name}' is not an armature!")
            return {'CANCELLED'}
        
        # MESH HANDLING
        
        meshes = utility.get_meshes_attached_to_rig(rigify_rig_obj)
        
        for mesh_obj in meshes:
            mesh_obj.hide_viewport = False
            mesh_obj.hide_set(False)
            
            attachment_info = utility.get_mesh_attachment_type(mesh_obj, rigify_rig_obj)
            
            modified_mesh = mesh_obj.copy()
            modified_mesh.data = mesh_obj.data.copy()
            
            modified_mesh.name = mesh_obj.name + "_Converted"
            scene.collection.objects.link(modified_mesh)

            mesh_obj.hide_viewport = True
            mesh_obj.hide_set(True)
        
            # Clearing old parent
            bpy.ops.object.select_all(action='DESELECT')
                        
            modified_mesh.select_set(True)
            context.view_layer.objects.active = modified_mesh
            
            bpy.ops.object.parent_clear(type='CLEAR')
        
            # Parenting modified_mesh to the deform_rig
            bpy.ops.object.select_all(action='DESELECT')
            
            deform_rig_obj.select_set(True)
            context.view_layer.objects.active = deform_rig_obj
            modified_mesh.select_set(True)
            
            if attachment_info['type'] == 'MODIFIER':
                bpy.ops.object.parent_set(type='ARMATURE')
            
            elif attachment_info['type'] == 'BONE_PARENT':
                original_bone_name = attachment_info['parent_bone']
                
                if original_bone_name in deform_rig_obj.data.bones:
                    bpy.ops.object.mode_set(mode='OBJECT')
                    
                    # Make deform rig active and enter pose mode
                    bpy.ops.object.select_all(action='DESELECT')
                    deform_rig_obj.select_set(True)
                    context.view_layer.objects.active = deform_rig_obj

                    bpy.ops.object.mode_set(mode='EDIT')

                    # Deselect all bones in edit mode
                    bpy.ops.armature.select_all(action='DESELECT')
                    
                    # Get the edit bone (EditBone has select attribute)
                    edit_bone = deform_rig_obj.data.edit_bones[original_bone_name]
                    edit_bone.select = True
                    edit_bone.select_head = True
                    edit_bone.select_tail = True
                    
                    # Make it active
                    deform_rig_obj.data.edit_bones.active = edit_bone
                    
                    # Return to object mode (bone selection is preserved)
                    bpy.ops.object.mode_set(mode='OBJECT')
                      
                    # Now parent mesh to the selected bone
                    bpy.ops.object.select_all(action='DESELECT')
                    modified_mesh.select_set(True)
                    deform_rig_obj.select_set(True)
                    context.view_layer.objects.active = deform_rig_obj
                    
                    # Parent to selected bone
                    bpy.ops.object.parent_set(type='BONE')
                        
            else:
                modified_mesh.parent = deform_rig_obj
                modified_mesh.parent_type = 'OBJECT'
                self.report({'WARNING'}, f"OBJECT attachment type detected, '{mesh_obj.name}' might not perform as expected")
            
            
        # RIG CONVERSION
        conversion_mode = scene.rigify_to_unreal_conversion_mode    
        
        # Run the appropriate conversion process
        try:
            if conversion_mode == 'SIMPLE':
                simple_converter.SimpleConverter.convert(deform_rig_obj, rigify_rig_obj, context)
                self.report({'INFO'}, "Simple Rigify to Unreal conversion completed!")
                
            elif conversion_mode == 'ADVANCED':
                advanced_converter.AdvancedConverter.convert(deform_rig_obj, rigify_rig_obj, context)
                self.report({'INFO'}, "Rigify to Unreal conversion with twist bones completed!")
        
        except Exception as e:
            self.report({'ERROR'}, f"Error during conversion: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    