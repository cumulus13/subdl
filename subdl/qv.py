import sys
import requests
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.QtCore import Qt, QRect
from PyQt5.Qt import QScreen
from io import BytesIO
import clipboard



class ImageViewer(QMainWindow):
    def __init__(self, image_path):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.image_label)

        self.load_image(image_path)
        self.center_window()

    def load_image(self, image_path):
        pixmap = self.get_pixmap(image_path)
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())

        if pixmap.width() > screen_geometry.width() or pixmap.height() > screen_geometry.height():
            scaled_width = int(screen_geometry.width() * 0.8)
            scaled_height = int(screen_geometry.height() * 0.8)
            pixmap = pixmap.scaled(scaled_width, scaled_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.image_label.setPixmap(pixmap)
        self.resize(pixmap.size())

    def get_pixmap(self, image_path):
        if image_path.startswith("http://") or image_path.startswith("https://"):
            response = requests.get(image_path)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                pixmap = QPixmap()
                pixmap.loadFromData(image_data.read())
                return pixmap
            else:
                print(f"Error loading image from URL: {response.status_code}")
                sys.exit(1)
        else:
            return QPixmap(image_path)

    def center_window(self):
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(screen_geometry.center())
        self.move(frame_geometry.topLeft())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Q or event.key() == Qt.Key_Escape:
            self.close()

def show(image_path):
    app = QApplication(sys.argv)
    viewer = ImageViewer(image_path)
    viewer.show()
    viewer.activateWindow()
    app.exec_()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python qv.py <image_path_or_url>")
        sys.exit(1)
    image_path = sys.argv[1]
    if image_path == 'c' or image_path == 'C':
        image_path = clipboard.paste()
    show(image_path)
