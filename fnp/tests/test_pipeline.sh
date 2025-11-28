#!/bin/bash
# Test script for blueprint to 3D converter

set -e

echo "=========================================="
echo "Testing Blueprint to 3D Converter"
echo "=========================================="

# Test 1: Sample PNG blueprint
echo ""
echo "Test 1: Converting sample PNG blueprint..."
python main.py --input ../sample_input/sample_blueprint.png --scale 100 --height 3.5 --output ../output/test_png

if [ -f "../output/test_png/model.glb" ]; then
    SIZE=$(stat -f%z "../output/test_png/model.glb" 2>/dev/null || stat -c%s "../output/test_png/model.glb" 2>/dev/null || echo "0")
    echo "✓ PNG test passed. model.glb size: $SIZE bytes"
else
    echo "✗ PNG test failed. model.glb not found."
    exit 1
fi

# Test 2: Direct Blender call
echo ""
echo "Test 2: Direct Blender call..."
blender --background --python ../blender_generator.py -- --plan ../output/test_png/plan.json --height 3.5 --out ../output/test_blender

if [ -f "../output/test_blender/model.glb" ]; then
    SIZE=$(stat -f%z "../output/test_blender/model.glb" 2>/dev/null || stat -c%s "../output/test_blender/model.glb" 2>/dev/null || echo "0")
    echo "✓ Blender test passed. model.glb size: $SIZE bytes"
else
    echo "✗ Blender test failed. model.glb not found."
    exit 1
fi

echo ""
echo "=========================================="
echo "All tests passed!"
echo "=========================================="
