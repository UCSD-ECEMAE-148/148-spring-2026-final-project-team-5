# UCSD ECEMAE148 Team2 FinalProject
Team 5 Final Project Repository - Hazardous Location Recon

<img src="">
<img src="">

<div>
<h3>This is the github repo for Team 5 </h3>
<body>
  <p>
  Text Here.
  </p>
  
</body>


<div id="top"></div>

<h1 align="center">Hazardous Location Reconissance</h1>
<h4 align="center"></h4>
<!-- PROJECT LOGO -->
<br />
<div align="center">

<h3>ECEMAE148 Final Project</h3>
<p>
Team 5 Spring 26
</p>

<img src="">

</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  refer to Jose github 
</details>



<!-- TEAM MEMBERS -->
## Team Members

<div align="center">
    <p align = "center">Josiah, Kim, Kathya, AnMei</p>
</div>

<h4>Team Member Major and Class </h4>
<ul>
  <li>Josiah - ME</li>
  <li>Kim - </li>
  <li>Kathya -  </li>
  <li>AnMei - </li>
</ul>

<!-- Final Project -->
## Final Project
<!-- put stuff here -->

<!-- Original Goals -->
### Original Goals
Description Here
<!--example non visible text here -->
   
<!-- End Results -->
### Goals We Met
<p>
  Write Here
</p>

<p>
  new Paragraph
</p>
<p>
  more details
</p>


### If We Have Another Week...
#### Stretch Goal 1
more


#### Stretch Goal 2
more


## Final Project Documentation

<!-- Early Quarter -->
### CAD Design etc etc
<!--<img src="/media/full%20car%20cad.png" width="400" height="300" />-->

#### Open Source Parts
Use below as example from Jose \/
| Part | CAD Model | Source |
|------|--------|-----------|
| Jetson Nano Case | <img src="jetsonCAD.png" /> | [Thingiverse](https://www.thingiverse.com/thing:3532828) |

### Software

#### Embedded Systems
The system is running based on jetson nano and oakd-lite camera. 
<!--To run the system, we used a Jetson Nano with an Oakd depth camera, an ld06 lidar sensor, and a point one Fusion Engine gps. For motion we used a VESC Driver within the Donkey Car framework. https://www.donkeycar.com/-->

#### ROS2
<p>
In this section we will specifically show the steps to set-up GPS in ROS2.
</p>
<p>
  To get started, click into /ucsd_robocar_hub2 folder and you can see a lot of packages listed. Below is the main flow of the nodes interect with each other when we tested the gps:
</p>
  <img src="block_diagram.png">
<p>
  
</p>




### How to Run
Use the UCSD Robocar Docker images. Python3 is required, you might need to install other dependencies if needed.

Step 1: Once you setup your docker container, open a terminal, go into the docker container.

```docker start name_of_your_container```

```docker exec -it name_of_your_container bash```

```source_ros2```

Clone this repository into ros2_ws.

```git clone https://github.com/UCSD-ECEMAE-148/148-winter-2025-final-project-team-2.git```

```build_ros2```

Step 2: Then, you can have a quick start to run the robot car at the EBU courtyard!

Since this is an extension of the github repository from <a href="https://gitlab.com/ucsd_robocar2/ucsd_robocar_hub2">ucsd_robocar_hub2</a>, the default path file on the repository is a small circle inside the courtyard of EBU building. 
This is the image showing the default path being used:

 <img src="EBUcourtyard.png" >
 
To start your robot car to follow the path, simply run:

```ros2 launch ucsd_robocar_nav2_pkg all_nodes.launch.py```


Step 3: If you would like to change the gps lap for your robot car to run on, you can put your recorded .csv file inside /home/projects/ros2_ws/ebu2_courtyard/ebu2_courtyard_man_2.csv

```cd /home/projects/ros2_ws/ebu2_courtyard```

Copy paste your own file here:

```nano ebu2_courtyard_man_2.csv```

### Notice that your .csv file has to have the format of "lat,lon,alt" as the column name, for example:
<p>
lat,    lon,     alt
</p>
<p>
37.7749,-122.4194,30.0
</p>
<p>
34.0522,-118.2437,100.5
</p>
<p>
40.7128,-74.0060,50.2
</p>


Step 5: Finally, to get the car running on your custom path:

```source_ros2```

```build_ros2```

```ros2 launch ucsd_robocar_nav2_pkg all_nodes.launch.py ```


Youtube link of our robot following EBU courtyard(small circle in the middle):
<a href= "https://www.youtube.com/shorts/zIVCutLHt0U">Demo Video of car running on GPS</a>

Slides are also published onto this repository.

<!-- Authors -->
## Authors

Andrew N, Daphne, Jose, and Rodolfo


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

*Big thanks to Professor Jack Silberman, our TA Alexander Haken and Winston Chou, you guys are super amazing and helpful! Thank you Alexander for the readme template.*


<!-- CONTACT -->
## Contact

* Andrew | ann054@ucsd.edu
* Daphne | hsc021@ucsd.edu 
* Jose
* Rodolfo | rpgonzalez@ucsd.edu
