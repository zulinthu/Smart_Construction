import argparse
from pathlib import Path

import cv2

from yolo_full_adapter import (
    YoloFullRunner,
    _is_image_source,
    _is_stream_source,
    _is_video_source,
    _is_webcam_source,
)


def detect(opt):
    runner = YoloFullRunner(
        weights=opt.weights,
        output_dir=opt.output,
        device=opt.device,
        img_size=opt.img_size,
        conf_thres=opt.conf_thres,
        iou_thres=opt.iou_thres,
    )

    source = str(opt.source)
    source_path = Path(source)

    if source_path.is_dir():
        files = sorted([p for p in source_path.iterdir() if p.is_file()])
        if not files:
            raise ValueError(f"No files found in source directory: {source}")
        for item in files:
            item_source = str(item)
            if _is_image_source(item_source):
                save_path = runner.run_image(item_source, save_img=not opt.nosave)
                print(f"image [{item.name}] -> {save_path}")
                continue
            if _is_video_source(item_source):
                for idx, total, frame, annotated, fps in runner.run_video(
                    item_source, save_img=not opt.nosave
                ):
                    print(
                        f"video [{item.name}] [{idx}/{total}] Done. "
                        f"({(1.0 / fps) if fps > 0 else 0:.3f}s)"
                    )
                    if opt.view_img:
                        cv2.imshow("video", annotated)
                        if cv2.waitKey(1) == ord("q"):
                            break
                continue
        return

    if _is_image_source(source):
        save_path = runner.run_image(source, save_img=not opt.nosave)
        print(f"Results saved to {save_path}")
        if opt.view_img:
            image = cv2.imread(save_path if not opt.nosave else source)
            cv2.imshow(Path(source).name, image)
            cv2.waitKey(0)
        return

    if _is_video_source(source):
        for idx, total, frame, annotated, fps in runner.run_video(source, save_img=not opt.nosave):
            print(f"video [{idx}/{total}] Done. ({(1.0 / fps) if fps > 0 else 0:.3f}s)")
            if opt.view_img:
                cv2.imshow("video", annotated)
                if cv2.waitKey(1) == ord("q"):
                    break
        return

    if _is_webcam_source(source) or _is_stream_source(source):
        camera_id = int(source) if _is_webcam_source(source) else 0
        for idx, total, frame, annotated, fps in runner.run_camera(
            camera_id=camera_id, save_img=not opt.nosave
        ):
            print(f"camera [{idx}] Done. ({(1.0 / fps) if fps > 0 else 0:.3f}s)")
            if opt.view_img:
                cv2.imshow("camera", annotated)
                if cv2.waitKey(1) == ord("q"):
                    break
        return

    raise ValueError(f"Unsupported source: {source}")


if __name__ == "__main__":
    default_weights = (
        Path(__file__).resolve().parent / "yolo_full" / "models" / "weights" / "yolov5x.pt"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--weights",
        nargs="+",
        type=str,
        default=[str(default_weights)],
    )
    parser.add_argument("--source", type=str, default="inference/images")
    parser.add_argument("--output", type=str, default="inference/output")
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--conf-thres", type=float, default=0.4)
    parser.add_argument("--iou-thres", type=float, default=0.5)
    parser.add_argument("--device", default="", help="cuda device id or cpu")
    parser.add_argument("--view-img", action="store_true")
    parser.add_argument("--nosave", action="store_true")
    parser.add_argument("--save-txt", action="store_true")
    parser.add_argument("--classes", nargs="+", type=int)
    parser.add_argument("--agnostic-nms", action="store_true")
    parser.add_argument("--augment", action="store_true")
    parser.add_argument("--update", action="store_true")
    opt = parser.parse_args()
    print(opt)
    detect(opt)
