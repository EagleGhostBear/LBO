import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu, JointState
from squaternion import Quaternion
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point32
from sensor_msgs.msg import LaserScan,PointCloud
from math import pi

class tt(Node):

    def __init__(self):
        super().__init__('tt')
        
        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            depth=10,
        )
        
        self.subscription = self.create_subscription(LaserScan,
        '/scan',self.scan_callback, qos)
        self.tt_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.imu_sub = self.create_subscription(Imu, '/imu', self.imu_callback, 10)
        self.test_pub = self.create_publisher(String, '/test', 10)
        self.timer = self.create_timer(1, self.timer_callback)

        self.is_odom = 0
        
    def scan_callback(self, msg):
        return
        print('good')

    def odom_callback(self, msg):
        return
    
    def imu_callback(self, msg):
        imu_q = Quaternion(msg.orientation.w, msg.orientation.x, msg.orientation.y, msg.orientation.z)
        _, _, yaw = imu_q.to_euler()
        print(yaw*180/pi)

    def timer_callback(self):
        msg = String()
        msg.data = 'tt'
        self.test_pub.publish(msg)
        
def main(args=None):
    rclpy.init(args=args)
    ttt = tt()
    rclpy.spin(ttt)
    ttt.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()