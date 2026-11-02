
#!/usr/bin/env python3

import math
import time

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor, ExternalShutdownException
from rclpy.node import Node

from my_robot_interfaces.action import Rotate


def yaw_from_quaternion(q):
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y),
        1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    )


def angle_difference(target, current):

    return math.atan2(
        math.sin(target - current),
        math.cos(target - current)
    )


class RotateServer(Node):

    def __init__(self):
        super().__init__('rotate_server')

        self.declare_parameter('turn_speed', 0.5)

        self.yaw = None

        group = ReentrantCallbackGroup()

        self.cmd_vel = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.create_subscription(
            Odometry,
            '/odom',
            self.on_odom,
            10,
            callback_group=group
        )

        self.action_server = ActionServer(
            self,
            Rotate,
            '/rotate',
            execute_callback=self.execute,
            goal_callback=self.on_goal,
            cancel_callback=lambda goal_handle: CancelResponse.ACCEPT,
            callback_group=group
        )

        self.get_logger().info('Rotate action server started')

    def on_odom(self, msg):
        self.yaw = yaw_from_quaternion(
            msg.pose.pose.orientation
        )

    def on_goal(self, goal):
        if abs(goal.angle) < 0.001 or self.yaw is None:
            return GoalResponse.REJECT

        return GoalResponse.ACCEPT

    def execute(self, goal_handle):

        goal = goal_handle.request.angle
        direction = 1.0 if goal > 0 else -1.0

        start_yaw = self.yaw
        turned = 0.0

        turn_speed = self.get_parameter('turn_speed').value

        twist = Twist()
        twist.angular.z = direction * turn_speed

        feedback = Rotate.Feedback()
        result = Rotate.Result()

        self.get_logger().info(
            f'Rotating {goal:.2f} radians'
        )

        while rclpy.ok():

            if goal_handle.is_cancel_requested:
                self.cmd_vel.publish(Twist())
                result.turned = turned
                goal_handle.canceled()
                return result

            current_yaw = self.yaw



            turned = angle_difference(current_yaw,start_yaw)
            previous_yaw = current_yaw

            progress = direction * turned

            feedback.turned = turned
            goal_handle.publish_feedback(feedback)

            if progress >= abs(goal):
                break

            self.cmd_vel.publish(twist)

            time.sleep(0.1)

        self.cmd_vel.publish(Twist())

        result.turned = turned
        goal_handle.succeed()

        self.get_logger().info(
            f'Rotation completed: {turned:.2f} radians'
        )

        return result


def main(args=None):
    rclpy.init(args=args)

    node = RotateServer()

    try:
        rclpy.spin(
            node,
            executor=MultiThreadedExecutor()
        )
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

