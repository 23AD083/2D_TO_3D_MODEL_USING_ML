#!/usr/bin/env python3
"""Generate simple report assets from plan.json:
- plan.obj : an OBJ file with polygon faces (z=0)
- blueprint.svg : 2D SVG rendering of polygons
- report.html : simple HTML page displaying SVG and vertex list

Usage: python generate_report.py --plan output/plan.json --out output
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

from ml.predictor import estimate_from_plan


def load_plan(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        return json.load(f)


def write_obj(plan: Dict[str, Any], out_path: str, height: float) -> None:
    """Write a high-quality OBJ with walls as extruded 3D boxes (floor and ceiling).
    Each wall segment is rendered as a vertical box with proper normals.
    """
    verts: List[Tuple[float, float, float]] = []
    normals: List[Tuple[float, float, float]] = []
    faces: List[List[Tuple[int, int]]] = []  # (vertex_idx, normal_idx)
    
    def add_box(p1: Tuple[float, float], p2: Tuple[float, float], z_low: float, z_high: float, thickness: float = 0.2):
        """Add a wall box between two points."""
        x1, y1 = p1
        x2, y2 = p2
        
        # Normalize direction and get perpendicular
        dx = x2 - x1
        dy = y2 - y1
        length = (dx**2 + dy**2)**0.5
        if length < 0.001:
            return
        
        dx /= length
        dy /= length
        
        # Perpendicular (outward normal)
        px = -dy * thickness / 2
        py = dx * thickness / 2
        
        # 8 vertices for the box
        v_base = len(verts)
        verts.append((x1 - px, y1 - py, z_low))
        verts.append((x1 + px, y1 + py, z_low))
        verts.append((x2 + px, y2 + py, z_low))
        verts.append((x2 - px, y2 - py, z_low))
        verts.append((x1 - px, y1 - py, z_high))
        verts.append((x1 + px, y1 + py, z_high))
        verts.append((x2 + px, y2 + py, z_high))
        verts.append((x2 - px, y2 - py, z_high))
        
        # Normals for each face
        n_base = len(normals)
        normals.append((-dy, dx, 0))      # outer wall
        normals.append((dy, -dx, 0))      # inner wall
        normals.append((0, 0, -1))        # bottom
        normals.append((0, 0, 1))         # top
        normals.append((dx, dy, 0))       # end cap 1
        normals.append((-dx, -dy, 0))    # end cap 2
        
        # Faces (with normals)
        # Outer wall
        faces.append([(v_base, n_base), (v_base+4, n_base), (v_base+5, n_base), (v_base+1, n_base)])
        # Inner wall
        faces.append([(v_base+2, n_base+1), (v_base+6, n_base+1), (v_base+7, n_base+1), (v_base+3, n_base+1)])
        # Bottom
        faces.append([(v_base, n_base+2), (v_base+3, n_base+2), (v_base+2, n_base+2), (v_base+1, n_base+2)])
        # Top
        faces.append([(v_base+4, n_base+3), (v_base+5, n_base+3), (v_base+6, n_base+3), (v_base+7, n_base+3)])
        # End cap 1
        faces.append([(v_base, n_base+4), (v_base+1, n_base+4), (v_base+5, n_base+4), (v_base+4, n_base+4)])
        # End cap 2
        faces.append([(v_base+2, n_base+5), (v_base+3, n_base+5), (v_base+7, n_base+5), (v_base+6, n_base+5)])
    
    # Process walls and create 3D boxes
    for wall in plan.get('walls', []):
        for i in range(len(wall)):
            pt1 = wall[i]
            pt2 = wall[(i + 1) % len(wall)]
            add_box((pt1[0], pt1[1]), (pt2[0], pt2[1]), 0.0, height, thickness=0.2)
    
    # Write OBJ file
    with open(out_path, 'w') as f:
        f.write('# High-quality OBJ with extruded walls\n')
        f.write('# Generated from plan.json\n\n')
        
        for v in verts:
            f.write('v {:.6f} {:.6f} {:.6f}\n'.format(v[0], v[1], v[2]))
        
        f.write('\n')
        
        for n in normals:
            f.write('vn {:.6f} {:.6f} {:.6f}\n'.format(n[0], n[1], n[2]))
        
        f.write('\n')
        
        for face in faces:
            face_str = ' '.join(f'{v+1}/{n+1}' for v, n in face)
            f.write(f'f {face_str}\n')


def write_svg(plan: Dict[str, Any], out_path: str, pixels_per_meter: float) -> None:
    # compute bounds
    bounds = plan.get('bounds')
    if bounds:
        minx, miny = bounds['min'][0], bounds['min'][1]
        maxx, maxy = bounds['max'][0], bounds['max'][1]
    else:
        # fallback: compute from polygons
        xs = []
        ys = []
        for k in ('walls', 'rooms'):
            for p in plan.get(k, []):
                for pt in p:
                    xs.append(pt[0]); ys.append(pt[1])
        if not xs:
            minx = miny = 0.0; maxx = maxy = 1.0
        else:
            minx, maxx = min(xs), max(xs)
            miny, maxy = min(ys), max(ys)

    width = int((maxx - minx) * pixels_per_meter) + 20
    height = int((maxy - miny) * pixels_per_meter) + 20

    def transform(pt):
        x, y = pt
        tx = (x - minx) * pixels_per_meter + 10
        ty = (maxy - y) * pixels_per_meter + 10
        return tx, ty

    svg_parts: List[str] = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    svg_parts.append('<rect width="100%" height="100%" fill="#ffffff"/>')

    # draw walls (stroke thick)
    for poly in plan.get('walls', []):
        pts = ' '.join(f"{transform(pt)[0]},{transform(pt)[1]}" for pt in poly)
        svg_parts.append(f'<polygon points="{pts}" fill="#eeeeee" stroke="#333333" stroke-width="2" />')

    # draw rooms (lighter fill)
    for poly in plan.get('rooms', []):
        pts = ' '.join(f"{transform(pt)[0]},{transform(pt)[1]}" for pt in poly)
        svg_parts.append(f'<polygon points="{pts}" fill="#d0f0ff" stroke="#006699" stroke-width="1" opacity="0.8" />')

    # draw doors as small lines if present
    for door in plan.get('doors', []):
        # door expected as [x1,y1,x2,y2] or a point
        if len(door) >= 4:
            x1, y1, x2, y2 = door[:4]
            x1t, y1t = transform((x1, y1))
            x2t, y2t = transform((x2, y2))
            svg_parts.append(f'<line x1="{x1t}" y1="{y1t}" x2="{x2t}" y2="{y2t}" stroke="#aa0000" stroke-width="3" />')

    svg_parts.append('</svg>')

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_parts))


def write_html(plan: Dict[str, Any], svg_name: str, obj_name: str, out_path: str) -> None:
    title = 'Plan Report'
    vertices = []
    for k in ('walls', 'rooms'):
        for poly in plan.get(k, []):
            for pt in poly:
                vertices.append(pt + [0.0])
    
    # Get predictions
    predictions = estimate_from_plan(plan)
    
    # Build vertex list and stats
    metadata_json = json.dumps(plan.get('metadata', {}), indent=2)
    vertices_json = json.dumps(vertices, indent=2)
    
    html = f'''<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
    .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    h1 {{ color: #333; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }}
    h2 {{ color: #0066cc; margin-top: 20px; }}
    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }}
    .stat-box {{ background: #f0f8ff; border-left: 4px solid #0066cc; padding: 15px; border-radius: 4px; }}
    .stat-label {{ font-size: 0.9em; color: #666; }}
    .stat-value {{ font-size: 1.8em; color: #0066cc; font-weight: bold; }}
    .stat-unit {{ font-size: 0.8em; color: #999; }}
    .visual {{ border: 1px solid #ddd; padding: 10px; margin: 15px 0; border-radius: 4px; }}
    .visual img {{ max-width: 100%; height: auto; }}
    .panel {{ margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 4px; }}
    .download-link {{ display: inline-block; padding: 10px 15px; background: #0066cc; color: white; text-decoration: none; border-radius: 4px; margin: 5px 5px 5px 0; }}
    .download-link:hover {{ background: #0052a3; }}
    pre {{ background: #f7f7f7; padding: 10px; overflow: auto; border-radius: 4px; border: 1px solid #ddd; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>📐 Building Plan Report</h1>
    
    <h2>📊 Predictions & Statistics</h2>
    <div class="stats-grid">
      <div class="stat-box">
        <div class="stat-label">Number of Rooms</div>
        <div class="stat-value">{predictions['num_rooms']}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Number of Walls</div>
        <div class="stat-value">{predictions['num_walls']}</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Total Area</div>
        <div class="stat-value">{predictions['total_area_sqm']}</div>
        <div class="stat-unit">sq meters</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Total Wall Length</div>
        <div class="stat-value">{predictions['total_wall_length_m']}</div>
        <div class="stat-unit">meters</div>
      </div>
      <div class="stat-box">
        <div class="stat-label">Estimated Work Days</div>
        <div class="stat-value">{predictions['estimated_work_days']}</div>
        <div class="stat-unit">days (at ~15 sqm/day)</div>
      </div>
    </div>
    
    <h2>📐 2D Blueprint</h2>
    <div class="visual">
      <img src="{svg_name}" alt="blueprint" />
    </div>
    
    <h2>📥 Downloads</h2>
    <div class="panel">
      <a href="{obj_name}" download class="download-link">⬇️ Download OBJ (3D Model)</a>
      <a href="{svg_name}" download class="download-link">⬇️ Download Blueprint (SVG)</a>
    </div>
    
    <h2>🔢 Vertex Coordinates (x, y, z)</h2>
    <div class="panel">
      <p>Total vertices: <strong>{len(vertices)}</strong></p>
      <pre>{vertices_json}</pre>
    </div>
    
    <h2>📋 Plan Metadata</h2>
    <div class="panel">
      <pre>{metadata_json}</pre>
    </div>
    
    <hr />
    <p style="text-align: center; color: #999; font-size: 0.9em;">Generated by 2D to 3D Building Blueprint Converter</p>
  </div>
</body>
</html>
'''

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', required=True, help='Path to plan.json')
    ap.add_argument('--out', required=True, help='Output directory where to place generated files')
    args = ap.parse_args()

    plan_path = args.plan
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    plan = load_plan(plan_path)
    height = float(plan.get('metadata', {}).get('height', 3.0))
    scale = float(plan.get('metadata', {}).get('scale', 100.0))

    obj_path = out_dir / 'plan.obj'
    svg_path = out_dir / 'blueprint.svg'
    html_path = out_dir / 'report.html'

    write_obj(plan, str(obj_path), height)
    write_svg(plan, str(svg_path), pixels_per_meter=scale)
    write_html(plan, svg_path.name, obj_path.name, str(html_path))

    print('Generated:', obj_path, svg_path, html_path)


if __name__ == '__main__':
    main()
