import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion, Pose, Point, TransformStamped
from nav_msgs.msg import Odometry
import tf2_ros
import math
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise

class ObjectOdometryCalculator(Node):
    def __init__(self):
        super().__init__('object_odometry_calculator')
        self.imu_sub = self.create_subscription(
            Imu,
            'handle_imu',  # 다른 객체에 부착된 IMU 센서 토픽 이름
            self.imu_callback,
            10)
        self.odom_pub = self.create_publisher(Odometry, 'handle_odom', 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.odom_frame_id = 'odom'
        self.base_frame_id = 'handle_frame'

        # Initialize object odometry variables
        self.is_imu = False
        self.last_time = None
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.vth = 0.0

        # Kalman Filter Initialization
        self.kf = KalmanFilter(dim_x=3, dim_z=3)
        self.kf.x = np.array([[0., 0., 0.]]).T  # [x, y, theta]
        self.kf.F = np.array([[1., 0., 0.],
                              [0., 1., 0.],
                              [0., 0., 1.]])  # State transition matrix
        self.kf.H = np.array([[1., 0., 0.],
                              [0., 1., 0.],
                              [0., 0., 1.]])  # Measurement function
        self.kf.P *= 1000.  # Covariance matrix
        self.kf.R = np.diag([0.1, 0.02, 0.01])  # Measurement noise covariance
        self.kf.Q = Q_discrete_white_noise(dim=3, dt=0.1, var=0.05)  # Process noise covariance

        # Gravity vector in the world frame
        #self.gravity = np.array([0.0, 0.0, -9.81])

    def imu_callback(self, msg):
        if not self.is_imu:
            self.offset = np.array([msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z])
            self.is_imu = True

        current_time = self.get_clock().now().to_msg()
        if self.last_time is not None:
            dt = (current_time.sec - self.last_time.sec) + 1e-9 * (current_time.nanosec - self.last_time.nanosec)

            # Remove gravity from linear acceleration
            linear_acceleration = np.array([msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z]) - self.offset
            #linear_acceleration -= np.dot(linear_acceleration, self.gravity) / np.dot(self.gravity, self.gravity) * self.gravity

            # Predict
            self.kf.predict()

            # Update
            z = np.array([[linear_acceleration[0], linear_acceleration[1], msg.angular_velocity.z]]).T
            self.kf.update(z)

            # Get estimated state from Kalman Filter
            x_est = self.kf.x

            self.vx = float(x_est[0])
            self.vy = float(x_est[1])
            self.vth = float(x_est[2])

            # Integrate velocities to get positions
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.theta += self.vth * dt

            # Publish odometry message
            odom = Odometry()
            odom.header.stamp = current_time
            odom.header.frame_id = self.odom_frame_id
            odom.child_frame_id = self.base_frame_id

            # Position
            odom.pose.pose.position = Point(x=self.x, y=self.y, z=0.0)
            odom.pose.pose.orientation = self.angle_to_quaternion(self.theta)

            # Velocity
            odom.twist.twist.linear.x = self.vx
            odom.twist.twist.linear.y = self.vy
            odom.twist.twist.angular.z = self.vth

            print("x : {0}, y : {1}, theta : {2}".format(self.x, self.y, self.theta))
            self.odom_pub.publish(odom)

            # Broadcast transform
            transform = TransformStamped()
            transform.header.stamp = current_time
            transform.header.frame_id = self.odom_frame_id
            transform.child_frame_id = self.base_frame_id
            transform.transform.translation.x = self.x
            transform.transform.translation.y = self.y
            transform.transform.translation.z = 0.0
            transform.transform.rotation = self.angle_to_quaternion(self.theta)

            self.tf_broadcaster.sendTransform(transform)

        self.last_time = current_time

    def angle_to_quaternion(self, theta):
        quat = Quaternion()
        quat.x = 0.0
        quat.y = 0.0
        quat.z = math.sin(theta / 2.0)
        quat.w = math.cos(theta / 2.0)
        return quat

def main(args=None):
    rclpy.init(args=args)
    object_odometry_calculator = ObjectOdometryCalculator()
    rclpy.spin(object_odometry_calculator)
    object_odometry_calculator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()