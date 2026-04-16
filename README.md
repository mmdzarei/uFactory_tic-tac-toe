# Human Robot tic-tac-toe Game
This is a tic-tac-toe game for the uFactory xArm lite6 robot.
The robot uses a camera to detect the game status and then sends it to the game engine, which decides the next move and sends a position command from 0-8 to the motion module. Then the motion module takes the cell number and moves the robot to the required position and draws an X figure on the paper. 
### There are three main packages and nodes:
**1- Image package** 
**2- Game engine package**
**3- Motion package**


## Quick use ROS2: 
Clone the repository in your home directory in `/dev_ws`

### installation

Clone the repository in your home directory in `/dev_ws`
Remove the build and install and log folders using 
```
sudo rm -r -f build install log
```

For Ubuntu 24.02 you can use the  `installation.sh` to install the robot drivers and required files. 
(For other distros, follow the bash file and install the requirements also, Install `ROS2`, `Gazebo`, and `MoveIt` according to your OS).

```
chmod +x installation.sh
./installation.sh
```

For more details on the installation refer to [[ufactory robot#2- Installing `ROS2` and `xarm`]]

Make sure you are in the `ROS2` packages in `/dev_ws` and not in `/dev_ws/src`

Using `--symlink-install` makes it easier to edit your codes
```
colcon build --symlink-install
```



### Running the packages

Make sure you source ROS2 and the installations before you run each command
```
source /opt/ros/humble/setup.bash 
source ~/dev_ws/install/setup.bash
```
#### 1- Robot Drivers
First connect to the robot using the appropriate `<IP ADDRESS>` for example: 
```
source /opt/ros/humble/setup.bash
source /dev_ws/install/setup.bash

ros2 launch xarm_planner lite6_planner_realmove.launch.py robot_ip:=192.168.1.181 add_gripper:=true load_controller:=true use_sim_time:=true
```

`RViz` has to be synced with the robot and all the joints are in similar positions in and outside the software.

#### 2- Image_package
In a new terminal 
```
source /opt/ros/humble/setup.bash
source /dev_ws/install/setup.bash
ros2 run img_package image_publisher_node 
```

The grid for the game has to be `3x3` and the whole grid has to be inside the camera window.
The circles must be closed.

#### 3- Motion package
In a new terminal 
```
source /opt/ros/humble/setup.bash
source /dev_ws/install/setup.bash
ros2 run motion_package grid_planner_node 
```

**ALERT: BE CAREFUL with the height of your pen or the tool.**
`CROSS_HEIGHT` >> The height of the paper
**USE High values first and reduce it according to the height of your pen and tool** 

Other values that you may modify frequently are:
`GRID_MAP`  >> 9 >> Home position is important for the cameras view
`safe_z` >> Safe height for the marker (like a rest position before reaching for drawing) 

After running this you can visualize the marker in `RViz` by adding the marker topics (one for grid, one for marker)
#### 4- Game 
**Be advised after running this node the robot will make the first move, so please always keep your hands on the EMERGENCY button** 

In a new terminal 
```
source /opt/ros/humble/setup.bash
source /dev_ws/install/setup.bash
ros2 run game_package game_engine_node 
```




