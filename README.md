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
![Pasted image 20260219195059](../imgs/Pasted%20image%2020260219195059.png)
on the bottom left corner of the VScode click on the >< arrows and chose, `connect to WSL using distro` and the chose Ubuntu 

![Pasted image 20260219195702](../imgs/Pasted%20image%2020260219195702.png)


The bottom left corner will turn blue and will have `WSL: Ubutnu` shown.

![Pasted image 20260219200247](../imgs/Pasted%20image%2020260219200247.png)


On the terminal mane chose `New Terminal` and proceed with the rest of the tutorial
![Pasted image 20260219195023](../imgs/Pasted%20image%2020260219195023.png)

![Pasted image 20260219200601](../imgs/Pasted%20image%2020260219200601.png)


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




