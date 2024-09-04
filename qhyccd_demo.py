def connect_camera(self):
    if self.handle is None:
        print("Starting camera connection...")
        
        print("Initializing QHYCCD resources...")
        ret = InitQHYCCDResource()
        if ret == QHYCCD_SUCCESS:
            print("QHYCCD resources initialized successfully")
        else:
            print(f"QHYCCD resource initialization failed, error code: {ret}")
            return
        
        print("Scanning for cameras...")
        num_cameras = ScanQHYCCD()
        print(f"Found {num_cameras} cameras")
        
        if num_cameras > 0:
            print("Attempting to open the first camera...")
            camera_id = ctypes.create_string_buffer(32)
            ret = GetQHYCCDId(ctypes.c_int(0), camera_id)
            if ret == QHYCCD_SUCCESS:
                print(f"Camera ID: {camera_id.value.decode()}")
                self.handle = OpenQHYCCD(camera_id)
                if self.handle:
                    print("Camera opened successfully")
                    
                    print("Setting stream mode...")
                    ret = SetQHYCCDStreamMode(self.handle, 0)  # Single frame mode
                    if ret == QHYCCD_SUCCESS:
                        print("Stream mode set successfully")
                    else:
                        print(f"Stream mode setting failed, error code: {ret}")
                    
                    print("Initializing camera...")
                    ret = InitQHYCCD(self.handle)
                    if ret == QHYCCD_SUCCESS:
                        print("Camera initialized successfully")
                        self.status_label.setText('Camera connected')
                    else:
                        print(f"Camera initialization failed, error code: {ret}")
                        self.status_label.setText('Camera initialization failed')
                else:
                    print(f"Unable to open camera, error code: {ctypes.get_last_error()}")
                    self.status_label.setText('Unable to open camera')
            else:
                print(f"Failed to get camera ID, error code: {ret}")
                self.status_label.setText('Failed to get camera ID')
        else:
            print("No cameras found")
            self.status_label.setText('No cameras found')
    else:
        print("Camera is already connected")
        self.status_label.setText('Camera is already connected')

import sys
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PIL import Image
import numpy as np

# Load DLL
try:
    qhyccd = ctypes.CDLL("./qhyccd.dll")
    print("Successfully loaded qhyccd.dll")
except Exception as e:
    print(f"Failed to load qhyccd.dll: {e}")
    sys.exit(1)

# Define constants and structures
QHYCCD_SUCCESS = 0
QHYCCD_ERROR = 0xFFFFFFFF

class QHYCCD_HANDLE(ctypes.Structure):
    pass

PQHYCCD_HANDLE = ctypes.POINTER(QHYCCD_HANDLE)

# Define function prototypes
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

        self.status_label = QLabel('Camera not connected')
        layout.addWidget(self.status_label)

        connect_button = QPushButton('Connect Camera')
        connect_button.clicked.connect(self.connect_camera)
        layout.addWidget(connect_button)

        capture_button = QPushButton('Capture Image')
        capture_button.clicked.connect(self.capture_image)
        layout.addWidget(capture_button)

        self.image_label = QLabel()
        layout.addWidget(self.image_label)

        central_widget.setLayout(layout)

    def connect_camera(self):
        if self.handle is None:
            print("Starting camera connection...")
            
            print("Initializing QHYCCD resources...")
            ret = InitQHYCCDResource()
            if ret == QHYCCD_SUCCESS:
                print("QHYCCD resources initialized successfully")
            else:
                print(f"QHYCCD resource initialization failed, error code: {ret}")
                return
            
            print("Scanning for cameras...")
            num_cameras = ScanQHYCCD()
            print(f"Found {num_cameras} cameras")
            
            if num_cameras > 0:
                print("Attempting to open the first camera...")
                camera_id = ctypes.create_string_buffer(32)
                ret = GetQHYCCDId(ctypes.c_int(0), camera_id)
                if ret == QHYCCD_SUCCESS:
                    print(f"Camera ID: {camera_id.value.decode()}")
                    self.handle = OpenQHYCCD(camera_id)
                    if self.handle:
                        print("Camera opened successfully")
                        
                        print("Setting stream mode...")
                        ret = SetQHYCCDStreamMode(self.handle, 0)  # Single frame mode
                        if ret == QHYCCD_SUCCESS:
                            print("Stream mode set successfully")
                        else:
                            print(f"Stream mode setting failed, error code: {ret}")
                        
                        print("Initializing camera...")
                        ret = InitQHYCCD(self.handle)
                        if ret == QHYCCD_SUCCESS:
                            print("Camera initialized successfully")
                            self.status_label.setText('Camera connected')
                        else:
                            print(f"Camera initialization failed, error code: {ret}")
                            self.status_label.setText('Camera initialization failed')
                    else:
                        print(f"Unable to open camera, error code: {ctypes.get_last_error()}")
                        self.status_label.setText('Unable to open camera')
                else:
                    print(f"Failed to get camera ID, error code: {ret}")
                    self.status_label.setText('Failed to get camera ID')
            else:
                print("No cameras found")
                self.status_label.setText('No cameras found')
        else:
            print("Camera is already connected")
            self.status_label.setText('Camera is already connected')

    def capture_image(self):
        if self.handle:
            print("Starting image capture...")
            try:
                # Set exposure time to 1 second
                ret = SetQHYCCDParam(self.handle, ctypes.c_int(8), ctypes.c_double(1000000))
                if ret != QHYCCD_SUCCESS:
                    print(f"Failed to set exposure time, error code: {ret}")
                    return

                # Start exposure
                ret = ExpQHYCCDSingleFrame(self.handle)
                if ret != QHYCCD_SUCCESS:
                    print(f"Failed to start exposure, error code: {ret}")
                    return

                # Get required memory size
                mem_length = GetQHYCCDMemLength(self.handle)
                if mem_length == 0:
                    print("Failed to get memory size")
                    return

                print(f"Required memory size for image: {mem_length} bytes")

                # Allocate memory
                buffer = (ctypes.c_uint8 * mem_length)()

                w = ctypes.c_uint32()
                h = ctypes.c_uint32()
                bpp = ctypes.c_uint32()
                channels = ctypes.c_uint32()

                # Get image data
                ret = GetQHYCCDSingleFrame(self.handle, ctypes.byref(w), ctypes.byref(h), ctypes.byref(bpp),
                                           ctypes.byref(channels), buffer)

                if ret == QHYCCD_SUCCESS:
                    print(f'Image captured: {w.value}x{h.value}, {bpp.value} bits, {channels.value} channels')
                    self.status_label.setText(f'Image captured: {w.value}x{h.value}')
                    
                    # Use returned image dimensions
                    width = w.value
                    height = h.value
                    bytes_per_pixel = bpp.value // 8
                    
                    print(f"Image size: {width}x{height}")
                    print(f"Bytes per pixel: {bytes_per_pixel}")
                    
                    # Convert image data to numpy array
                    image_data = np.frombuffer(buffer, dtype=np.uint16 if bpp.value > 8 else np.uint8)
                    image_data = image_data[:width * height * bytes_per_pixel].reshape(width, height, -1)
                    
                    print(f"Image data shape: {image_data.shape}")
                    
                    # Convert 16-bit image if necessary
                    if bpp.value == 16:
                        image_data = (image_data / 256).astype(np.uint8)
                    
                    # Remove extra dimension for single-channel images
                    if channels.value == 1:
                        image_data = image_data.squeeze()
                    
                    # Create QImage and display
                    if channels.value == 1:
                        qimage = QImage(image_data.data, width, height, width, QImage.Format_Grayscale8)
                    else:
                        qimage = QImage(image_data.data, width, height, width * 3, QImage.Format_RGB888)
                    
                    pixmap = QPixmap.fromImage(qimage)
                    
                    # Adjust image widget size to fit the image
                    self.image_label.setPixmap(pixmap)
                    self.image_label.setScaledContents(True)
                    self.resize_window_to_fit_image(pixmap.size())
                else:
                    print(f'Capture failed, error code: {ret}')
                    self.status_label.setText('Capture failed')

            except Exception as e:
                print(f"Error occurred during capture: {e}")
                self.status_label.setText('Error occurred during capture')

        else:
            print("Camera not connected")
            self.status_label.setText('Please connect the camera first')

    def resize_window_to_fit_image(self, image_size):
        # Get screen size
        screen = QApplication.primaryScreen().geometry()
        
        # Calculate new window size, ensuring it doesn't exceed 80% of screen size
        new_width = min(image_size.width() + 40, screen.width() * 0.8)
        new_height = min(image_size.height() + 100, screen.height() * 0.8)
        
        # Resize window
        self.resize(new_width, new_height)
        
        # Move window to the center of the screen
        self.move(screen.center() - self.rect().center())

    def closeEvent(self, event):
        if self.handle:
            print("Closing camera connection...")
            CloseQHYCCD(self.handle)
        print("Releasing QHYCCD resources...")
        ReleaseQHYCCDResource()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = QHYCCDDemo()
    demo.show()
    sys.exit(app.exec_())
