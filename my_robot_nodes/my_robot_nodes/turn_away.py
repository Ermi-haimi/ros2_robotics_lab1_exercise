
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter

from geometry_msgs.msg import Twist
from lab_interfaces.msg import ObstacleInfo
from my_robot_interfaces.msg import RobotStatus
from my_robot_interfaces.srv import SetTurnSpeed
from std_srvs.srv import SetBool


class TurnAway(Node):

    def __init__(self):
        super().__init__('turn_away')


        self.declare_parameter('forward_speed', 0.2)
        self.declare_parameter('turn_speed', 0.5)
        self.declare_parameter('max_turn_speed', 1.5)


        self.enabled = False
        self.last_obstacle_distance = float('inf')

        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.subscription = self.create_subscription(
            ObstacleInfo,
            '/obstacle',
            self.obstacle_callback,
            10
        )


        self.status_publisher = self.create_publisher(
            RobotStatus,
            '/robot_status',
            10
        )

        self.enable_service = self.create_service(
            SetBool,
            '/turn_away_enable',
            self.enable_callback
        )

        self.speed_service = self.create_service(
            SetTurnSpeed,
            '/set_turn_speed',
            self.set_turn_speed_callback
        )

        self.get_logger().info('Turn Away node started (disabled)')

    def obstacle_callback(self, msg):

        self.last_obstacle_distance = msg.distance

        cmd = Twist()
        status = RobotStatus()

        status.obstacle_distance = msg.distance

        if not self.enabled:
            status.state = 'stopped'

        else:
            forward_speed = self.get_parameter(
                'forward_speed'
            ).value

            turn_speed = self.get_parameter(
                'turn_speed'
            ).value

            if not msg.too_close:
                cmd.linear.x = forward_speed
                cmd.angular.z = 0.0
                status.state = 'forward'

            else:
                cmd.linear.x = 0.0

                if msg.angle > 0:
                    cmd.angular.z = -turn_speed
                else:
                    cmd.angular.z = turn_speed

                status.state = 'turning'

        self.publisher.publish(cmd)
        self.status_publisher.publish(status)

    def enable_callback(self, request, response):

        self.enabled = request.data

        if not self.enabled:
            # Stop the robot immediately
            self.publisher.publish(Twist())

            status = RobotStatus()
            status.state = 'stopped'
            status.obstacle_distance = self.last_obstacle_distance
            self.status_publisher.publish(status)

            response.message = 'robot disabled and stopped'

        else:
            response.message = 'robot enabled'

        response.success = True

        self.get_logger().info(response.message)

        return response

    def set_turn_speed_callback(self, request, response):

        turn_speed = request.turn_speed
        max_turn_speed = self.get_parameter(
            'max_turn_speed'
        ).value

        if turn_speed <= 0 or turn_speed > max_turn_speed:
            response.success = False
            response.message = (
                f'turn speed must be above 0 and at most '
                f'{max_turn_speed} rad/s'
            )

        else:
            self.set_parameters([
                Parameter('turn_speed', value=float(turn_speed))
            ])

            response.success = True
            response.message = f'turn speed set to {turn_speed} rad/s'

        self.get_logger().info(response.message)

        return response


def main(args=None):
    rclpy.init(args=args)

    node = TurnAway()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

