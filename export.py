import bpy

from . import utility

# Export properties
def register_export_properties():
    
    # Register scene properties
    # bpy.types.Scene.rigify_to_unreal_modified_mesh = bpy.props.PointerProperty(
    #     name="Modified Mesh",
    #     description="Processed mesh object",
    #     type=bpy.types.Object,
    #     poll=lambda self, obj: obj.type == 'MESH'
    # )
    
    bpy.types.Scene.rigify_to_unreal_converted_rig = bpy.props.PointerProperty(
        name="Rig",
        description="Resulting UE4 rig",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    
    # Export path
    bpy.types.Scene.rigify_to_unreal_export_filepath = bpy.props.StringProperty(
        name="File",
        description="Export file path",
        default="",
        subtype='FILE_PATH'
    )
    
    # Include options
    bpy.types.Scene.rigify_to_unreal_export_mesh = bpy.props.BoolProperty(
        name="Export Mesh",
        description="Include mesh in export",
        default=True
    )
    
    bpy.types.Scene.rigify_to_unreal_export_armature = bpy.props.BoolProperty(
        name="Export Armature",
        description="Include armature in export",
        default=True
    )
    
    bpy.types.Scene.rigify_to_unreal_export_animation = bpy.props.BoolProperty(
        name="Export Animation",
        description="Include animation in export",
        default=False
    )
    
    # Transform settings
    bpy.types.Scene.rigify_to_unreal_fbx_scale = bpy.props.FloatProperty(
        name="Scale",
        description="Scale factor for export",
        default=100.0,
        min=0.01,
        max=10000.0
    )
    
    bpy.types.Scene.rigify_to_unreal_fbx_apply_scale = bpy.props.EnumProperty(
        name="Apply Scaling",
        description="How to apply scale on export",
        items=[
            ('FBX_SCALE_NONE', "None", "No scale"),
            ('FBX_SCALE_ALL', "All", "Apply scale to all objects"),
            ('FBX_SCALE_UNITS', "Units", "Apply scale based on units"),
        ],
        default='FBX_SCALE_ALL'
    )
    
    # Forward axis
    bpy.types.Scene.rigify_to_unreal_fbx_forward = bpy.props.EnumProperty(
        name="Forward",
        description="Forward axis for export",
        items=[
            ('X', "X", "X axis forward"),
            ('Y', "Y", "Y axis forward"),
            ('Z', "Z", "Z axis forward"),
            ('-X', "-X", "Negative X axis forward"),
            ('-Y', "-Y", "Negative Y axis forward"),
            ('-Z', "-Z", "Negative Z axis forward"),
        ],
        default='-Z'
    )
    
    # Up axis
    bpy.types.Scene.rigify_to_unreal_fbx_up = bpy.props.EnumProperty(
        name="Up",
        description="Up axis for export",
        items=[
            ('X', "X", "X axis up"),
            ('Y', "Y", "Y axis up"),
            ('Z', "Z", "Z axis up"),
            ('-X', "-X", "Negative X axis up"),
            ('-Y', "-Y", "Negative Y axis up"),
            ('-Z', "-Z", "Negative Z axis up"),
        ],
        default='Y'
    )
    
    # Armature settings
    bpy.types.Scene.rigify_to_unreal_fbx_primary_bone_axis = bpy.props.EnumProperty(
        name="Primary Bone Axis",
        description="Primary bone axis for export",
        items=[
            ('X', "X", "X axis"),
            ('Y', "Y", "Y axis"),
            ('Z', "Z", "Z axis"),
            ('-X', "-X", "Negative X axis"),
            ('-Y', "-Y", "Negative Y axis"),
            ('-Z', "-Z", "Negative Z axis"),
        ],
        default='X'
    )
    
    bpy.types.Scene.rigify_to_unreal_fbx_secondary_bone_axis = bpy.props.EnumProperty(
        name="Secondary Bone Axis",
        description="Secondary bone axis for export",
        items=[
            ('X', "X", "X axis"),
            ('Y', "Y", "Y axis"),
            ('Z', "Z", "Z axis"),
            ('-X', "-X", "Negative X axis"),
            ('-Y', "-Y", "Negative Y axis"),
            ('-Z', "-Z", "Negative Z axis"),
        ],
        default='-Y'
    )
    
    # Animation settings
    bpy.types.Scene.rigify_to_unreal_export_nla_strips = bpy.props.BoolProperty(
        name="NLA Strips",
        description="Export NLA strips as animations",
        default=False
    )
    
    bpy.types.Scene.rigify_to_unreal_export_all_actions = bpy.props.BoolProperty(
        name="All Actions",
        description="Export all actions as animations",
        default=False
    )
    

def unregister_export_properties():
    #del bpy.types.Scene.rigify_to_unreal_modified_mesh
    del bpy.types.Scene.rigify_to_unreal_converted_rig
    
    del bpy.types.Scene.rigify_to_unreal_export_filepath
    del bpy.types.Scene.rigify_to_unreal_export_mesh
    del bpy.types.Scene.rigify_to_unreal_export_armature
    del bpy.types.Scene.rigify_to_unreal_export_animation
    
    del bpy.types.Scene.rigify_to_unreal_fbx_scale
    del bpy.types.Scene.rigify_to_unreal_fbx_apply_scale
    del bpy.types.Scene.rigify_to_unreal_fbx_forward
    del bpy.types.Scene.rigify_to_unreal_fbx_up
    del bpy.types.Scene.rigify_to_unreal_fbx_primary_bone_axis
    del bpy.types.Scene.rigify_to_unreal_fbx_secondary_bone_axis
    del bpy.types.Scene.rigify_to_unreal_export_nla_strips
    del bpy.types.Scene.rigify_to_unreal_export_all_actions
    
        
          
# OPERATOR

class RIGIFYTOUNREAL_OT_export(bpy.types.Operator):
    """Export the converted rig as FBX for Unreal Engine"""
    bl_idname = "rigify_to_unreal.export"
    bl_label = "Export to Unreal"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        """Check if we're in object mode and have required objects"""
        return context.mode == 'OBJECT' \
            and context.scene.rigify_to_unreal_converted_rig != None
    
    def execute(self, context):
        scene = context.scene
        
        # Get objects to export
        rig_obj = scene.rigify_to_unreal_converted_rig
        meshes = utility.get_meshes_attached_to_rig(rig_obj)
        
        # Validate objects
        if (not len(meshes) > 0 and scene.rigify_to_unreal_export_mesh) or not rig_obj:
            self.report({'ERROR'}, "No objects to export!")
            return {'CANCELLED'}
        
        # Get export path
        export_path = scene.rigify_to_unreal_export_filepath
        
        # Validate path
        if not export_path:
            self.report({'ERROR'}, "Export path not set!")
            return {'CANCELLED'}
        
        # Ensure .fbx extension
        if not export_path.lower().endswith('.fbx'):
            export_path += '.fbx'
        
        # Apply scale to objects (scale them up by 100)
        export_scale = scene.rigify_to_unreal_fbx_scale
        
        rig_obj.scale *= export_scale
        
        bpy.ops.object.select_all(action='DESELECT')
        rig_obj.select_set(True)
        context.view_layer.objects.active = rig_obj
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        # Deselect all objects first
        bpy.ops.object.select_all(action='DESELECT')
        
        # Select objects based on export options
        if scene.rigify_to_unreal_export_mesh:
            for mesh_obj in meshes:
                if mesh_obj:
                    mesh_obj.select_set(True)
                    context.view_layer.objects.active = mesh_obj
        
        if scene.rigify_to_unreal_export_armature and rig_obj:
            rig_obj.select_set(True)
            context.view_layer.objects.active = rig_obj
        
        # Check if we have any objects selected
        if not context.selected_objects:
            self.report({'ERROR'}, "No objects selected for export!")
            return {'CANCELLED'}
        
        # Export FBX with Unreal Engine settings
        try:
            bpy.ops.export_scene.fbx(
            filepath=export_path,
            use_selection=True,
            global_scale=1.0,
            apply_scale_options=scene.rigify_to_unreal_fbx_apply_scale,
            axis_forward=scene.rigify_to_unreal_fbx_forward,
            axis_up=scene.rigify_to_unreal_fbx_up,
            primary_bone_axis=scene.rigify_to_unreal_fbx_primary_bone_axis,
            secondary_bone_axis=scene.rigify_to_unreal_fbx_secondary_bone_axis,
            add_leaf_bones=False,
            use_armature_deform_only=True,
            bake_anim=scene.rigify_to_unreal_export_animation,
            bake_anim_use_nla_strips=scene.rigify_to_unreal_export_nla_strips,
            bake_anim_use_all_actions=scene.rigify_to_unreal_export_all_actions,
            bake_space_transform=True
        )
            
            self.report({'INFO'}, f"Exported successfully to {export_path}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            return {'CANCELLED'}
        
        if rig_obj:
            rig_obj.scale /= export_scale
            
            bpy.ops.object.select_all(action='DESELECT')
            rig_obj.select_set(True)
            context.view_layer.objects.active = rig_obj
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        return {'FINISHED'}
    
    
# PANEL

class RIGIFYTOUNREAL_PT_export_settings(bpy.types.Panel):
    """Export settings subpanel"""
    bl_label = "Export Settings"
    bl_idname = "RIGIFYTOUNREAL_PT_export_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RigifyToUnreal"
    bl_parent_id = "RIGIFYTOUNREAL_PT_main_panel"  # This makes it a subpanel
    bl_options = {'DEFAULT_CLOSED'}  # Start collapsed

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Content
        # layout.prop(scene, "rigify_to_unreal_modified_mesh", text="Converted Mesh")
        layout.prop(scene, "rigify_to_unreal_converted_rig", text="Converted Rig")
        
        # Export path
        layout.prop(scene, "rigify_to_unreal_export_filepath", text="Path")
        
        # Include options
        layout.separator()
        row = layout.row()
        row.prop(scene, "rigify_to_unreal_export_mesh", text="Mesh")
        row.prop(scene, "rigify_to_unreal_export_armature", text="Armature")
        layout.prop(scene, "rigify_to_unreal_export_animation", text="Animation")
        
        # Transform section
        box = layout.box()
        box.label(text="Transform:", icon='ORIENTATION_GLOBAL')
        box.prop(scene, "rigify_to_unreal_fbx_scale", text="Scale")
        box.prop(scene, "rigify_to_unreal_fbx_apply_scale", text="Apply Scaling")
        
        row = box.row(align=True)
        row.prop(scene, "rigify_to_unreal_fbx_forward", text="Forward")
        row.prop(scene, "rigify_to_unreal_fbx_up", text="Up")
        
        # Armature section
        box = layout.box()
        box.label(text="Armature:", icon='ARMATURE_DATA')
        box.prop(scene, "rigify_to_unreal_fbx_primary_bone_axis", text="Primary Bone Axis")
        box.prop(scene, "rigify_to_unreal_fbx_secondary_bone_axis", text="Secondary Bone Axis")
        
        # Animation section
        box = layout.box()
        box.label(text="Animation:", icon='ACTION')
        row = box.row(align=True)
        row.prop(scene, "rigify_to_unreal_export_nla_strips", text="NLA Strips")
        row.prop(scene, "rigify_to_unreal_export_all_actions", text="All Actions")
        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("rigify_to_unreal.setup_scene", text="Setup Scene", icon='SCENE')
        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("rigify_to_unreal.export", text="Export", icon='EXPORT')