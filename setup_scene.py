import bpy

class RIGIFYTOUNREAL_OT_setup_scene(bpy.types.Operator):
    """Sets up scene's mesurment system to match Unreal's units"""
    bl_idname = "rigify_to_unreal.setup_scene"
    bl_label = "Setup Scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        """Check if we're in object mode"""
        return context.mode == 'OBJECT'
    
    def execute(self, context):
        scene = context.scene
        
        # Setting units to centimeters
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.scale_length = 0.01
        
        return {'FINISHED'}
        