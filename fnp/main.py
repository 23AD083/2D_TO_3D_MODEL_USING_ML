#!/usr/bin/env python3
"""
2D to 3D Building Blueprint Converter - Main Entry Point
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import parser
import map_downloader


# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# Try to import numpy for encoder
try:
    import numpy as np
except ImportError:
    np = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_blender_available():
    """Check if Blender is available in PATH."""
    try:
        result = subprocess.run(
            ['blender', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info(f"Blender found: {result.stdout.strip().split()[1]}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    logger.error("Blender not found. Please install Blender 3.5+ and ensure it's in PATH.")
    logger.error("Alternatively, set BLENDER_PATH environment variable.")
    return False


def call_blender(plan_json_path, height, output_dir, wall_thickness=0.2, stair_width=1.5, furniture_enabled=True, map_path=None, door_height=None, door_width=1.0):
    """
    Call Blender in background mode to generate 3D model.
    
    Args:
        plan_json_path: Path to plan.json file
        height: Building height in meters
        output_dir: Output directory for generated files
        wall_thickness: Wall thickness in meters
        stair_width: Stair width in meters
        furniture_enabled: Whether to generate furniture
        map_path: Path to map file (mbtiles)
        door_height: Door height in meters (defaults to height * 0.85)
        door_width: Door width in meters
    """
    blender_path = os.environ.get('BLENDER_PATH', 'blender')
    blender_script = Path(__file__).parent / 'blender_generator.py'
    
    # Build Blender command
    cmd = [
        blender_path,
        '--background',
        '--python', str(blender_script),
        '--',
        '--plan', plan_json_path,
        '--height', str(height),
        '--out', output_dir,
        '--wall-thickness', str(wall_thickness),
        '--stair-width', str(stair_width),
        '--door-width', str(door_width)
    ]
    
    if not furniture_enabled:
        cmd.append('--no-furniture')
    
    if map_path:
        cmd.extend(['--map', map_path])
    
    if door_height is not None:
        cmd.extend(['--door-height', str(door_height)])
    
    logger.info("Calling Blender to generate 3D model...")
    logger.debug(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            logger.error(f"Blender execution failed with code {result.returncode}")
            logger.error("Blender stdout:")
            logger.error(result.stdout)
            logger.error("Blender stderr:")
            logger.error(result.stderr)
            return False
        
        logger.info("Blender execution completed successfully")
        if result.stdout:
            logger.debug("Blender output:")
            logger.debug(result.stdout)
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Blender execution timed out (>5 minutes)")
        return False
    except Exception as e:
        logger.error(f"Error calling Blender: {e}")
        return False


def parse_optional_json(flag_value):
    """Parse JSON from string or file path."""
    if not flag_value:
        return None
    
    # Try to parse as JSON string
    try:
        return json.loads(flag_value)
    except json.JSONDecodeError:
        pass
    
    # Try to read from file
    if os.path.exists(flag_value):
        try:
            with open(flag_value, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read JSON from file {flag_value}: {e}")
    
    logger.error(f"Invalid JSON: {flag_value}")
    return None


def serve_viewer(output_dir):
    """Launch a simple HTTP server for the viewer."""
    import http.server
    import socketserver
    import webbrowser
    from pathlib import Path
    
    PORT = 8000
    
    # Create handler that serves files relative to project root
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            url = f"http://localhost:{PORT}/viewer/index.html"
            logger.info(f"Serving viewer at {url}")
            webbrowser.open(url)
            
            logger.info("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except OSError as e:
        logger.error(f"Failed to start server on port {PORT}: {e}")


def main():
    """Main entry point."""
    parser_args = argparse.ArgumentParser(
        description='Convert 2D building blueprints to 3D models',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser_args.add_argument(
        '--input',
        required=False,
        help='Path to blueprint file (PNG/JPG/DXF)'
    )
    parser_args.add_argument(
        '--output',
        default='output',
        help='Output directory (default: output/)'
    )
    parser_args.add_argument(
        '--height',
        type=float,
        default=3.0,
        help='Building height in meters (default: 3.0)'
    )
    parser_args.add_argument(
        '--scale',
        type=float,
        default=100.0,
        help='Pixels per meter for image inputs (default: 100)'
    )
    parser_args.add_argument(
        '--stairs',
        help='JSON string or file path for stair locations'
    )
    parser_args.add_argument(
        '--entries',
        help='JSON string or file path for door coordinates'
    )
    parser_args.add_argument(
        '--serve-viewer',
        action='store_true',
        help='Launch a web server to preview the model'
    )
    parser_args.add_argument(
        '--download-maps',
        action='store_true',
        help='Download OSM tiles for context (optional)'
    )
    parser_args.add_argument(
        '--wall-thickness',
        type=float,
        default=0.2,
        help='Wall thickness in meters (default: 0.2)'
    )
    parser_args.add_argument(
        '--stair-width',
        type=float,
        default=1.2,
        help='Stair width in meters (default: 1.2)'
    )
    parser_args.add_argument(
        '--no-furniture',
        action='store_true',
        help='Disable furniture generation'
    )
    parser_args.add_argument(
        '--map',
        type=str,
        default=None,
        help='Path to map file (mbtiles) for overlay'
    )
    parser_args.add_argument(
        '--ui',
        action='store_true',
        help='Launch GUI mode'
    )
    parser_args.add_argument(
        '--ml',
        action='store_true',
        help='Enable ML-based enhancement (rooms/labels) for image blueprints'
    )
    parser_args.add_argument(
        '--ml-model',
        type=str,
        default=None,
        help='Path to ONNX model for ML enhancement'
    )
    parser_args.add_argument(
        '--ml-task',
        type=str,
        default='rooms',
        help='ML task (e.g., rooms)'
    )
    parser_args.add_argument(
        '--no-blender',
        action='store_true',
        help='Skip calling Blender and continue to save plan.json'
    )
    
    args = parser_args.parse_args()
    
    # Handle UI mode
    if args.ui:
        try:
            import ui
            ui.launch_ui()
            return 0
        except ImportError:
            logger.error("UI module not found. Run without --ui flag for CLI mode.")
            return 1
    
    # For CLI mode, input is required
    if not args.input:
        logger.error("Error: --input is required for CLI mode")
        return 1
    
    # Verify input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return 1
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("2D to 3D Building Blueprint Converter")
    logger.info("=" * 60)
    logger.info(f"Input: {args.input}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Height: {args.height}m")
    
    # Parse optional JSON parameters
    stairs_data = parse_optional_json(args.stairs) if args.stairs else None
    entries_data = parse_optional_json(args.entries) if args.entries else None
    
    # Parse blueprint
    logger.info("Parsing blueprint...")
    try:
        plan_data = parser.parse_blueprint(
            args.input,
            pixels_per_meter=args.scale,
            stairs_data=stairs_data,
            entries_data=entries_data
        )
        
        if not plan_data:
            logger.error("Failed to parse blueprint")
            return 1
        
        logger.info(f"Detected {len(plan_data['walls'])} walls")
        logger.info(f"Detected {len(plan_data['doors'])} doors")
        logger.info(f"Detected {len(plan_data['stairs'])} stair regions")
        logger.info(f"Detected {len(plan_data.get('furniture', []))} furniture regions")
        
    except Exception as e:
        logger.error(f"Error parsing blueprint: {e}", exc_info=True)
        return 1
    
    # Optional ML enhancement for image inputs
    try:
        file_ext = os.path.splitext(args.input)[1].lower()
        if args.ml and file_ext in ['.png', '.jpg', '.jpeg', '.bmp']:
            import cv2  # local import to avoid hard dependency if ML disabled
            from ml.inference import detect_rooms_and_objects
            from ml.postprocess import merge_ml_into_plan
            
            logger.info("Running ML enhancement...")
            img = cv2.imread(args.input, cv2.IMREAD_COLOR)
            if img is None:
                logger.warning("Cannot load image for ML; skipping ML enhancement.")
            else:
                h, w = img.shape[:2]
                ml_out = detect_rooms_and_objects(args.input, model_path=args.ml_model, task=args.ml_task)
                plan_data = merge_ml_into_plan(plan_data, ml_out, pixels_per_meter=args.scale, img_width=w, img_height=h)
                logger.info(f"ML enhancement added {len(plan_data.get('rooms', []))} rooms")
    except Exception as e:
        logger.warning(f"ML enhancement failed: {e}")
    
    # Add metadata
    plan_data['metadata'] = {
        'scale': args.scale,
        'height': args.height,
        'input_file': args.input
    }
    
    # Save plan.json
    plan_json_path = output_dir / 'plan.json'
    try:
        with open(plan_json_path, 'w') as f:
            encoder = NumpyEncoder if np else json.JSONEncoder
            json.dump(plan_data, f, indent=2, cls=encoder)
        logger.info(f"Saved plan data to {plan_json_path}")
    except Exception as e:
        logger.error(f"Failed to save plan.json: {e}")
        return 1
    
    # Optionally download maps
    if args.download_maps:
        logger.info("Downloading OSM tiles...")
        try:
            map_downloader.download_tiles(plan_data['bounds'], output_dir)
        except Exception as e:
            logger.warning(f"Map download failed: {e}")
    
    # Check Blender availability unless user chose to skip it
    if not args.no_blender:
        if not check_blender_available():
            logger.error("Cannot proceed without Blender. Install Blender 3.5+ and ensure it's in PATH.")
            return 1
    else:
        logger.info("Skipping Blender invocation because --no-blender was specified")
    
    # Generate 3D model with Blender (skip if requested)
    if not args.no_blender:
        if not call_blender(
            str(plan_json_path), 
            args.height, 
            str(output_dir),
            wall_thickness=args.wall_thickness,
            stair_width=args.stair_width,
            furniture_enabled=not args.no_furniture,
            map_path=args.map,
            door_height=args.height * 0.85 if args.height else None,
            door_width=1.0
        ):
            logger.error("Failed to generate 3D model")
            return 1
    else:
        logger.info("Blender generation skipped; plan.json saved in output directory")
    
    logger.info("=" * 60)
    logger.info("Conversion complete!")
    logger.info(f"Output files in: {output_dir}")
    logger.info(f"- plan.json: Parsed blueprint data")
    logger.info(f"- model.glb: 3D model (web-ready)")
    logger.info(f"- model.obj: 3D model (standard format)")
    logger.info("=" * 60)
    
    # Generate report (plan.obj, blueprint.svg, report.html)
    try:
        import subprocess
        report_script = Path(__file__).parent / 'generate_report.py'
        result = subprocess.run(
            ['python', str(report_script), '--plan', str(plan_json_path), '--out', str(output_dir)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            logger.info("Report files generated successfully")
        else:
            logger.warning(f"Report generation failed: {result.stderr}")
    except Exception as e:
        logger.warning(f"Could not generate report: {e}")
    
    # Serve viewer if requested
    if args.serve_viewer:
        serve_viewer(output_dir)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
