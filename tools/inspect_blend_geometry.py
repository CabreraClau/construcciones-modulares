import bpy
import json
from mathutils import Vector


def world_bounds(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return {
        "min": [min(point[i] for point in corners) for i in range(3)],
        "max": [max(point[i] for point in corners) for i in range(3)],
    }


def connected_components(mesh):
    vertex_count = len(mesh.vertices)
    parent = list(range(vertex_count))
    size = [1] * vertex_count

    def find(item):
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left, right):
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        if size[left_root] < size[right_root]:
            left_root, right_root = right_root, left_root
        parent[right_root] = left_root
        size[left_root] += size[right_root]

    for edge in mesh.edges:
        union(edge.vertices[0], edge.vertices[1])

    summaries = {}
    for vertex in mesh.vertices:
        root = find(vertex.index)
        coordinate = vertex.co
        summary = summaries.setdefault(
            root,
            {
                "vertices": 0,
                "min": [float("inf")] * 3,
                "max": [float("-inf")] * 3,
                "sum": [0.0] * 3,
            },
        )
        summary["vertices"] += 1
        for axis in range(3):
            value = coordinate[axis]
            summary["min"][axis] = min(summary["min"][axis], value)
            summary["max"][axis] = max(summary["max"][axis], value)
            summary["sum"][axis] += value

    result = []
    for root, summary in summaries.items():
        summary["root"] = root
        summary["center"] = [value / summary["vertices"] for value in summary.pop("sum")]
        result.append(summary)

    result.sort(key=lambda item: item["vertices"], reverse=True)
    return result


report = {
    "file": bpy.data.filepath,
    "objects": [],
}

for obj in bpy.data.objects:
    item = {
        "name": obj.name,
        "type": obj.type,
        "hidden_viewport": obj.hide_get(),
        "hidden_render": obj.hide_render,
        "location": list(obj.location),
    }
    if obj.type == "MESH":
        mesh = obj.data
        item.update(
            {
                "mesh": mesh.name,
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
                "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
                "bounds_world": world_bounds(obj),
                "components": connected_components(mesh)[:40],
            }
        )
    report["objects"].append(item)

print("BLEND_INSPECTION_BEGIN")
print(json.dumps(report, indent=2))
print("BLEND_INSPECTION_END")
