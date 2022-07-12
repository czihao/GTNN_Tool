# GTNN_Tool
## Introduction
GTNN_tool is an open source GUI program that implements large-scale growth transform neural network in real-time. GTNN_tool provides full configurability of the neural network for the users, including the dynamics of the neural membrane potential evolution, inputs to the neurons, and connectivity among neurons. The tool also contains visuliazed probes that monitor the real-time power consumption of the network and the membrane potential updates of user-specified neurons. GTNN_tool grants user accessibity of large-scale GT neural network, which can be configured to take on different optimization tasks.  
## First Release
FIRST RELEASE SUPPOSED TO HAVE ROUTING AND NORMAL MODE, STILL WORKING ON ROUTING.  
Multiple pre-defined modes aiming to solve different optimization problem will be added in future releases.  
## Installation
Run installation script **install.sh** in the cloned repository  
`$ ./install.sh`  
After the required packages have been installed, then launch the GUI prgram by  
`$ ./gtnn_gui.py`
## GUI Interface
![GUI](/figures/fig_gui.png)
## Membrane Potential Probe
The probes provide real-time visualization of membrane potential updates for up to 5 different neurons. The probes take on indices from the user and display the real-time membrane potential update of the neurons specified by the incdices to the left of the membrane potential plot.  
## Energy Plot
This real-time energy plot monitors the power consumption of the entire network in arb. unit.
## Neural Model Parameters
User can configure the dynamics of the individual neuron through this panel. In the first release, the MODE dropbox contains 2 pre-defined mode, normal growth transform update rule and tweaked update rule for routing problem specifically, and the number of neurons should be kept below 100,000. RIGHT NOW ONLY NORMAL IS READY, ROUTING STILL NEED TO BE FIGURED OUT.
## Input Parameters
The GTNN_tool currently supports three modes of inputs: random, user file, and zero. Under random mode, one random input is generated for each neuron. The user can also specify a file that contains a N-by-1 array that represents inputs for each of the N neurons. 
## Neural Network Connectivity Parameters
5 modes have been implemented to generate different neural connectivity graphs. Random identity and random feedforward modes take three parameters: overall density value, number of recip, and btwn layer overlap %.  
 - **overall density value** This parameter dictates the number of layers (1/overall density) of the neural network. It is recommended to have less than 0.01% for networks that have more than 50,000 neurons. 
 - **number of recip** This parameter determines the number of reciprocal connections of the neural network.  
 - **btwn layer overlap** This parameter determines the percentage of overlap between layers in the network.
Identity and feedforward modes take 3 parameter: recip format file, layer format file, and btwn layer overlap %
 - **recip format file** This parameter reads a user defined file that contains the ((row, col), data) of all the reciprocal connection in the file.  
 - **layer format file** This parameter reads a user defined file that contains the (number of neuron, layer density) for each layer of the neural network.  
 - **btwn layer overlap** This parameter determines the percentage of overlap between layers in the network.
User data mode takes 1 parameter that reads the entire connectivity graph of the neural network in ((row, col), data) format.


