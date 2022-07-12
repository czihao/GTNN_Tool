# GTNN_Tool
## Introduction
GTNN_tool is an open source GUI program that implements large-scale growth transform neural network in real-time. GTNN_tool provides full configurability of the neural network for the users, including the dynamics of the neural membrane potential evolution, inputs to the neurons, and connectivity among neurons. The tool also contains visuliazed probes that monitor the real-time power consumption of the network and the membrane potential updates of user-specified neurons. GTNN_tool grants user accessibity of large-scale GT neural network, which can be configured to take on different optimization tasks.  
## First Release
FIRST RELEASE SUPPOSED TO HAVE ROUTING AND NORMAL MODE, STILL WORKING ON ROUTING.  
Multiple pre-defined modes aiming to solve different optimization problem will be added in future releases.  
## Installation
Run installation script **install.sh** in the cloned repository  
`$ ./install.sh`
## GUI Interface
![GUI](/figures/fig_gui.png)
## Membrane Potential Probe
The probes provide real-time visualization of membrane potential updates for up to 5 different neurons. The probes take on indices from the user and display the real-time membrane potential update of the neurons specified by the incdices to the left of the membrane potential plot.  
## 
