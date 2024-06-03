import rclpy, json, requests
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu, JointState
from squaternion import Quaternion
from nav_msgs.msg import Odometry
from math import pi,cos,sin
import tf2_ros
import geometry_msgs.msg
import time


class odom(Node):

    def __init__(self):
        super().__init__('odom')
        
        # 로직 1. publisher, subscriber, broadcaster 만들기
        self.imu_sub = self.create_subscription(Imu,'/imu',self.imu_callback,10)
        self.joint_sub = self.create_subscription(JointState, '/joint_states', self.joint_callback, 10)
        self.odom_publisher = self.create_publisher(Odometry, 'odom_test', 10)
        self.broadcaster = tf2_ros.StaticTransformBroadcaster(self)


        # 로봇의 pose를 저장해 publish 할 메시지 변수 입니다.
        self.odom_msg=Odometry()
        self.imu_msg = Imu()
        # Map -> base_link 좌표계에 대한 정보를 가지고 있는 변수 입니다.
        self.base_link_transform=geometry_msgs.msg.TransformStamped()
        # base_link -> laser 좌표계에 대한 정보를 가지고 있는 변수 입니다.
        self.laser_transform=geometry_msgs.msg.TransformStamped()
        self.is_status=False
        self.is_imu=False
        # x,y,theta는 추정한 로봇의 위치를 저장할 변수 입니다.
        self.x= 0.0
        self.y= 0.0

        self.theta=0
        # imu_offset은 초기 로봇의 orientation을 저장할 변수 입니다.
        self.imu_offset=0
        self.prev_time=0

        self.first_offset = 0.0
        # 로직 2. publish, broadcast 할 메시지 설정

        self.odom_msg.header.frame_id = 'map'
        self.odom_msg.child_frame_id = 'base_link'

        self.base_link_transform.header.frame_id = 'map'
        self.base_link_transform.child_frame_id = 'base_link'

        self.laser_transform.header.frame_id = 'base_link'
        self.laser_transform.child_frame_id = 'laser'
        self.laser_transform.transform.translation.x = 0.0
        self.laser_transform.transform.translation.y = 0.0
        self.laser_transform.transform.translation.z = 1.0
        self.laser_transform.transform.rotation.w = 1.0

    def imu_callback(self,msg):
        # 로직 3. IMU 에서 받은 quaternion을 euler angle로 변환해서 사용
        self.imu_msg = msg

        if not self.is_imu:
            imu_q = Quaternion(msg.orientation.w, msg.orientation.x, msg.orientation.y, msg.orientation.z)
            _, _, yaw = imu_q.to_euler()
            self.is_imu = True
            self.theta = yaw


    def joint_callback(self, msg):
        if self.is_imu ==True:
            if self.is_status == False :
                self.is_status=True
                self.prev_time=rclpy.clock.Clock().now()
            else :
                
                self.current_time=rclpy.clock.Clock().now()
                # 계산 주기를 저장한 변수 입니다. 단위는 초(s)
                self.period = (self.current_time-self.prev_time).nanoseconds/1000000000
                # 로봇의 선속도, 각속도를 저장하는 변수, 시뮬레이터에서 주는 각 속도는 방향이 반대이므로 (-)를 붙여줍니다.
                linear_x = (msg.velocity[0] + msg.velocity[1])/2
                angular_z = self.imu_msg.angular_velocity.z
                
                # 로직 4. 로봇 위치 추정
                # (테스트) linear_x = 1, self.theta = 1.5707(rad), self.period = 1 일 때
                # self.x=0, self.y=1 이 나와야 합니다. 로봇의 헤딩이 90도 돌아가 있는
                # 상태에서 선속도를 가진다는 것은 x축방향이 아니라 y축방향으로 이동한다는 뜻입니다.

                self.x += linear_x*cos(self.theta)*self.period
                self.y += linear_x*sin(self.theta)*self.period
                self.theta += angular_z*self.period

                self.base_link_transform.header.stamp = rclpy.clock.Clock().now().to_msg()
                self.laser_transform.header.stamp = rclpy.clock.Clock().now().to_msg()
                
                # 로직 5. 추정한 로봇 위치를 메시지에 담아 publish, broadcast

                q = Quaternion.from_euler(0, 0, self.theta)
                
                self.base_link_transform.transform.translation.x = self.x
                self.base_link_transform.transform.translation.y = self.y
                self.base_link_transform.transform.rotation.x = q.x
                self.base_link_transform.transform.rotation.y = q.y
                self.base_link_transform.transform.rotation.z = q.z
                self.base_link_transform.transform.rotation.w = q.w
                
                self.odom_msg.pose.pose.position.x = self.x
                self.odom_msg.pose.pose.position.y = self.y
                self.odom_msg.pose.pose.orientation.x = q.x
                self.odom_msg.pose.pose.orientation.y = q.y
                self.odom_msg.pose.pose.orientation.z = q.z
                self.odom_msg.pose.pose.orientation.w = q.w
                self.odom_msg.twist.twist.linear.x = linear_x
                self.odom_msg.twist.twist.angular.z = angular_z

                self.broadcaster.sendTransform(self.base_link_transform)
                self.broadcaster.sendTransform(self.laser_transform)
                self.odom_publisher.publish(self.odom_msg)
                self.prev_time=self.current_time
        
def main(args=None):
    rclpy.init(args=args)
    odom_node = odom()
    rclpy.spin(odom_node)
    odom_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()