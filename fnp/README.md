# 2D to 3D Building Blueprint Converter

A Python-based tool that converts 2D building blueprints (PNG/JPG/PDF/DXF) into 3D models using Blender. Designed for strategic building walkthroughs and visualization.

## Features

- **Multiple Input Formats**: Supports PNG, JPG (via OpenCV), and DXF files
- **Automated Parsing**: Extracts walls, doors, windows, stairs, and furniture from blueprints
- **3D Generation**: Creates semantically correct 3D models with proper geometry
- **Multiple Outputs**: Exports to GLB (for web viewers) and OBJ formats
- **Web Viewer**: Built-in Three.js viewer for quick preview
- **Flexible Configuration**: Configurable building height, scale, wall thickness, and structural elements
- **GUI Mode**: User-friendly Tkinter interface for non-technical users
- **Furniture Detection**: Automatically detects and includes furniture elements
- **Map Overlay Support**: Optional map file integration for geographic context

## Prerequisites

- **Python 3.10+**
- **Blender 3.5+** installed and available in PATH as `blender` command
- System OS: Windows/Linux/macOS

### Verify Blender Installation

```bash
blender --version
```

Expected output: `Blender 3.5.x` or newer

If Blender is not found:
- **Windows**: Add Blender installation directory to PATH or use full path
- **Linux/macOS**: Install via package manager or download from blender.org

## Installation

1. Clone or download this repository

2. Install Python dependencies:

```bash
python -m pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
python main.py --input sample_input/sample_blueprint.png --scale 100 --height 4.0 --output output/
```

This will:
1. Parse the blueprint image
2. Extract walls and doors
3. Generate a 3D model with 4.0m height
4. Export `output/model.glb` and `output/model.obj`

### Command-Line Options

```
--input           Path to blueprint file (PNG/JPG/PDF/DXF)
--output          Output directory (default: output/)
--height          Building height in meters (default: 3.0)
--scale           Pixels per meter for image inputs (default: 100)
--wall-thickness  Wall thickness in meters (default: 0.2)
--stair-width     Stair width in meters (default: 1.2)
--stairs          Optional JSON string or file path for stair locations
--entries         Optional JSON string of door coordinates
--no-furniture    Disable furniture generation
--map             Path to map file (mbtiles) for overlay
--ui              Launch GUI mode
--serve-viewer    Launch a web server to preview the model
```

### Advanced Examples

**With custom stair locations:**
```bash
python main.py --input blueprints/building.png --scale 120 --height 3.5 --stairs '{"stair": [[5, 5], [6, 5], [6, 8], [5, 8]]}'
```

**DXF input:**
```bash
python main.py --input plan.dxf --height 5.0 --output output/
```

**GUI Mode:**
```bash
python main.py --ui
```
Or simply:
```bash
python ui.py
```

The GUI provides a user-friendly interface with:
- File browser for selecting blueprints
- Adjustable parameters (height, scale, wall thickness, etc.)
- Progress indicator
- One-click conversion

**With custom parameters:**
```bash
python main.py --input building.png --scale 100 --height 4.0 --wall-thickness 0.3 --stair-width 1.5 --no-furniture
```

## Testing

Run the provided test case:

```bash
python main.py --input sample_input/sample_blueprint.png --scale 100 --height 3.5 --output output/
```

Expected output:
- `output/plan.json` - Parsed blueprint data
- `output/model.glb` - 3D model (web-ready)
- `output/model.obj` - 3D model (standard format)

Verify Blender script directly:
```bash
blender --background --python blender_generator.py -- --plan output/plan.json --height 3.5 --out output/
```

## Viewing the Model

### Option 1: Built-in Web Viewer

```bash
python main.py --input sample_input/sample_blueprint.png --scale 100 --height 3.5 --output output/ --serve-viewer
```

Then open: `http://localhost:8000/viewer/index.html`

### Option 2: Manual Server

```bash
cd viewer
python -m http.server 8000
```

Open `http://localhost:8000/index.html` in your browser.

### Option 3: External Tools

Import `output/model.glb` into:
- Blender (native support)
- Unreal Engine
- Unity
- Three.js applications
- Online GLB viewers (gltf-viewer.donmccurdy.com)

## Project Structure

```
.
├── main.py                 # CLI entry point
├── parser.py              # Blueprint parsing (image/DXF)
├── blender_generator.py   # Blender script for 3D generation
├── map_downloader.py      # Optional OSM tile downloader
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── sample_input/
│   └── sample_blueprint.png
├── viewer/
│   ├── index.html        # Three.js viewer
│   ├── three.min.js     # Three.js library
│   └── OrbitControls.js # Camera controls
└── output/              # Generated files (created on first run)
```

## How It Works

### 1. Parsing (`parser.py`)

**Image Input (PNG/JPG):**
- Converts to grayscale
- Applies adaptive thresholding
- Uses morphological operations to clean noise
- Detects contours and approximates wall polygons
- Identifies door gaps in wall segments
- Converts pixel coordinates to meters using scale factor

**DXF Input:**
- Extracts LINE and POLYLINE entities using `ezdxf`
- Converts to polyline format
- Maintains coordinate system consistency

**Output:** `output/plan.json` with:
```json
{
  "walls": [[[x1, y1], [x2, y2], ...], ...],
  "doors": [[[x1, y1], [x2, y2]], ...],
  "stairs": [[[x1, y1], ...], ...],
  "bounds": {"min": [x, y], "max": [x, y]},
  "metadata": {"scale": 100, "height": 3.5}
}
```

### 2. 3D Generation (`blender_generator.py`)

- Reads `plan.json`
- Creates wall meshes by extruding footprints to specified height
- Generates floor and ceiling planes
- Applies boolean operations for door openings
- Creates stair geometry for specified polygons
- Applies materials and UV coordinates
- Exports GLB and OBJ files

### 3. Web Viewer (`viewer/index.html`)

Three.js-based viewer with:
- Orbit camera controls
- First-person camera mode (toggle)
- Wireframe/rendered view toggle
- Automatic centering and scaling

## Troubleshooting

### Blender Not Found

**Error:** `blender: command not found`

**Solution:**
- Windows: Add Blender to PATH or use full path: `"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"`
- Linux: Install via `sudo apt install blender` or download from blender.org
- macOS: `brew install --cask blender` or download from blender.org

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'cv2'`

**Solution:**
```bash
python -m pip install -r requirements.txt
```

### Empty or Incorrect Model

**Possible causes:**
1. Incorrect scale factor — adjust `--scale` parameter
2. No walls detected — check blueprint quality and contrast
3. Coordinates outside expected bounds — verify input file

**Debug:**
- Enable verbose logging: The script logs detected walls/doors
- Check `output/plan.json` to verify parsing
- Open blueprint in image viewer to verify quality

### Blender Export Fails

**Error:** Blender returns non-zero exit code

**Solution:**
1. Verify Blender version: `blender --version` (needs 3.5+)
2. Check `output/plan.json` is valid JSON
3. Review Blender console output for errors
4. Ensure output directory is writable

### Viewer Shows Blank Screen

**Possible causes:**
1. GLB file not generated — check `output/model.glb` exists
2. CORS issues — use `python -m http.server` (not `file://` protocol)
3. Browser console errors — check browser developer tools

## Development

### Adding New Input Formats

Extend `parser.py`:

```python
def parse_pdf(filepath):
    # Implement PDF parsing
    pass
```

Register in `main.py`:

```python
if input_path.endswith('.pdf'):
    plan_data = parse_pdf(input_path)
```

### Customizing Materials

Edit `blender_generator.py`:

```python
# After creating mesh
mat = bpy.data.materials.new(name="WallMaterial")
mat.use_nodes = True
# Configure material nodes
obj.data.materials.append(mat)
```

## Limitations

- **Image Quality**: Low-resolution or blurry blueprints may produce incorrect results
- **Complex Geometry**: Current implementation focuses on simple rectangular buildings
- **Scale Manual Input**: Automatic scale detection not implemented (user must provide)
- **Material Complexity**: Basic materials only (no textures)
- **Stair Geometry**: Simplified stepped geometry

## Future Enhancements

- Automatic scale detection from blueprint annotations
- Multi-floor support
- Roof generation
- Texture mapping from blueprint
- Collision mesh generation
- Export to additional formats (FBX, USDZ)

## License

This project uses open-source libraries only. See individual library licenses for details.

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review generated `output/plan.json` for parsing issues
3. Verify Blender installation and PATH configuration
4. Check Python version compatibility (3.10+)

## Credits

- **OpenCV** - Image processing
- **Blender** - 3D generation
- **Three.js** - Web viewer
- **ezdxf** - DXF parsing
- **Shapely** - Geometric operations
