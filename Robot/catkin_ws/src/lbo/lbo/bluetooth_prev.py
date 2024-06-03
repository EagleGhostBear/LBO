import rclpy, json
from rclpy.node import Node
from std_msgs.msg import String, Float64
from sensor_msgs.msg import Imu
import threading
from bluetooth import *

class BluetoothClientNode(Node):
    def __init__(self):
        super().__init__('bluetooth_client')
        self.sock = None
        self.buf_size = 1024
        self.uwb_pub = self.create_publisher(Float64, 'uwb', 10)
        self.imu_pub = self.create_publisher(Imu, 'handle_imu', 10)

        self.servo_sub = self.create_subscription(Float64, '/servo', self.servo_callback, 10)

        self.imu_msg = Imu()
        self.imu_msg.header.frame_id = 'imu_link'

    def servo_callback(self, msg):
        # self.is_servo = True
        send_json = {}
        send_json["data"]["servo"] = msg.data
        json_data = json.dumps(send_data)
        json_data += '@'
        self.sock.send(json_data)
        self.sock.send("\n")
        print("succeces send!")

    def input_and_send(self):
        self.get_logger().info("Type something")
        
    def rx_and_echo(self):
        while True:
            data_string = ""
            while True:
                ret = data_string.find('@')
                if ret != -1:
                    break
                temp = self.sock.recv(self.buf_size).decode('utf-8')
                data_string += temp
            data_string = data_string[:-1]
            if data_string:
                data_json = json.loads(data_string)
                uwb_msg = Float64()
                uwb_msg.data = float(data_json["data"]["uwb"])
                self.uwb_pub.publish(uwb_msg)
                self.imu_msg.linear_acceleration.x = float(data_json["data"]["imu"]["acc"]["x"])
                self.imu_msg.linear_acceleration.y = float(data_json["data"]["imu"]["acc"]["y"])
                self.imu_msg.linear_acceleration.z = float(data_json["data"]["imu"]["acc"]["z"])
                self.imu_msg.orientation.x = float(data_json["data"]["imu"]["gyro"]["x"])
                self.imu_msg.orientation.y = float(data_json["data"]["imu"]["gyro"]["y"])
                self.imu_msg.orientation.z = float(data_json["data"]["imu"]["gyro"]["z"])
                self.imu_msg.orientation.w = float(data_json["data"]["imu"]["gyro"]["w"])
                self.imu_msg.header.stamp = rclpy.clock.Clock().now().to_msg()
                self.imu_pub.publish(self.imu_msg)
                
    def bluetooth_communication(self):
        # MAC address of ESP32
        addr = "08:D1:F9:D7:94:8A"
        service_matches = find_service(address=addr)
        
        if len(service_matches) == 0:
            self.get_logger().info("Couldn't find the SampleServer service =(")
            return
        
        first_match = service_matches[0]
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]
        port = 1  # Manually setting the port to 1
        self.get_logger().info("Connecting to \"%s\" on %s, port %s" % (name, host, port))
        
        # Create the client socket
        self.sock = BluetoothSocket(RFCOMM)
        self.sock.connect((host, port))
        self.get_logger().info("Connected")
        
        # Start threads for input and receiving
        #input_thread = threading.Thread(target=self.input_and_send)
        rx_thread = threading.Thread(target=self.rx_and_echo)
        
        #input_thread.start()
        rx_thread.start()
        
        #input_thread.join()
        rx_thread.join()
        
        self.sock.close()
        self.get_logger().info("--- Bye ---")

def main(args=None):
    rclpy.init(args=args)
    bluetooth_client = BluetoothClientNode()
    bluetooth_client.bluetooth_communication()
    rclpy.spin(bluetooth_client)
    bluetooth_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()