bl_info = {
    "name": "B2G Pipeline v2",
    "author": "Kimedero",
    "version": (0, 0, 2),
    "blender": (3, 0, 0),
    # "location": "View3D > Sidebar > My Tab 2",
    "description": "A pipeline to export meshes with collisions into Godot",
    "category": "3D View",
}

import bpy

class VIEW3D_PT_main_panel(bpy.types.Panel):
    bl_label = "B2G Main Panel"
    bl_idname = "VIEW3D_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "B2G Pipeline"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # layout.label(text="Hello world!")
        
        # layout.separator()

        layout.prop(scene, "body_type", text="Body type:")        
    
        if scene.body_type != 'NONE' and scene.body_type != 'NAVMESH':  
            layout.prop(scene, "collision_type", text="Collision shape:")
            
            if scene.collision_type == 'PRIMITIVE':
                layout.prop(scene, "primitive_collision_type", text="Primitive collision type:")
        
        layout.separator()

        if scene.body_type == 'RIGID':
            layout.prop(scene, "rigid_body_mass")
            layout.prop(scene, "rigid_body_center_of_mass_mode")
            layout.prop(scene, "rigid_body_center_of_mass")

            layout.separator()

            layout.prop(scene, "physics_material_override_toggle")

            if scene.physics_material_override_toggle:
                layout.prop(scene, "physics_material_friction") 
                layout.prop(scene, "physics_material_rough") 
                layout.prop(scene, "physics_material_bounce") 
                layout.prop(scene, "physics_material_absorbent")

            layout.separator()
        
        if scene.body_type == 'AREA':
            layout.prop(scene, "area_3d_monitoring")
            layout.prop(scene, "area_3d_monitorable")

            layout.separator()

        # layout.operator("object.select_all")
        layout.operator("wm.set_mesh_properties")

        layout.separator()


# The Set Mesh Properties button
class WM_OT_set_mesh_properties(bpy.types.Operator):
    bl_idname = "wm.set_mesh_properties"
    bl_label = "Set Mesh Properties"

    def execute(self, context):
        scene = context.scene
        object_type = scene.body_type # mesh_object_type

        selected_objects = bpy.context.selected_objects

        # print(f"Mesh reset! - {dir(scene)}")

        if object_type == 'NONE':
            process_mesh_reset(selected_objects, scene)
        elif object_type == 'STATIC':
            process_static_body(selected_objects, scene)
        elif object_type == 'CHARACTER':
            process_character_body(selected_objects, scene)
        elif object_type == 'RIGID':
            process_rigid_body(selected_objects, scene)
        elif object_type == 'AREA':
            process_area_3d(selected_objects, scene)
        elif object_type == 'NAVMESH':
            process_navmesh(selected_objects, scene)
        elif object_type == 'COLLISION_SHAPE':
            process_collision_shape(selected_objects, scene)

        return {'FINISHED'}


def process_mesh_reset(selected_objects, scene):
    for obj in selected_objects:
        delete_all_custom_properties(obj)

        print(f"Mesh reset for '{obj.name}'! - {scene.body_type} - {scene.mesh_object_type}")


def process_collision_properties(obj, scene):
    create_custom_property(obj, "collision_type", scene.collision_type)

    if scene.collision_type == 'PRIMITIVE':
        create_custom_property(obj, "primitive_collision_type", scene.primitive_collision_type)


def process_static_body(selected_objects, scene):
    for obj in selected_objects:
        delete_all_custom_properties(obj)

        if obj.type == 'MESH':
            create_custom_property(obj, "is_static_body", True)

            process_collision_properties(obj, scene)

        print(f"Processing '{obj.name}' as static body! -> {scene.body_type}")


def process_character_body(selected_objects, scene):
    for obj in selected_objects:
        delete_all_custom_properties(obj)

        if obj.type == 'MESH':
            create_custom_property(obj, "is_character_body", True)

            process_collision_properties(obj, scene)

        print(f"Processing '{obj.name}' as character body! -> {scene.body_type}")


def process_rigid_body(selected_objects, scene):
    for obj in selected_objects:
        delete_all_custom_properties(obj)

        if obj.type == 'MESH':
            create_custom_property(obj, "is_rigid_body", True)

            create_custom_property(obj, "rigid_body_mass", scene.rigid_body_mass)
            create_custom_property(obj, "rigid_body_center_of_mass_mode", scene.rigid_body_center_of_mass_mode)
            create_custom_property(obj, "rigid_body_center_of_mass", scene.rigid_body_center_of_mass)

            # Physics Material Override
            create_custom_property(obj, "physics_material_override_toggle", scene.physics_material_override_toggle)
            create_custom_property(obj, "physics_material_friction", scene.physics_material_friction)
            create_custom_property(obj, "physics_material_rough", scene.physics_material_rough)
            create_custom_property(obj, "physics_material_bounce", scene.physics_material_bounce) 
            create_custom_property(obj, "physics_material_absorbent", scene.physics_material_absorbent)

            process_collision_properties(obj, scene)

        print(f"Processing '{obj.name}' as rigid body! -> {scene.body_type}")


def process_area_3d(selected_objects, scene):
    for obj in selected_objects:
        delete_all_custom_properties(obj)

        if obj.type == 'MESH':
            create_custom_property(obj, "is_area_3d", True)
            
            area_3d_monitoring = scene.area_3d_monitoring
            create_custom_property(obj, "area_3d_monitoring", area_3d_monitoring)
            
            area_3d_monitorable = scene.area_3d_monitorable
            create_custom_property(obj, "area_3d_monitorable", area_3d_monitorable)

            process_collision_properties(obj, scene)

        print(f"Processing '{obj.name}' as area 3d! -> {scene.body_type}")


def process_navmesh(selected_objects, scene):
    for obj in selected_objects:
        delete_all_custom_properties(obj)

        if obj.type == 'MESH':
            create_custom_property(obj, "is_navmesh", True)
        
        print(f"Processing '{obj.name}' as navmesh! -> {scene.body_type}")


def process_collision_shape(selected_objects, scene):
    for obj in selected_objects:
        delete_all_custom_properties(obj)

        if obj.type == 'MESH':
            create_custom_property(obj, "is_collision_shape", True)

            process_collision_properties(obj, scene)
        
        print(f"Processing '{obj.name}' as collision shape! -> {scene.body_type}")


# creating a new custom property for a selected object
def create_custom_property(object, property_name, property_value):
    object[property_name] = property_value


def delete_all_custom_properties(object):
    for key in list(object.keys()):
        del object[key]


def register_properties():
    # we create a new property in scenes
    bpy.types.Scene.body_type = bpy.props.EnumProperty(
        items=[
            ('NONE', "None", ""),
            (None),
            ('STATIC', "StaticBody3D", ""),
            ('CHARACTER', "CharacterBody3D", ""),
            ('RIGID', "RigidBody3D", ""),
            (None),
            ('AREA', "Area3D", ""),
            (None),
            ('NAVMESH', "Navigation Mesh", ""),
            (None),
            ('COLLISION_SHAPE', "Collision Shape", ""),
        ]
    )
    bpy.types.Scene.collision_type = bpy.props.EnumProperty(
        items=[
            ('NO_COL', "None", ""),
            (None),
            ('CONVEX', "Convex", ""),
            ('CONCAVE', "Concave", ""),
            ('PRIMITIVE', "Primitive", ""),
        ],
        default="CONVEX",
    )
    bpy.types.Scene.primitive_collision_type = bpy.props.EnumProperty(
        items=[
            ('BOX', "Box", ""),
            # ('SPHERE', "Sphere", ""),
            # ('CYLINDER', "Cylinder", ""),
        ]
    )

    # RigidBody properties and toggles    
    bpy.types.Scene.rigid_body_mass = bpy.props.IntProperty(
        name="RigidBody Mass",
        default=1,
        min=1,
        description="Text input for RigidBody mass",
        # update=rigid_text_update
    )  
    bpy.types.Scene.rigid_body_center_of_mass_mode = bpy.props.EnumProperty(
        name="Center of Mass Mode",
        items=[
            ('CUSTOM', "Custom", ""),
            ('AUTO', "Auto", ""),
        ],
        default='CUSTOM',
        # update=lambda self, ctx: print_toggle("RigidBody - Center of Mass Mode")
    )
    bpy.types.Scene.rigid_body_center_of_mass = bpy.props.FloatVectorProperty(
        name="RigidBody Center of Mass",
        default=(0.0, 0.0, 0.0),
        size=3,
        description="Text input for RigidBody center of mass",
    )
    bpy.types.Scene.physics_material_override_toggle = bpy.props.BoolProperty(
        name="Physics Material Override",
        default=False,
    )
    bpy.types.Scene.physics_material_friction = bpy.props.FloatProperty(
        name="Physics Material Friction",
        default=1.0,
        min=0.0,
        max=1.0,
        description="Text input for Physics Material Friction",
        # update=rigid_text_update
    )
    bpy.types.Scene.physics_material_rough = bpy.props.BoolProperty(
        name="Physics Material Rough",
        default=False,
    )
    bpy.types.Scene.physics_material_bounce = bpy.props.FloatProperty(
        name="Physics Material Bounce",
        default=0.0,
        min=0.0,
        max=1.0,
        description="Text input for Physics Material Bounce",
        # update=rigid_text_update
    )
    bpy.types.Scene.physics_material_absorbent = bpy.props.BoolProperty(
        name="Physics Material Absorbent",
        default=False,
    )

    # Area3D properties and toggles    
    bpy.types.Scene.area_3d_monitoring = bpy.props.BoolProperty(
        name="Monitoring",
        default=True,
    )
    bpy.types.Scene.area_3d_monitorable = bpy.props.BoolProperty(
        name="Monitorable",
        default=True,
    )
    


def unregister_properties():
    props = [
        "body_type",
        "collision_type",
        "primitive_collision_type",
        "rigid_body_mass", "rigid_body_center_of_mass_mode", "rigid_body_center_of_mass", 
        "physics_material_override_toggle", "physics_material_friction", "physics_material_rough", "physics_material_bounce", "physics_material_absorbent",
        "area_3d_monitoring", "area_3d_monitorable",
    ]
    for p in props:
        delattr(bpy.types.Scene, p)


classes = (
    WM_OT_set_mesh_properties,
    VIEW3D_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()


def unregister():
    unregister_properties()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
