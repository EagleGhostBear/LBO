import rclpy
import numpy as np
import math
import json
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Imu
from std_msgs.msg import String, Float64
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise

class Quat:
    def __init__(self, x, y, z, w):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def quat_to_euler(self):
        x, y, z, w = self.x, self.y, self.z, self.w
        
        # Roll (x-axis rotation)
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(t0, t1)
        
        # Pitch (y-axis rotation)
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch = math.asin(t2)
        
        # Yaw (z-axis rotation)
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(t3, t4)
        
        return [yaw, pitch, roll]

class find_direction(Node):

    def __init__(self):
        super().__init__('findDirection')

        self.is_robot_imu = False
        self.is_handle_imu = False

        self.target1 = None
        self.target2 = None
        self.result_angle = None
        self.robot_angle = None
        self.handle_angle = None

        self.robot_offset = 0
        self.handle_offset = 0

        self.robot_imu_sub = self.create_subscription(Imu, '/imu', self.robot_imu_callback, 10)
        self.handle_imu_sub = self.create_subscription(Imu, '/handle_imu', self.handle_imu_callback, 10)

        self.servo_pub = self.create_publisher(Float64, 'servo', 10)

        self.timer = self.create_timer(0.3, self.cal_direction)

        self.kf = KalmanFilter(dim_x=4, dim_z=4)
        self.kf.x = np.array([1., 0., 0., 0.])  # 초기 상태값
        self.kf.F = np.eye(4)  # 상태 전이 행렬
        self.kf.H = np.eye(4)  # 측정 모델
        self.kf.P *= 1000.  # 초기 공분산
        self.kf.R = np.diag([0.01, 0.01, 0.01, 0.01])  # 측정 오차 공분산
        self.kf.Q = Q_discrete_white_noise(dim=4, dt=0.1, var=1.0)
    
    def robot_imu_callback(self, msg):
        robot_quat = Quat(msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w)
        robot_euler = robot_quat.quat_to_euler() # yaw, pitch, roll
        self.robot_angle = math.degrees(robot_euler[0]) + 360

        if not self.is_robot_imu:
            self.robot_offset = self.robot_angle
            self.is_robot_imu = True
        
        if(self.robot_angle - self.robot_offset < 0):
            self.robot_angle = self.robot_angle - self.robot_offset + 360
        else:
            self.robot_angle = self.robot_angle - self.robot_offset
    
    def handle_imu_callback(self, msg):
        handle_quat = Quat(msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w)
        filtered_quat  = self.kf.filter_update(np.array([handle_quat.x, handle_quat.y, handle_quat.z, handle_quat.w]))
        filtered_euler = Quat(filtered_quat[0], filtered_quat[1], filtered_quat[2], filtered_quat[3]).quat_to_euler()
        self.handle_angle = math.degrees(filtered_euler[0]) + 360

        if not self.is_handle_imu:
            self.handle_offset = self.handle_angle
            self.is_handle_imu = True
            
        if(self.handle_angle - self.handle_offset < 0):
            self.handle_angle = self.handle_angle - self.handle_offset + 360
        else:
            self.handle_angle = self.handle_angle - self.handle_offset

    def cal_direction(self):
        if self.is_robot_imu and self.is_handle_imu:
            self.target_angle1 = self.robot_angle - self.handle_angle
            self.target_angle2 = 360 - abs(self.target_angle1)
            if(self.target_angle1 >= 0):
                self.target_angle2 *= -1
            if(abs(self.target_angle1) <= abs(self.target_angle2)):
                self.result_angle = self.target_angle1
            else:
                self.result_angle = self.target_angle2

            # servo 0 ~ 180, middle = 90
            if(self.result_angle <= -90):
                self.result_angle = 0.0
            elif(self.result_angle >= 90):
                self.result_angle = 180.0
            else:
                self.result_angle += 90.0
                
            servo_msg = Float64()
            servo_msg.data = self.result_angle
            self.servo_pub.publish(servo_msg)
            
            # print(self.result_angle)
            
        elif not self.is_robot_imu and not self.is_handle_imu:
            print("Not Receive Data!!")
        elif not self.is_robot_imu:
            print("Not Receive robot_imu!")
        else:
            print("Not Receive handle_imu!")

def main(args=None):
    rclpy.init(args=args)
    findDirection = find_direction()
    rclpy.spin(findDirection)
    findDirection.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()