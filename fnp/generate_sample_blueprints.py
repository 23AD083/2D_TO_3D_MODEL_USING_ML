#!/usr/bin/env python3
"""
Generate sample 2D blueprint floor plans as PNG images.
Useful for testing without manual input.
"""

import numpy as np
import cv2
from pathlib import Path


def create_simple_floor_plan(output_path: str, width: int = 800, height: int = 600) -> None:
    """
    Create a simple 2-room floor plan with walls, doors, and windows.
    """
    img = np.ones((height, width, 3), dtype=np.uint8) * 255  # white background
    
    # Wall color (dark gray)
    wall_color = (100, 100, 100)
    door_color = (200, 100, 50)
    window_color = (150, 200, 255)
    
    # Draw outer walls (thick rectangle)
    wall_thick = 8
    cv2.rectangle(img, (50, 50), (width - 50, height - 50), wall_color, wall_thick)
    
    # Draw interior wall (divides rooms)
    cv2.line(img, (width // 2, 50), (width // 2, height - 50), wall_color, wall_thick)
    
    # Draw doors (gaps in walls)
    door_width = 40
    # Door between rooms
    cv2.line(img, (width // 2 - door_width, height // 2 - 20), (width // 2 + door_width, height // 2 + 20), (255, 255, 255), 8)
    
    # Door to outside (left wall)
    cv2.line(img, (50, height // 2 - 30), (50, height // 2 + 30), (255, 255, 255), 8)
    
    # Draw windows (light blue rectangles)
    window_size = 30
    # Top wall
    cv2.rectangle(img, (150, 50), (150 + window_size, 50 + 10), window_color, -1)
    cv2.rectangle(img, (350, 50), (350 + window_size, 50 + 10), window_color, -1)
    
    # Right wall
    cv2.rectangle(img, (width - 50, 150), (width - 40, 150 + window_size), window_color, -1)
    
    # Save
    cv2.imwrite(output_path, img)
    print(f"✓ Sample floor plan created: {output_path}")


def create_complex_floor_plan(output_path: str, width: int = 1000, height: int = 800) -> None:
    """
    Create a more complex 4-room floor plan.
    """
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    wall_color = (80, 80, 80)
    wall_thick = 10
    
    # Outer walls
    cv2.rectangle(img, (60, 60), (width - 60, height - 60), wall_color, wall_thick)
    
    # Interior walls (grid layout: 2x2 rooms)
    mid_x = width // 2
    mid_y = height // 2
    
    cv2.line(img, (mid_x, 60), (mid_x, height - 60), wall_color, wall_thick)
    cv2.line(img, (60, mid_y), (width - 60, mid_y), wall_color, wall_thick)
    
    # Add some doors
    door_size = 35
    cv2.circle(img, (mid_x + 40, mid_y), door_size, (255, 255, 255), -1)
    cv2.circle(img, (mid_x - 40, mid_y), door_size, (255, 255, 255), -1)
    
    # Add windows
    win_color = (100, 180, 255)
    for x in [100, 300, mid_x + 100, mid_x + 300]:
        cv2.rectangle(img, (x, 55), (x + 25, 75), win_color, -1)
        cv2.rectangle(img, (x, height - 75), (x + 25, height - 55), win_color, -1)
    
    cv2.imwrite(output_path, img)
    print(f"✓ Complex floor plan created: {output_path}")


def create_studio_floor_plan(output_path: str, width: int = 800, height: int = 600) -> None:
    """Single-room studio with kitchenette and small bathroom."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    wall_color = (90, 90, 90)
    wall_thick = 8
    cv2.rectangle(img, (40, 40), (width - 40, height - 40), wall_color, wall_thick)

    # kitchenette area
    cv2.rectangle(img, (60, height - 160), (220, height - 80), (200, 200, 200), -1)
    cv2.putText(img, 'KT', (80, height - 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 80, 80), 2)

    # bathroom
    cv2.rectangle(img, (width - 180, 60), (width - 60, 160), wall_color, wall_thick)
    cv2.putText(img, 'Bath', (width - 170, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)

    # windows
    cv2.rectangle(img, (150, 40), (230, 52), (140, 200, 255), -1)
    cv2.rectangle(img, (width - 260, 40), (width - 180, 52), (140, 200, 255), -1)

    cv2.imwrite(output_path, img)
    print(f"✓ Studio floor plan created: {output_path}")


def create_1br_floor_plan(output_path: str, width: int = 900, height: int = 700) -> None:
    """One-bedroom apartment: living, kitchen, bedroom, bathroom."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    wall_color = (80, 80, 80)
    wall_thick = 10
    cv2.rectangle(img, (50, 50), (width - 50, height - 50), wall_color, wall_thick)

    # living/kitchen open area
    cv2.rectangle(img, (60, 60), (width - 320, height - 120), (230, 230, 230), -1)
    cv2.putText(img, 'Living/Kitchen', (80, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60,60,60), 2)

    # bedroom
    cv2.rectangle(img, (width - 300, 80), (width - 60, height - 300), wall_color, wall_thick)
    cv2.putText(img, 'Bed', (width - 260, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

    # bathroom
    cv2.rectangle(img, (width - 300, height - 260), (width - 60, height - 120), wall_color, wall_thick)
    cv2.putText(img, 'Bath', (width - 260, height - 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)

    cv2.imwrite(output_path, img)
    print(f"✓ 1BR floor plan created: {output_path}")


def create_2br_floor_plan(output_path: str, width: int = 1000, height: int = 800) -> None:
    """Two-bedroom apartment with central corridor."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    wall_color = (70, 70, 70)
    wall_thick = 10
    cv2.rectangle(img, (40, 40), (width - 40, height - 40), wall_color, wall_thick)

    # central corridor
    cv2.rectangle(img, (120, 60), (200, height - 60), (230,230,230), -1)

    # left rooms
    cv2.rectangle(img, (220, 60), (width - 60, height // 2 - 10), (240,240,240), -1)
    cv2.putText(img, 'Living', (240, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (60,60,60), 2)

    # bedrooms (two on the right side)
    cv2.rectangle(img, (220, height // 2 + 10), (width // 2, height - 80), wall_color, wall_thick)
    cv2.putText(img, 'Bed1', (240, height // 2 + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)
    cv2.rectangle(img, (width // 2 + 20, height // 2 + 10), (width - 80, height - 80), wall_color, wall_thick)
    cv2.putText(img, 'Bed2', (width // 2 + 40, height // 2 + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

    # bathroom
    cv2.rectangle(img, (width - 200, 80), (width - 80, 200), wall_color, wall_thick)
    cv2.putText(img, 'Bath', (width - 185, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)

    cv2.imwrite(output_path, img)
    print(f"✓ 2BR floor plan created: {output_path}")


def create_3br_floor_plan(output_path: str, width: int = 1100, height: int = 900) -> None:
    """Three-bedroom house layout with corridor and living area."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    wall_color = (80, 80, 80)
    wall_thick = 10
    cv2.rectangle(img, (50, 50), (width - 50, height - 50), wall_color, wall_thick)

    # corridor
    cv2.rectangle(img, (120, 80), (200, height - 80), (245,245,245), -1)

    # living/dining
    cv2.rectangle(img, (220, 80), (width - 80, 300), (230,230,230), -1)
    cv2.putText(img, 'Living/Dining', (240, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (60,60,60), 2)

    # three bedrooms stacked
    h_third = (height - 200) // 3
    for i, y in enumerate(range(320, height - 80, h_third)):
        top = y
        bottom = min(y + h_third - 20, height - 90)
        cv2.rectangle(img, (220, top), (width - 220, bottom), wall_color, wall_thick)
        cv2.putText(img, f'Bed{i+1}', (240, top + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

    cv2.imwrite(output_path, img)
    print(f"✓ 3BR floor plan created: {output_path}")


def create_small_office_floor_plan(output_path: str, width: int = 1000, height: int = 700) -> None:
    """Small office layout with open desks, meeting room and reception."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    wall_color = (70, 70, 70)
    wall_thick = 10
    cv2.rectangle(img, (40, 40), (width - 40, height - 40), wall_color, wall_thick)

    # reception
    cv2.rectangle(img, (60, 60), (260, 160), (230,230,230), -1)
    cv2.putText(img, 'Reception', (80, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50,50,50), 2)

    # open desks area
    for r in range(2):
        for c in range(3):
            x = 300 + c * 140
            y = 80 + r * 120
            cv2.rectangle(img, (x, y), (x + 100, y + 60), (240,240,240), -1)

    # meeting room
    cv2.rectangle(img, (60, 200), (260, 380), wall_color, wall_thick)
    cv2.putText(img, 'Meeting', (80, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

    cv2.imwrite(output_path, img)
    print(f"✓ Small office floor plan created: {output_path}")


def create_open_office_floor_plan(output_path: str, width: int = 1200, height: int = 800) -> None:
    """Large open-plan office with rows of desks and a few private rooms."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    wall_color = (80, 80, 80)
    wall_thick = 10
    cv2.rectangle(img, (30, 30), (width - 30, height - 30), wall_color, wall_thick)

    # desk rows
    start_x = 80
    start_y = 80
    for row in range(4):
        for col in range(8):
            x = start_x + col * 120
            y = start_y + row * 110
            cv2.rectangle(img, (x, y), (x + 90, y + 60), (245,245,245), -1)

    # private rooms right side
    for i in range(3):
        x1 = width - 320
        y1 = 80 + i * 220
        cv2.rectangle(img, (x1, y1), (width - 60, y1 + 180), wall_color, wall_thick)
        cv2.putText(img, f'Room{i+1}', (x1 + 10, y1 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

    cv2.imwrite(output_path, img)
    print(f"✓ Open office floor plan created: {output_path}")


def create_townhouse_floor_plan(output_path: str, width: int = 1000, height: int = 900) -> None:
    """Elongated townhouse-like layout with multiple small rooms."""
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    wall_color = (85, 85, 85)
    wall_thick = 10
    cv2.rectangle(img, (40, 40), (width - 40, height - 40), wall_color, wall_thick)

    # series of rooms along corridor
    room_h = (height - 120) // 5
    for i in range(5):
        top = 60 + i * room_h
        bottom = top + room_h - 10
        cv2.rectangle(img, (60, top), (width - 200, bottom), wall_color, wall_thick)
        cv2.putText(img, f'Room{i+1}', (80, top + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)

    # narrow corridor to the right
    cv2.rectangle(img, (width - 200, 60), (width - 60, height - 60), (240,240,240), -1)

    cv2.imwrite(output_path, img)
    print(f"✓ Townhouse floor plan created: {output_path}")


def main():
    sample_dir = Path(__file__).parent / 'sample_input'
    sample_dir.mkdir(exist_ok=True)
    
    samples = [
        ('sample_blueprint_studio.png', create_studio_floor_plan),
        ('sample_blueprint_1br.png', create_1br_floor_plan),
        ('sample_blueprint_2br.png', create_2br_floor_plan),
        ('sample_blueprint_3br.png', create_3br_floor_plan),
        ('sample_blueprint_small_office.png', create_small_office_floor_plan),
        ('sample_blueprint_open_office.png', create_open_office_floor_plan),
        ('sample_blueprint_townhouse.png', create_townhouse_floor_plan),
    ]

    for name, fn in samples:
        path = sample_dir / name
        try:
            fn(str(path))
        except Exception as e:
            print(f"! Failed to create {name}: {e}")

    print("\nSample blueprints created successfully!")
    for name, _ in samples:
        print(str(sample_dir / name))


if __name__ == '__main__':
    main()
