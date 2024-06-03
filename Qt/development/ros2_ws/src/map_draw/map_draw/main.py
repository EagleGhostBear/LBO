import sys
import os
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
sys.path.append(current_directory)

import threading
import time
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QGraphicsScene
from PySide6.QtGui import QImage, QPixmap, QTransform, QPainter, QPen
from PySide6.QtCore import Qt, Signal, QObject
import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import CompressedImage
from geometry_msgs.msg import Twist
from mainUI import Ui_MainWindow


class SubNodeHandler(QObject):
    map_signal = Signal(object)
    camera_signal = Signal(object)
    odom_signal = Signal(object)


class Sub_node(Node):
    def __init__(self):
        super().__init__('Sub_node')
        self.map_sub = self.create_subscription(OccupancyGrid, '/map', self.map_callback, 10)
        self.camera_sub = self.create_subscription(CompressedImage, '/cam/frame', self.camera_callback, 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom',self.odom_callback,10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel',10)
        self.handler = SubNodeHandler()
        self.last_cmd_time = time.time()
        self.cmd_interval = 0.1
        self.robot_x = 0.0
        self.robot_y = 0.0

    def map_callback(self, msg):
        print("map Call_back")
        self.handler.map_signal.emit(msg)

    def camera_callback(self, msg):
        self.handler.camera_signal.emit(msg)

    def odom_callback(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

    def publish_cmd_vel(self, linear_x, angular_z):
        current_time = time.time()
        if current_time - self.last_cmd_time >= self.cmd_interval:
            twist = Twist()
            twist.linear.x = linear_x
            twist.angular.z = angular_z
            self.cmd_pub.publish(twist)

class MyApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # self.main()
        self.sub_node = Sub_node()
        self.sub_node.handler.map_signal.connect(self.update_map_image)
        self.sub_node.handler.camera_signal.connect(self.update_camera_image)
        self.img_once = 0
        self.map_once = 0
        self.before_scale_factor = 0;

    def closeEvent(self, event):
        # ROS 2 노드 종료
        rclpy.shutdown()
        event.accept()

    def Reset_click(self):
        print("Reset")

    def LEFT_click(self):
        print("Left")
        self.sub_node.publish_cmd_vel(0.0, 1.0)

    def DOWN_click(self):
        print("Down")
        self.sub_node.publish_cmd_vel(-0.1, 0.0)

    def RIGHT_click(self):
        print("Right")
        self.sub_node.publish_cmd_vel(0.0, -1.0)

    def STOP_click(self):
        print("Stop")
        self.sub_node.publish_cmd_vel(0.0, 0.0)

    def UP_click(self):
        print("Up")
        self.sub_node.publish_cmd_vel(0.1, 0.0)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            print("Escape key pressed")
        else:
            if key == 87:
                print(f"Key pressed: {key} (char: {event.text()})")
                self.sub_node.publish_cmd_vel(0.2, 0.0)
            elif key == 83:
                print(f"Key pressed: {key} (char: {event.text()})")
                self.sub_node.publish_cmd_vel(-0.2, 0.0)
            elif key == 65:
                print(f"Key pressed: {key} (char: {event.text()})")
                self.sub_node.publish_cmd_vel(0.0, -1.0)
            elif key == 68:
                print(f"Key pressed: {key} (char: {event.text()})")
                self.sub_node.publish_cmd_vel(0.0, 1.0)
            else:
                print(f"Key pressed: {key} (char: {event.text()})")
                self.sub_node.publish_cmd_vel(0.0, 0.0)
        super().keyPressEvent(event)

    def update_map_image(self, map_msg):
        width = map_msg.info.width
        height = map_msg.info.height
        resolution = map_msg.info.resolution
        origin_x = int((self.sub_node.robot_x - map_msg.info.origin.position.x) / resolution)
        origin_y = int((self.sub_node.robot_y - map_msg.info.origin.position.y) /resolution)# 시작 위치 저장 필요

        # OccupancyGrid 데이터를 numpy 배열로 변환하고, 2D 배열로 reshape
        map_array = np.array(map_msg.data).reshape((height, width))

        start_x = width - origin_x
        start_y = height - origin_y
        print(width, height, resolution, origin_x, origin_y)
        print(start_x, start_y)
        map_array = np.clip(map_array, 0, 100)  # -1과 100 이상 값들을 처리
        flipped_array = np.fliplr(map_array)
        new_array = np.copy(flipped_array)

        # numpy 배열을 QImage로 변환
        image = QImage(new_array.data, width, height, width, QImage.Format_Grayscale8)


        # 이미지를 반시계 방향으로 90도 회전
        transform = QTransform().rotate(90)
        rotated_image = image.transformed(transform)

        robot_px = start_x
        robot_py = start_y

        pixmap = QPixmap.fromImage(rotated_image)  # 회전된 이미지를 설정
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.red, 5))
        painter.drawPoint(int(robot_py),int(robot_px))
        painter.end()

        # QGraphicsScene에 pixmap 설정
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.graphicsView_2.setScene(scene)

        self.graphicsView_2.setFixedSize(470, 470)

        # Fit the scene to the view
        # -3을 하는 이유는  graphicsView 크기 그대로 하면 graphicsView의 경계선과 곂쳐져 스크롤이 발생하기 때문입니다.
        view_width = self.graphicsView_2.width() - 3
        view_height = self.graphicsView_2.height() - 3

        scale_factor = min(view_width / width, view_height / height)

        
        if self.map_once == 1:
            self.graphicsView_2.scale(1 / self.before_scale_factor, 1 / self.before_scale_factor)

        self.before_scale_factor = scale_factor
        self.graphicsView_2.scale(scale_factor, scale_factor)
        self.map_once = 1

        self.graphicsView_2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsView_2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def update_camera_image(self, img_msg):
        np_arr = np.frombuffer(img_msg.data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        # QImage to QPixmap
        pixmap = QPixmap.fromImage(q_image)

        # QGraphicsScene에 pixmap 설정
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.graphicsView.setScene(scene)

        self.graphicsView.setFixedSize(470, 470)

        # Fit the scene to the view
        # -3을 하는 이유는  graphicsView 크기 그대로 하면 graphicsView의 경계선과 곂쳐져 스크롤이 발생하기 때문입니다.
        view_width = self.graphicsView.width() - 3
        view_height = self.graphicsView.height() - 3

        scale_factor = min(view_width / width, view_height / height)


        #
        # # Scale the scene to fit the image into QGraphicsView
        if self.img_once ==0:
            self.graphicsView.scale(scale_factor, scale_factor)
            self.img_once = self.img_once + 1

        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


def ros_thread(sub_node):
    rclpy.spin(sub_node)


def main(args=None):
    # ROS 2 초기화
    rclpy.init(args=args)

    app = QApplication(sys.argv)
    win = MyApp()
    win.show()

    # ROS 2 노드를 별도의 스레드에서 실행
    ros_thread_instance = threading.Thread(target=ros_thread, args=(win.sub_node,))
    ros_thread_instance.start()

    sys.exit(app.exec())

    # 종료시 ROS 2 종료
    rclpy.shutdown()


if __name__ == '__main__':
    main()
