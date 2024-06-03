import cv2
import numpy as np
import random
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QImage, QColor
from mainUI import Ui_MainWindow
from PySide6.QtCore import Qt, QSize, QRectF

class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.main()

    def main(self):
        # 핵심 함수 (np.array를 사용한느거)
        # qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        # qimage2 = QImage(image_array.data, width, height, QImage.Format_Grayscale8)

        # [예시 1]
        # # 2차원 (GreyScale) 이미지를 가져옴. 이때, image는 numpy의 array
        # # !!!!!!!!!!     2차원 이미지 3차원으로 만들기
        image = cv2.imread("lena512.png", cv2.IMREAD_GRAYSCALE)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = width * channel

        # # !!!!!!!!!     3차원 Q이미지에 빨간색 점 찍기
        qimage = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

        x = random.randint(0, width - 5)
        y = random.randint(0, height - 5)
        for i in range(x, x + 5):
            for j in range(y, y + 5):
                qimage.setPixelColor(i, j, QColor(255, 0, 0))

        # Convert QImage to QPixmap
        pixmap = QPixmap.fromImage(qimage)

        # Create a QGraphicsScene and add the pixmap
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)

        # Set the scene to the QGraphicsView
        self.graphicsView.setScene(scene)

        # Set the fixed size of QGraphicsView
        self.graphicsView.setFixedSize(365, 322)

        # Fit the scene to the view
        # -3을 하는 이유는  graphicsView 크기 그대로 하면 graphicsView의 경계선과 곂쳐져 스크롤이 발생하기 때문입니다.
        view_width = self.graphicsView.width() - 3
        view_height = self.graphicsView.height() - 3

        scale_factor = min(view_width / width, view_height / height)
        #
        # # Scale the scene to fit the image into QGraphicsView
        self.graphicsView.scale(scale_factor, scale_factor)

        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)





        # [예시 2] 랜덤 array 사용
        # 이미지 배열 생성
        image_array = np.random.randint(-128, 128, size=(100, 100), dtype=np.int8)

        # Convert numpy array to QImage
        height_2, width_2 = image_array.shape

        # 핵심
        qimage2 = QImage(image_array.data, width_2, height_2, QImage.Format_Grayscale8)

        # Convert QImage to QPixmap
        pixmap2 = QPixmap.fromImage(qimage2)

        # Create a QGraphicsScene and add the pixmap
        scene2 = QGraphicsScene()
        scene2.addPixmap(pixmap2)

        # Set the scene to the QGraphicsView
        self.graphicsView_2.setScene(scene2)
        self.graphicsView_2.setFixedSize(365, 322)

        view_width_2 = self.graphicsView_2.width() - 3
        view_height_2 = self.graphicsView_2.height() - 3

        scale_factor2 = min(view_width_2 / width_2, view_height_2 / height_2)
        #
        # # Scale the scene to fit the image into QGraphicsView
        self.graphicsView_2.scale(scale_factor2, scale_factor2)

        self.graphicsView_2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsView_2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            print("위쪽 방향키가 눌렸습니다.")
        elif event.key() == Qt.Key_S:
            print("아래쪽 방향키가 눌렸습니다.")
        elif event.key() == Qt.Key_A:
            print("왼쪽 방향키가 눌렸습니다.")
        elif event.key() == Qt.Key_D:
            print("오른쪽 방향키가 눌렸습니다.")
        else:
            print("방향키 감지")
            super().keyPressEvent(event)

    def Reset_click(self):
        print("Reset")

    def LEFT_click(self):
        print("Left")

    def DOWN_click(self):
        print("Down")

    def RIGHT_click(self):
        print("Right")

    def STOP_click(self):
        print("Stop")

    def UP_click(self):
        print("Up")

    # 버튼이 눌리면,
    def KFC(self):
        # QMessageBox 객체 생성
        self.msg = QMessageBox()
        # QMessageBox의 text를 텍스트에디터에 적힌 text로 정한다.
        self.msg.setText("IP 연결 완료")
        # QMessageBox는 독립적인 창이므로, User가 닫기 버튼을 누를 때까지 실행될 수 있게 .exec() 사용한다.
        self.msg.exec()



if __name__ == '__main__':
    app = QApplication()
    win = MyApp()
    win.show()
    app.exec()