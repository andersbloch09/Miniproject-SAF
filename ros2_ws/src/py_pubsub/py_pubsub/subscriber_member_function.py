import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class xml_sub(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,                                              # CHANGE
            '/xml_data',
            self.listener_callback,
            10)
        self.subscription
        self.id_value = String()

    def listener_callback(self, msg):
        self.id_value = msg.data
        print("This value is the carrier ID  =  ",self.id_value)


def main(args=None):
    rclpy.init(args=args)

    xml_node = xml_sub()

    rclpy.spin(xml_node)

    xml_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()