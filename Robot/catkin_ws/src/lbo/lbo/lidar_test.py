import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from geometry_msgs.msg import Point32
from sensor_msgs.msg import LaserScan,PointCloud
from math import pi,cos,sin
class lidarTrans(Node):

    def __init__(self):
        super().__init__('lidar_trans')

        qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            depth=10,
            )

        self.lidar_sub = self.create_subscription(LaserScan, '/scan', self.lidar_callback, qos)
        self.pcd_pub = self.create_publisher(PointCloud, 'pcd', 10)

    def lidar_callback(self, msg):
        pcd_msg = PointCloud()
        pcd_msg.header.frame_id = 'laser'

        for angle,r in enumerate(msg.ranges):
            lidar_point = Point32()

            if 0.0 < r < 3.5:
                lidar_point.x = r*cos(angle*pi/180)
                lidar_point.y = r*sin(angle*pi/180)
                pcd_msg.points.append(lidar_point)
    
        self.pcd_pub.publish(pcd_msg)

def main(args = None):
    rclpy.init(args=args)
    lidar_trans = lidarTrans()
    rclpy.spin(lidar_trans)
    lidar_trans.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
  main()