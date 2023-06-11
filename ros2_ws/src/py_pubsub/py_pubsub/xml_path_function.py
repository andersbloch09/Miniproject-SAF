import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class XMLPublisherNode(Node):

    def __init__(self):
        super().__init__('xml_publisher_node')
        self.publisher_ = self.create_publisher(String, 'xml_file_path', 10)
        timer_period = 2.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        xml_file_path = '/home/ulf/Desktop/time.xml'
        msg = String()
        msg.data = xml_file_path
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing XML file path: ' + xml_file_path)

def main(args=None):
    rclpy.init(args=args)
    xml_publisher_node = XMLPublisherNode()
    rclpy.spin(xml_publisher_node)
    xml_publisher_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
