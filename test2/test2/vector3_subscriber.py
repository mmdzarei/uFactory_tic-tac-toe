import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3


class Vector3Subscriber(Node):

    def __init__(self):
        super().__init__('vector3_subscriber')

        self.subscription = self.create_subscription(
            Vector3,
            '/vector_topic',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        # Call your custom function
        print("things go here")

def main(args=None):
    rclpy.init(args=args)

    node = Vector3Subscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
