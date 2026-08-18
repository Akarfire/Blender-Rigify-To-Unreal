bl_info = {
    "name": "RigifyToUnreal",
    "author": "AkarFire / K Scarlet",
    "version": (1, 0),
    "blender": (5, 2, 0),
    "location": "View3D > Sidebar > RigifyToUnreal",
    "description": "Convert Rigify deform rig to Unreal Engine compatible skeleton",
    "category": "Rigging",
}

import bpy

from . import panel
from . import convert_operator
from . import export 
from . import setup_scene

# Registration
classes = [
    panel.RIGIFYTOUNREAL_PT_main_panel,
    convert_operator.RIGIFYTOUNREAL_OT_execute,
    export.RIGIFYTOUNREAL_PT_export_settings,
    export.RIGIFYTOUNREAL_OT_export,
    setup_scene.RIGIFYTOUNREAL_OT_setup_scene
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register scene properties
    # bpy.types.Scene.rigify_to_unreal_mesh = bpy.props.PointerProperty(
    #     name="Source Mesh",
    #     description="Select the mesh object to process",
    #     type=bpy.types.Object,
    #     poll=lambda self, obj: obj.type == 'MESH'
    # )
    
    bpy.types.Scene.rigify_to_unreal_rigify_rig = bpy.props.PointerProperty(
        name="Rig",
        description="Select rigify armature to process",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    
    bpy.types.Scene.rigify_to_unreal_conversion_mode = bpy.props.EnumProperty(
        name="Conversion Mode",
        description="Select the conversion mode",
        items=[
            ('SIMPLE', "Simple", "Basic skeleton, no twist bones"),
            ('ADVANCED', "Advanced", "Keep twist bones for better deformation + additional settings"),
        ],
        default='SIMPLE'
    )
    
    bpy.types.Scene.rigify_to_unreal_twist_interpolation_arm_length = bpy.props.FloatProperty(
        name="Twist Interpolation Arm Length",
        description="Distance threshold for twist bone interpolation",
        default=0.25,
        min=0.0,
        max=1.0,
        precision=3,
        subtype='DISTANCE'
    )
    
    bpy.types.Scene.rigify_to_unreal_twist_interpolation_leg_length = bpy.props.FloatProperty(
        name="Twist Interpolation Leg Length",
        description="Distance threshold for twist bone interpolation",
        default=0.45,
        min=0.0,
        max=1.0,
        precision=3,
        subtype='DISTANCE'
    )
    
    bpy.types.Scene.rigify_to_unreal_keep_breasts = bpy.props.BoolProperty(
        name="Keep breast bones",
        description="Whether to keep breast bones or not",
        default=False
    )
    
    export.register_export_properties()

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    # Unregister scene properties
    # del bpy.types.Scene.rigify_to_unreal_mesh
    del bpy.types.Scene.rigify_to_unreal_rigify_rig
    
    del bpy.types.Scene.rigify_to_unreal_conversion_mode
    del bpy.types.Scene.rigify_to_unreal_twist_interpolation_arm_length
    del bpy.types.Scene.rigify_to_unreal_twist_interpolation_leg_length
    del bpy.types.Scene.rigify_to_unreal_keep_breasts
    
    export.unregister_export_properties()


if __name__ == "__main__":
    register()