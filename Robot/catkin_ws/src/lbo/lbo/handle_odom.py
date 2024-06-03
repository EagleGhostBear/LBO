import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Quaternion, Twist, Pose, Vector3Stamped, Point
from nav_msgs.msg import Odometry
from filterpy.kalman import KalmanFilter
import numpy as np
import math

class OdometryCalculator(Node):
    def __init__(self):
        super().__init__('odometry_calculator')
        self.subscription = self.create_subscription(
            Imu,
            '/imu',  # IMU 데이터가 발행되는 토픽 이름으로 변경해야 합니다.
            self.imu_callback,
            10)
        self.prev_time = None
        self.prev_orientation = Quaternion()
        self.odom_pub = self.create_publisher(Odometry, 'handle_odom', 10)  # odometry 데이터를 발행할 토픽 이름으로 변경해야 합니다.
        self.current_pose = Pose()

        # Initialize Kalman Filter
        self.kf = KalmanFilter(dim_x=3, dim_z=3)
        self.kf.x = np.array([0., 0., 0.])  # Initial state [x, y, theta]
        self.kf.F = np.array([[1., 0., 0.],
                              [0., 1., 0.],
                              [0., 0., 1.]])  # State transition matrix
        self.kf.H = np.array([[1., 0., 0.],
                              [0., 1., 0.],
                              [0., 0., 1.]])  # Measurement function
        self.kf.P *= 1000.  # Covariance matrix
        self.kf.R *= 0.01  # Measurement noise covariance
        self.kf.Q *= 0.01  # Process noise covariance

    def imu_callback(self, msg):
        if self.prev_time is None:
            self.prev_time = msg.header.stamp
            self.prev_orientation = msg.orientation
            return

        current_time = msg.header.stamp

        # Calculate delta time
        delta_t = (current_time.sec - self.prev_time.sec) + 1e-9 * (current_time.nanosec - self.prev_time.nanosec)

        # Update previous time
        self.prev_time = current_time

        # Calculate change in orientation using quaternion rotation
        delta_orientation = self.quaternion_to_euler(msg.orientation) - self.quaternion_to_euler(self.prev_orientation)

        # Normalize angle to -pi to pi
        delta_orientation[2] = self.normalize_angle(delta_orientation[2])

        # Subtract gravity from linear acceleration
        linear_acceleration = msg.linear_acceleration
        gravity = 9.81  # Earth's gravity, you may need to adjust this depending on your IMU
        linear_acceleration.x -= gravity

        # Predict state using Kalman Filter
        self.kf.predict()

        # Update measurement
        self.kf.update(np.array([[delta_orientation[0]], [delta_orientation[1]], [delta_orientation[2]]]))

        # Get estimated state from Kalman Filter
        x_est = self.kf.x

        # Calculate linear velocity in x and y directions
        linear_velocity_x = x_est[0] * delta_t
        linear_velocity_y = x_est[1] * delta_t

        # Calculate angular velocity
        angular_velocity = x_est[2] / delta_t

        # Integrate velocities to update position
        self.current_pose.position.x += linear_velocity_x
        self.current_pose.position.y += linear_velocity_y
        self.current_pose.orientation.z += angular_velocity * delta_t

        # Publish odometry message
        odom_msg = Odometry()
        odom_msg.header.stamp = current_time
        odom_msg.header.frame_id = 'handle_odom'
        odom_msg.child_frame_id = 'handle_link'
        odom_msg.pose.pose.position = self.current_pose.position
        odom_msg.pose.pose.orientation = self.current_pose.orientation
        odom_msg.twist.twist.linear.x = linear_velocity_x
        odom_msg.twist.twist.linear.y = linear_velocity_y
        odom_msg.twist.twist.angular.z = angular_velocity
        self.odom_pub.publish(odom_msg)

        # Update previous orientation
        self.prev_orientation = msg.orientation

    def quaternion_to_euler(self, quaternion):
        x = quaternion.x
        y = quaternion.y
        z = quaternion.z
        w = quaternion.w

        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        pitch = math.asin(2.0 * (w * y - z * x))
        yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

        return np.array([roll, pitch, yaw])

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

def main(args=None):
    rclpy.init(args=args)
    odometry_calculator = OdometryCalculator()
    rclpy.spin(odometry_calculator)
    odometry_calculator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()