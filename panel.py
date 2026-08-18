import bpy

class RIGIFYTOUNREAL_PT_main_panel(bpy.types.Panel):
    """Main panel for RigifyToUnreal tool"""
    bl_label = "RigifyToUnreal"
    bl_idname = "RIGIFYTOUNREAL_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RigifyToUnreal"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Header box
        box = layout.box()
        box.label(text="Convert Rigify rigs to Unreal Engine 4-type rig", icon='ARMATURE_DATA')
        
        layout.separator()
        
        # Mesh object selector
        layout.prop(scene, "rigify_to_unreal_mesh", text="Mesh")
        
        # Rig object selectors
        layout.prop(scene, "rigify_to_unreal_rigify_rig", text="Rigify Rig")
        
        layout.separator()
        
        # Conversion mode dropdown
        layout.prop(scene, "rigify_to_unreal_conversion_mode", text="Mode")
        
        layout.separator()
        
        if scene.rigify_to_unreal_conversion_mode == 'ADVANCED':
            box = layout.box()
            box.label(text="Advanced Settings:", icon='BONE_DATA')
            box.prop(scene, "rigify_to_unreal_twist_interpolation_arm_length", text="Twist Interpolation Arm Length")
            box.prop(scene, "rigify_to_unreal_twist_interpolation_leg_length", text="Twist Interpolation Leg Length")
            
            box.prop(scene, "rigify_to_unreal_keep_breasts", text="Keep Breast Bones")
            
        layout.separator()
        
        # Execute button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("rigify_to_unreal.convert", text="Convert", icon='CON_ROTLIKE')
        
        layout.separator()
    
