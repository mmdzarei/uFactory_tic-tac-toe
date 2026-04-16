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
