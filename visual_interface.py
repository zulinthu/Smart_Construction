# -*- coding: utf-8 -*-
# @Time    : 2021/3/6 15:36
# @Author  : PeterH
# @Email   : peterhuang0323@outlook.com
# @File    : visual_interface.py
# @Software: PyCharm
# @Brief   :

# 解决 exe 打包 Can't get source for 的问题 start ======
# https://github.com/pytorch/vision/issues/1899#issuecomment-598200938
import torch.jit


def script_method(fn, _rcb=None):
    return fn


def script(obj, optimize=True, _frames_up=0, _rcb=None):
    return obj


torch.jit.script_method = script_method
torch.jit.script = script
# 解决 exe 打包 Can't get source for 的问题 end ======

import os
import time
import sys
from pathlib import Path
import cv2
from GPUtil import GPUtil
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, pyqtSlot, QTimer, QDateTime, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QSizePolicy
from PyQt5.QtGui import QColor, QBrush, QIcon, QPixmap
from PyQt5.QtChart import QDateTimeAxis, QValueAxis, QSplineSeries, QChart
import torch
from UI.main_window import Ui_MainWindow
from detect_visual import YOLOPredict

CODE_VER = "V2.0"
PREDICT_SHOW_TAB_INDEX = 0
REAL_TIME_PREDICT_TAB_INDEX = 1

# Avoid importing legacy top-level `utils` package here.
# It conflicts with torch.hub yolov5 runtime imports.
IMG_FORMATS = {".bmp", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".dng", ".webp", ".mpo"}


def get_gpu_info():
    """
    获取 GPU 信息
    :return:
    """

    gpu_list = []
    # GPUtil.showUtilization()

    # 获取多个GPU的信息，存在列表里
    for gpu in GPUtil.getGPUs():
        # print('gpu.id:', gpu.id)
        # print('GPU总量：', gpu.memoryTotal)
        # print('GPU使用量：', gpu.memoryUsed)
        # print('gpu使用占比:', gpu.memoryUtil * 100)  # 内存使用率
        # print('gpu load:', gpu.load * 100)  # 使用率
        # 按GPU逐个添加信息
        gpu_list.append({"gpu_id": gpu.id,
                         "gpu_memoryTotal": gpu.memoryTotal,
                         "gpu_memoryUsed": gpu.memoryUsed,
                         "gpu_memoryUtil": gpu.memoryUtil * 100,
                         "gpu_load": gpu.load * 100})

    return gpu_list


class PredictDataHandlerThread(QThread):
    """
    打印信息的线程
    """
    predict_message_trigger = pyqtSignal(str)

    def __init__(self, predict_model):
        super(PredictDataHandlerThread, self).__init__()
        self.running = False
        self.predict_model = predict_model

    def __del__(self):
        self.running = False
        # self.destroyed()

    def run(self):
        self.running = True
        over_time = 0
        while self.running:
            if self.predict_model.predict_info != "":
                self.predict_message_trigger.emit(self.predict_model.predict_info)
                self.predict_model.predict_info = ""
                over_time = 0
            time.sleep(0.01)
            over_time += 1

            if over_time > 100000:
                self.running = False


class PredictHandlerThread(QThread):
    """
    进行模型推理的线程
    """

    preview_frame_trigger = pyqtSignal(object, object)
    result_ready_trigger = pyqtSignal(str, str, bool)

    def __init__(self, input_player, output_player, out_file_path, weight_path,
                 predict_info_plain_text_edit, predict_progress_bar, fps_label,
                 button_dict, input_tab, output_tab, input_image_label, output_image_label,
                 real_time_show_predict_flag):
        super(PredictHandlerThread, self).__init__()
        self.running = False

        '''加载模型'''
        self.predict_model = YOLOPredict(weight_path, out_file_path)
        self.output_predict_file = ""
        self.parameter_source = ''

        # 传入的QT插件
        self.input_player = input_player
        self.output_player = output_player
        self.predict_info_plainTextEdit = predict_info_plain_text_edit
        self.predict_progressBar = predict_progress_bar
        self.fps_label = fps_label
        self.button_dict = button_dict
        self.input_tab = input_tab
        self.output_tab = output_tab
        self.input_image_label = input_image_label
        self.output_image_label = output_image_label

        # 是否实时显示推理图片
        self.real_time_show_predict_flag = real_time_show_predict_flag

        # 创建显示进程
        self.predict_data_handler_thread = PredictDataHandlerThread(self.predict_model)
        self.predict_data_handler_thread.predict_message_trigger.connect(self.add_messages)
        self.preview_emit_interval = 1.0 / 20.0
        self._last_preview_emit_ts = 0.0
        self.pause_requested = False

    def __del__(self):
        self.running = False
        # self.destroyed()

    def run(self):
        self.running = True
        self.pause_requested = False
        self.output_predict_file = ""
        if not self.predict_data_handler_thread.isRunning():
            self.predict_data_handler_thread.start()

        image_flag = os.path.splitext(self.parameter_source)[-1].lower() in IMG_FORMATS
        frame_callback = self._emit_preview if (not image_flag and self.real_time_show_predict_flag) else None

        try:
            with torch.no_grad():
                self.output_predict_file = self.predict_model.detect(
                    self.parameter_source,
                    frame_callback=frame_callback,
                    should_pause=self._should_pause,
                )
        except Exception as e:
            self.output_predict_file = ""
            self.predict_model.predict_info = f"ERROR {type(e).__name__}: {e}"
        finally:
            self.running = False

        if self.output_predict_file != "" and Path(self.output_predict_file).exists():
            self.result_ready_trigger.emit(self.parameter_source, self.output_predict_file, image_flag)
        else:
            if not str(self.predict_model.predict_info).startswith("ERROR"):
                self.predict_model.predict_info = "ERROR Inference failed or output file is empty."
        self.predict_data_handler_thread.running = False

    def _emit_preview(self, frame, annotated):
        now = time.time()
        if now - self._last_preview_emit_ts < self.preview_emit_interval:
            return
        self._last_preview_emit_ts = now
        self.preview_frame_trigger.emit(frame, annotated)

    def _should_pause(self):
        return self.pause_requested and self.running

    @pyqtSlot(str)
    def add_messages(self, message):
        if message != "":
            self.predict_info_plainTextEdit.appendPlainText(message)

            split_message = message.split(" ")

            # 设置进度条
            if "video [" in message:
                try:
                    percent = split_message[1][1:-1].split("/")  # 提取帧序号
                    value = int((int(percent[0]) / int(percent[1])) * 100)
                    value = value if (int(percent[1]) - int(percent[0])) > 2 else 100
                    self.predict_progressBar.setValue(value)
                except Exception:
                    pass
            elif "image Done." in message:
                self.predict_progressBar.setValue(100)

            # 设置 FPS
            if message.endswith("s)") and "(" in message:
                try:
                    second_count = 1 / float(split_message[-1][1:-2])
                    self.fps_label.setText(f"--> {second_count:.1f} FPS")
                except Exception:
                    pass


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, weight_path, out_file_path, real_time_show_predict_flag: bool, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Intelligent Monitoring System of Construction Site Software")
        self.showMaximized()
        if hasattr(self, "author_label"):
            self.author_label.hide()
            self.author_label.setMaximumHeight(0)

        '''按键绑定'''
        # 输入媒体
        self.import_media_pushButton.clicked.connect(self.import_media)  # 导入
        self.start_predict_pushButton.clicked.connect(self.predict_button_click)  # 开始推理
        # 输出媒体
        self.open_predict_file_pushButton.clicked.connect(self.open_file_in_browser)  # 文件中显示推理视频
        # 下方
        self.pause_pushButton.clicked.connect(self.pause_resume_button_click)  # Pause/Resume
        self.button_dict = dict()
        self.button_dict.update({"import_media_pushButton": self.import_media_pushButton,
                                 "start_predict_pushButton": self.start_predict_pushButton,
                                 "open_predict_file_pushButton": self.open_predict_file_pushButton,
                                 "pause_pushButton": self.pause_pushButton,
                                 "real_time_checkBox": self.real_time_checkBox
                                 })

        '''媒体流绑定输出'''
        self.input_player = QMediaPlayer()  # 媒体输入的widget
        self.input_player.setVideoOutput(self.input_video_widget)
        self.input_player.positionChanged.connect(self.change_slide_bar)  # 播放进度条

        self.output_player = QMediaPlayer()  # 媒体输出的widget
        self.output_player.setVideoOutput(self.output_video_widget)

        '''初始化GPU chart'''
        self.series = QSplineSeries()
        self.chart_init()

        '''初始化GPU定时查询定时器'''
        # 使用QTimer，0.5秒触发一次，更新数据
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.draw_gpu_info_chart)
        self.timer.start(1000)

        # 播放时长, 以 input 的时长为准
        self.video_length = 0
        self.out_file_path = out_file_path
        # 推理使用另外一线程
        self.predict_handler_thread = PredictHandlerThread(self.input_player,
                                                           self.output_player,
                                                           self.out_file_path,
                                                           weight_path,
                                                           self.predict_info_plainTextEdit,
                                                           self.predict_progressBar,
                                                           self.fps_label,
                                                           self.button_dict,
                                                           self.input_media_tabWidget,
                                                           self.output_media_tabWidget,
                                                           self.input_real_time_label,
                                                           self.output_real_time_label,
                                                           real_time_show_predict_flag
                                                           )
        self.predict_handler_thread.preview_frame_trigger.connect(self.on_preview_frame)
        self.predict_handler_thread.result_ready_trigger.connect(self.on_predict_result_ready)
        self.predict_handler_thread.finished.connect(self.on_predict_thread_finished)
        self.weight_label.setText(f" Using weight : ****** {Path(weight_path[0]).name} ******")
        # 界面美化
        self.gen_better_gui()

        self.media_source = ""  # 推理媒体的路径

        self.predict_progressBar.setValue(0)  # 进度条归零

        '''check box 绑定'''
        self.real_time_checkBox.stateChanged.connect(self.real_time_checkbox_state_changed)
        self.real_time_checkBox.setChecked(real_time_show_predict_flag)
        self.real_time_check_state = self.real_time_checkBox.isChecked()
        self._last_preview_render_ts = 0.0
        self.preview_render_interval = 1.0 / 20.0

        # Model selector button (runtime switchable .pt weights)
        self.select_model_pushButton = QPushButton("Select Model")
        self.select_model_pushButton.setMinimumSize(0, 25)
        self.select_model_pushButton.setStyleSheet(self.import_media_pushButton.styleSheet())
        self.select_model_pushButton.clicked.connect(self.select_model)
        self.horizontalLayout_13.insertWidget(0, self.select_model_pushButton)
        self.button_dict.update({"select_model_pushButton": self.select_model_pushButton})

    def gen_better_gui(self):
        """
        美化界面
        :return:
        """
        # Keep a single Pause/Resume button for detection control.
        self.play_pushButton.hide()
        self.play_pushButton.setEnabled(False)

        # Pause button
        play_icon = QIcon()
        play_icon.addPixmap(QPixmap("./UI/icon/pause.png"), QIcon.Normal, QIcon.Off)
        self.pause_pushButton.setIcon(play_icon)
        self.pause_pushButton.setText("Pause")

        # 隐藏 tab 标题栏
        self.input_media_tabWidget.tabBar().hide()
        self.output_media_tabWidget.tabBar().hide()
        # tab 设置显示第一栏
        self.input_media_tabWidget.setCurrentIndex(PREDICT_SHOW_TAB_INDEX)
        self.output_media_tabWidget.setCurrentIndex(PREDICT_SHOW_TAB_INDEX)

        # 设置显示图片的 label 为黑色背景
        self.input_real_time_label.setStyleSheet("QLabel{background:black}")
        self.output_real_time_label.setStyleSheet("QLabel{background:black}")
        self.input_real_time_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.output_real_time_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

    def real_time_checkbox_state_changed(self):
        """
        切换是否实时显示推理图片
        :return:
        """
        self.real_time_check_state = self.real_time_checkBox.isChecked()
        self.predict_handler_thread.real_time_show_predict_flag = self.real_time_check_state

    def select_model(self):
        if self.predict_handler_thread.isRunning():
            self.predict_info_plainTextEdit.appendPlainText(
                "INFO Inference is running. Please wait before switching model."
            )
            return

        selected_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select model file",
            str(Path.home()),
            "PyTorch Model (*.pt);;All Files (*.*)",
        )
        if not selected_file:
            return

        model_path = Path(selected_file).resolve()
        if not model_path.exists():
            self.predict_info_plainTextEdit.appendPlainText(f"ERROR Model file not found: {model_path}")
            return

        self.predict_handler_thread.predict_model.weights = [str(model_path)]
        self.weight_label.setText(f" Using weight : ****** {model_path.name} ******")
        self.predict_info_plainTextEdit.appendPlainText(f"Model switched: {model_path}")


    def _set_buttons_after_predict(self, image_flag: bool, has_output: bool):
        for item, button in self.button_dict.items():
            if item == "pause_pushButton":
                button.setEnabled(False)
                button.setText("Pause")
                continue
            if item == "open_predict_file_pushButton":
                button.setEnabled(has_output)
                continue
            button.setEnabled(True)

    @pyqtSlot(object, object)
    def on_preview_frame(self, frame, annotated):
        # Ensure all widget updates happen on UI thread.
        now = time.time()
        if now - self._last_preview_render_ts < self.preview_render_interval:
            return
        self._last_preview_render_ts = now
        if self.input_media_tabWidget.currentIndex() != REAL_TIME_PREDICT_TAB_INDEX:
            self.input_media_tabWidget.setCurrentIndex(REAL_TIME_PREDICT_TAB_INDEX)
        if self.output_media_tabWidget.currentIndex() != REAL_TIME_PREDICT_TAB_INDEX:
            self.output_media_tabWidget.setCurrentIndex(REAL_TIME_PREDICT_TAB_INDEX)
        YOLOPredict.show_real_time_image(self.input_real_time_label, frame)
        YOLOPredict.show_real_time_image(self.output_real_time_label, annotated)

    @pyqtSlot(str, str, bool)
    def on_predict_result_ready(self, source_path: str, output_path: str, image_flag: bool):
        self.input_player.setMedia(QMediaContent(QUrl.fromLocalFile(source_path)))
        self.input_player.pause()
        self.output_player.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
        self.output_player.pause()
        self.input_media_tabWidget.setCurrentIndex(PREDICT_SHOW_TAB_INDEX)
        self.output_media_tabWidget.setCurrentIndex(PREDICT_SHOW_TAB_INDEX)
        self._set_buttons_after_predict(image_flag, True)

    @pyqtSlot()
    def on_predict_thread_finished(self):
        source = self.predict_handler_thread.parameter_source
        image_flag = os.path.splitext(source)[-1].lower() in IMG_FORMATS if source else True
        has_output = bool(
            self.predict_handler_thread.output_predict_file
            and Path(self.predict_handler_thread.output_predict_file).exists()
        )
        if not has_output:
            self._set_buttons_after_predict(image_flag, False)

    def chart_init(self):
        """
        初始化 GPU 折线图
        :return:
        """
        # self.gpu_info_chart._chart = QChart(title="折线图堆叠")  # 创建折线视图
        self.gpu_info_chart._chart = QChart()  # 创建折线视图
        # chart._chart.setBackgroundVisible(visible=False)      # 背景色透明
        self.gpu_info_chart._chart.setBackgroundBrush(QBrush(QColor("#FFFFFF")))  # 改变图背景色

        # 设置曲线名称
        self.series.setName("GPU Utilization")
        # 把曲线添加到QChart的实例中
        self.gpu_info_chart._chart.addSeries(self.series)
        # 声明并初始化X轴，Y轴
        self.dtaxisX = QDateTimeAxis()
        self.vlaxisY = QValueAxis()
        # 设置坐标轴显示范围
        self.dtaxisX.setMin(QDateTime.currentDateTime().addSecs(-300 * 1))
        self.dtaxisX.setMax(QDateTime.currentDateTime().addSecs(0))
        self.vlaxisY.setMin(0)
        self.vlaxisY.setMax(100)
        # 设置X轴时间样式
        self.dtaxisX.setFormat("hh:mm:ss")
        # 设置坐标轴上的格点
        self.dtaxisX.setTickCount(5)
        self.vlaxisY.setTickCount(10)
        # 设置坐标轴名称
        self.dtaxisX.setTitleText("Time")
        self.vlaxisY.setTitleText("Percent")
        # 设置网格不显示
        self.vlaxisY.setGridLineVisible(False)
        # 把坐标轴添加到chart中
        self.gpu_info_chart._chart.addAxis(self.dtaxisX, Qt.AlignBottom)
        self.gpu_info_chart._chart.addAxis(self.vlaxisY, Qt.AlignLeft)
        # 把曲线关联到坐标轴
        self.series.attachAxis(self.dtaxisX)
        self.series.attachAxis(self.vlaxisY)
        # 生成 折线图
        self.gpu_info_chart.setChart(self.gpu_info_chart._chart)

    def draw_gpu_info_chart(self):
        """
        绘制 GPU 折线图
        :return:
        """
        # 获取当前时间
        time_current = QDateTime.currentDateTime()
        # 更新X轴坐标
        self.dtaxisX.setMin(QDateTime.currentDateTime().addSecs(-300 * 1))
        self.dtaxisX.setMax(QDateTime.currentDateTime().addSecs(0))
        # 当曲线上的点超出X轴的范围时，移除最早的点
        remove_count = 600
        if self.series.count() > remove_count:
            self.series.removePoints(0, self.series.count() - remove_count)
        # 对 y 赋值
        # yint = random.randint(0, 100)
        gpu_info = get_gpu_info()
        yint = gpu_info[0].get("gpu_load") if gpu_info else 0
        # 添加数据到曲线末端
        self.series.append(time_current.toMSecsSinceEpoch(), yint)

    def import_media(self):
        """
        导入媒体文件
        :return:
        """
        selected_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select media file",
            str(Path.home()),
            "Media Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.m4v *.jpg *.jpeg *.png *.bmp *.webp);;All Files (*.*)",
        )
        if not selected_file:
            return

        is_running = self.predict_handler_thread.isRunning()
        if is_running:
            self.predict_info_plainTextEdit.appendPlainText(
                "INFO Detection is running. New media is loaded for the next run."
            )

        local_path = str(Path(selected_file).resolve())
        if not Path(local_path).exists():
            self.predict_info_plainTextEdit.appendPlainText(f"ERROR File not found: {local_path}")
            return

        self.media_source = local_path
        self.input_player.setMedia(QMediaContent(QUrl.fromLocalFile(local_path)))  # 选取视频文件

        # 设置 output 为一张图片，防止资源被占用
        path_current = Path(__file__).resolve().parent.joinpath("area_dangerous", "1.jpg")
        if path_current.exists():
            self.output_player.setMedia(QMediaContent(QUrl.fromLocalFile(str(path_current))))
        else:
            self.output_player.setMedia(QMediaContent())

        # 将路径传给推理线程
        self.predict_handler_thread.parameter_source = local_path
        self.input_player.pause()  # 显示媒体

        image_flag = os.path.splitext(self.predict_handler_thread.parameter_source)[-1].lower() in IMG_FORMATS
        for item, button in self.button_dict.items():
            if image_flag and item == 'pause_pushButton':
                button.setEnabled(False)
            else:
                button.setEnabled(True)
        self.predict_info_plainTextEdit.appendPlainText(f"Loaded: {local_path}")
        # self.output_player.setMedia(QMediaContent(QFileDialog.getOpenFileUrl()[0]))  # 选取视频文件

    def predict_button_click(self):
        """
        推理按钮
        :return:
        """
        source = self.predict_handler_thread.parameter_source
        if not source:
            self.predict_info_plainTextEdit.appendPlainText("ERROR Please import an image or video first.")
            return
        if not Path(source).exists():
            self.predict_info_plainTextEdit.appendPlainText(f"ERROR File not found: {source}")
            return
        image_flag = os.path.splitext(source)[-1].lower() in IMG_FORMATS
        if not image_flag:
            cap = cv2.VideoCapture(source)
            ok = cap.isOpened()
            cap.release()
            if not ok:
                self.predict_info_plainTextEdit.appendPlainText(
                    "ERROR Cannot read this video. The codec may be unsupported (e.g. H.265/HEVC) or the file is corrupted."
                )
                self.predict_info_plainTextEdit.appendPlainText(
                    "TIP: Transcode to MP4 (H.264/AAC) and import again."
                )
                return
        if self.predict_handler_thread.isRunning():
            self.predict_info_plainTextEdit.appendPlainText("INFO Inference is already running, please wait.")
            return

        self.predict_progressBar.setValue(0)
        self.predict_handler_thread.pause_requested = False
        for item, button in self.button_dict.items():
            if item == "import_media_pushButton":
                button.setEnabled(True)
            elif item == "pause_pushButton" and not image_flag:
                button.setEnabled(True)
                button.setText("Pause")
            else:
                button.setEnabled(False)
        self.predict_info_plainTextEdit.appendPlainText(f"Start: {source}")
        # 启动线程去调用
        self.predict_handler_thread.start()

    def change_slide_bar(self, position):
        """
        进度条移动
        :param position:
        :return:
        """
        self.video_length = self.input_player.duration() + 0.1
        self.video_horizontalSlider.setValue(round((position / self.video_length) * 100))
        self.video_percent_label.setText(str(round((position / self.video_length) * 100, 2)) + '%')

    @pyqtSlot()
    def pause_resume_button_click(self):
        """
        Pause/Resume detection while thread is running.
        :return:
        """
        if self.predict_handler_thread.isRunning():
            if not self.predict_handler_thread.pause_requested:
                self.predict_handler_thread.pause_requested = True
                self.pause_pushButton.setText("Resume")
                self.predict_info_plainTextEdit.appendPlainText("INFO Detection paused.")
            else:
                self.predict_handler_thread.pause_requested = False
                self.pause_pushButton.setText("Pause")
                self.predict_info_plainTextEdit.appendPlainText("INFO Detection resumed.")
            return

        self.predict_info_plainTextEdit.appendPlainText("INFO Detection is not running.")

    @pyqtSlot()
    def open_file_in_browser(self):
        os.system(f'start explorer "{self.out_file_path}"')

    @pyqtSlot()
    def closeEvent(self, *args, **kwargs):
        """
        重写关闭事件
        :param args:
        :param kwargs:
        :return:
        """
        print("Close")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    root_dir = Path(__file__).resolve().parent
    os.chdir(root_dir)
    preferred_weight_files = [
        root_dir.joinpath("weights", "best.pt"),
        root_dir.parent.joinpath("deliverables", "weights", "best.pt"),
        root_dir.parent.joinpath("submission_bundle", "weights", "best.pt"),
        root_dir.joinpath("yolo_full", "models", "weights", "best.pt"),
    ]
    selected_weight = next((p for p in preferred_weight_files if p.exists()), None)

    if selected_weight is None:
        preferred_weight_dirs = [
            root_dir.joinpath("weights"),
            root_dir.joinpath("yolo_full", "models", "weights"),
        ]
        weight_file = []
        for weight_dir in preferred_weight_dirs:
            if weight_dir.exists():
                weight_file = [item for item in weight_dir.iterdir() if item.suffix == ".pt"]
                if weight_file:
                    break
        if not weight_file:
            raise FileNotFoundError(
                "No .pt weights found in ./weights, ../deliverables/weights, "
                "../submission_bundle/weights, or ./yolo_full/models/weights"
            )
        selected_weight = weight_file[0]

    weight_root = [str(selected_weight)]  # 权重文件位置
    out_file_root = root_dir.joinpath(r'inference/output')
    out_file_root.parent.mkdir(exist_ok=True)
    out_file_root.mkdir(exist_ok=True)

    real_time_show_predict = True  # 是否实时显示推理图片，有可能导致卡顿，软件卡死

    main_window = MainWindow(weight_root, out_file_root, real_time_show_predict)

    # 设置窗口图标
    icon = QIcon()
    icon.addPixmap(QPixmap("./UI/icon/icon.ico"), QIcon.Normal, QIcon.Off)
    main_window.setWindowIcon(icon)

    main_window.show()
    sys.exit(app.exec_())
