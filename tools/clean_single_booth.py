import argparse
import math
import os

import bmesh
import bpy
from mathutils import Vector


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keep", choices=("positive", "negative"), default="positive")
    parser.add_argument("--output-blend", required=True)
    parser.add_argument("--output-glb", required=True)
    parser.add_argument("--preview", required=True)
    return parser.parse_args(os.sys.argv[os.sys.argv.index("--") + 1 :])


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_area_light(name, location, energy, size, color):
    light_data = bpy.data.lights.new(name=name, type="AREA")
    light_data.energy = energy
    light_data.shape = "DISK"
    light_data.size = size
    light_data.color = color
    light_object = bpy.data.objects.new(name, light_data)
    bpy.context.scene.collection.objects.link(light_object)
    light_object.location = location
    look_at(light_object, (0.0, 0.0, 0.45))
    return light_object


def bounds(obj):
    coordinates = [vertex.co.copy() for vertex in obj.data.vertices]
    return (
        Vector(tuple(min(coordinate[axis] for coordinate in coordinates) for axis in range(3))),
        Vector(tuple(max(coordinate[axis] for coordinate in coordinates) for axis in range(3))),
    )


args = parse_args()
scene = bpy.context.scene

mesh_objects = [obj for obj in scene.objects if obj.type == "MESH"]
if not mesh_objects:
    raise RuntimeError("No mesh object found")

booth = max(mesh_objects, key=lambda obj: len(obj.data.vertices))
for obj in list(scene.objects):
    if obj != booth:
        bpy.data.objects.remove(obj, do_unlink=True)

original_vertices = len(booth.data.vertices)
original_polygons = len(booth.data.polygons)

mesh = booth.data
bm = bmesh.new()
bm.from_mesh(mesh)
if args.keep == "positive":
    vertices_to_remove = [vertex for vertex in bm.verts if vertex.co.x < 0.0]
else:
    vertices_to_remove = [vertex for vertex in bm.verts if vertex.co.x > 0.0]

bmesh.ops.delete(bm, geom=vertices_to_remove, context="VERTS")
bm.to_mesh(mesh)
bm.free()
mesh.update()

minimum, maximum = bounds(booth)
offset = Vector((-(minimum.x + maximum.x) / 2.0, -(minimum.y + maximum.y) / 2.0, -minimum.z))
for vertex in mesh.vertices:
    vertex.co += offset
mesh.update()

booth.name = "Cabina_Base_Generada"
mesh.name = "Cabina_Base_Generada_Mesh"
booth["estado_activo"] = "PRELIMINAR_GENERADO_IA"
booth["uso"] = "Visualizacion y validacion; no usar como plano constructivo"
booth["lado_conservado"] = args.keep

scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"

minimum, maximum = bounds(booth)
dimensions = maximum - minimum

# Render a neutral preview without retaining helper objects in the deliverable.
preview_objects = []

camera_data = bpy.data.cameras.new("Preview_Camera")
camera = bpy.data.objects.new("Preview_Camera", camera_data)
scene.collection.objects.link(camera)
camera.location = (dimensions.x * 2.6, -dimensions.y * 2.7, dimensions.z * 1.8)
camera_data.lens = 52
look_at(camera, (0.0, 0.0, dimensions.z * 0.48))
scene.camera = camera
preview_objects.append(camera)

preview_objects.append(
    add_area_light(
        "Preview_Key",
        (dimensions.x * 2.0, -dimensions.y * 2.0, dimensions.z * 3.0),
        950.0,
        3.0,
        (1.0, 0.82, 0.67),
    )
)
preview_objects.append(
    add_area_light(
        "Preview_Fill",
        (-dimensions.x * 2.5, -dimensions.y * 0.5, dimensions.z * 1.7),
        550.0,
        2.5,
        (0.66, 0.78, 1.0),
    )
)

bpy.ops.mesh.primitive_plane_add(size=max(dimensions.x, dimensions.y) * 8.0, location=(0.0, 0.0, -0.003))
ground = bpy.context.object
ground.name = "Preview_Ground"
ground_material = bpy.data.materials.new("Preview_Ground_Material")
ground_material.diffuse_color = (0.035, 0.04, 0.05, 1.0)
ground.data.materials.append(ground_material)
preview_objects.append(ground)

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = args.preview
scene.world.color = (0.012, 0.014, 0.018)
scene.render.image_settings.color_mode = "RGBA"

bpy.ops.render.render(write_still=True)

for obj in preview_objects:
    if obj.name in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

# Keep only the booth selected for export.
bpy.ops.object.select_all(action="DESELECT")
booth.select_set(True)
bpy.context.view_layer.objects.active = booth

os.makedirs(os.path.dirname(args.output_blend), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=args.output_blend)

bpy.ops.export_scene.gltf(
    filepath=args.output_glb,
    export_format="GLB",
    use_selection=True,
    export_apply=True,
)

print("CLEAN_BOOTH_RESULT")
print(f"source_vertices={original_vertices}")
print(f"source_polygons={original_polygons}")
print(f"kept_vertices={len(mesh.vertices)}")
print(f"kept_polygons={len(mesh.polygons)}")
print(f"dimensions={tuple(round(value, 6) for value in dimensions)}")
print(f"blend={args.output_blend}")
print(f"glb={args.output_glb}")
print(f"preview={args.preview}")
