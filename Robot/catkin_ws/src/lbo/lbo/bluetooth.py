import rclpy, json
from rclpy.node import Node
from std_msgs.msg import String, Float64, Int64
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
        self.btn_pub = self.create_publisher(Int64, 'btn', 10)

        self.servo_sub = self.create_subscription(Float64, '/servo', self.servo_callback, 10)

        self.imu_msg = Imu()
        self.imu_msg.header.frame_id = 'imu_link'

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

        self.timer = self.create_timer(0, self.rx_and_echo)

    def __del__(self):
        self.sock.close()
        self.get_logger().info("--- Bye ---")

    def servo_callback(self, msg):
        send_json = {
            "info": {
                "name": 0,
                "time": str(datetime.datetime.now())
            },
            "data": {
                "servo": str(msg.data),
                "beep": 0
            }   
        }
        send_string = json.dumps(send_json)
        send_string += '@'

        self.sock.send(send_string)
        self.sock.send("\n")
        print("succeces send : " + str(msg.data))
        
    def rx_and_echo(self):
        data_string = ""

        while True:
            ret = data_string.find('@')
            if ret != -1:
                break
            temp = self.sock.recv(self.buf_size).decode('utf-8')
            data_string += temp

        data_string = data_string[:-1]
        
        if data_string:
            try:
                data_json = json.loads(data_string)
                
                uwb_msg = Float64()
                uwb_msg.data = float(data_json["data"]["uwb"])
                self.uwb_pub.publish(uwb_msg)

                btn_msg = Int64()
                btn_msg.data = int(data_json["data"]["button"])
                self.btn_pub.publish(btn_msg)
            
                self.imu_msg.linear_acceleration.x = float(data_json["data"]["imu"]["acc"]["x"])
                self.imu_msg.linear_acceleration.y = float(data_json["data"]["imu"]["acc"]["y"])
                self.imu_msg.linear_acceleration.z = float(data_json["data"]["imu"]["acc"]["z"])
            
                self.imu_msg.orientation.x = float(data_json["data"]["imu"]["gyro"]["x"])
                self.imu_msg.orientation.y = float(data_json["data"]["imu"]["gyro"]["y"])
                self.imu_msg.orientation.z = float(data_json["data"]["imu"]["gyro"]["z"])
                self.imu_msg.orientation.w = float(data_json["data"]["imu"]["gyro"]["w"])
            
                self.imu_msg.header.stamp = rclpy.clock.Clock().now().to_msg()
                self.imu_pub.publish(self.imu_msg)
            except json.decoder.JSONDecodeError as e:
                print("JSONDecodeError:", e)
                print("data : ", data_string)
               
def main(args=None):
    rclpy.init(args=args)
    bluetooth_client = BluetoothClientNode()
    rclpy.spin(bluetooth_client)
    bluetooth_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()