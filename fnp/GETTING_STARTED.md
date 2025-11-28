# Quick Start Guide

This guide will help you get up and running with the 2D to 3D Building Blueprint Converter in minutes.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.10+** installed
2. **Blender 3.5+** installed and accessible in your PATH

### Verify Installation

```bash
python --version    # Should show Python 3.10+
blender --version   # Should show Blender 3.5+
```

## Installation Steps

### 1. Install Python Dependencies

```bash
python -m pip install -r requirements.txt
```

This will install:
- OpenCV for image processing
- NumPy for numerical operations
- Pillow for image handling
- ezdxf for DXF file support
- shapely for geometric operations
- matplotlib for visualization
- flask for the web viewer

### 2. Test Installation

Run the test script to verify everything is installed correctly:

```bash
python test_installation.py
```

Expected output:
```
✓ opencv-python (version x.x.x)
✓ numpy
✓ Pillow
✓ ezdxf
✓ shapely
✓ matplotlib
✓ Blender (version x.x.x)

✓ All dependencies installed successfully!
```

## Your First Conversion

### Basic Example

Convert the sample blueprint to a 3D model:

```bash
python main.py --input sample_input/sample_blueprint.png --scale 100 --height 3.5 --output output/
```

This command will:
1. Parse the blueprint image
2. Extract walls and doors
3. Generate a 3D model with 3.5m height
4. Export `model.glb` and `model.obj` to the `output/` directory

### What Each Parameter Does

- `--input`: Path to your blueprint file (PNG/JPG/DXF)
- `--scale`: Pixels per meter (adjust based on your blueprint scale)
- `--height`: Building height in meters
- `--output`: Where to save the generated files

### Viewing Your Model

**Option 1: Built-in Web Viewer**

```bash
python main.py --input sample_input/sample_blueprint.png --scale 100 --height 3.5 --serve-viewer
```

Then open `http://localhost:8000/viewer/index.html` in your browser.

**Option 2: Manual Server**

```bash
cd viewer
python -m http.server 8000
```

Open `http://localhost:8000/index.html` in your browser.

**Option 3: External Tools**

Open `output/model.glb` in:
- Blender (File → Import → glTF)
- Unreal Engine
- Unity
- Online viewer (https://gltf-viewer.donmccurdy.com/)

## Understanding the Output

After conversion, you'll find these files in the `output/` directory:

- **plan.json**: Parsed blueprint data (walls, doors, stairs, bounds)
- **model.glb**: 3D model in glTF format (web-ready, includes materials)
- **model.obj**: 3D model in Wavefront format (compatible with most 3D software)

## Common Issues

### Blender Not Found

If you get an error that Blender is not found:

**Windows:**
1. Find your Blender installation (usually `C:\Program Files\Blender Foundation\Blender 4.x\`)
2. Add the Blender directory to your PATH environment variable
3. Or set the `BLENDER_PATH` environment variable to the full path of `blender.exe`

**Linux/macOS:**
```bash
# Add to PATH or create alias
export PATH=$PATH:/path/to/blender
```

### ModuleNotFoundError

If Python modules are missing:

```bash
python -m pip install --upgrade -r requirements.txt
```

### Empty or Incorrect Model

Common causes:
1. **Wrong scale**: Adjust the `--scale` parameter (try 50, 100, 150)
2. **Low quality blueprint**: Ensure your blueprint has clear black lines on white background
3. **No walls detected**: Check `output/plan.json` to verify parsing

## Next Steps

- Try different blueprints with varying scales
- Experiment with different building heights
- Add custom stairs or doors using the `--stairs` and `--entries` parameters
- Read the full [README.md](README.md) for advanced features

## Need Help?

1. Check the [README.md](README.md) troubleshooting section
2. Review the `output/plan.json` to debug parsing issues
3. Ensure your Python version is 3.10+
4. Verify Blender version is 3.5+

Happy converting! 🏗️
