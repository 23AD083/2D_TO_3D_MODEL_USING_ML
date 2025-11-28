# Exact Blueprint → Metric 3D Model Generator

## Repository Summary

### Files Created/Updated

**Core Files:**
- ✅ `utils.py` - NEW: Geometry transformation utilities (snapping, simplification, validation)
- ✅ `viewer/index.html` - UPDATED: Three.js glTF viewer for model preview
- ✅ `parser.py` - ENHANCED: DXF layer detection (WALLS, DOORS, WINDOWS, STAIRS) with unit conversion
- ✅ `blender_generator.py` - UPDATED: Blender 4.5+ compatible (uses `extrude_face_region`)
- ✅ `main.py` - UPDATED: Added new CLI parameters (wall-thickness, stair-width, etc.)
- ✅ `requirements.txt` - Existing dependencies maintained
- ✅ `README.md` - Existing documentation

**Test Files:**
- ✅ `tests/test_pipeline.sh` - Bash test script for Linux/Mac
- ✅ `tests/test_pipeline.bat` - Windows batch test script

**Directories:**
- ✅ `sample_input/` - Contains sample_blueprint.png
- ✅ `output/` - Created at runtime for generated files
- ✅ `viewer/` - Three.js viewer for web preview
- ✅ `tests/` - Test scripts

### Key Features Implemented

1. **DXF Layer Detection**
   - Automatically detects layers: WALLS, DOORS, WINDOWS, STAIRS
   - Falls back to geometry-based classification if no layers found
   - Unit conversion support (DXF units to meters)

2. **Geometry Processing** (`utils.py`)
   - Coordinate snapping and simplification
   - Polygon validation and orientation fixing
   - Wall thickness offset generation
   - Bounding box calculations

3. **Blender 4.5+ Compatibility**
   - Uses `bmesh.ops.extrude_face_region` instead of deprecated `extrude_region`
   - Proper geometry translation using Vector
   - Metric unit system enforced

4. **Enhanced CLI**
   - `--wall-thickness` (default: 0.2m)
   - `--stair-width` (default: 1.2m)
   - `--no-furniture` flag
   - `--map` for optional map file
   - `--ui` for GUI mode

5. **Web Viewer**
   - Three.js-based glTF viewer
   - Orbit controls, wireframe toggle, camera reset
   - Loads `output/model.glb` dynamically

### How to Run

**Quick Test:**
```bash
python main.py --input sample_input/sample_blueprint.png --scale 100 --height 3.5
```

**GUI Mode:**
```bash
python main.py --ui
# OR
python ui.py
```

**View Results:**
```bash
cd viewer
python -m http.server 8000
# Then open http://localhost:8000/index.html
```

**With Custom Parameters:**
```bash
python main.py --input blueprint.png --scale 100 --height 4.0 --wall-thickness 0.3 --stair-width 1.5
```

### Expected Output Files

After running the conversion, you'll find in `output/`:

- **`plan.json`** (~654 bytes) - Parsed blueprint data in JSON format
- **`model.glb`** (~6-7 KB) - 3D model in glTF binary format (web-ready)
- **`model.obj`** (~3-4 KB) - 3D model in OBJ format (standard)
- **`model.mtl`** (~617 bytes) - Material file for OBJ format

### Test Results

✅ **Pipeline Status:** Working
- ✅ Parser extracts geometry from images
- ✅ Blender 4.5.3 generates 3D models
- ✅ GLB and OBJ files created successfully
- ✅ All CLI parameters accepted

### Architecture

```
Blueprint (PNG/JPG/DXF)
    ↓
parser.py → Extracts geometry, detects layers
    ↓
plan.json → JSON format with walls, doors, stairs
    ↓
blender_generator.py → Creates 3D meshes
    ↓
model.glb + model.obj → Final 3D models
    ↓
viewer/index.html → Web preview
```

### Dependencies

- Python 3.10+
- Blender 4.5+ (available as `blender` command)
- Packages: opencv-python, numpy, shapely, ezdxf, pillow, pyproj, matplotlib, flask
- Three.js (loaded from CDN in viewer)

### Notes

- DXF files with layers are preferred for best results
- Image blueprints require `--scale` parameter (pixels per meter)
- Wall thickness, stair width, and furniture can be customized
- The system is Blender 4.5+ compatible using modern bmesh operations
- All coordinates are normalized to metric meters
