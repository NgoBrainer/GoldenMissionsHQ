"""
Golden Missions Headquarters — Procedural Room Shell v1
Authoring target: Blender 4.x Python

Purpose:
    Starts from an empty scene and builds an object-based, fully editable Golden Missions
    Headquarters room shell. Every architectural element is a separate object so it can
    be modified individually later.

Scope included:
    - Curved/octagonal headquarters room shell
    - Separate wall segments
    - Separate floor and ceiling objects
    - Separate door-frame/opening placeholder objects
    - Separate command dais base and three stair objects: ST-01, ST-02, ST-03
    - Separate camera objects for Camera A, B, C, and D
    - Canonical Mission Lounge placeholder geometry

Scope intentionally excluded:
    - Finished furniture assets
    - Main Console / Secondary Console
    - Finished couches, rug, center table, screens as furniture/detail assets
    - Materials beyond simple architectural placeholders

How to use:
    1. Open Blender.
    2. Go to Scripting workspace.
    3. Open this file and Run Script.
    4. All generated objects are named and organized into collections.
"""

import bpy
import math
from mathutils import Vector

# -----------------------------------------------------------------------------
# Global configuration
# -----------------------------------------------------------------------------

ROOM_WIDTH = 22.0          # X axis, west/east span
ROOM_DEPTH = 16.0          # Y axis, south/north span
WALL_HEIGHT = 5.0
WALL_THICKNESS = 0.35
FLOOR_THICKNESS = 0.18
CEILING_THICKNESS = 0.18
CORNER_CUT = 3.0           # chamfered/curved-room corner approximation

# Golden Missions canonical orientation for this shell:
# North  = +Y: Main Screen / Ms. C Office zone
# South  = -Y: Camera A / Command Dais side
# West   = -X: Elevator/DFP side depending camera view
# East   = +X: Tinkletorium side

MATERIALS = {}


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_collection(name):
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def link_to_collection(obj, collection):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    collection.objects.link(obj)


def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    MATERIALS[name] = mat
    return mat


def apply_material(obj, mat_name):
    obj.data.materials.append(MATERIALS[mat_name])


def cube_obj(name, location, scale, mat_name, collection):
    """Create an editable cube-based object with applied scale."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_material(obj, mat_name)
    link_to_collection(obj, collection)
    return obj


def wall_segment(name, start_xy, end_xy, height, thickness, mat_name, collection):
    """Create a separate rectangular wall segment between two XY points."""
    sx, sy = start_xy
    ex, ey = end_xy
    mid = Vector(((sx + ex) / 2, (sy + ey) / 2, height / 2))
    length = math.hypot(ex - sx, ey - sy)
    angle = math.atan2(ey - sy, ex - sx)

    obj = cube_obj(
        name=name,
        location=mid,
        scale=(length, thickness, height),
        mat_name=mat_name,
        collection=collection,
    )
    obj.rotation_euler[2] = angle
    return obj


def add_label_empty(name, location, collection, display_size=0.5):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "CUBE"
    empty.empty_display_size = display_size
    empty.location = location
    collection.objects.link(empty)
    return empty


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


# -----------------------------------------------------------------------------
# Scene creation
# -----------------------------------------------------------------------------

def setup_scene():
    clear_scene()
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0

    # Collections
    collections = {
        "architecture": make_collection("GMH_Architecture_Room_Shell"),
        "doors": make_collection("GMH_Doors_And_Openings"),
        "stairs": make_collection("GMH_Command_Dais_Stairs"),
        "cameras": make_collection("GMH_Cameras"),
        "furniture": make_collection("GMH_Furniture_Placeholders"),
        "guides": make_collection("GMH_Orientation_Guides"),
    }

    # Materials: intentionally simple and easy to replace
    create_material("GMH_Wall_Warm_Concrete", (0.62, 0.58, 0.50, 1.0))
    create_material("GMH_Floor_Matte_Dark", (0.22, 0.22, 0.21, 1.0))
    create_material("GMH_Ceiling_Dim_Metal", (0.38, 0.37, 0.34, 1.0))
    create_material("GMH_Door_Frame_Brushed_Metal", (0.46, 0.43, 0.38, 1.0))
    create_material("GMH_Command_Dais_Base", (0.30, 0.29, 0.27, 1.0))
    create_material("GMH_Stair_Surfaces", (0.36, 0.34, 0.31, 1.0))
    create_material("GMH_Lounge_Couch_Placeholder", (0.32, 0.30, 0.28, 1.0))
    create_material("GMH_Lounge_Rug_Placeholder", (0.18, 0.24, 0.30, 1.0))
    create_material("GMH_Lounge_Table_Placeholder", (0.42, 0.34, 0.24, 1.0))

    return collections


def build_room_shell(collections):
    arch = collections["architecture"]
    doors = collections["doors"]
    stairs = collections["stairs"]
    guides = collections["guides"]

    half_w = ROOM_WIDTH / 2
    half_d = ROOM_DEPTH / 2
    c = CORNER_CUT

    # Octagonal/chamfered perimeter points, clockwise from north-west shoulder.
    pts = [
        (-half_w + c, half_d),
        ( half_w - c, half_d),
        ( half_w, half_d - c),
        ( half_w, -half_d + c),
        ( half_w - c, -half_d),
        (-half_w + c, -half_d),
        (-half_w, -half_d + c),
        (-half_w, half_d - c),
    ]

    # Floor and ceiling are separate editable objects.
    floor = cube_obj(
        "GMH_Floor_Plate",
        location=(0, 0, -FLOOR_THICKNESS / 2),
        scale=(ROOM_WIDTH, ROOM_DEPTH, FLOOR_THICKNESS),
        mat_name="GMH_Floor_Matte_Dark",
        collection=arch,
    )
    ceiling = cube_obj(
        "GMH_Ceiling_Plate",
        location=(0, 0, WALL_HEIGHT + CEILING_THICKNESS / 2),
        scale=(ROOM_WIDTH, ROOM_DEPTH, CEILING_THICKNESS),
        mat_name="GMH_Ceiling_Dim_Metal",
        collection=arch,
    )

    wall_names = [
        "GMH_Wall_North_MainScreen_Zone",
        "GMH_Wall_NorthEast_Curve",
        "GMH_Wall_East_Tinkletorium_Zone",
        "GMH_Wall_SouthEast_Curve",
        "GMH_Wall_South_CommandDais_Back",
        "GMH_Wall_SouthWest_Curve",
        "GMH_Wall_West_Elevator_DFP_Zone",
        "GMH_Wall_NorthWest_Curve_MsC_Zone",
    ]

    for i, name in enumerate(wall_names):
        wall_segment(
            name,
            pts[i],
            pts[(i + 1) % len(pts)],
            WALL_HEIGHT,
            WALL_THICKNESS,
            "GMH_Wall_Warm_Concrete",
            arch,
        )

    # Door/opening objects are separate editable frame placeholders.
    # They intentionally sit in front of the wall shell instead of boolean-cutting it,
    # keeping every item independent and easy to modify.
    door_specs = [
        ("GMH_DoorFrame_Elevator_Flush_West", (-half_w - 0.02, -4.8, 1.35), (0.22, 2.0, 2.7), 0),
        ("GMH_DoorFrame_DFP_West_Secure", (-half_w - 0.02,  2.9, 1.35), (0.22, 1.7, 2.7), 0),
        ("GMH_DoorFrame_MsC_Office_NorthWest", (-6.9, half_d + 0.02, 1.35), (2.0, 0.22, 2.7), 0),
        ("GMH_DoorFrame_Tinkletorium_East", (half_w + 0.02, 2.3, 1.35), (0.22, 1.9, 2.7), 0),
    ]

    for name, loc, scale, rot_z in door_specs:
        obj = cube_obj(name, loc, scale, "GMH_Door_Frame_Brushed_Metal", doors)
        obj.rotation_euler[2] = rot_z

    # Command dais shell only: separate base and three stair objects.
    # Dais is on the south side; stair line remains in front of the dais.
    dais = cube_obj(
        "GMH_Command_Dais_Base_Shell",
        location=(4.8, -5.75, 0.42),
        scale=(8.2, 3.8, 0.84),
        mat_name="GMH_Command_Dais_Base",
        collection=stairs,
    )

    stair_specs = [
        ("GMH_ST-01_Left_Stair",  (1.1, -3.55, 0.14), (2.2, 1.0, 0.28)),
        ("GMH_ST-02_Center_Stair", (4.8, -3.55, 0.14), (2.8, 1.0, 0.28)),
        ("GMH_ST-03_Right_Stair", (8.5, -3.55, 0.14), (2.2, 1.0, 0.28)),
    ]
    for name, loc, scale in stair_specs:
        cube_obj(name, loc, scale, "GMH_Stair_Surfaces", stairs)

    # Orientation guide empties, not mesh furniture.
    add_label_empty("GUIDE_North_MainScreen_Wall", (0, half_d + 0.75, 2.5), guides)
    add_label_empty("GUIDE_South_CommandDais_CameraA", (0, -half_d - 0.75, 2.5), guides)
    add_label_empty("GUIDE_West_Elevator_DFP", (-half_w - 0.75, 0, 2.5), guides)
    add_label_empty("GUIDE_East_Tinkletorium", (half_w + 0.75, 0, 2.5), guides)


def build_mission_lounge(collections):
    """Create CSR placeholder geometry for the Canonical Mission Lounge.

    These are simple editable footprint blocks only. They establish location,
    rotation, scale, occupied space, and replacement-ready object origins without
    finished furniture detailing.
    """
    furniture = collections["furniture"]

    # Three-couch arrangement leaves the north / Main Screen side open.
    couch_specs = [
        ("GMH_Couch_South_Placeholder", (0.0, -1.45, 0.45), (4.8, 0.85, 0.90), 0.0),
        ("GMH_Couch_West_Placeholder", (-3.05, 1.2, 0.45), (3.6, 0.85, 0.90), math.radians(90)),
        ("GMH_Couch_East_Placeholder", (3.05, 1.2, 0.45), (3.6, 0.85, 0.90), math.radians(90)),
    ]

    for name, loc, scale, rot_z in couch_specs:
        obj = cube_obj(name, loc, scale, "GMH_Lounge_Couch_Placeholder", furniture)
        obj.rotation_euler[2] = rot_z

    # Low, thin footprint marker for the approved Mission Lounge rug.
    cube_obj(
        "GMH_MissionLounge_Rug",
        location=(0.0, 1.2, 0.015),
        scale=(5.6, 4.3, 0.03),
        mat_name="GMH_Lounge_Rug_Placeholder",
        collection=furniture,
    )

    # Simple center block defining the coffee table replacement volume.
    cube_obj(
        "GMH_MissionLounge_CoffeeTable",
        location=(0.0, 1.2, 0.32),
        scale=(2.2, 1.2, 0.38),
        mat_name="GMH_Lounge_Table_Placeholder",
        collection=furniture,
    )


def create_cameras(collections):
    cam_collection = collections["cameras"]
    camera_specs = [
        ("GMH_Camera_A_CommandDais_South_Facing_North", (0, -11.5, 2.2), (0, 1.0, 2.0), 35),
        ("GMH_Camera_B_Elevator_Threshold_Facing_Room", (-10.8, -4.8, 1.7), (1.5, 1.0, 1.8), 32),
        ("GMH_Camera_C_MainScreen_Facing_CommandDais", (0, 10.8, 2.4), (4.8, -5.3, 1.8), 35),
        ("GMH_Camera_D_Tinkletorium_Threshold_Facing_West", (12.2, 2.3, 1.8), (0, 0, 1.8), 32),
    ]

    for name, loc, target, lens in camera_specs:
        cam_data = bpy.data.cameras.new(name)
        cam_data.lens = lens
        cam_obj = bpy.data.objects.new(name, cam_data)
        cam_obj.location = loc
        look_at(cam_obj, target)
        cam_collection.objects.link(cam_obj)

    bpy.context.scene.camera = bpy.data.objects["GMH_Camera_B_Elevator_Threshold_Facing_Room"]


def add_lighting():
    bpy.ops.object.light_add(type="AREA", location=(0, 0, 5.7))
    light = bpy.context.object
    light.name = "GMH_Temporary_Area_Light_RoomShell"
    light.data.energy = 450
    light.data.size = 9


def set_view_settings():
    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"
    bpy.context.scene.eevee.taa_render_samples = 64
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080


def main():
    collections = setup_scene()
    build_room_shell(collections)
    build_mission_lounge(collections)
    create_cameras(collections)
    add_lighting()
    set_view_settings()

    # Set origins to object geometry centers and keep all transforms simple.
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    bpy.ops.object.select_all(action="DESELECT")

    print("Golden Missions Headquarters room shell generated successfully.")
    print("Finished furniture and consoles intentionally excluded from this room-shell pass.")


if __name__ == "__main__":
    main()
