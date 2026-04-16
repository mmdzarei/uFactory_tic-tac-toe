#!/usr/bin/env python3
#dev_ws/motion/scripts/grid_to_pose.py
#https://github.com/mmdzarei/ufactory_motion.git
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from xarm_msgs.srv import PlanPose, PlanExec
# from xarm_msgs.srv import JointPose, JointExec
# from xarm_msgs.srv import PlanSingleStraight # test later if the planpose was not good enough for the cross motion

from std_msgs.msg import Float32MultiArray, Bool
from geometry_msgs.msg import Vector3
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
import sys

safe_z = 0.07



CROSS_HEIGHT = 0.056  # 0.057 is touching height 
CROSS_OFFSET = 0.015
HOME = 9
GRID_DISTANCE = 0.055# Grid positions: (grid_x, grid_y) -> (x, y, z)
OFFSET_to_RIGHT = 0.054 # for the pen
XXX = 0.22
GRID_MAP = {
            0: (XXX, -GRID_DISTANCE+OFFSET_to_RIGHT, safe_z),
            1: (XXX, 0.0+OFFSET_to_RIGHT, safe_z),
            2: (XXX, GRID_DISTANCE+OFFSET_to_RIGHT, safe_z), 

            3: (XXX+GRID_DISTANCE, -GRID_DISTANCE+OFFSET_to_RIGHT, safe_z), 
            4: (XXX+GRID_DISTANCE, 0.0+OFFSET_to_RIGHT, safe_z), 
            5: (XXX+GRID_DISTANCE, GRID_DISTANCE+OFFSET_to_RIGHT, safe_z), 

            6: (XXX+GRID_DISTANCE*2, -GRID_DISTANCE+OFFSET_to_RIGHT, safe_z),
            7: (XXX+GRID_DISTANCE*2, 0.0+OFFSET_to_RIGHT, safe_z),
            8: (XXX+GRID_DISTANCE*2, GRID_DISTANCE+OFFSET_to_RIGHT, safe_z),

            9: (0.21+GRID_DISTANCE, 0.09, 0.35)  # Home position
            }
                                        
marker_points = []
for i in range(4):
    for j in range(4):
        marker_points.append((0.22 - GRID_DISTANCE/2 + i*GRID_DISTANCE, OFFSET_to_RIGHT -3*GRID_DISTANCE/2 + j*GRID_DISTANCE, CROSS_HEIGHT))
print(marker_points)
marker_points = [marker_points[0], marker_points[1], marker_points[2], marker_points[3],
                marker_points[7], marker_points[6], marker_points[5], marker_points[4],
                marker_points[8], marker_points[9], marker_points[10], marker_points[11],
                marker_points[15], marker_points[14], marker_points[13], marker_points[12],
                marker_points[0], marker_points[1], marker_points[13], marker_points[14],marker_points[2], marker_points[3], marker_points[15],
                ]

class GridPlanner(Node):
    def __init__(self):
        super().__init__('grid_planner')
        self.pose_client = self.create_client(PlanPose, 'xarm_pose_plan')
        self.exec_client = self.create_client(PlanExec, 'xarm_exec_plan')
        self.pose_client.wait_for_service()
        self.exec_client.wait_for_service()
        self.gridmap_draw_pub = self.create_publisher(Marker, 'gridmap_marker', 10)



        # self.joint_client = self.create_client(PlanPose, 'xarm_joint_plan')
        # self.joint_exec_client = self.create_client(PlanExec, 'xarm_exec_plan')
        # self.joint_client.wait_for_service()
        # self.joint_exec_client.wait_for_service()

        # self.create_subscription(Float32MultiArray, 'grid_position', self.callback, 10)
        self.create_subscription(Vector3, 'grid_position', self.callback, 10)
        self.at_home_pub = self.create_publisher(Bool, 'robot_at_home', 10)
        self.cross_marker_pub = self.create_publisher(Marker, 'cross_trajectory_marker', 10)
        self.current_target = None
        self.current_pos = None
        self.cross_step = 0
        self.cross_trace_points = []
        self.dance_ok = False
        self.dance_pending = False  # Flag to trigger dance when at home
        # Move to home on startup
        self.get_logger().info('Moving to HOME on startup...')
        self.init_timer = self.create_timer(0.5, self.go_home_once)
        self.init_timer2 = self.create_timer(0.5, self.create_grid_marker)


    def create_grid_marker(self):

        marker2 = Marker()
        marker2.header.frame_id = "link_base"
        marker2.type = Marker.LINE_STRIP
        marker2.action = Marker.ADD
        marker2.pose.orientation.w = 1.0
        marker2.scale.x = 0.004
        marker2.color.r = 1.0
        marker2.color.g = 1.0
        marker2.color.b = 0.0
        marker2.color.a = 1.0
        
        for i, (x, y, z) in enumerate(marker_points):
            point = Point()
            point.x, point.y, point.z = x, y, z
            marker2.points.append(point)

            
        # marker.points = marker_points
        self.gridmap_draw_pub.publish(marker2)
        return marker2
    
    def go_home_once(self):
        self.move_to(HOME)
        self.get_logger().info("Published robot_at_home: True")
        self.gridmap_draw_pub.publish(self.create_grid_marker())
        self.init_timer.cancel()
        
    def callback(self, msg):
        # print(msg)
        # print(msg.x, msg.y)
        pass
        if not isinstance(msg.x, (int, float)) or not isinstance(msg.y, (int, float)):
            self.get_logger().error('grid_position needs [grip_position, game_status]')
            return
        self.get_logger().info(f'Received message: grip_position={msg.x}, game_status={msg.y}')
        if msg.y == 0:  # Game ongoing
            self.move_to(msg.x)
        elif msg.y == 1:  # Game draw
            self.get_logger().info('Game is a draw - moving to HOME')
            self.move_to(HOME)
        elif msg.y == 2:  # x has won
            self.get_logger().info('Game won by X - gonna dance after reaching home')
            self.dance_pending = True
            self.move_to(msg.x)  # Move to position, do cross motion, then return home
            
        elif msg.y == 3:  # o has won
            self.get_logger().info('Game won by O - moving to HOME')
            self.move_to(HOME)
        elif msg.y == 4:  
            self.get_logger().error(f'Unknown game status: {msg.y}')
            self.move_to(HOME)

    def move_to(self, grid_x, grid_y=0):
        # key = (int(grid_x), int(grid_y))
        key = (int(grid_x))
        if key not in GRID_MAP:
            self.get_logger().error(f'Invalid grid (only use 0-9 | 9 for home): {key}')
            return

        self.current_target = key
        x, y, z = GRID_MAP[key]
        self.current_pos = (x, y, z)
        pose = Pose()
        pose.position.x, pose.position.y, pose.position.z = float(x), float(y), float(z)
        pose.orientation.x, pose.orientation.w = 1.0, 0.0

        self.get_logger().info(f'Planning to pose: x={x}, y={y}, z={z}')
        plan_req = PlanPose.Request()
        plan_req.target = pose
        plan_future = self.pose_client.call_async(plan_req)
        plan_future.add_done_callback(self._on_plan_done)

    def _on_plan_done(self, future):
        result = future.result()
        if not result or not result.success:
            self.get_logger().error('Plan failed')
            return
        self.get_logger().info('Plan succeeded, executing...')
        exec_req = PlanExec.Request()
        exec_req.wait = True
        self.exec_client.call_async(exec_req).add_done_callback(self._on_exec_done)

    def _on_exec_done(self, future):
        result = future.result()
        if not result or not result.success:
            self.get_logger().error('Execution failed')
            return
        self.get_logger().info('Execution complete')
        
        # Publish if at home
        if self.current_target == HOME:
            msg = Bool()
            msg.data = True
            self.at_home_pub.publish(msg)
            self.get_logger().info('Robot at HOME - published to /robot_at_home')
            
            # Dance if pending
            if self.dance_pending:
                self.get_logger().info('Starting dance now that robot is at HOME')
                self.dance_pending = False
                self.dance()
            return
        
        # Execute cross motion if not at home
        self.get_logger().info('Starting cross motion')
        self.cross_step = 0
        self.cross_trace_points = []
        self.execute_cross_motion()

    def _publish_cross_marker(self):
        marker = Marker()
        marker.header.frame_id = 'link_base'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'cross_trajectory'
        marker.id = 0
        marker.type = Marker.LINE_LIST
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.004
        marker.color.r = 0.0
        marker.color.g = 1.0
        marker.color.b = 0.0
        marker.color.a = 1.0
        marker.points = self.cross_trace_points
        self.cross_marker_pub.publish(marker)

    def execute_cross_motion(self):
        if not self.current_pos:
            return
        
        x, y, z_safe = self.current_pos
        z = CROSS_HEIGHT
        
        cross_positions = [
            # (x + CROSS_OFFSET, y + CROSS_OFFSET, z_safe), 
            (x + CROSS_OFFSET, y + CROSS_OFFSET, z),  
            (x - CROSS_OFFSET, y - CROSS_OFFSET, z),
            (x - CROSS_OFFSET, y - CROSS_OFFSET, z_safe),  

            (x + CROSS_OFFSET, y - CROSS_OFFSET, z_safe),
            (x + CROSS_OFFSET, y - CROSS_OFFSET, z),
            (x - CROSS_OFFSET, y + CROSS_OFFSET, z),
            (x - CROSS_OFFSET, y + CROSS_OFFSET, z_safe),
        ]
        
        if self.cross_step >= len(cross_positions):
            self.get_logger().info('Cross motion complete, returning home...')
            self.move_to(HOME)
            return


        target_x, target_y, target_z = cross_positions[self.cross_step]
        if target_z == z: 
            p = Point()
            p.x = float(target_x)
            p.y = float(target_y)
            p.z = float(target_z)
            self.cross_trace_points.append(p)
            self._publish_cross_marker()

        pose = Pose()
        pose.position.x, pose.position.y, pose.position.z = float(target_x), float(target_y), float(target_z)
        pose.orientation.x, pose.orientation.w = 1.0, 0.0
        
        plan_req = PlanPose.Request()
        plan_req.target = pose
        plan_future = self.pose_client.call_async(plan_req)
        plan_future.add_done_callback(self._on_cross_plan_done)

    def _on_cross_plan_done(self, future):
        if not future.result().success:
            self.get_logger().error('Cross plan failed')
            return
        exec_req = PlanExec.Request()

        exec_req.wait = True
        self.exec_client.call_async(exec_req).add_done_callback(self._on_cross_exec_done)

    def _on_cross_exec_done(self, future):
        if not future.result().success:
            self.get_logger().error('Cross exec failed')
            return
        self.cross_step += 1
        self.execute_cross_motion()
        self.dance_ok = True

    def dance(self):
        x, y, z = 0.01, 0.01, 0.8
        self.current_pos = (x, y, z)
        pose = Pose()
        pose.position.x, pose.position.y, pose.position.z = float(x), float(y), float(z)
        pose.orientation.x, pose.orientation.w = 0.0, 1.0

        self.get_logger().info(f'Planning to dance to: x={x}, y={y}, z={z}')
        plan_req = PlanPose.Request()
        plan_req.target = pose
        plan_future = self.pose_client.call_async(plan_req)
        plan_future.add_done_callback(self._on_plan_done)
        

def main(args=None):
    rclpy.init(args=args)
    node = GridPlanner()
    
    # Logic for arguments and spinning
    if len(sys.argv) >= 3:
        node.move_to(float(sys.argv[1]), float(sys.argv[2])) # Note: sys.argv[0] is the script name
        rclpy.shutdown()
    else:
        rclpy.spin(node)
        rclpy.shutdown()


if __name__ == '__main__':
    main()
