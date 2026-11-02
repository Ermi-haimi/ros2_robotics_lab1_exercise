import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus

from lab_interfaces.action import DriveDistance
from my_robot_interfaces.action import Rotate


class SquareDriver(Node):

    def __init__(self):
        super().__init__('square_driver')

        self.declare_parameter('side_length', 0.5)

        self.drive_client = ActionClient(
            self, DriveDistance, '/drive_distance'
        )

        self.rotate_client = ActionClient(
            self, Rotate, '/rotate'
        )

    def send_goal(self, client, goal, action_name):
        self.get_logger().info(f'Sending {action_name} goal')

        if not client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error(f'{action_name} server not available')
            return False

        future = client.send_goal_async(
            goal,
            feedback_callback=lambda msg: None
        )

        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()

        if not goal_handle or not goal_handle.accepted:
            self.get_logger().error(f'{action_name} goal rejected')
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        response = result_future.result()

        if response.status != GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().error(f'{action_name} failed')
            return False

        return True

    def run_square(self):
        side_length = self.get_parameter('side_length').value

        for side in range(4):
            self.get_logger().info(
                f'Side {side + 1}/4: driving {side_length} metres'
            )

            drive_goal = DriveDistance.Goal()
            drive_goal.distance = float(side_length)

            if not self.send_goal(
                self.drive_client, drive_goal, 'drive_distance'
            ):
                return

            self.get_logger().info('Turning left 90 degrees')

            rotate_goal = Rotate.Goal()
            rotate_goal.angle = 1.5708

            if not self.send_goal(
                self.rotate_client, rotate_goal, 'rotate'
            ):
                return

        self.get_logger().info('Square completed!')


def main(args=None):
    rclpy.init(args=args)

    node = SquareDriver()

    try:
        node.run_square()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
