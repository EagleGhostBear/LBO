import os
import rclpy
import json
from std_msgs.msg import Int64
import playsound

CONST_PATH_JSON = "/home/jetson/turtlebot3_ws/src/lbo/lbo/tts_dict.json"
CONST_PATH_OUTPUT = "/home/jetson/turtlebot3_ws/src/lbo/lbo/sounds"

DICT_IDX_START = 0
DICT_IDX_END = 15

meta_dict = None

def read_json(path, enc='UTF8'):
    with open(path, 'r', encoding=enc) as f:
        return json.load(f)

def tts_callback(msg):
    global meta_dict
    num_data = int(msg.data)
    print(num_data)
    if DICT_IDX_START <= num_data <= DICT_IDX_END:
        file_path = os.path.join(CONST_PATH_OUTPUT, meta_dict[str(num_data)]["file"])

        if not os.path.exists(file_path):
            return None

        playsound.playsound(file_path)

def main():
	global meta_dict
       
	try:
		meta_dict = read_json(CONST_PATH_JSON)
	except Exception as e:
			print(e)
			exit()

	rclpy.init()
	node = rclpy.create_node('tts_node')
	sub = node.create_subscription(Int64, "/tts", tts_callback, 10)

	rclpy.spin(node)

	node.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
        main()
