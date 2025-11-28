#!/usr/bin/env python3
"""
Blueprint Parser Module
Handles parsing of image (PNG/JPG) and DXF files to extract building geometry.
"""

import logging
import json
import math
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Try to import ezdxf (optional for DXF support)
try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False
    logger.warning("ezdxf not available. DXF support disabled.")


def parse_image_blueprint(
    image_path: str,
    pixels_per_meter: float = 100.0
) -> Dict[str, Any]:
    """
    Parse a PNG/JPG blueprint image to extract walls, doors, and structural elements.
    
    Args:
        image_path: Path to image file
        pixels_per_meter: Scale factor for pixel to meter conversion
    
    Returns:
        Dictionary with walls, doors, stairs, and bounds
    """
    logger.info(f"Parsing image blueprint: {image_path}")
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        logger.error(f"Failed to load image: {image_path}")
        return None
    
    height, width = img.shape[:2]
    logger.info(f"Image dimensions: {width}x{height} pixels")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(
        gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        11, 2
    )
    
    # Morphological operations to clean up
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    
    # Detect contours
    contours, _ = cv2.findContours(
        cleaned, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    logger.info(f"Found {len(contours)} contours")
    
    # Filter and approximate contours to polygons
    walls = []
    min_area = 100  # Minimum area threshold
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        
        # Approximate contour to polyline
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        if len(approx) >= 3:  # Valid polygon
            # Convert to list of coordinates in meters
            polyline = []
            for point in approx:
                x, y = point[0]
                # Convert pixel to meters, center origin
                x_m = (x - width/2) / pixels_per_meter
                y_m = (height/2 - y) / pixels_per_meter  # Flip Y-axis
                polyline.append([x_m, y_m])
            
            walls.append(polyline)
    
    logger.info(f"Extracted {len(walls)} wall polygons")
    
    # Detect doors from image
    doors = detect_doors_from_image(binary, walls, pixels_per_meter)
    logger.info(f"Detected {len(doors)} doors")
    
    # Detect stairs from image
    stairs = detect_stairs_from_image(binary, pixels_per_meter)
    logger.info(f"Detected {len(stairs)} stair regions")
    
    # Detect furniture regions
    furniture = detect_furniture_regions(cleaned, pixels_per_meter)
    logger.info(f"Detected {len(furniture)} furniture regions")
    
    # Calculate bounds
    bounds = calculate_bounds(walls)
    
    return {
        'walls': walls,
        'doors': doors,
        'stairs': stairs,
        'furniture': furniture,
        'bounds': bounds
    }


def detect_doors_from_image(
    binary: np.ndarray,
    walls: List[List[List[float]]],
    pixels_per_meter: float
) -> List[Dict[str, float]]:
    """
    Detect door openings by finding arcs and gaps in wall segments.
    
    Args:
        binary: Binary thresholded image
        walls: List of wall polylines
        pixels_per_meter: Scale factor
    
    Returns:
        List of door dictionaries with x1, y1, x2, y2 coordinates
    """
    doors = []
    height, width = binary.shape
    
    # Detect circular/elliptical patterns (door swing arcs)
    circles = cv2.HoughCircles(
        binary,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=int(0.8 * pixels_per_meter),
        param1=50,
        param2=30,
        minRadius=int(0.3 * pixels_per_meter),
        maxRadius=int(0.7 * pixels_per_meter)
    )
    
    if circles is not None:
        for circle in circles[0]:
            x, y, r = circle
            # Find wall intersection point
            door_x = x
            door_y = y + r
            
            # Convert to meters
            x_m = (door_x - width/2) / pixels_per_meter
            y_m = (height/2 - door_y) / pixels_per_meter
            
            # Create door opening (0.9m wide by 2.1m high)
            door_width = 0.9
            doors.append({
                'x1': x_m - door_width/2,
                'y1': y_m,
                'x2': x_m + door_width/2,
                'y2': y_m
            })
    
    logger.info(f"Detected {len(doors)} doors from arcs")
    return doors


def detect_stairs_from_image(
    binary: np.ndarray,
    pixels_per_meter: float
) -> List[List[float]]:
    """
    Detect stair regions by finding repeated parallel narrow rectangles.
    
    Args:
        binary: Binary thresholded image
        pixels_per_meter: Scale factor
    
    Returns:
        List of stair polygon coordinates
    """
    stairs = []
    height, width = binary.shape
    
    # Detect parallel lines
    lines = cv2.HoughLines(binary, 1, np.pi/180, int(0.8 * pixels_per_meter))
    
    if lines is not None:
        # Group lines by angle
        grouped_lines = {}
        for rho, theta in lines[:, 0]:
            angle = int(theta * 180 / np.pi)
            if angle not in grouped_lines:
                grouped_lines[angle] = []
            grouped_lines[angle].append((rho, theta))
        
        # Find stair patterns (multiple parallel lines)
        for angle, line_group in grouped_lines.items():
            if len(line_group) >= 3:  # Stairs typically have 3+ steps
                # Extract region bounds
                rhos = [l[0] for l in line_group]
                min_rho = min(rhos)
                max_rho = max(rhos)
                
                # Convert to polygon
                stair_width = (max_rho - min_rho) / pixels_per_meter
                if 1.0 < stair_width < 3.0:  # Reasonable stair width
                    # Simple rectangular approximation
                    stairs.append([
                        [-1.0, 0.0],
                        [1.0, 0.0],
                        [1.0, stair_width],
                        [-1.0, stair_width]
                    ])
    
    return stairs


def detect_furniture_regions(
    binary: np.ndarray,
    pixels_per_meter: float
) -> List[Dict[str, Any]]:
    """
    Detect furniture by finding small rectangular regions.
    
    Args:
        binary: Binary image
        pixels_per_meter: Scale factor
    
    Returns:
        List of furniture dictionaries
    """
    furniture = []
    height, width = binary.shape
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        # Furniture typically has area < 8 sqm
        max_area = 8.0 * pixels_per_meter * pixels_per_meter
        
        if 50 < area < max_area:
            # Approximate as rectangle
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            
            # Convert to meters
            points_m = []
            for point in box:
                x, y = point
                x_m = (x - width/2) / pixels_per_meter
                y_m = (height/2 - y) / pixels_per_meter
                points_m.append([x_m, y_m])
            
            furniture.append({
                'polygon': points_m,
                'type': 'furniture'
            })
    
    return furniture


def calculate_bounds(walls: List[List[List[float]]]) -> Dict[str, List[float]]:
    """Calculate bounding box of all walls."""
    all_points = []
    for wall in walls:
        all_points.extend(wall)
    
    if not all_points:
        return {'min': [0, 0], 'max': [10, 10]}
    
    all_points = np.array(all_points)
    return {
        'min': all_points.min(axis=0).tolist(),
        'max': all_points.max(axis=0).tolist()
    }


def parse_dxf_blueprint(dxf_path: str) -> Dict[str, Any]:
    """
    Parse a DXF file to extract walls, doors, windows, and stairs based on layers.
    
    Args:
        dxf_path: Path to DXF file
    
    Returns:
        Dictionary with walls, doors, windows, stairs, and bounds
    """
    if not HAS_EZDXF:
        logger.error("ezdxf not available. Cannot parse DXF files.")
        return None
    
    logger.info(f"Parsing DXF blueprint: {dxf_path}")
    
    try:
        doc = ezdxf.readfile(dxf_path)
        modelspace = doc.modelspace()
        
        # Get DXF units
        units = doc.header.get('$INSUNITS', '0') if doc.header else '0'
        logger.info(f"DXF units code: {units}")
        
        # Import utils for unit conversion
        import utils
        unit_conversion = utils.convert_dxf_units(1.0, units)
        logger.info(f"Unit conversion factor: {unit_conversion} to meters")
        
        walls = []
        doors = []
        windows = []
        stairs = []
        
        # Helper function to normalize layer names
        def normalize_layer(layer_name):
            name = layer_name.upper().strip()
            if 'WALL' in name or 'EXTERIOR' in name:
                return 'WALL'
            elif 'DOOR' in name or 'OPENING' in name:
                return 'DOOR'
            elif 'WINDOW' in name:
                return 'WINDOW'
            elif 'STAIR' in name or 'STEP' in name:
                return 'STAIR'
            else:
                return 'UNKNOWN'
        
        # Extract entities grouped by layer
        layer_groups = {
            'WALL': [],
            'DOOR': [],
            'WINDOW': [],
            'STAIR': []
        }
        
        # Process all entities
        for entity in modelspace:
            layer = entity.dxf.layer if hasattr(entity.dxf, 'layer') else '0'
            layer_type = normalize_layer(layer)
            
            # Extract LINE entities
            if entity.dxftype() == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                segment = [
                    [start.x * unit_conversion, start.y * unit_conversion],
                    [end.x * unit_conversion, end.y * unit_conversion]
                ]
                if layer_type in layer_groups:
                    layer_groups[layer_type].append(segment)
            
            # Extract POLYLINE entities
            elif entity.dxftype() == 'POLYLINE':
                if entity.is_2d_polyline:
                    points = []
                    for vertex in entity.vertices:
                        if vertex.dxf.location:
                            loc = vertex.dxf.location
                            points.append([loc.x * unit_conversion, loc.y * unit_conversion])
                    if len(points) >= 2:
                        if layer_type in layer_groups:
                            layer_groups[layer_type].append(points)
            
            # Extract LWPOLYLINE entities (more common)
            elif entity.dxftype() == 'LWPOLYLINE':
                points = []
                with entity.points() as pl:
                    for point in pl:
                        points.append([point[0] * unit_conversion, point[1] * unit_conversion])
                if len(points) >= 2:
                    if layer_type in layer_groups:
                        layer_groups[layer_type].append(points)
        
        walls = layer_groups['WALL']
        doors = layer_groups['DOOR']
        windows = layer_groups['WINDOW']
        stairs = layer_groups['STAIR']
        
        # If no layers found, try geometry-based classification
        if not walls and not doors and not windows and not stairs:
            logger.warning("No layer-based classification found. Using geometry-based detection.")
            all_segments = layer_groups['WALL'] + layer_groups['DOOR'] + layer_groups['WINDOW'] + layer_groups['STAIR']
            
            if all_segments:
                # Classify by segment length
                for segment in all_segments:
                    if len(segment) < 2:
                        continue
                    
                    # Calculate segment length
                    total_length = 0.0
                    for i in range(len(segment) - 1):
                        dx = segment[i+1][0] - segment[i][0]
                        dy = segment[i+1][1] - segment[i][1]
                        total_length += math.sqrt(dx*dx + dy*dy)
                    
                    # Classify by length
                    if total_length > 3.0:  # Long segments are walls
                        walls.append(segment)
                    elif 0.7 < total_length < 1.2:  # Door-sized gaps
                        doors.append(segment)
                    elif total_length < 0.7:  # Short segments might be windows
                        windows.append(segment)
        
        logger.info(f"Extracted {len(walls)} wall segments, {len(doors)} doors, {len(windows)} windows, {len(stairs)} stairs from DXF")
        
        # Calculate bounds
        all_elements = walls + doors + windows + stairs
        bounds = calculate_bounds(all_elements) if all_elements else {'min': [0, 0], 'max': [10, 10]}
        
        return {
            'walls': walls,
            'doors': doors,
            'windows': windows,
            'stairs': stairs,
            'bounds': bounds
        }
        
    except Exception as e:
        logger.error(f"Error parsing DXF: {e}", exc_info=True)
        return None


def parse_blueprint(
    input_path: str,
    pixels_per_meter: float = 100.0,
    stairs_data: Optional[Dict] = None,
    entries_data: Optional[Dict] = None
) -> Optional[Dict[str, Any]]:
    """
    Main parsing function that routes to appropriate parser based on file type.
    
    Args:
        input_path: Path to blueprint file
        pixels_per_meter: Scale factor for image inputs
        stairs_data: Optional stairs data from CLI
        entries_data: Optional door data from CLI
    
    Returns:
        Dictionary with plan data
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return None
    
    # Determine file type and parse
    file_ext = input_path.suffix.lower()
    
    if file_ext in ['.png', '.jpg', '.jpeg', '.bmp']:
        plan_data = parse_image_blueprint(str(input_path), pixels_per_meter)
    elif file_ext == '.dxf':
        plan_data = parse_dxf_blueprint(str(input_path))
    else:
        logger.error(f"Unsupported file format: {file_ext}")
        return None
    
    if plan_data is None:
        return None
    
    # Apply user-provided stairs and entry data
    if stairs_data:
        plan_data['stairs'] = stairs_data.get('stairs', [])
    
    if entries_data:
        plan_data['doors'] = entries_data.get('doors', entries_data.get('entries', []))
    
    return plan_data


if __name__ == '__main__':
    # Test parsing with sample blueprint
    logging.basicConfig(level=logging.INFO)
    
    sample_path = Path(__file__).parent / 'sample_input' / 'sample_blueprint.png'
    if sample_path.exists():
        result = parse_blueprint(str(sample_path), pixels_per_meter=100)
        if result:
            print(json.dumps(result, indent=2))
    else:
        print("Sample blueprint not found. Create a test image to test parsing.")
