#!/usr/bin/env python3
"""
Utility functions for geometry transformations, validation, and coordinate handling.
"""

import logging
import math
from typing import List, Tuple, Dict, Any, Optional
from shapely.geometry import LineString, Polygon, Point
from shapely.ops import unary_union, linemerge
import numpy as np

logger = logging.getLogger(__name__)


def snap_coordinate(point: List[float], tolerance: float = 0.01) -> List[float]:
    """
    Snap coordinates to grid based on tolerance.
    
    Args:
        point: [x, y] coordinate
        tolerance: Snap tolerance in meters
    
    Returns:
        Snapped [x, y] coordinate
    """
    return [
        round(point[0] / tolerance) * tolerance,
        round(point[1] / tolerance) * tolerance
    ]


def simplify_polyline(
    points: List[List[float]], 
    tolerance: float = 0.05
) -> List[List[float]]:
    """
    Simplify polyline using Douglas-Peucker algorithm via Shapely.
    
    Args:
        points: List of [x, y] coordinates
        tolerance: Simplification tolerance in meters
    
    Returns:
        Simplified list of [x, y] coordinates
    """
    if len(points) < 3:
        return points
    
    try:
        line = LineString(points)
        simplified = line.simplify(tolerance, preserve_topology=True)
        
        if simplified.geom_type == 'LineString':
            return [[p[0], p[1]] for p in simplified.coords]
        else:
            # Handle MultiLineString
            coords = []
            for part in simplified.geoms:
                coords.extend([[p[0], p[1]] for p in part.coords])
            return coords
    except Exception as e:
        logger.warning(f"Simplification failed: {e}. Returning original points.")
        return points


def close_polygon(points: List[List[float]]) -> List[List[float]]:
    """
    Ensure polygon is closed (first and last points are the same).
    
    Args:
        points: List of [x, y] coordinates
    
    Returns:
        Closed polygon points
    """
    if not points:
        return points
    
    # Check if already closed
    first = points[0]
    last = points[-1]
    
    if len(points) > 2 and abs(first[0] - last[0]) < 0.01 and abs(first[1] - last[1]) < 0.01:
        return points
    
    return points + [first]


def fix_polygon_orientation(points: List[List[float]]) -> List[List[float]]:
    """
    Fix polygon orientation to be counter-clockwise (standard for exterior rings).
    
    Args:
        points: List of [x, y] coordinates
    
    Returns:
        Correctly oriented polygon points
    """
    if len(points) < 3:
        return points
    
    try:
        poly = Polygon(points)
        
        # Check orientation and reverse if needed
        if not poly.exterior.is_ccw:
            return list(poly.exterior.coords)[:-1]  # Remove duplicate last point
        else:
            return points
    except Exception as e:
        logger.warning(f"Orientation fix failed: {e}")
        return points


def validate_geometry(points: List[List[float]]) -> bool:
    """
    Validate geometry for self-intersections and degeneracy.
    
    Args:
        points: List of [x, y] coordinates
    
    Returns:
        True if valid, False otherwise
    """
    if len(points) < 3:
        return False
    
    try:
        poly = Polygon(points)
        
        # Check if valid
        if not poly.is_valid:
            logger.warning(f"Invalid geometry detected: {poly.wkt[:50]}")
            return False
        
        # Check for self-intersections
        if poly.exterior.is_ring is False:
            logger.warning("Geometry is not a closed ring")
            return False
        
        return True
    except Exception as e:
        logger.warning(f"Validation failed: {e}")
        return False


def calculate_bounds(points_list: List[List[List[float]]]) -> Dict[str, List[float]]:
    """
    Calculate bounding box for a list of polylines.
    
    Args:
        points_list: List of polylines, each is a list of [x, y] coordinates
    
    Returns:
        Dictionary with 'min' and 'max' keys containing [x, y] bounds
    """
    all_points = []
    for poly in points_list:
        all_points.extend(poly)
    
    if not all_points:
        return {'min': [0, 0], 'max': [10, 10]}
    
    all_points = np.array(all_points)
    return {
        'min': all_points.min(axis=0).tolist(),
        'max': all_points.max(axis=0).tolist()
    }


def normalize_to_origin(points: List[List[float]]) -> Tuple[List[List[float]], List[float]]:
    """
    Translate coordinates to origin (0, 0).
    
    Args:
        points: List of [x, y] coordinates
    
    Returns:
        Tuple of (translated points, offset)
    """
    if not points:
        return points, [0, 0]
    
    all_points = np.array(points)
    min_coords = all_points.min(axis=0).tolist()
    
    translated = (all_points - min_coords).tolist()
    return translated, min_coords


def convert_dxf_units(value: float, units: str) -> float:
    """
    Convert DXF units to meters.
    
    Args:
        value: Value in DXF units
        units: DXF unit code ('0'=Unitless, '1'=Inches, '2'=Feet, etc.)
    
    Returns:
        Value in meters
    """
    # DXF unit codes
    UNIT_CONVERSIONS = {
        0: 1.0,        # Unitless (treat as meters)
        1: 0.0254,     # Inches to meters
        2: 0.3048,     # Feet to meters
        3: 0.3048,     # Miles (handled separately if needed)
        4: 1e-6,       # Millimeters to meters
        5: 0.01,       # Centimeters to meters
        6: 1.0,        # Meters
        7: 1000.0,     # Kilometers to meters
        8: 1852.0,     # Microinches to meters
        9: 1609.344,   # Mils to meters
        10: 100.0,     # Yards to meters (approximate)
        11: 39370.1,   # Angstroms to meters
        12: 1e9,       # Nanometers to meters
        13: 1e6,       # Microns to meters
        14: 1e-2,      # Decimeters to meters
        15: 10.0,      # Decameters to meters
        16: 100.0,     # Hectometers to meters
        17: 1000.0,    # Gigameters to meters
        18: 1.0        # Astronomical units (approximate)
    }
    
    unit_code = int(units) if isinstance(units, str) else units
    conversion = UNIT_CONVERSIONS.get(unit_code, 1.0)
    return value * conversion


def merge_wall_segments(
    wall_points: List[List[float]], 
    angle_threshold: float = math.radians(15)
) -> List[List[float]]:
    """
    Merge wall segments that are nearly collinear.
    
    Args:
        wall_points: List of [x, y] coordinates
        angle_threshold: Maximum angle difference in radians to merge
    
    Returns:
        Merged wall points
    """
    if len(wall_points) < 3:
        return wall_points
    
    merged = [wall_points[0]]
    
    for i in range(1, len(wall_points) - 1):
        p1 = np.array(wall_points[i-1])
        p2 = np.array(wall_points[i])
        p3 = np.array(wall_points[i+1])
        
        v1 = p2 - p1
        v2 = p3 - p2
        
        # Normalize vectors
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-9)
        v2_norm = v2 / (np.linalg.norm(v2) + 1e-9)
        
        # Calculate angle between segments
        cos_angle = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
        angle = math.acos(cos_angle)
        
        # If angle is small, skip this point
        if angle > angle_threshold:
            merged.append(p2.tolist())
    
    merged.append(wall_points[-1])
    return merged


def calculate_polygon_area(points: List[List[float]]) -> float:
    """
    Calculate area of polygon using shoelace formula.
    
    Args:
        points: List of [x, y] coordinates
    
    Returns:
        Area in square meters
    """
    if len(points) < 3:
        return 0.0
    
    area = 0.0
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    
    return abs(area) / 2.0


def detect_wall_direction(points: List[List[float]]) -> str:
    """
    Detect primary direction of wall (horizontal, vertical, or diagonal).
    
    Args:
        points: List of [x, y] coordinates
    
    Returns:
        'horizontal', 'vertical', or 'diagonal'
    """
    if len(points) < 2:
        return 'diagonal'
    
    total_dx = 0.0
    total_dy = 0.0
    
    for i in range(len(points) - 1):
        dx = abs(points[i+1][0] - points[i][0])
        dy = abs(points[i+1][1] - points[i][1])
        total_dx += dx
        total_dy += dy
    
    if total_dx > total_dy * 2:
        return 'horizontal'
    elif total_dy > total_dx * 2:
        return 'vertical'
    else:
        return 'diagonal'


def create_wall_thickness_offset(
    points: List[List[float]], 
    thickness: float,
    outward: bool = True
) -> List[List[float]]:
    """
    Create offset for wall thickness using Shapely.
    
    Args:
        points: List of [x, y] coordinates
        thickness: Wall thickness in meters
        outward: If True, expand outward; if False, shrink inward
    
    Returns:
        Offset polygon points
    """
    if len(points) < 3:
        return points
    
    try:
        poly = Polygon(points)
        
        if not poly.is_valid:
            # Try to fix self-intersections
            poly = poly.buffer(0)
        
        # Create offset
        if outward:
            offset_poly = poly.buffer(thickness / 2, join_style=2, mitre_limit=2.0)
        else:
            offset_poly = poly.buffer(-thickness / 2, join_style=2, mitre_limit=2.0)
        
        if offset_poly.is_empty:
            logger.warning("Offset polygon is empty. Returning original.")
            return points
        
        # Return coordinates
        coords = list(offset_poly.exterior.coords)
        return [[p[0], p[1]] for p in coords[:-1]]  # Remove duplicate last point
    except Exception as e:
        logger.warning(f"Offset creation failed: {e}")
        return points
