import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from std_msgs.msg import String
from geometry_msgs.msg import Pose, PoseStamped, PoseWithCovarianceStamped
from squaternion import Quaternion
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan,PointCloud
from math import pi
import threading

params_user = {
    "START_POSE" : [0.0, 0.0, 0.0],
    "START_ORIENTATION" : [0.0, 0.0, 0.0, 1.0],
    "GOAL_POSE" : [
        [4.21496, 2.65447, 0.0],
    ],
    "GOAL_ORIENTATION" : [
        [0.0, 0.0, 0.0, 1.0],
    ],
}

class User(Node):

    def __init__(self):
        super().__init__('User')
        
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            depth=10,
        )
        
        self.initial_pub = self.create_publisher(PoseWithCovarianceStamped, 'initialpose', qos)
        self.goal_pub = self.create_publisher(PoseStamped, 'goal_pose', 10)
        self.timer = self.create_timer(0.2, self.timer_callback)

        self.init = 0
        self.is_init = False

        self.goal_msg = PoseStamped()
        self.goal_msg.header.frame_id = 'map'

        self.input_thread = threading.Thread(target=self.input_and_goal)
        self.input_thread.start()

    def timer_callback(self):
        if not self.is_init:
            if self.init < 5:
                initial_msg = PoseWithCovarianceStamped()
                initial_msg.header.frame_id = 'map'

                initial_msg.pose.pose.position.x = params_user["START_POSE"][0]
                initial_msg.pose.pose.position.y = params_user["START_POSE"][1]
                initial_msg.pose.pose.position.z = params_user["START_POSE"][2]

                initial_msg.pose.pose.orientation.x = params_user["START_ORIENTATION"][0]
                initial_msg.pose.pose.orientation.y = params_user["START_ORIENTATION"][1]
                initial_msg.pose.pose.orientation.z = params_user["START_ORIENTATION"][2]
                initial_msg.pose.pose.orientation.w = params_user["START_ORIENTATION"][3]

                ## nav2 rviz 기본 설정
                initial_msg.pose.covariance[0] = 0.25
                initial_msg.pose.covariance[7] = 0.25
                initial_msg.pose.covariance[35] = 0.06853891945200942

                initial_msg.header.stamp = rclpy.clock.Clock().now().to_msg()
                self.initial_pub.publish(initial_msg)
                self.init += 1
            else:
                self.is_init = True
        
    def input_and_goal(self):
        while True:
            menu=input('목적지 : ')
            if not self.is_init:
                print('잠시만 기다리세요')
                continue

            self.goal_msg.pose.position.x = params_user["GOAL_POSE"][0][0]
            self.goal_msg.pose.position.y = params_user["GOAL_POSE"][0][1]

            self.goal_msg.pose.orientation.x = params_user["GOAL_ORIENTATION"][0][0]
            self.goal_msg.pose.orientation.y = params_user["GOAL_ORIENTATION"][0][1]
            self.goal_msg.pose.orientation.z = params_user["GOAL_ORIENTATION"][0][2]
            self.goal_msg.pose.orientation.w = params_user["GOAL_ORIENTATION"][0][3]

            self.goal_msg.header.stamp = rclpy.clock.Clock().now().to_msg()
            self.goal_pub.publish(self.goal_msg)
        
def main(args=None):
    rclpy.init(args=args)
    ttt = User()
    rclpy.spin(ttt)
    ttt.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()