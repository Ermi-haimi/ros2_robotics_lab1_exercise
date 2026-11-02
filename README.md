# ROS 2 Robotics Lab 1

**Course:** Introduction to Robotics and Intelligent Systems  
**Program:** BSc Software Engineering  
**University:** Addis Ababa University  
**Academic Year:** 2026

## Overview

A differential-drive robot simulation built with ROS 2 Jazzy and Gazebo Harmonic.

The project implements robot movement, obstacle detection, sensor integration, custom ROS 2 interfaces, and automated square driving.

## Packages

- `diffdrive_bot` – Robot model, Gazebo world, sensors, and basic control nodes.
- `lab_interfaces` – Custom obstacle message, speed service, and drive-distance action.
- `my_robot_interfaces` – Robot status message, turn-speed service, and rotation action.
- `my_robot_nodes` – Obstacle avoidance, rotation server, and square driver.

## Sensors

- LiDAR
- RGB camera
- Depth camera
- IMU

## Build

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --symlink-install --packages-up-to my_robot_nodes
source install/setup.bash
