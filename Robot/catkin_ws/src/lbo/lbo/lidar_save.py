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
        self.timer = self.create_timer(1, self.timer_callback)

        self.lidar_msg = LaserScan()

    def lidar_callback(self, msg):
        self.lidar_msg = msg
    
    def timer_callback(self):
        full_path = 'C:\\Users\\SSAFY\\Desktop\\lidar.txt'
        f=open(full_path,'w')
        data=''
        for angle,r in enumerate(self.lidar_msg.ranges):
            data += '{0} '.format(r)

        data += '\n'

        f.write(data) 
        f.close()


def main(args = None):
    rclpy.init(args=args)
    lidar_trans = lidarTrans()
    rclpy.spin(lidar_trans)
    lidar_trans.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
  main()