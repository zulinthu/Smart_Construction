# YOLO Full Capability Integration

`yolo_full/` contains the full migrated codebase from the standalone YOLO helmet-detection project.

## Included

- GUI app and detector core (`yolo_full/app/`)
- Training and evaluation scripts (`yolo_full/train/`, `yolo_full/evaluate/`)
- Improved model modules (`yolo_full/models/improved/`)
- Build/startup scripts and docs (`yolo_full/build.*`, `yolo_full/README.md`, `yolo_full/QUICK_START.md`)

## Quick Start

1. `cd yolo_full`
2. Create/activate Python environment
3. `pip install -r requirements.txt`
4. `python test_detector.py`
5. `python app/main.py`

## Notes

- This integration keeps the original `Smart_Construction` code unchanged and adds the full migrated project in parallel.
- Use `yolo_full/` when you want the complete migrated capability set.
- `detect.py` and `detect_visual.py` are now wired to use `yolo_full` detector runtime.
