import os
import cv2
import numpy as np
import tensorflow as tf
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String

CONST_STRING_RESOLUTION = '1280x720' # width x height

CONST_INT_WIDTH = int(CONST_STRING_RESOLUTION.split('x')[0])
CONST_INT_HEIGHT = int(CONST_STRING_RESOLUTION.split('x')[1])

CONST_FLOAT_TIME = 0.1
CONST_FLOAT_FREQ = cv2.getTickFrequency()
CONST_FLOAT_THRESHOLD = 0.5

CONST_PATH_MODEL = "/home/jetson/ros2_ws/src/lbo/lbo/models/detect.tflite"
CONST_PATH_LABEL = "/home/jetson/ros2_ws/src/lbo/lbo/models/labelmap.txt"

class Cam():
    def __init__(self, camera_id=0):
        self.__set_camera(camera_id)

    def __set_camera(self, camera_id):
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
        self.window_title = "USB Camera"
    
    def close_camera(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def get_frame(self):
        assert self.cap.isOpened()

        res, frame = self.cap.read()
        if res:
            self.frame = frame
        else:
            raise ValueError("Can't get frame from Camera")

class Model():
    def __init__(self, model_path, label_path):
        try:
            self.set_gpu()
        except:
            pass
        
        self.labels = self.load_labels(label_path)
        self.set_interpreter(CONST_PATH_MODEL)

    def set_gpu(self):
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVIES"] = "0"

    def load_labels(self, path=CONST_PATH_LABEL):
        with open(path, 'r') as f:
            labels = [line.strip() for line in f.readlines()]
        return labels[1:] if labels[0] == '???' else labels
    
    def set_interpreter(self, path=CONST_PATH_MODEL):
        self.interpreter = tf.lite.Interpreter(model_path = path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]

        self.floating_model = (self.input_details[0]['dtype'] == np.float32)

class Detector(Node):

    def __init__(self, model):
        super().__init__('detector')
        self.model = model

        self.cap = Cam()

        self.cam_pub = self.create_publisher(CompressedImage, 'cam', 10)
        self.person_pub = self.create_publisher(String, 'person', 10)

        self.timer = self.create_timer(CONST_FLOAT_TIME, self.timer_callback)

    def __floating_input_data(self, input_data, input_mean=127.5, input_std = 127.5):
        return (np.float32(input_data) - input_mean) / input_std

    def __convert_image(self, image, floating=False):
        d_image = cv2.cuda_GpuMat()
        d_image.upload(image)
        image_rgb = cv2.cuda.cvtColor(d_image, cv2.COLOR_BGR2RGB)
        image_resized = cv2.cuda.resize(image_rgb, (self.model.width, self.model.height))
        n_image = image_resized.download()
        input_data = np.expand_dims(n_image, axis=0)

        if floating:
            input_data = self.__floating_input_data(input_data)

        return input_data
    
    def __calculate_inference_time(self, init_time):
        now = cv2.getTickCount()
        return (now - init_time)/CONST_FLOAT_FREQ

    def extract_object(self, interpreter):
        boxes = interpreter.get_tensor(self.model.output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(self.model.output_details[1]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(self.model.output_details[2]['index'])[0] # Confidence of detected objects

        for i in range(len(scores)):
            if ((scores[i] <= CONST_FLOAT_THRESHOLD) or (scores[i] > 1.0)):
                continue


    def draw_object(self, interpreter, image):
        boxes = interpreter.get_tensor(self.model.output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(self.model.output_details[1]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(self.model.output_details[2]['index'])[0] # Confidence of detected objects

        for i in range(len(scores)):
            if ((scores[i] <= CONST_FLOAT_THRESHOLD) or (scores[i] > 1.0)):
                continue
            
            ymin = int(max(1,(boxes[i][0] * CONST_INT_HEIGHT)))
            xmin = int(max(1,(boxes[i][1] * CONST_INT_WIDTH)))
            ymax = int(min(CONST_INT_HEIGHT,(boxes[i][2] * CONST_INT_HEIGHT)))
            xmax = int(min(CONST_INT_WIDTH,(boxes[i][3] * CONST_INT_WIDTH)))
        
            cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

            # Draw label
            label = '%s: %d%%' % (self.model.labels[int(classes[i])], int(scores[i]*100)) # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            cv2.rectangle(image, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            cv2.putText(image, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
            
        return image
    
    def publish_image(self, image):
        result = encoded_image = cv2.imencode(ext='.jpg', img=image)

        if result:
            msg = CompressedImage()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.format = "jpeg"
            msg.data = np.array(encoded_image).tobytes()


            self.cam_pub.publish(msg)
            self.get_logger().info("Publishing compressed image")

    def timer_callback(self):
        self.cap.get_frame()

        image = self.cap.frame
        
        input_data = self.__convert_image(image, floating = self.model.floating_model)
        
        t1 = cv2.getTickCount()
        
        # Perform the actual detection by running the model with the image as input
        with tf.device('/gpu:0'):
            self.model.interpreter.set_tensor(self.model.input_details[0]['index'],input_data)
            self.model.interpreter.invoke()

        # Retrieve detection results
        # self.extract_object(self.model.interpreter)
        image = self.draw_object(self.model.interpreter, image)

        cv2.putText(image,'infer_time: {0:2.5f}'.format(self.__calculate_inference_time(t1)),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)

        self.publish_image(image)

        # All the results have been drawn on the frame, so it's time to display it.
        # cv2.imshow('Object detector', image)

        # if cv2.waitKey(1) == ord('q'):
        #     cv2.destroyAllWindows()
        #     return

def main(args = None):
    rclpy.init(args=args)
    model = Model(CONST_PATH_MODEL, CONST_PATH_LABEL)
    object_detector = Detector(model)
    rclpy.spin(object_detector)
    object_detector.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
