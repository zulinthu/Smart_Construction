# -*- coding: utf-8 -*-
from pathlib import Path

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

from yolo_full_adapter import (
    YoloFullRunner,
    _is_image_source,
    _is_stream_source,
    _is_video_source,
    _is_webcam_source,
)


class YOLOPredict(object):
    def __init__(self, weights, out_file_path):
        self.agnostic_nms = False
        self.augment = False
        self.classes = None
        self.conf_thres = 0.4
        self.device = ""
        self.img_size = 640
        self.iou_thres = 0.5
        self.output = out_file_path
        self.save_txt = False
        self.update = False
        self.view_img = False
        self.weights = weights
        self.predict_info = ""

    @staticmethod
    def show_real_time_image(image_label, img):
        if img is None or img.size == 0:
            return

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        height, width = img_rgb.shape[:2]
        q_image = QImage(img_rgb.data, width, height, width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        target_size = image_label.size()
        if target_size.width() > 0 and target_size.height() > 0:
            pixmap = pixmap.scaled(
                target_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

        image_label.setAlignment(Qt.AlignCenter)
        image_label.setPixmap(pixmap)

    def detect(self, source, save_img=False, qt_input=None, qt_output=None, frame_callback=None):
        output_dir = Path(self.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        runner = YoloFullRunner(
            weights=self.weights,
            output_dir=output_dir,
            device=self.device,
            img_size=self.img_size,
            conf_thres=self.conf_thres,
            iou_thres=self.iou_thres,
        )

        source = str(source)

        if _is_image_source(source):
            save_path = runner.run_image(source, save_img=True)
            self.predict_info = "image Done. (0.000s)"
            return save_path

        if _is_video_source(source):
            source_name = Path(source).name
            save_path = str(output_dir / source_name)
            for idx, total, frame, annotated, fps in runner.run_video(source, save_img=True):
                infer_t = (1.0 / fps) if fps > 0 else 0
                self.predict_info = f"video [{idx}/{total}] Done. ({infer_t:.3f}s)"
                if frame_callback is not None:
                    frame_callback(frame, annotated)
                elif qt_input is not None and qt_output is not None:
                    # Backward compatibility for legacy callers
                    self.show_real_time_image(qt_input, frame)
                    self.show_real_time_image(qt_output, annotated)
            self.predict_info = "Done."
            return save_path

        if _is_webcam_source(source) or _is_stream_source(source):
            camera_id = int(source) if _is_webcam_source(source) else 0
            save_path = str(output_dir / "camera_output.mp4")
            for idx, total, frame, annotated, fps in runner.run_camera(
                camera_id=camera_id, save_img=save_img
            ):
                infer_t = (1.0 / fps) if fps > 0 else 0
                self.predict_info = f"video [{idx}/{idx + 1}] Done. ({infer_t:.3f}s)"
                if frame_callback is not None:
                    frame_callback(frame, annotated)
                elif qt_input is not None and qt_output is not None:
                    # Backward compatibility for legacy callers
                    self.show_real_time_image(qt_input, frame)
                    self.show_real_time_image(qt_output, annotated)
            self.predict_info = "Done."
            return save_path

        raise ValueError(f"Unsupported source: {source}")


if __name__ == "__main__":
    print(
        "This is not for run, may be you want to run 'detect.py' or 'visual_interface.py', pls check your file name. Thx ! "
    )
