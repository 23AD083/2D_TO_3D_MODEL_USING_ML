#!/usr/bin/env python3
"""
Installation test script
Checks if all required dependencies are installed.
"""

import sys

def test_imports():
    """Test if all required modules can be imported."""
    modules = [
        'cv2',
        'numpy',
        'PIL',
        'ezdxf',
        'shapely',
        'matplotlib'
    ]
    
    failed = []
    
    for module_name in modules:
        try:
            if module_name == 'PIL':
                __import__('PIL')
                print(f"✓ {module_name} (Pillow)")
            elif module_name == 'cv2':
                import cv2
                print(f"✓ opencv-python (version {cv2.__version__})")
            else:
                __import__(module_name)
                print(f"✓ {module_name}")
        except ImportError:
            print(f"✗ {module_name} - NOT INSTALLED")
            failed.append(module_name)
    
    return failed


def test_blender():
    """Check if Blender is available."""
    import subprocess
    try:
        result = subprocess.run(
            ['blender', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip().split()[1]
            print(f"✓ Blender (version {version})")
            return True
        else:
            print("✗ Blender - Command failed")
            return False
    except FileNotFoundError:
        print("✗ Blender - NOT FOUND in PATH")
        return False
    except Exception as e:
        print(f"✗ Blender - Error: {e}")
        return False


def main():
    print("=" * 60)
    print("2D to 3D Converter - Installation Test")
    print("=" * 60)
    print()
    
    print("Testing Python modules...")
    failed = test_imports()
    print()
    
    print("Testing Blender...")
    blender_ok = test_blender()
    print()
    
    print("=" * 60)
    if failed:
        print(f"\n❌ FAILED: Missing {len(failed)} module(s)")
        print("Install missing modules with:")
        print("  python -m pip install -r requirements.txt")
        return 1
    
    if not blender_ok:
        print("\n⚠️  WARNING: Blender not found")
        print("Install Blender 3.5+ and ensure it's in PATH")
        print("Or set BLENDER_PATH environment variable")
        return 1
    
    print("\n✓ All dependencies installed successfully!")
    print("\nYou can now run:")
    print("  python main.py --input sample_input/sample_blueprint.png --scale 100 --height 3.5")
    return 0


if __name__ == '__main__':
    sys.exit(main())
