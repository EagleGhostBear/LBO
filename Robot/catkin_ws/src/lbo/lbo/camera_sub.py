import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
import cv2
import numpy as np

class ImageSubscriber(Node):
    def __init__(self):
        super().__init__('image_subscriber')
        self.subscription_rgb = self.create_subscription(
            CompressedImage,
            'cam',
            self.listener_callback_rgb,
            10)
        
    def listener_callback_rgb(self, msg):
        np_arr = np.frombuffer(msg.data, np.uint8)
        # 이미지 디코딩
        image_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # 이미지가 null이 아닌지 확인
        if image_np is not None:
            # 이미지 크기가 유효한지 확인
            if image_np.shape[0] > 0 and image_np.shape[1] > 0:
                cv2.imshow('RGB Image', image_np)
                cv2.waitKey(1)  # Display the image until a keypress
            else:
                print("이미지 크기가 유효하지 않습니다.")
        else:
            print("이미지 디코딩 실패")

def main(args=None):
    rclpy.init(args=args)
    image_subscriber = ImageSubscriber()
    rclpy.spin(image_subscriber)
    image_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()