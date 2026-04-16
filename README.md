# ROS2 Human Robot tic-tac-toe Game
This is a tic-tac-toe game for the uFactory xArm lite6 robot.
The robot uses a camera to detect the game status and then sends it to the game engine, which decides the next move and sends a position command from 0-8 to the motion module. Then the motion module takes the cell number and moves the robot to the required position and draws an X figure on the paper. 
### There are three main packages and nodes:
**1- Image package** 
**2- Game engine package**
**3- Motion package**


![ufactory2_ros2_rviz2](/imgs/ufactory2_ros2_rviz2.gif)


## Quick use ROS2: 
Clone the repository in your home directory in `/dev_ws`

### installation

Clone the repository in your home directory in `/dev_ws`
If you want to rebuild the packages yourself, remove the build and install and log folders using 
```
sudo rm -r -f build install log
```

For Ubuntu 24.02 you can use the  `installation.sh` to install the robot drivers and required files. 
(For other distros, follow the bash file and install the requirements also, Install `ROS2`, `Gazebo`, and `MoveIt` according to your OS).

```
chmod +x installation.sh
./installation.sh
```

For more details on the installation refer to [[[Installing ROS2 and xarm]]](#2--installing-ros2-and-xarm)

Before building the package make sure you are in `/dev_ws` and not in `/dev_ws/src`
Using `--symlink-install` argument makes it easier to edit your code, so to build, do this
```
colcon build --symlink-install
```

### Running the packages

Make sure you source ROS2 and the installations before you run each command in new terminals:
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

# Ubuntu in Windows 

This is an alternative approach to Virtual Machines. You can access Linux in your windows machine using **Windows Subsystem for Linux** (`WSL`). So, if your machine does not have Linux o.s installed you can still take advantage of your windows to create an Ubuntu machine inside your Windows o.s.


In this section we will install the prerequisites for robot drivers and simulations, including the installation of `ros2` and `Rviz`, and `Gazebo` plus the `robot drivers`.

 
# 1- Installing `WSL` and Ubuntu 24.04

Use this command in you windows power-shell. Open the windows power-shell in admin mode and type this:
### 1 Update `WSL`
First update the `wsl`
```
wsl --update
```
### 2 Install default Linux (Ubuntu 24.04)
To install the latest default Ubuntu:
```
wsl --install
```

#### 2.1 Other o.s options
In case you want to have a specific name:
Check for the available installations of Linux distros use:
```
wsl --list --online
```
copy the name of the operation system that you want to be using `<ctrl>+<c>` in our case it is 
#### 2.2 
To paste either use `<right-click>` or  `<ctrl>+<v>`
```
wsl --install Ubuntu-24.04
```


### 3 Set `WSL` to `WSL2`
You may upgrade your `WSL` to version 2 for your Ubuntu session (Ubuntu is your distro Name)
```
wsl --set-version Ubuntu 2
```

### 4 Run your Ubuntu session
To connect to the a currently created `WSL` in power-shell use(Ubuntu is the name):
```
 wsl --distribution Ubuntu
```
After this you should see your Ubuntu machine running as root
`(root@the_name_of_your_pc)`
### 5 Add a user
If you logged in as root create a user i.e `is3l`:
Create a name for your user account and a password if you are doing it for the second time (we chose `is3l` ):

`Create a default Unix user account: is3l`

```
adduser is3l
```
If you are logged in as a user already, skip 5 and 6 steps

Type and retype the password, and you are good to go. Now your Ubuntu is up and running if you see your username in the terminal. 
<span style="color:green">`>>is3l@your_computer_name`</span>
### 6 Give admin privileges to your user 
After you have created a new user, add it to the `sudo` group in order to have admin privileges:
```
adduser is3l sudo 
```

### 7 (optional for future use)
In power-shell, use this command to avoid logging in as `root` every time:
```
wsl --manage Ubuntu --set-default-user is3l
```

### 8 Exit `wsl` from power-shell and move to `VSCode` terminal
Exit the Ubuntu session:
```
exit
```


### 9 Just install `VScode`
Install `VScode` since we will be using the `VScode` terminal from now on

### Extra Note
To delete your distro:
and uninstall the Ubuntu from apps and programs in your windows:
```
wsl --terminate Ubuntu
```

```
 wsl --unregister Ubuntu
```


# 2- Installing `ROS2` and `xarm`
After installing the `VScode` we have to install these libraries:
1- installation of `ROS2`
2- installation of `Moveit2`
3- installation of `Gazebo`

 You can manually install the or use a ready-to-use script to install all of them. First the automatic installation is going to be explained and then the manual installation.
We will proceed with the rest of the tutorial in `VScode` terminal
After installing the `VScode` install  the `WSL` extension
![Pasted image 20260219195059](/imgs/Pasted%20image%2020260219195059.png)
on the bottom left corner of the VScode click on the >< arrows and chose, `connect to WSL using distro` and the chose Ubuntu 

![Pasted image 20260219195702](/imgs/Pasted%20image%2020260219195702.png)


The bottom left corner will turn blue and will have `WSL: Ubutnu` shown.

![Pasted image 20260219200247](/imgs/Pasted%20image%2020260219200247.png)


On the terminal mane chose `New Terminal` and proceed with the rest of the tutorial
![Pasted image 20260219195023](/imgs/Pasted%20image%2020260219195023.png)

![Pasted image 20260219200601](/imgs/Pasted%20image%2020260219200601.png)


To check your Ubuntu version use 
```
lsb_release -a
```
result should be something like:
```
	No LSB modules are available.
	Distributor ID: Ubuntu                                           
	Description:    Ubuntu 24.04.4 LTS
	Release:        24.04     
	Codename:       noble   
```



## Method 1


![ufactory_wsl2](/imgs/ufactory_wsl2.gif)


In the terminal create a file named `install.sh` using 
```
touch install.sh
```

Use `<left-click>+<ctrl>` to open the file in `VScode`
Then paste this script inside the empty file 
``` install.sh#!/bin/bash
#!/bin/bash
# Exit on error
set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== Starting script execution ===${NC}"
date

# Set ROS distribution early
export ROS_DISTRO=jazzy

# Locale setup
echo -e "${GREEN}Setting up locale...${NC}"
locale
sudo apt update
sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# Add repositories and install APT dependencies
echo -e "${YELLOW}Setting up repositories...${NC}"
sudo apt install software-properties-common curl lsb-release gnupg -y
sudo add-apt-repository universe -y

# Setup ROS APT source
echo -e "${MAGENTA}Installing ROS APT source...${NC}"
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

# Install ROS and tools
echo -e "${BLUE}Installing ROS and development tools...${NC}"
sudo apt update
sudo apt upgrade -y
sudo apt install ros-dev-tools ros-jazzy-desktop ros-jazzy-moveit -y

# Setup Gazebo
echo -e "${YELLOW}Setting up Gazebo...${NC}"
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt update
sudo apt install gz-jetty ros-jazzy-gz-* libsdformat14-dev -y

# Source ROS setup
source /opt/ros/jazzy/setup.bash

# Create workspace and clone repository
echo -e "${GREEN}Setting up ROS workspace...${NC}"
mkdir -p ~/dev_ws/src
cd ~/dev_ws/src
git clone https://github.com/xArm-Developer/xarm_ros2.git --recursive -b $ROS_DISTRO

# Initialize rosdep and install dependencies
echo -e "${MAGENTA}Initializing rosdep and installing dependencies...${NC}"
cd ~/dev_ws/src/xarm_ros2
git submodule update --init --recursive
git pull --recurse-submodules
sudo rosdep init
rosdep update
cd ~/dev_ws/src
rosdep install --from-paths . --ignore-src --rosdistro $ROS_DISTRO -y -r

# Build workspace
echo -e "${BLUE}Building workspace...${NC}"
cd ~/dev_ws
colcon build --symlink-install

# Source workspace
echo -e "${GREEN}Setting up environment...${NC}"
source /opt/ros/jazzy/setup.bash
source ~/dev_ws/install/setup.bash

# Persist ROS environment in bashrc
echo -e "${GREEN}Updating ~/.bashrc...${NC}"
if ! grep -Fxq "source /opt/ros/jazzy/setup.bash" ~/.bashrc; then
	echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
fi
if ! grep -Fxq "source ~/dev_ws/install/setup.bash" ~/.bashrc; then
	echo "source ~/dev_ws/install/setup.bash" >> ~/.bashrc
fi

echo -e "${CYAN}=== All commands completed successfully ===${NC}"
date

```

Then save the file and use this command to make it executable:
```
sudo chmod +x install.sh
```

And now we can run the installation script:
```
./install.sh
```

After the installation was complete you will see the successful message,

To test the robotic arm in the simulation first we have to source `ros2` and the `xarm` installation *for EACH TERMINAL that we open*
To source `ros2`:
```
source /opt/ros/jazzy/setup.bash 
```
To source `xarm`:
```
cd ~/dev_ws 
source install/setup.bash
```

To run a fake robot in `Rviz`:
```
ros2 launch xarm_moveit_servo lite6_moveit_servo_fake.launch.py
```

To control our fake robot using keyboard, open another terminal or split the terminal and source both `ros2` and `xarm` again, then:
```
ros2 run xarm_moveit_servo xarm_keyboard_input
```

using number keys and the `R` button you can move each axis `CW` or `CCW` also by using `,` and `;` you can move the robot in Cartesian coordinates


## Method 2
### ROS2 installation on Ubuttu 24.02

Source: https://docs.ros.org/en/ros2_documentation/jazzy/Installation.html

(We will install the binary files in this tutorial)
Paste these commands into your terminal and put your password if you were asked 
```
locale  # check for UTF-8

sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

locale  # verify settings
```

After a successful execution, use these commands,

```
sudo apt install software-properties-common
sudo add-apt-repository universe
```

```
sudo apt update && sudo apt install curl -y
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
```

Install developments tools (optional)

```
sudo apt update && sudo apt install ros-dev-tools -y
```

```
sudo apt update
```

```
sudo apt upgrade
```

```
sudo apt install ros-jazzy-desktop 
```

```
source /opt/ros/jazzy/setup.bash
```

Test one talker and listener seperately:
```
source /opt/ros/jazzy/setup.bash
ros2 run demo_nodes_cpp talker
```

```
source /opt/ros/jazzy/setup.bash
ros2 run demo_nodes_py listener
```

### MoveIt2 installation

```
sudo apt install ros-jazzy-moveit
```

### Gazebo installation

```
sudo apt-get update
sudo apt-get install curl lsb-release gnupg
```

```
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt-get update
sudo apt-get install gz-jetty
```


```
sudo apt-get install ros-$ROS_DISTRO-gz-*  # This installs Gazebo vendor packages for your ROS distro
```

```
sudo apt-get update
sudo apt-get install libsdformat14-dev
```

Check the gazebo version:
```
gz sim --version
```


### Install xarm 

```
cd ~
mkdir -p dev_ws/src
```

```
cd ~/dev_ws/src

git clone https://github.com/xArm-Developer/xarm_ros2.git --recursive -b $ROS_DISTRO
```


```
cd ~/dev_ws/src/xarm_ros2
git submodule update --init --recursive
git pull --recurse-submodules
```

```
sudo rosdep init
rosdep update
```

```
source /opt/ros/jazzy/setup.bash 
```

```
# Remember to source ros2 environment settings first
cd ~/dev_ws/src/
rosdep update
rosdep install --from-paths . --ignore-src --rosdistro $ROS_DISTRO -y -r
```

```
# Remember to source ros2 and moveit2 environment settings first
cd ~/dev_ws/

colcon build

colcon build --packages-select xarm_api
```


Source the `xarm` and `ros2` before using each terminal 
```
cd ~/dev_ws/
source install/setup.bash
source /opt/ros/jazzy/setup.bash  
```


## Motion Commands

## Robot Connection in simulation and Real

Use this command to open the `lite6` arm in a **simulation** for testing 
```
ros2 launch xarm_planner lite6_planner_fake.launch.py add_realsense_d435i:=true add_gripper:=true load_controller:=true use_sim_time:=true
```

or for the **real** robot you may use this(not tested):

```
ros2 launch xarm_planner lite6_planner_realmove.launch.py robot_ip:=192.168.1.160 add_gripper:=true load_controller:=true use_sim_time:=true
```




Do not forget to add Markers for the grid and the cross to the `Rviz`
( `grid_map_marker` and `cross_trajectory_marker`)
![Pasted image 20260305172035](/imgs/Pasted%20image%2020260305172035.png)

## Notes 

### Services to use as client for Cartesian movements
Using services to plan and execute a move. In this way we call a service to move the robot to a certain position.
You can `plan` a command and see if it is feasible then `execute` it, 

Command to `plan` a motion:
```
ros2 service call /xarm_pose_plan xarm_msgs/srv/PlanPose "{target: {position: {x: 0.3, y: -0.1, z: 0.2}, orientation: {x: 1.0, y: 0.0, z: 0.0, w: 0.0}}}"
```
For a straight path we can use:
```
ros2 service call /xarm_straight_plan xarm_msgs/srv/PlanSingleStraight "{target: {position: {x: 0.1, y: 0.1, z: 0.2 }, orientation: {x: 1.0, y: 0.0, z: 0.0, w: 0.0}}}"
```

Command to `execute` a motion:
```
ros2 service call /xarm_exec_plan xarm_msgs/srv/PlanExec "{wait: true}"
```

### Gripper activation for `lite6`

First go to this file and enable the `lite6_gripper` 
`~/dev_ws/src/xarm_ros2/xarm_api/config/xarm_params.yaml`
Edit these three lines:
```
open_lite6_gripper: true
close_lite6_gripper: true
stop_lite6_gripper: true
```

Now rebuild the package again using (in `~/dev_ws`):
```
colcon build --packages-select motion
```

Now you should be able to `open`, `close`, and `stop` the gripper's compressor using:
```
ros2 service call /ufactory/close_lite6_gripper xarm_msgs/srv/Call
ros2 service call /ufactory/open_lite6_gripper xarm_msgs/srv/Call
ros2 service call /ufactory/stop_lite6_gripper xarm_msgs/srv/Call
```

Now source again:
```
source ~/dev_ws/install/setup.bash
```

*Note: the gripper service in only available for the real robot*

## To send position goals to `MoveIt2` and monitoring in `Gazebo`

First run in order to call `MoveIt2` and `Gazebo` to run 
```
ros2 launch xarm_moveit_config lite6_moveit_gazebo.launch.py add_realsense_d435i:=true add_gripper:=true load_controller:=true use_sim_time:=true
```


Then in another terminal use this to send goal commands to `MoveIt` and in gazebo you will see the robot executing the action
```
ros2 action send_goal /move_action moveit_msgs/action/MoveGroup "{
  request: {
    group_name: 'lite6',
    goal_constraints: [{
      position_constraints: [{
        header: {frame_id: 'link_base'},
        link_name: 'link6',
        constraint_region: {
          primitive_poses: [{
            position: {x: 0.3, y: 0.1, z: 0.2},
            orientation: {x: 1.0, y: 0.0, z: 0.0, w: 0.0}
          }],
          primitives: [{type: 1, dimensions: [0.001, 0.001, 0.001]}]
        },
        weight: 1.0
      }]
    }],
    allowed_planning_time: 10.0,
    max_velocity_scaling_factor: 0.1,
    max_acceleration_scaling_factor: 0.1
  }
}"
```
# Mechanical Parts 

We have designed two 3D printed parts to hold the various pens with different sizes the spring could be softer and it is subjected to future re-designs 
An overview of the designated parts and the `.stl` files are available in `stl` folder.
![4](/imgs/4.jpg)
