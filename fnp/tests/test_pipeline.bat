@echo off
REM Test script for blueprint to 3D converter (Windows)

echo ==========================================
echo Testing Blueprint to 3D Converter
echo ==========================================

echo.
echo Test 1: Converting sample PNG blueprint...
python main.py --input ../sample_input/sample_blueprint.png --scale 100 --height 3.5 --output ../output/test_png

if exist "../output/test_png/model.glb" (
    echo Test 1 passed: model.glb created
) else (
    echo Test 1 failed: model.glb not found
    exit /b 1
)

echo.
echo Test 2: Direct Blender call...
blender --background --python ../blender_generator.py -- --plan ../output/test_png/plan.json --height 3.5 --out ../output/test_blender

if exist "../output/test_blender/model.glb" (
    echo Test 2 passed: model.glb created
) else (
    echo Test 2 failed: model.glb not found
    exit /b 1
)

echo.
echo ==========================================
echo All tests passed!
echo ==========================================
