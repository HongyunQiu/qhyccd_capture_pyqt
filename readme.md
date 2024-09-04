# QHYCCD Camera Control Demo

This project demonstrates how to control a QHYCCD camera using Python and PyQt5. It provides a graphical user interface for connecting to the camera, capturing images, and displaying them. The dll file in the folder is from QHYCCD and it is a X64 version.

## Features

- Connect to QHYCCD cameras
- Capture single-frame images
- Display captured images in the GUI
- Automatically resize the window to fit the captured image

## Requirements

- Python 3.x
- PyQt5
- NumPy
- Pillow
- QHYCCD SDK (qhyccd.dll)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/qhyccd-demo.git
   cd qhyccd-demo
   ```

2. Install the required Python packages:
   ```bash
   pip install PyQt5 numpy Pillow
   ```

3. Ensure that the QHYCCD SDK (qhyccd.dll) is in the same directory as the script or in your system PATH.

## Usage

Run the script using Python:

```bash
python qhyccd_demo.py
```

This method captures an image from the connected camera and displays it in the GUI.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

This project uses the QHYCCD SDK, which is provided by QHYCCD (https://www.qhyccd.com/).

