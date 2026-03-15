import time
from pathlib import Path
from typing import Generator, Optional, Tuple

import cv2

import sys


ROOT_DIR = Path(__file__).resolve().parent
YOLO_FULL_DIR = ROOT_DIR / "yolo_full"
if str(YOLO_FULL_DIR) not in sys.path:
    sys.path.insert(0, str(YOLO_FULL_DIR))


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".m4v"}


def _pick_weights_path(weights) -> Optional[str]:
    if isinstance(weights, (list, tuple)):
        weights = weights[0] if weights else None
    if weights:
        weights_path = Path(str(weights))
        if weights_path.exists():
            return str(weights_path)

    fallback_candidates = [
        YOLO_FULL_DIR / "models" / "weights" / "yolov5x.pt",
        YOLO_FULL_DIR / "models" / "weights" / "yolov5s.pt",
    ]
    for candidate in fallback_candidates:
        if candidate.exists():
            return str(candidate)

    return None


def _is_webcam_source(source: str) -> bool:
    return source == "0" or source.isdigit()


def _is_stream_source(source: str) -> bool:
    lowered = source.lower()
    return lowered.startswith("rtsp://") or lowered.startswith("http://") or lowered.startswith("https://")


def _is_image_source(source: str) -> bool:
    return Path(source).suffix.lower() in IMAGE_SUFFIXES


def _is_video_source(source: str) -> bool:
    return Path(source).suffix.lower() in VIDEO_SUFFIXES


class YoloFullRunner:
    def __init__(
        self,
        weights=None,
        output_dir="inference/output",
        device="",
        img_size=640,
        conf_thres=0.4,
        iou_thres=0.5,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        device = "cpu" if device == "cpu" else "cuda:0"
        from app.core.detector import HelmetDetector

        self.detector = HelmetDetector(
            weights_path=_pick_weights_path(weights),
            device=device,
            img_size=img_size,
        )
        self.detector.set_confidence_threshold(conf_thres)
        self.detector.set_iou_threshold(iou_thres)

    def run_image(self, source: str, save_img: bool = True) -> str:
        image_path = Path(source)
        save_path = self.output_dir / image_path.name
        annotated_img, _, _ = self.detector.detect_image(str(image_path))
        if save_img:
            cv2.imwrite(str(save_path), annotated_img)
        return str(save_path)

    def run_video(
        self,
        source: str,
        save_img: bool = True,
    ) -> Generator[Tuple[int, int, object, object, float], None, str]:
        source_path = Path(source)
        save_path = self.output_dir / source_path.name

        cap = cv2.VideoCapture(str(source_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        writer = None
        if save_img:
            cap = cv2.VideoCapture(str(source_path))
            fps = int(cap.get(cv2.CAP_PROP_FPS)) or 25
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            writer = cv2.VideoWriter(
                str(save_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
            )

        frame_idx = 0
        for frame, annotated_frame, detections, statistics, fps in self.detector.detect_video(
            str(source_path), output_path=None, show=False
        ):
            frame_idx += 1
            if writer is not None:
                writer.write(annotated_frame)
            yield frame_idx, total_frames, frame, annotated_frame, fps

        if writer is not None:
            writer.release()
        return str(save_path)

    def run_camera(
        self,
        camera_id: int = 0,
        save_img: bool = False,
    ) -> Generator[Tuple[int, int, object, object, float], None, str]:
        save_path = self.output_dir / f"camera_{int(time.time())}.mp4"
        writer = None
        frame_idx = 0

        for frame, annotated_frame, detections, statistics, fps in self.detector.detect_camera(camera_id):
            frame_idx += 1
            if save_img:
                if writer is None:
                    height, width = annotated_frame.shape[:2]
                    writer = cv2.VideoWriter(
                        str(save_path),
                        cv2.VideoWriter_fourcc(*"mp4v"),
                        int(fps) if fps > 1 else 25,
                        (width, height),
                    )
                writer.write(annotated_frame)
            yield frame_idx, -1, frame, annotated_frame, fps

        if writer is not None:
            writer.release()
        return str(save_path)
