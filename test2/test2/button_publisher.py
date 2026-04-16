

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import threading

class ButtonPublisher(Node):

    def __init__(self):
        super().__init__('button_publisher')
        self.publisher_ = self.create_publisher(String, 'button_topic', 10)
        self.get_logger().info("Press ENTER to simulate button press...")

        # Run input listener in separate thread so ROS can spin
        self.input_thread = threading.Thread(target=self.wait_for_input)
        self.input_thread.daemon = True
        self.input_thread.start()

    def wait_for_input(self):
        while rclpy.ok():
            input()  # Wait for Enter key
            msg = String()
            msg.data = "Button pressed!"
            self.publisher_.publish(msg)
            self.get_logger().info(f'Published: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = ButtonPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()


