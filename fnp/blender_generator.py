#!/usr/bin/env python3
"""
Blender 3D Model Generator
This script runs inside Blender to generate 3D models from plan.json data.
"""

import sys
import json
import argparse
import math
from pathlib import Path

# Import Blender modules
try:
    import bpy
    import bmesh
    from mathutils import Vector
except ImportError:
    print("Error: This script must be run from within Blender")
    print("Usage: blender --background --python blender_generator.py -- --plan <plan.json> --height <height> --out <output_dir>")
    sys.exit(1)


def clear_scene():
    """Clear all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def setup_scene():
    """Set up scene for metric units and correct settings."""
    # Set units to metric
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0
    
    # Set viewport shading for better visibility
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].shading.type = 'SOLID'
    
    print("Scene configured for metric units")


def create_wall_mesh(wall_points, height, thickness=0.2):
    """
    Create a wall mesh from a polyline.
    
    Args:
        wall_points: List of [x, y] coordinates
        height: Wall height in meters
        thickness: Wall thickness in meters
    """
    if len(wall_points) < 2:
        return None
    
    # Convert to 3D coordinates
    points_3d = [Vector([p[0], p[1], 0]) for p in wall_points]
    
    # Create wall geometry by extruding along the path
    mesh = bpy.data.meshes.new(name="WallMesh")
    
    bm = bmesh.new()
    
    # For each segment, create a rectangular face
    for i in range(len(points_3d) - 1):
        p1 = points_3d[i]
        p2 = points_3d[i + 1]
        
        # Calculate perpendicular direction for thickness
        direction = (p2 - p1).normalized()
        perpendicular = Vector([-direction.y, direction.x, 0])
        
        # Create base rectangle vertices
        v1 = p1 + perpendicular * (thickness / 2)
        v2 = p1 - perpendicular * (thickness / 2)
        v3 = p2 - perpendicular * (thickness / 2)
        v4 = p2 + perpendicular * (thickness / 2)
        
        # Add vertices
        verts = bm.verts.new(v1), bm.verts.new(v2), bm.verts.new(v3), bm.verts.new(v4)
        
        # Add face
        bm.faces.new(verts)
    
    # Extrude upward
    ret = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    geom_extruded = ret['geom']
    
    # Move the extruded geometry upward by wall height
    bmesh.ops.translate(
        bm,
        vec=Vector((0, 0, height)),
        verts=[v for v in geom_extruded if isinstance(v, bmesh.types.BMVert)]
    )
    
    bm.to_mesh(mesh)
    bm.free()
    
    return mesh


def create_floor_ceiling(bounds, height):
    """Create floor and ceiling planes."""
    min_x, min_y = bounds['min']
    max_x, max_y = bounds['max']
    
    # Expand bounds slightly
    padding = 1.0
    min_x -= padding
    min_y -= padding
    max_x += padding
    max_y += padding
    
    # Floor
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor.scale = [max_x - min_x, max_y - min_y, 1]
    floor.location = [(min_x + max_x) / 2, (min_y + max_y) / 2, 0]
    
    # Apply material
    mat_floor = bpy.data.materials.new(name="FloorMaterial")
    mat_floor.use_nodes = True
    mat_floor.node_tree.nodes.clear()
    bsdf = mat_floor.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1.0)
    output = mat_floor.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    mat_floor.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
    floor.data.materials.append(mat_floor)
    
    # Ceiling
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, height))
    ceiling = bpy.context.active_object
    ceiling.name = "Ceiling"
    ceiling.scale = [max_x - min_x, max_y - min_y, 1]
    ceiling.location = [(min_x + max_x) / 2, (min_y + max_y) / 2, height]
    
    # Apply material
    mat_ceiling = bpy.data.materials.new(name="CeilingMaterial")
    mat_ceiling.use_nodes = True
    mat_ceiling.node_tree.nodes.clear()
    bsdf = mat_ceiling.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.9, 1.0)
    output = mat_ceiling.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    mat_ceiling.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
    ceiling.data.materials.append(mat_ceiling)


def create_stairs(stair_polygon, height, width=1.2):
    """Create stair geometry from a polygon."""
    if not stair_polygon or len(stair_polygon) < 3:
        return
    
    # Calculate bounds of stair polygon
    min_x = min(p[0] for p in stair_polygon)
    max_x = max(p[0] for p in stair_polygon)
    min_y = min(p[1] for p in stair_polygon)
    max_y = max(p[1] for p in stair_polygon)
    
    # Create stepped geometry
    num_steps = max(3, int(height / 0.17))  # ~17cm per step
    step_height = height / num_steps
    step_x = (max_x - min_x) / num_steps if max_x > min_x else width
    
    for i in range(num_steps):
        bpy.ops.mesh.primitive_cube_add(
            size=2,
            location=(
                min_x + step_x * (i + 0.5),
                (min_y + max_y) / 2,
                step_height * (i + 0.5)
            )
        )
        step = bpy.context.active_object
        step.name = f"Step_{i}"
        step.scale = [step_x / 2, (max_y - min_y) / 2, step_height / 2]
        
        # Apply material
        mat_stair = bpy.data.materials.new(name="StairMaterial")
        mat_stair.use_nodes = True
        mat_stair.node_tree.nodes.clear()
        bsdf = mat_stair.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.6, 0.5, 0.4, 1.0)
        output = mat_stair.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        mat_stair.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
        step.data.materials.append(mat_stair)


def create_door_opening(wall_obj, door_data):
    """Create door opening using boolean modifier."""
    # Create a cutting box for the door opening
    door_width = abs(door_data.get('x2', 0) - door_data.get('x1', 0))
    if door_width < 0.01:
        return  # Skip very small doors
    
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.05))
    cutter = bpy.context.active_object
    cutter.scale = [door_width/2, 0.3, 1.05]
    
    # Position at door location
    center_x = (door_data.get('x1', 0) + door_data.get('x2', 0)) / 2
    center_y = (door_data.get('y1', 0) + door_data.get('y2', 0)) / 2
    cutter.location = [center_x, center_y, 1.05]
    
    # Apply boolean difference
    bpy.context.view_layer.objects.active = wall_obj
    wall_obj.select_set(True)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    wall_obj.modifiers[-1].operation = 'DIFFERENCE'
    wall_obj.modifiers[-1].object = cutter
    bpy.ops.object.modifier_apply(modifier=wall_obj.modifiers[-1].name)
    
    # Remove cutter
    bpy.data.objects.remove(cutter, do_unlink=True)


def create_furniture(polygon, height=1.0):
    """Create simple furniture placeholder."""
    if not polygon or len(polygon) < 3:
        return None
    
    bm = bmesh.new()
    
    # Create base vertices
    for point in polygon:
        bm.verts.new(Vector([point[0], point[1], 0]))
    
    # Create face
    bm.faces.new(bm.verts)
    
    # Extrude upward
    bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    ret = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    geom_extruded = ret['geom']
    bmesh.ops.translate(
        bm,
        vec=Vector((0, 0, height)),
        verts=[v for v in geom_extruded if isinstance(v, bmesh.types.BMVert)]
    )
    
    mesh = bpy.data.meshes.new(name="FurnitureMesh")
    bm.to_mesh(mesh)
    bm.free()
    
    return mesh


def generate_model(plan_json_path, height, output_dir, wall_thickness=0.2, stair_width=1.2, furniture_enabled=True, map_path=None, door_height=None, door_width=1.0):
    """Generate 3D model from plan data."""
    
    # Read plan data
    print(f"Loading plan data from {plan_json_path}")
    with open(plan_json_path, 'r') as f:
        plan_data = json.load(f)
    
    # Set defaults based on height
    if door_height is None:
        door_height = height * 0.85  # 85% of building height
    
    walls = plan_data.get('walls', [])
    doors = plan_data.get('doors', [])
    windows = plan_data.get('windows', [])
    stairs = plan_data.get('stairs', [])
    furniture = plan_data.get('furniture', [])
    bounds = plan_data.get('bounds', {'min': [0, 0], 'max': [10, 10]})
    
    print(f"Generating model with {len(walls)} walls, {len(doors)} doors, {len(windows)} windows, {len(stairs)} stairs, {len(furniture)} furniture")
    print(f"Parameters: wall_thickness={wall_thickness}m, door_height={door_height}m, door_width={door_width}m, stair_width={stair_width}m")
    
    # Clear scene
    clear_scene()
    setup_scene()
    
    # Create wall meshes
    wall_objects = []
    for i, wall_points in enumerate(walls):
        wall_mesh = create_wall_mesh(wall_points, height, wall_thickness)
        if wall_mesh:
            wall_obj = bpy.data.objects.new(f"Wall_{i}", wall_mesh)
            bpy.context.collection.objects.link(wall_obj)
            wall_objects.append(wall_obj)
            
            # Apply material
            mat_wall = bpy.data.materials.new(name="WallMaterial")
            mat_wall.use_nodes = True
            mat_wall.node_tree.nodes.clear()
            bsdf = mat_wall.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
            output = mat_wall.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
            mat_wall.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
            wall_obj.data.materials.append(mat_wall)
    
    # Create door openings
    for door in doors:
        # Simple approach: mark door locations (boolean operations can be finicky)
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, 0, 1.0))
        door_marker = bpy.context.active_object
        door_marker.name = f"Door_{door.get('x1', 0)}"
        door_marker.location = [(door.get('x1', 0) + door.get('x2', 0)) / 2,
                                (door.get('y1', 0) + door.get('y2', 0)) / 2,
                                1.0]
    
    # Create floor and ceiling
    create_floor_ceiling(bounds, height)
    
    # Create stairs
    for stair_poly in stairs:
        create_stairs(stair_poly, height, stair_width)
    
    # Create furniture
    if furniture_enabled:
        for i, furn in enumerate(furniture):
            poly = furn.get('polygon', [])
            if poly:
                furn_mesh = create_furniture(poly, height=1.0)
                if furn_mesh:
                    furn_obj = bpy.data.objects.new(f"Furniture_{i}", furn_mesh)
                    bpy.context.collection.objects.link(furn_obj)
                    
                    # Apply furniture material
                    mat_furn = bpy.data.materials.new(name="FurnitureMaterial")
                    mat_furn.use_nodes = True
                    mat_furn.node_tree.nodes.clear()
                    bsdf = mat_furn.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
                    bsdf.inputs['Base Color'].default_value = (0.6, 0.4, 0.3, 1.0)
                    output = mat_furn.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
                    mat_furn.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
                    furn_obj.data.materials.append(mat_furn)
    
    # Set up camera
    bpy.ops.object.camera_add(location=(10, -10, 8))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    
    # Set as active camera
    bpy.context.scene.camera = camera
    
    # Export GLB
    glb_path = Path(output_dir) / 'model.glb'
    print(f"Exporting GLB to {glb_path}")
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format='GLB',
        use_selection=False,
        export_materials='EXPORT'
    )
    
    # Export OBJ
    obj_path = Path(output_dir) / 'model.obj'
    print(f"Exporting OBJ to {obj_path}")
    bpy.ops.wm.obj_export(
        filepath=str(obj_path),
        export_selected_objects=False,
        export_materials=True,
        path_mode='AUTO'
    )
    
    print("Model generation complete!")


def main():
    """Main entry point when run from Blender."""
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Generate 3D model from plan data')
    parser.add_argument('--plan', required=True, help='Path to plan.json file')
    parser.add_argument('--height', type=float, required=True, help='Building height in meters')
    parser.add_argument('--out', required=True, help='Output directory')
    parser.add_argument('--wall-thickness', type=float, default=0.2, help='Wall thickness in meters')
    parser.add_argument('--stair-width', type=float, default=1.5, help='Stair width in meters')
    parser.add_argument('--no-furniture', action='store_true', help='Disable furniture generation')
    parser.add_argument('--map', type=str, default=None, help='Path to map file (mbtiles)')
    parser.add_argument('--door-height', type=float, default=None, help='Door height in meters (defaults to height * 0.85)')
    parser.add_argument('--door-width', type=float, default=1.0, help='Door width in meters')
    
    # Blender passes arguments after '--', so we need to handle that
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        argv = []
    
    args = parser.parse_args(argv)
    
    # Verify files
    if not Path(args.plan).exists():
        print(f"Error: Plan file not found: {args.plan}")
        sys.exit(1)
    
    # Create output directory
    Path(args.out).mkdir(parents=True, exist_ok=True)
    
    # Generate model
    try:
        generate_model(
            args.plan, 
            args.height, 
            args.out,
            wall_thickness=args.wall_thickness,
            stair_width=args.stair_width,
            furniture_enabled=not args.no_furniture,
            map_path=args.map,
            door_height=args.door_height,
            door_width=args.door_width
        )
        print("Success!")
        sys.exit(0)
    except Exception as e:
        print(f"Error generating model: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
