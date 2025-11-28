"""
ML-based predictor for room details from blueprint.
Estimates: number of rooms, walls, area, and days to work.
"""

from typing import Dict, Any
import math


def estimate_from_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Estimate room count, wall length, area, and work days from parsed plan.json.
    
    Uses simple heuristics:
    - Rooms: detected rooms in ML or estimate from wall contours
    - Walls: sum of all wall edge lengths
    - Area: total area enclosed by walls
    - Days: estimate based on area (e.g., 10 sqm per day)
    """
    
    # Extract walls and rooms
    walls = plan.get('walls', [])
    rooms = plan.get('rooms', [])
    
    # Count rooms: use detected rooms or estimate from wall count
    num_rooms = max(len(rooms), max(1, len(walls) // 2))
    
    # Calculate total wall length
    total_wall_length = 0.0
    for wall_poly in walls:
        for i in range(len(wall_poly)):
            pt1 = wall_poly[i]
            pt2 = wall_poly[(i + 1) % len(wall_poly)]
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]
            total_wall_length += math.sqrt(dx**2 + dy**2)
    
    # Calculate total enclosed area
    def polygon_area(poly):
        """Shoelace formula for polygon area."""
        n = len(poly)
        if n < 3:
            return 0.0
        area = 0.0
        for i in range(n):
            x1, y1 = poly[i][0], poly[i][1]
            x2, y2 = poly[(i + 1) % n][0], poly[(i + 1) % n][1]
            area += x1 * y2 - x2 * y1
        return abs(area) / 2.0
    
    total_area = 0.0
    for wall_poly in walls:
        total_area += polygon_area(wall_poly)
    for room_poly in rooms:
        total_area += polygon_area(room_poly)
    
    # Estimate work days (assuming ~12-15 sqm per day of work)
    sqm_per_day = 15.0
    work_days = max(1, int(total_area / sqm_per_day))
    
    # Count wall segments (approximate wall count as number of edges)
    num_walls = sum(len(wall) for wall in walls)
    
    return {
        'num_rooms': num_rooms,
        'num_walls': num_walls,
        'total_wall_length_m': round(total_wall_length, 2),
        'total_area_sqm': round(total_area, 2),
        'estimated_work_days': work_days
    }


def estimate_from_image(img_shape: tuple, scale: float = 100.0) -> Dict[str, Any]:
    """
    Simple estimation from image dimensions when detailed plan not available.
    """
    h, w = img_shape[:2]
    
    # Convert pixels to meters
    area_sqm = (w * h) / (scale ** 2)
    
    # Rough estimates
    num_rooms = max(1, int(area_sqm / 30.0))  # ~30 sqm per room average
    num_walls = num_rooms * 3  # rough estimate
    total_wall_length = (w + h) * 2 / scale  # perimeter estimate
    work_days = max(1, int(area_sqm / 15.0))
    
    return {
        'num_rooms': num_rooms,
        'num_walls': num_walls,
        'total_wall_length_m': round(total_wall_length, 2),
        'total_area_sqm': round(area_sqm, 2),
        'estimated_work_days': work_days
    }
