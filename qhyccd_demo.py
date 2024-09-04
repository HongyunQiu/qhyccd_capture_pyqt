def connect_camera(self):
    if self.handle is None:
        print("开始连接相机...")
        
        print("初始化 QHYCCD 资源...")
        ret = InitQHYCCDResource()
        if ret == QHYCCD_SUCCESS:
            print("QHYCCD 资源初始化成功")
        else:
            print(f"QHYCCD 资源初始化失败，错误码: {ret}")
            return
        
        print("扫描相机...")
        num_cameras = ScanQHYCCD()
        print(f"找到 {num_cameras} 个相机")
        
        if num_cameras > 0:
            print("尝试打开第一个相机...")
            camera_id = ctypes.create_string_buffer(32)
            ret = GetQHYCCDId(ctypes.c_int(0), camera_id)
            if ret == QHYCCD_SUCCESS:
                print(f"相机ID: {camera_id.value.decode()}")
                self.handle = OpenQHYCCD(camera_id)
                if self.handle:
                    print("相机成功打开")
                    
                    print("设置流模式...")
                    ret = SetQHYCCDStreamMode(self.handle, 0)  # 单帧模式
                    if ret == QHYCCD_SUCCESS:
                        print("流模式设置成功")
                    else:
                        print(f"流模式设置失败，错误码: {ret}")
                    
                    print("初始化相机...")
                    ret = InitQHYCCD(self.handle)
                    if ret == QHYCCD_SUCCESS:
                        print("相机初始化成功")
                        self.status_label.setText('相机已连接')
                    else:
                        print(f"相机初始化失败，错误码: {ret}")
                        self.status_label.setText('相机初始化失败')
                else:
                    print(f"无法打开相机，错误码: {ctypes.get_last_error()}")
                    self.status_label.setText('无法打开相机')
            else:
                print(f"获取相机ID失败，错误码: {ret}")
                self.status_label.setText('获取相机ID失败')
        else:
            print("未找到相机")
            self.status_label.setText('未找到相机')
    else:
        print("相机已经连接")
        self.status_label.setText('相机已经连接')

import sys
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PIL import Image
import numpy as np

# 加载 DLL
try:
    qhyccd = ctypes.CDLL("./qhyccd.dll")
    print("成功加载 qhyccd.dll")
except Exception as e:
    print(f"加载 qhyccd.dll 失败: {e}")
    sys.exit(1)

# 定义一些常量和结构体
QHYCCD_SUCCESS = 0
QHYCCD_ERROR = 0xFFFFFFFF

class QHYCCD_HANDLE(ctypes.Structure):
    pass

PQHYCCD_HANDLE = ctypes.POINTER(QHYCCD_HANDLE)

# 定义函数原型
InitQHYCCDResource = qhyccd.InitQHYCCDResource
InitQHYCCDResource.restype = ctypes.c_uint32

ScanQHYCCD = qhyccd.ScanQHYCCD
ScanQHYCCD.restype = ctypes.c_uint32

OpenQHYCCD = qhyccd.OpenQHYCCD
OpenQHYCCD.argtypes = [ctypes.c_char_p]
OpenQHYCCD.restype = PQHYCCD_HANDLE

SetQHYCCDStreamMode = qhyccd.SetQHYCCDStreamMode
SetQHYCCDStreamMode.argtypes = [PQHYCCD_HANDLE, ctypes.c_uint8]
SetQHYCCDStreamMode.restype = ctypes.c_uint32

InitQHYCCD = qhyccd.InitQHYCCD
InitQHYCCD.argtypes = [PQHYCCD_HANDLE]
InitQHYCCD.restype = ctypes.c_uint32

SetQHYCCDParam = qhyccd.SetQHYCCDParam
SetQHYCCDParam.argtypes = [PQHYCCD_HANDLE, ctypes.c_int, ctypes.c_double]
SetQHYCCDParam.restype = ctypes.c_uint32

ExpQHYCCDSingleFrame = qhyccd.ExpQHYCCDSingleFrame
ExpQHYCCDSingleFrame.argtypes = [PQHYCCD_HANDLE]
ExpQHYCCDSingleFrame.restype = ctypes.c_uint32

GetQHYCCDSingleFrame = qhyccd.GetQHYCCDSingleFrame
GetQHYCCDSingleFrame.argtypes = [PQHYCCD_HANDLE, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), 
                                 ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), 
                                 ctypes.POINTER(ctypes.c_uint8)]
GetQHYCCDSingleFrame.restype = ctypes.c_uint32

GetQHYCCDMemLength = qhyccd.GetQHYCCDMemLength
GetQHYCCDMemLength.argtypes = [PQHYCCD_HANDLE]
GetQHYCCDMemLength.restype = ctypes.c_uint32

CloseQHYCCD = qhyccd.CloseQHYCCD
CloseQHYCCD.argtypes = [PQHYCCD_HANDLE]
CloseQHYCCD.restype = ctypes.c_uint32

ReleaseQHYCCDResource = qhyccd.ReleaseQHYCCDResource
ReleaseQHYCCDResource.restype = ctypes.c_uint32

GetQHYCCDId = qhyccd.GetQHYCCDId
GetQHYCCDId.argtypes = [ctypes.c_int, ctypes.c_char_p]
GetQHYCCDId.restype = ctypes.c_uint32

class QHYCCDDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.handle = None

    def initUI(self):
        self.setWindowTitle('QHYCCD Demo')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.status_label = QLabel('未连接相机')
        layout.addWidget(self.status_label)

        connect_button = QPushButton('连接相机')
        connect_button.clicked.connect(self.connect_camera)
        layout.addWidget(connect_button)

        capture_button = QPushButton('拍摄图像')
        capture_button.clicked.connect(self.capture_image)
        layout.addWidget(capture_button)

        self.image_label = QLabel()
        layout.addWidget(self.image_label)

        central_widget.setLayout(layout)

    def connect_camera(self):
        if self.handle is None:
            print("开始连接相机...")
            
            print("初始化 QHYCCD 资源...")
            ret = InitQHYCCDResource()
            if ret == QHYCCD_SUCCESS:
                print("QHYCCD 资源初始化成功")
            else:
                print(f"QHYCCD 资源初始化失败，错误码: {ret}")
                return
            
            print("扫描相机...")
            num_cameras = ScanQHYCCD()
            print(f"找到 {num_cameras} 个相机")
            
            if num_cameras > 0:
                print("尝试打开第一个相机...")
                camera_id = ctypes.create_string_buffer(32)
                ret = GetQHYCCDId(ctypes.c_int(0), camera_id)
                if ret == QHYCCD_SUCCESS:
                    print(f"相机ID: {camera_id.value.decode()}")
                    self.handle = OpenQHYCCD(camera_id)
                    if self.handle:
                        print("相机成功打开")
                        
                        print("设置流模式...")
                        ret = SetQHYCCDStreamMode(self.handle, 0)  # 单帧模式
                        if ret == QHYCCD_SUCCESS:
                            print("流模式设置成功")
                        else:
                            print(f"流模式设置失败，错误码: {ret}")
                        
                        print("初始化相机...")
                        ret = InitQHYCCD(self.handle)
                        if ret == QHYCCD_SUCCESS:
                            print("相机初始化成功")
                            self.status_label.setText('相机已连接')
                        else:
                            print(f"相机初始化失败，错误码: {ret}")
                            self.status_label.setText('相机初始化失败')
                    else:
                        print(f"无法打开相机，错误码: {ctypes.get_last_error()}")
                        self.status_label.setText('无法打开相机')
                else:
                    print(f"获取相机ID失败，错误码: {ret}")
                    self.status_label.setText('获取相机ID失败')
            else:
                print("未找到相机")
                self.status_label.setText('未找到相机')
        else:
            print("相机已经连接")
            self.status_label.setText('相机已经连接')

    def capture_image(self):
        if self.handle:
            print("开始拍摄图像...")
            try:
                # 设置曝光时间为1秒
                ret = SetQHYCCDParam(self.handle, ctypes.c_int(8), ctypes.c_double(1000000))
                if ret != QHYCCD_SUCCESS:
                    print(f"设置曝光时间失败，错误码: {ret}")
                    return

                # 开始曝光
                ret = ExpQHYCCDSingleFrame(self.handle)
                if ret != QHYCCD_SUCCESS:
                    print(f"开始曝光失败，错误码: {ret}")
                    return

                # 获取所需的内存大小
                mem_length = GetQHYCCDMemLength(self.handle)
                if mem_length == 0:
                    print("获取内存大小失败")
                    return

                print(f"图像所需内存大小: {mem_length} 字节")

                # 分配内存
                buffer = (ctypes.c_uint8 * mem_length)()

                w = ctypes.c_uint32()
                h = ctypes.c_uint32()
                bpp = ctypes.c_uint32()
                channels = ctypes.c_uint32()

                # 获取图像数据
                ret = GetQHYCCDSingleFrame(self.handle, ctypes.byref(w), ctypes.byref(h), ctypes.byref(bpp),
                                           ctypes.byref(channels), buffer)

                if ret == QHYCCD_SUCCESS:
                    print(f'图像已拍摄: {w.value}x{h.value}, {bpp.value}位, {channels.value}通道')
                    self.status_label.setText(f'图像已拍摄: {w.value}x{h.value}')
                    
                    # 使用返回的图像尺寸
                    width = w.value
                    height = h.value
                    bytes_per_pixel = bpp.value // 8
                    
                    print(f"图像尺寸: {width}x{height}")
                    print(f"每像素字节数: {bytes_per_pixel}")
                    
                    # 将图像数据转换为numpy数组
                    image_data = np.frombuffer(buffer, dtype=np.uint16 if bpp.value > 8 else np.uint8)
                    image_data = image_data[:width * height * bytes_per_pixel].reshape(width, height, -1)
                    
                    print(f"图像数据形状: {image_data.shape}")
                    
                    # 如果是16位图像，需要进行转换
                    if bpp.value == 16:
                        image_data = (image_data / 256).astype(np.uint8)
                    
                    # 如果是单通道图像，去掉多余的维度
                    if channels.value == 1:
                        image_data = image_data.squeeze()
                    
                    # 创建QImage并显示
                    if channels.value == 1:
                        qimage = QImage(image_data.data, width, height, width, QImage.Format_Grayscale8)
                    else:
                        qimage = QImage(image_data.data, width, height, width * 3, QImage.Format_RGB888)
                    
                    pixmap = QPixmap.fromImage(qimage)
                    
                    # 调整图像控件大小以适应图像
                    self.image_label.setPixmap(pixmap)
                    self.image_label.setScaledContents(True)
                    self.resize_window_to_fit_image(pixmap.size())
                else:
                    print(f'拍摄失败，错误码: {ret}')
                    self.status_label.setText('拍摄失败')

            except Exception as e:
                print(f"拍摄过程中发生错误: {e}")
                self.status_label.setText('拍摄过程中发生错误')

        else:
            print("相机未连接")
            self.status_label.setText('请先连接相机')

    def resize_window_to_fit_image(self, image_size):
        # 获取屏幕大小
        screen = QApplication.primaryScreen().geometry()
        
        # 计算新的窗口大小，确保不超过屏幕大小的80%
        new_width = min(image_size.width() + 40, screen.width() * 0.8)
        new_height = min(image_size.height() + 100, screen.height() * 0.8)
        
        # 调整窗口大小
        self.resize(new_width, new_height)
        
        # 将窗口移动到屏幕中央
        self.move(screen.center() - self.rect().center())

    def closeEvent(self, event):
        if self.handle:
            print("关闭相机连接...")
            CloseQHYCCD(self.handle)
        print("释放 QHYCCD 资源...")
        ReleaseQHYCCDResource()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = QHYCCDDemo()
    demo.show()
    sys.exit(app.exec_())
