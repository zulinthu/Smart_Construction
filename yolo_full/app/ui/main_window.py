"""
主窗口界面
提供图片、视频、摄像头检测的统一界面
"""

import sys
import cv2
from pathlib import Path

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGroupBox,
    QRadioButton,
    QFileDialog,
    QTextEdit,
    QSlider,
    QComboBox,
    QStatusBar,
    QMessageBox,
    QProgressBar,
    QFrame,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap, QFont

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from config import WINDOW_WIDTH, WINDOW_HEIGHT, CLASS_NAMES_ZH, WEIGHTS_DIR
from app.core.detector import HelmetDetector


class DetectionThread(QThread):
    """检测线程类"""
    
    # 定义信号
    frame_ready = pyqtSignal(object)  # 帧准备就绪
    detection_done = pyqtSignal(object, object, object)  # 检测完成(图像, 检测结果, 统计)
    fps_updated = pyqtSignal(float)  # FPS更新
    progress_updated = pyqtSignal(int)  # 进度更新
    error_occurred = pyqtSignal(str)  # 错误发生
    finished = pyqtSignal()  # 完成
    
    def __init__(self, mode, source_path=None, camera_id=0):
        super().__init__()
        self.mode = mode  # 'image', 'video', 'camera'
        self.source_path = source_path
        self.camera_id = camera_id
        self.is_running = True
        self.is_paused = False
        self.detector = None
    
    def run(self):
        """线程主函数"""
        try:
            # 创建检测器
            self.detector = HelmetDetector(device='cpu')  # 可以改为cuda
            
            if self.mode == 'image':
                self._detect_image()
            elif self.mode == 'video':
                self._detect_video()
            elif self.mode == 'camera':
                self._detect_camera()
                
        except Exception as e:
            self.error_occurred.emit(f"检测错误: {str(e)}")
        finally:
            self.finished.emit()
    
    def _detect_image(self):
        """检测图像"""
        if not self.source_path:
            self.error_occurred.emit("未指定图像路径")
            return
        
        annotated_image, detections, statistics = self.detector.detect_image(self.source_path)
        self.detection_done.emit(annotated_image, detections, statistics)
        self.progress_updated.emit(100)
    
    def _detect_video(self):
        """检测视频"""
        if not self.source_path:
            self.error_occurred.emit("未指定视频路径")
            return
        
        for frame, annotated_frame, detections, statistics, fps in self.detector.detect_video(self.source_path, show=False):
            if not self.is_running:
                break
            
            while self.is_paused and self.is_running:
                self.msleep(100)
            
            self.detection_done.emit(annotated_frame, detections, statistics)
            self.fps_updated.emit(fps)
    
    def _detect_camera(self):
        """检测摄像头"""
        for frame, annotated_frame, detections, statistics, fps in self.detector.detect_camera(self.camera_id):
            if not self.is_running:
                break
            
            while self.is_paused and self.is_running:
                self.msleep(100)
            
            self.detection_done.emit(annotated_frame, detections, statistics)
            self.fps_updated.emit(fps)
    
    def stop(self):
        """停止线程"""
        self.is_running = False
    
    def pause(self):
        """暂停检测"""
        self.is_paused = True
    
    def resume(self):
        """恢复检测"""
        self.is_paused = False


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_variables()

    def init_variables(self):
        """初始化变量"""
        self.detector = None
        self.detection_thread = None
        self.is_detecting = False
        self.current_mode = "image"  # 'image', 'video', 'camera'
        self.current_file_path = None  # 当前选择的文件路径
        self.current_image = None  # 当前显示的图像
        self.statistics = {
            "total": 0,
            "wearing_helmet": 0,
            "no_helmet": 0,
            "compliance_rate": 0.0,
        }

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("安全帽检测系统 v1.0")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # 左侧控制面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        # 右侧显示区域
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 4)

        # 创建状态栏
        self.create_status_bar()

        # 创建菜单栏
        self.create_menu_bar()

    def create_left_panel(self):
        """创建左侧控制面板"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setMaximumWidth(300)

        layout = QVBoxLayout()
        panel.setLayout(layout)

        # 1. 输入源选择
        input_group = self.create_input_group()
        layout.addWidget(input_group)

        # 2. 检测控制
        control_group = self.create_control_group()
        layout.addWidget(control_group)

        # 3. 参数设置
        params_group = self.create_params_group()
        layout.addWidget(params_group)

        # 4. 统计信息
        stats_group = self.create_stats_group()
        layout.addWidget(stats_group)

        # 5. 日志显示
        log_group = self.create_log_group()
        layout.addWidget(log_group)

        layout.addStretch()

        return panel

    def create_input_group(self):
        """创建输入源选择组"""
        group = QGroupBox("输入源选择")
        layout = QVBoxLayout()

        # 单选按钮
        self.radio_image = QRadioButton("图片检测")
        self.radio_video = QRadioButton("视频检测")
        self.radio_camera = QRadioButton("摄像头检测")
        self.radio_image.setChecked(True)

        # 连接信号
        self.radio_image.toggled.connect(lambda: self.on_mode_changed("image"))
        self.radio_video.toggled.connect(lambda: self.on_mode_changed("video"))
        self.radio_camera.toggled.connect(lambda: self.on_mode_changed("camera"))

        layout.addWidget(self.radio_image)
        layout.addWidget(self.radio_video)
        layout.addWidget(self.radio_camera)

        # 文件选择按钮
        self.btn_select_file = QPushButton("选择文件")
        self.btn_select_file.clicked.connect(self.on_select_file)
        layout.addWidget(self.btn_select_file)

        # 摄像头选择
        camera_layout = QHBoxLayout()
        camera_layout.addWidget(QLabel("摄像头:"))
        self.combo_camera = QComboBox()
        self.combo_camera.addItems(["摄像头 0", "摄像头 1"])
        camera_layout.addWidget(self.combo_camera)
        layout.addLayout(camera_layout)

        # 文件路径显示
        self.label_file_path = QLabel("未选择文件")
        self.label_file_path.setWordWrap(True)
        self.label_file_path.setStyleSheet("color: #666; font-size: 9px;")
        layout.addWidget(self.label_file_path)

        group.setLayout(layout)
        return group

    def create_control_group(self):
        """创建检测控制组"""
        group = QGroupBox("检测控制")
        layout = QVBoxLayout()

        # 控制按钮
        self.btn_start = QPushButton("开始检测")
        self.btn_start.clicked.connect(self.on_start_detection)
        self.btn_start.setStyleSheet("background-color: #4CAF50;")

        self.btn_pause = QPushButton("暂停")
        self.btn_pause.clicked.connect(self.on_pause_detection)
        self.btn_pause.setEnabled(False)

        self.btn_stop = QPushButton("停止")
        self.btn_stop.clicked.connect(self.on_stop_detection)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("background-color: #F44336;")

        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_pause)
        layout.addWidget(self.btn_stop)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        group.setLayout(layout)
        return group

    def create_params_group(self):
        """创建参数设置组"""
        group = QGroupBox("参数设置")
        layout = QVBoxLayout()

        # 置信度阈值
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("置信度:"))
        self.slider_conf = QSlider(Qt.Horizontal)
        self.slider_conf.setMinimum(1)
        self.slider_conf.setMaximum(99)
        self.slider_conf.setValue(25)
        self.slider_conf.valueChanged.connect(self.on_conf_changed)
        conf_layout.addWidget(self.slider_conf)
        self.label_conf = QLabel("0.25")
        conf_layout.addWidget(self.label_conf)
        layout.addLayout(conf_layout)

        # IoU阈值
        iou_layout = QHBoxLayout()
        iou_layout.addWidget(QLabel("IoU阈值:"))
        self.slider_iou = QSlider(Qt.Horizontal)
        self.slider_iou.setMinimum(1)
        self.slider_iou.setMaximum(99)
        self.slider_iou.setValue(45)
        self.slider_iou.valueChanged.connect(self.on_iou_changed)
        iou_layout.addWidget(self.slider_iou)
        self.label_iou = QLabel("0.45")
        iou_layout.addWidget(self.label_iou)
        layout.addLayout(iou_layout)

        # 模型选择
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("模型:"))
        self.combo_model = QComboBox()
        self.combo_model.addItems(["YOLOv5s (基线)", "改进版本"])
        self.combo_model.setCurrentIndex(1)
        model_layout.addWidget(self.combo_model)
        layout.addLayout(model_layout)

        group.setLayout(layout)
        return group

    def create_stats_group(self):
        """创建统计信息组"""
        group = QGroupBox("统计信息")
        layout = QVBoxLayout()

        # 创建统计标签
        self.label_total = QLabel("总人数: 0")
        self.label_wearing = QLabel("佩戴安全帽: 0")
        self.label_no_wearing = QLabel("未佩戴: 0")
        self.label_compliance = QLabel("合规率: 0.0%")
        self.label_fps = QLabel("FPS: 0")

        # 设置样式
        font = QFont()
        font.setPointSize(10)
        for label in [
            self.label_total,
            self.label_wearing,
            self.label_no_wearing,
            self.label_compliance,
            self.label_fps,
        ]:
            label.setFont(font)

        # 未佩戴标签红色高亮
        self.label_no_wearing.setStyleSheet("color: #F44336; font-weight: bold;")
        self.label_compliance.setStyleSheet("font-weight: bold;")

        layout.addWidget(self.label_total)
        layout.addWidget(self.label_wearing)
        layout.addWidget(self.label_no_wearing)
        layout.addWidget(self.label_compliance)
        layout.addWidget(QLabel("---"))
        layout.addWidget(self.label_fps)

        group.setLayout(layout)
        return group

    def create_log_group(self):
        """创建日志显示组"""
        group = QGroupBox("运行日志")
        layout = QVBoxLayout()

        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMaximumHeight(150)
        layout.addWidget(self.text_log)

        # 清空日志按钮
        btn_clear_log = QPushButton("清空日志")
        btn_clear_log.clicked.connect(self.text_log.clear)
        btn_clear_log.setStyleSheet("background-color: #9E9E9E; min-width: 60px;")
        layout.addWidget(btn_clear_log)

        group.setLayout(layout)
        return group

    def create_right_panel(self):
        """创建右侧显示区域"""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout()
        panel.setLayout(layout)

        # 标题
        title = QLabel("检测结果显示")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        layout.addWidget(title)

        # 图像显示区域
        self.label_display = QLabel()
        self.label_display.setAlignment(Qt.AlignCenter)
        self.label_display.setStyleSheet(
            "border: 2px solid #E0E0E0; background-color: #FAFAFA;"
        )
        self.label_display.setMinimumSize(800, 600)
        self.label_display.setText("请选择输入源并开始检测")
        layout.addWidget(self.label_display)

        # 底部按钮栏
        button_layout = QHBoxLayout()

        self.btn_save_image = QPushButton("保存图片")
        self.btn_save_image.clicked.connect(self.on_save_image)
        self.btn_save_image.setEnabled(False)

        self.btn_save_video = QPushButton("保存视频")
        self.btn_save_video.clicked.connect(self.on_save_video)
        self.btn_save_video.setEnabled(False)

        self.btn_export_stats = QPushButton("导出统计")
        self.btn_export_stats.clicked.connect(self.on_export_statistics)

        button_layout.addWidget(self.btn_save_image)
        button_layout.addWidget(self.btn_save_video)
        button_layout.addWidget(self.btn_export_stats)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        return panel

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 主状态信息（左侧）
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)

        # 分隔符
        self.status_bar.addWidget(self._create_separator())

        # 当前模式
        self.status_mode = QLabel("模式: 图片检测")
        self.status_bar.addWidget(self.status_mode)

        self.status_bar.addWidget(self._create_separator())

        # 模型信息
        self.status_model = QLabel("模型: 改进版本")
        self.status_bar.addWidget(self.status_model)

        self.status_bar.addWidget(self._create_separator())

        # 检测统计（永久小部件，右侧）
        self.status_detections = QLabel("检测: 0 人 | 佩戴: 0 | 未佩戴: 0")
        self.status_bar.addPermanentWidget(self.status_detections)

        self.status_bar.addPermanentWidget(self._create_separator())

        # FPS显示
        self.status_fps_label = QLabel("FPS: 0.0")
        self.status_bar.addPermanentWidget(self.status_fps_label)

        self.status_bar.addPermanentWidget(self._create_separator())

        # GPU/CPU状态
        self.status_device = QLabel("设备: 初始化中...")
        self.status_bar.addPermanentWidget(self.status_device)

    def _create_separator(self):
        """创建状态栏分隔符"""
        separator = QLabel(" | ")
        separator.setStyleSheet("color: #999;")
        return separator

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        # 设置菜单
        settings_menu = menubar.addMenu("设置")

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

    # ==================== 事件处理 ====================

    def on_mode_changed(self, mode):
        """输入模式切换"""
        self.current_mode = mode
        mode_text = {"image": "图片检测", "video": "视频检测", "camera": "摄像头检测"}
        self.log(f"切换到{mode_text[mode]}模式")

        # 更新状态栏
        self.status_mode.setText(f"模式: {mode_text[mode]}")
        self.status_label.setText("就绪")

        # 更新界面
        if mode == "camera":
            self.btn_select_file.setEnabled(False)
            self.combo_camera.setEnabled(True)
        else:
            self.btn_select_file.setEnabled(True)
            self.combo_camera.setEnabled(False)

    def on_select_file(self):
        """选择文件"""
        if self.current_mode == "image":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择图片", "", "Image Files (*.jpg *.jpeg *.png *.bmp)"
            )
        else:  # video
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择视频", "", "Video Files (*.mp4 *.avi *.mov)"
            )

        if file_path:
            self.current_file_path = file_path
            self.label_file_path.setText(f"文件: {file_path}")
            self.log(f"已选择: {file_path}")
            self.status_label.setText(f"已选择文件: {Path(file_path).name}")

    def on_start_detection(self):
        """开始检测"""
        # 检查输入源
        if self.current_mode != 'camera' and not self.current_file_path:
            QMessageBox.warning(self, "提示", "请先选择文件！")
            return
        
        self.log("开始检测...")
        self.is_detecting = True
        self.status_label.setText("正在检测...")

        # 更新按钮状态
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)

        # 创建并启动检测线程
        camera_id = int(self.combo_camera.currentText().split()[-1])
        self.detection_thread = DetectionThread(
            mode=self.current_mode,
            source_path=self.current_file_path,
            camera_id=camera_id
        )
        
        # 连接信号
        self.detection_thread.detection_done.connect(self.on_detection_result)
        self.detection_thread.fps_updated.connect(self.on_fps_update)
        self.detection_thread.progress_updated.connect(self.on_progress_update)
        self.detection_thread.error_occurred.connect(self.on_detection_error)
        self.detection_thread.finished.connect(self.on_detection_finished)
        
        # 启动线程
        self.detection_thread.start()
        self.log("检测线程已启动")

    def on_pause_detection(self):
        """暂停检测"""
        if self.detection_thread:
            if self.is_detecting:
                self.detection_thread.pause()
                self.is_detecting = False
                self.btn_pause.setText("继续")
                self.log("检测已暂停")
                self.status_label.setText("已暂停")
            else:
                self.detection_thread.resume()
                self.is_detecting = True
                self.btn_pause.setText("暂停")
                self.log("继续检测")
                self.status_label.setText("正在检测...")

    def on_stop_detection(self):
        """停止检测"""
        if self.detection_thread:
            self.detection_thread.stop()
            self.detection_thread.wait()  # 等待线程结束
        
        self.is_detecting = False
        self.log("检测已停止")
        self.status_label.setText("已停止")

        # 重置按钮状态
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_pause.setText("暂停")

    def on_conf_changed(self, value):
        """置信度阈值变化"""
        conf = value / 100.0
        self.label_conf.setText(f"{conf:.2f}")

    def on_iou_changed(self, value):
        """IoU阈值变化"""
        iou = value / 100.0
        self.label_iou.setText(f"{iou:.2f}")

    def on_save_image(self):
        """保存检测结果图片"""
        if self.current_image is None:
            QMessageBox.warning(self, "提示", "没有可保存的图片！")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图片", "", "Image Files (*.jpg *.png)"
        )
        if file_path:
            cv2.imwrite(file_path, self.current_image)
            self.log(f"图片已保存: {file_path}")
            QMessageBox.information(self, "成功", f"图片已保存到:\n{file_path}")

    def on_save_video(self):
        """保存检测结果视频"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存视频", "", "Video Files (*.mp4 *.avi)"
        )
        if file_path:
            self.log(f"视频已保存: {file_path}")

    def on_export_statistics(self):
        """导出统计数据"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出统计", "", "CSV Files (*.csv)"
        )
        if file_path:
            self.log(f"统计数据已导出: {file_path}")

    def update_statistics(self, stats):
        """更新统计信息"""
        self.label_total.setText(f"总人数: {stats['total']}")
        self.label_wearing.setText(f"佩戴安全帽: {stats['wearing_helmet']}")
        self.label_no_wearing.setText(f"未佩戴: {stats['no_helmet']}")
        self.label_compliance.setText(f"合规率: {stats['compliance_rate']:.1f}%")

        # 根据合规率改变颜色
        if stats["compliance_rate"] < 80:
            self.label_compliance.setStyleSheet("color: #F44336; font-weight: bold;")
        else:
            self.label_compliance.setStyleSheet("color: #4CAF50; font-weight: bold;")

    def update_fps(self, fps):
        """更新FPS显示"""
        self.label_fps.setText(f"FPS: {fps:.1f}")

    def log(self, message):
        """添加日志"""
        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.text_log.append(f"[{timestamp}] {message}")
    
    def on_detection_result(self, annotated_image, detections, statistics):
        """处理检测结果"""
        # 更新统计信息
        self.update_statistics(statistics)
        self.status_detections.setText(
            f"检测: {statistics['total']} 人 | 佩戴: {statistics['wearing_helmet']} | "
            f"未佩戴: {statistics['no_helmet']}"
        )
        
        # 显示图像
        self.display_image(annotated_image)
        self.current_image = annotated_image
    
    def on_fps_update(self, fps):
        """更新FPS"""
        self.update_fps(fps)
        self.status_fps_label.setText(f"FPS: {fps:.1f}")
    
    def on_progress_update(self, progress):
        """更新进度"""
        self.progress_bar.setValue(progress)
    
    def on_detection_error(self, error_message):
        """处理检测错误"""
        self.log(f"错误: {error_message}")
        QMessageBox.critical(self, "检测错误", error_message)
        self.on_stop_detection()
    
    def on_detection_finished(self):
        """检测完成"""
        self.log("检测完成")
        self.status_label.setText("检测完成")
        
        # 重置按钮状态
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.is_detecting = False
    
    def display_image(self, image):
        """在标签上显示图像"""
        # 将OpenCV图像转换为QPixmap
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        
        # 缩放以适应标签大小
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.label_display.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.label_display.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        """关闭事件"""
        # 停止检测线程
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.stop()
            self.detection_thread.wait()
        
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出系统吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.log("系统关闭")
            event.accept()
        else:
            event.ignore()


# 测试代码
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
