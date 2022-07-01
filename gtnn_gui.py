import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLineEdit, QComboBox, QLabel, QMessageBox, QInputDialog, QSlider
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
# from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import time
import threading
import matplotlib
from scipy.sparse import csr_matrix, vstack, block_diag, coo_matrix

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar

import gtnn_functions as gtnn
from gtnn_config import arg_list


# matplotlib.use("Qt5Agg")

I = np.empty((0))
Q = np.empty((0))

def setCustomSize(x, width, height):
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(x.sizePolicy().hasHeightForWidth())
    x.setSizePolicy(sizePolicy)
    x.setMaximumSize(QtCore.QSize(width, height))



class CustomMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        global arg_list, I, Q
        popup = QInputDialog()
        popup.setWindowTitle("Number of neurons")
        num, ok = QInputDialog.getInt(popup, "Number of neurons", "enter a number btwn 5 to 100,000",\
             value=5, min=5, max = 100000)
        if ok:
            arg_list['NUM_NEURON'] = num
            I = np.zeros((arg_list['NUM_NEURON'], 1), dtype=np.float16)

        super(CustomMainWindow, self).__init__()

        # Define the geometry of the main window
        # self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("GTNN Simulation Tool V1.0")

        # Create FRAME_A
        self.FRAME_A = QtWidgets.QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(210, 210, 235, 255).name())
        self.outer_layout = QtWidgets.QGridLayout()
        self.FRAME_A.setLayout(self.outer_layout)
        self.setCentralWidget(self.FRAME_A)

        self.plot_layout = QtWidgets.QGridLayout()
        self.config_layout = QtWidgets.QGridLayout()

        self.vplot_layout = QtWidgets.QGridLayout()
        self.config_param_layout = QtWidgets.QGridLayout()
        self.config_input_layout = QtWidgets.QGridLayout()
        self.config_Q_layout = QtWidgets.QHBoxLayout()
        self.config_connectivity_layout = QtWidgets.QGridLayout()
        self.Qplot_layout = QtWidgets.QGridLayout()


        


        # self.FRAME_A.setLayout(self.LAYOUT_A)
        # self.setCentralWidget(self.FRAME_A)


        ###############################################################################################################
        #                                      Parameter Configuration Layout                                         #
        ###############################################################################################################
        self._param_numneuron = QLineEdit(self)
        self._param_numneuron.setText(str(arg_list['NUM_NEURON']))
        self._param_numneuron.returnPressed.connect(self.update_param)
        self._param_vmax = QLineEdit(self)
        self._param_vmax.setText(str(arg_list['VMAX']))
        self._param_vmax.returnPressed.connect(self.update_param)
        self._param_dt = QLineEdit(self)
        self._param_dt.setText(str(arg_list['DT']))
        self._param_dt.returnPressed.connect(self.update_param)
        self._param_tmax = QLineEdit(self)
        self._param_tmax.setText(str(arg_list['TMAX']))
        self._param_tmax.returnPressed.connect(self.update_param)
        self._param_tau = QLineEdit(self)
        self._param_tau.setText(str(arg_list['TAU']))
        self._param_tau.returnPressed.connect(self.update_param)
        self._param_eta = QLineEdit(self)
        self._param_eta.setText(str(arg_list['ETA']))
        self._param_eta.returnPressed.connect(self.update_param)
        
        self._param_c = QLineEdit(self)
        self._param_c.setText(str(arg_list['C']))
        self._param_c.returnPressed.connect(self.update_param) 
        self._param_vth = QLineEdit(self)
        self._param_vth.setText(str(arg_list['VTH']))
        self._param_vth.returnPressed.connect(self.update_param) 
        self._param_lambda = QLineEdit(self)
        self._param_lambda.setText(str(arg_list['LAMBDA']))
        self._param_lambda.returnPressed.connect(self.update_param)

        self._label_param_dt = QLabel(self)
        self._label_param_dt.setText("dt")
        self._label_param_tau = QLabel(self)
        self._label_param_tau.setText("tau")
        self._label_param_vmax = QLabel(self)
        self._label_param_vmax.setText("Vmax")
        self._label_param_tmax = QLabel(self) 
        self._label_param_tmax.setText("Tmax")
        self._label_param_numneuron = QLabel(self)
        self._label_param_numneuron.setText("#neuron")
        self._label_param_eta = QLabel(self)
        self._label_param_eta.setText("eta")
        
        self._label_param_c = QLabel(self)
        self._label_param_c.setText("C")
        self._label_param_lambda = QLabel(self)
        self._label_param_lambda.setText("lambda")
        self._label_param_vth = QLabel(self)
        self._label_param_vth.setText("Vth")

        self.startBtn = QtWidgets.QPushButton(text='start')
        setCustomSize(self.startBtn, 100, 50)
        self.startBtn.clicked.connect(self.startBtnAction)

        self._dropdown_updateMode = QComboBox(self)
        self._dropdown_updateMode.addItems(["routing", "combinatorial", "normal"])
        self._dropdown_updateMode.setCurrentIndex(0)
        self.updateMode = self._dropdown_updateMode.currentText()
        self._dropdown_updateMode.currentTextChanged.connect(self.update_param)

        self._slider_speed = QSlider(QtCore.Qt.Horizontal)
        self._slider_speed.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._slider_speed.setTickPosition(QSlider.TicksBothSides)
        self._slider_speed.setTickInterval(10)
        self._slider_speed.setSingleStep(1)
        self._slider_speed.valueChanged.connect(self.update_speed)
        self.speed = self._slider_speed.value()

        self.config_param_layout.addWidget(self.startBtn, 1, 0)
        self.config_param_layout.addWidget(self._dropdown_updateMode, 2, 0)
        self.config_param_layout.addWidget(self._slider_speed, 3, 0)
        
        self.config_param_layout.addWidget(self._param_dt, 1, 1)
        self.config_param_layout.addWidget(self._param_tau, 3, 1)
        self.config_param_layout.addWidget(self._param_vmax, 5, 1)
        self.config_param_layout.addWidget(self._param_tmax, 7, 1)
        self.config_param_layout.addWidget(self._param_numneuron, 1, 2)
        self.config_param_layout.addWidget(self._param_eta, 3, 2)
        
        self.config_param_layout.addWidget(self._param_c, 7, 2)
        self.config_param_layout.addWidget(self._param_lambda, 1, 3)
        self.config_param_layout.addWidget(self._param_vth, 3, 3)

        self.config_param_layout.addWidget(self._label_param_dt, 0, 1)
        self.config_param_layout.addWidget(self._label_param_tau, 2, 1)
        self.config_param_layout.addWidget(self._label_param_vmax, 4, 1)
        self.config_param_layout.addWidget(self._label_param_tmax, 6, 1)
        self.config_param_layout.addWidget(self._label_param_numneuron, 0, 2)
        self.config_param_layout.addWidget(self._label_param_eta, 2, 2)
        
        self.config_param_layout.addWidget(self._label_param_c, 6, 2)
        self.config_param_layout.addWidget(self._label_param_lambda, 0, 3)
        self.config_param_layout.addWidget(self._label_param_vth, 2, 3)

        

        ###############################################################################################################
        #                                           Input configuration Layout                                        #
        ###############################################################################################################
        self.input_file = QLineEdit(self)
        # MODE: "random", "user file", "zero"
        self._dropdown_Iformat = QComboBox(self)
        self._dropdown_Iformat.addItems(["random", "user file", "zero"])
        self._dropdown_Iformat.setCurrentIndex(0)
        self._dropdown_Iformat.currentTextChanged.connect(self.init_I)
        
        self.mode_I = self._dropdown_Iformat.currentText()
        if np.char.equal(self.mode_I, 'user file'):
            self.input_file.show()
            self.file_I = self.input_file.text()
        else:
            self.input_file.hide()
            self.file_I = None
        I = gtnn.generateI(self.mode_I, self.file_I)

        self.input_label_neuron = QLabel(self)
        self.input_label_neuron.setText("neuron")
        self.input_label_value = QLabel(self)
        self.input_label_value.setText("value")
        self.input_neuron_1 = QLineEdit(self)
        self.input_neuron_1.setText("0")
        self.input_neuron_1.returnPressed.connect(self.update_input_neuron) 
        self.input_neuron_2 = QLineEdit(self)
        self.input_neuron_2.setText("1")
        self.input_neuron_2.returnPressed.connect(self.update_input_neuron)
        self.input_neuron_3 = QLineEdit(self)
        self.input_neuron_3.setText("2")
        self.input_neuron_3.returnPressed.connect(self.update_input_neuron)
        self.input_neuron_4 = QLineEdit(self)
        self.input_neuron_4.setText("3")
        self.input_neuron_4.returnPressed.connect(self.update_input_neuron)
        self.input_neuron_5 = QLineEdit(self)
        self.input_neuron_5.setText("4")
        self.input_neuron_5.returnPressed.connect(self.update_input_neuron)
        
        self.input_neuron_1_value = QLineEdit(self)
        temp = float(I[int(self.input_neuron_1.text()), :])
        self.input_neuron_1_value.setText(str(temp))
        self.input_neuron_1_value.returnPressed.connect(self.update_input) 
        self.input_neuron_2_value = QLineEdit(self)
        temp = float(I[int(self.input_neuron_2.text()), :])
        self.input_neuron_2_value.setText(str(temp))
        self.input_neuron_2_value.returnPressed.connect(self.update_input)
        self.input_neuron_3_value = QLineEdit(self)
        temp = float(I[int(self.input_neuron_3.text()), :])
        self.input_neuron_3_value.setText(str(temp))
        self.input_neuron_3_value.returnPressed.connect(self.update_input)
        self.input_neuron_4_value = QLineEdit(self)
        temp = float(I[int(self.input_neuron_4.text()), :])
        self.input_neuron_4_value.setText(str(temp))
        self.input_neuron_4_value.returnPressed.connect(self.update_input)
        self.input_neuron_5_value = QLineEdit(self)
        temp = float(I[int(self.input_neuron_5.text()), :])
        self.input_neuron_5_value.setText(str(temp))
        self.input_neuron_5_value.returnPressed.connect(self.update_input)

        self.update_input()

        self.config_input_layout.addWidget(self._dropdown_Iformat, 0, 0)
        self.config_input_layout.addWidget(self.input_file, 0, 1)

        self.config_input_layout.addWidget(self.input_label_neuron, 1, 0)
        self.config_input_layout.addWidget(self.input_label_value, 1, 1)
        
        self.config_input_layout.addWidget(self.input_neuron_1, 2, 0)
        self.config_input_layout.addWidget(self.input_neuron_2, 3, 0)
        self.config_input_layout.addWidget(self.input_neuron_3, 4, 0)
        self.config_input_layout.addWidget(self.input_neuron_4, 5, 0)
        self.config_input_layout.addWidget(self.input_neuron_5, 6, 0)

        self.config_input_layout.addWidget(self.input_neuron_1_value, 2, 1)
        self.config_input_layout.addWidget(self.input_neuron_2_value, 3, 1)
        self.config_input_layout.addWidget(self.input_neuron_3_value, 4, 1)
        self.config_input_layout.addWidget(self.input_neuron_4_value, 5, 1)
        self.config_input_layout.addWidget(self.input_neuron_5_value, 6, 1)
        

        ###############################################################################################################
        #                                                 Vplot Layout                                                #
        ###############################################################################################################
        self.vplot1 = CustomFigCanvas()
        self.vplot_layout.addWidget(self.vplot1, 0, 1)
        self.vplot2 = CustomFigCanvas()
        self.vplot_layout.addWidget(self.vplot2, 1, 1)
        self.vplot3 = CustomFigCanvas()
        self.vplot_layout.addWidget(self.vplot3, 2, 1)
        self.vplot4 = CustomFigCanvas()
        self.vplot_layout.addWidget(self.vplot4, 3, 1)
        self.vplot5 = CustomFigCanvas()
        self.vplot_layout.addWidget(self.vplot5, 4, 1)

        self.vplot_1 = QLineEdit(self)
        self.vplot_1.setText("0")
        self.vplot_1.returnPressed.connect(self.update_neuron) 
        self.vplot_2 = QLineEdit(self)
        self.vplot_2.setText("1")
        self.vplot_2.returnPressed.connect(self.update_neuron)
        self.vplot_3 = QLineEdit(self)
        self.vplot_3.setText("2")
        self.vplot_3.returnPressed.connect(self.update_neuron)
        self.vplot_4 = QLineEdit(self)
        self.vplot_4.setText("3")
        self.vplot_4.returnPressed.connect(self.update_neuron)
        self.vplot_5 = QLineEdit(self)
        self.vplot_5.setText("4")
        self.vplot_5.returnPressed.connect(self.update_neuron)

        self.vplot_layout.addWidget(self.vplot_1, 0, 0)
        self.vplot_layout.addWidget(self.vplot_2, 1, 0)
        self.vplot_layout.addWidget(self.vplot_3, 2, 0)
        self.vplot_layout.addWidget(self.vplot_4, 3, 0)
        self.vplot_layout.addWidget(self.vplot_5, 4, 0)

        ###############################################################################################################
        #                                          Connectivity Layout                                                #
        ###############################################################################################################
        self._dropdown_Qshape = QComboBox(self)
        self._dropdown_Qshape.addItems(["random identity", "identity", "random feedforward", "feedforward", "user data"])
        self._dropdown_Qshape.setCurrentIndex(0)
        self._dropdown_Qshape.currentTextChanged.connect(self.update_Qparam)
        
        self.update_Qconfig = QtWidgets.QPushButton(text='update')
        # setCustomSize(self.updateBtn, 100, 50)
        self.update_Qconfig.clicked.connect(self.update_Qparam)

        self._label_overlap = QLabel(self)
        self._label_overlap.setText("btwn layer overlap %")
        self._overlap = QLineEdit(self)
        self._overlap.setText(str(arg_list['OVERLAP']))
        
        # ff and identity takes user file
        # user defined layer sizes and density, user defined sparse recip
        self._ff_label_num_recip = QLabel(self)
        self._ff_label_num_recip.setText("recip format file")
        self._ff_num_recip = QLineEdit(self)
        self._ff_num_recip.setText(str(arg_list['RECIP_FILE']))
        self._ff_label_layer_density = QLabel(self)
        self._ff_label_layer_density.setText("layer format file")
        self._ff_layer_density = QLineEdit(self)
        self._ff_num_recip.setText(str(arg_list['LAYER_FILE']))

        # random takes density value
        # random layer sizes, userdefined overall density and recip density
        self._rand_label_num_recip = QLabel(self)
        self._rand_label_num_recip.setText("number of recip")
        self._rand_num_recip = QLineEdit(self)
        self._rand_num_recip.setText(str(arg_list['NUM_RECIP']))
        self._rand_label_layer_density = QLabel(self)
        self._rand_label_layer_density.setText("overall density value")
        self._rand_layer_density = QLineEdit(self)
        self._rand_layer_density.setText(str(arg_list['LAYER_DENSITY']))

        # user data takes entire Q
        self._Q_file = QLineEdit(self)
        self._Q_file.setText(str(arg_list['QFILE']))
        self._label_Q_file = QLabel(self)
        self._label_Q_file.setText("connectivity file")

        self._canvas_Q = MatCanvas(self, width=5, height=4, dpi=100)

        self.update_Qparam()
        # self.init_Q()
        
        # QPlot
        # norm = matplotlib.colors.Normalize()
        # self._canvas_Q.axes.imshow(Q.toarray(), norm=norm, cmap=plt.cm.gray)
        # self._canvas_Q.axes.set_xticks([])
        # self._canvas_Q.axes.set_yticks([])
                
        self.config_connectivity_layout.addWidget(self._dropdown_Qshape, 0, 0)
        self.config_connectivity_layout.addWidget(self._label_overlap, 1, 0)
        self.config_connectivity_layout.addWidget(self._overlap, 1, 1)
        # Hide when random
        self.config_connectivity_layout.addWidget(self._ff_label_num_recip, 2, 0)
        self.config_connectivity_layout.addWidget(self._ff_num_recip, 2, 1)
        self.config_connectivity_layout.addWidget(self._ff_label_layer_density, 3, 0)
        self.config_connectivity_layout.addWidget(self._ff_layer_density, 3, 1)
        # Hide when not random
        self.config_connectivity_layout.addWidget(self._rand_label_num_recip, 2, 0)
        self.config_connectivity_layout.addWidget(self._rand_num_recip, 2, 1)
        self.config_connectivity_layout.addWidget(self._rand_label_layer_density, 3, 0)
        self.config_connectivity_layout.addWidget(self._rand_layer_density, 3, 1)
        # Hide when not user data
        self.config_connectivity_layout.addWidget(self._Q_file, 1, 1)
        self.config_connectivity_layout.addWidget(self._label_Q_file, 1, 0)

        self.config_connectivity_layout.addWidget(self.update_Qconfig, 4, 0)

        self.Qplot_layout.addWidget(self._canvas_Q, 0, 2)

        
        # Add the callbackfunc to ..
        # self.myDataLoop = threading.Thread(name='myDataLoop', target=dataSendLoop, daemon=True, args=([self.addData_callbackFunc]))
        self.myGTNN = threading.Thread(name='myGTNN', target=self.gtnn_evolve, daemon=True)
        # self.myDataLoop = threading.Thread(name='myDataLoop', target=self.dataSendLoop, daemon=True)
        # self.myDataLoop.start()
        
        # self.update_signal = Communicate()
        # self.update_signal.data_signal[bool].connect(self.updateI)
        
        # self.plot_layout.addLayout(self.probe_layout, 0, 0)
        self.plot_layout.addLayout(self.vplot_layout, 0, 0)

        self.config_Q_layout.addLayout(self.config_connectivity_layout, 0)
        self.config_Q_layout.addLayout(self.Qplot_layout, 1)
        
        self.config_layout.addLayout(self.config_param_layout, 0, 0)
        self.config_layout.addLayout(self.config_input_layout, 0, 1)
        self.config_layout.addLayout(self.config_Q_layout, 0, 2)

        self.outer_layout.addLayout(self.plot_layout, 0, 0)
        self.outer_layout.addLayout(self.config_layout, 1, 0)

        self.show()

    def startBtnAction(self):
        self.myGTNN.start()
    
    def update_speed(self):
        self.speed = self._slider_speed.value()

    def init_I(self):
        global I, arg_list
        self.mode_I = self._dropdown_Iformat.currentText()
        if np.char.equal(self.mode_I, 'user file'):
            self.input_file.show()
            self.file_I = self.input_file.text()
        else:
            self.input_file.hide()
            self.file_I = None

        I = gtnn.generateI(self.mode_I, self.file_I)

        temp = float(I[int(self.input_neuron_1.text()), :])
        self.input_neuron_1_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_2.text()), :])
        self.input_neuron_2_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_3.text()), :])
        self.input_neuron_3_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_4.text()), :])
        self.input_neuron_4_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_5.text()), :])
        self.input_neuron_5_value.setText(str(temp))
    
    # Update the input into neurons
    # Called upon when enter is pressed for input value text boxes
    def update_input(self):
        global I, arg_list
        I[int(self.input_neuron_1.text())] = float(self.input_neuron_1_value.text())
        I[int(self.input_neuron_2.text())] = float(self.input_neuron_2_value.text())
        I[int(self.input_neuron_3.text())] = float(self.input_neuron_3_value.text())
        I[int(self.input_neuron_4.text())] = float(self.input_neuron_4_value.text())
        I[int(self.input_neuron_5.text())] = float(self.input_neuron_5_value.text())

        print("update input value")

    # Update the neuron that receives the input and displayed in plot
    # Called upon enter is pressed for input neuron text boxes
    def update_neuron(self):
        global I, arg_list

        self.input_neuron_1.setText(self.vplot_1.text())
        self.input_neuron_2.setText(self.vplot_2.text())
        self.input_neuron_3.setText(self.vplot_3.text())
        self.input_neuron_4.setText(self.vplot_4.text())
        self.input_neuron_5.setText(self.vplot_5.text())

        temp = float(I[int(self.input_neuron_1.text()), :])
        self.input_neuron_1_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_2.text()), :])
        self.input_neuron_2_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_3.text()), :])
        self.input_neuron_3_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_4.text()), :])
        self.input_neuron_4_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_5.text()), :])
        self.input_neuron_5_value.setText(str(temp))

        return None
    def update_input_neuron(self):
        global I, arg_list

        self.vplot_1.setText(self.input_neuron_1.text())
        self.vplot_2.setText(self.input_neuron_2.text())
        self.vplot_3.setText(self.input_neuron_3.text())
        self.vplot_4.setText(self.input_neuron_4.text())
        self.vplot_5.setText(self.input_neuron_5.text())

        temp = float(I[int(self.input_neuron_1.text()), :])
        self.input_neuron_1_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_2.text()), :])
        self.input_neuron_2_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_3.text()), :])
        self.input_neuron_3_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_4.text()), :])
        self.input_neuron_4_value.setText(str(temp))
        temp = float(I[int(self.input_neuron_5.text()), :])
        self.input_neuron_5_value.setText(str(temp))

    # Update the global parameter arg_list
    # Called upon enter is pressed for parameter text boxes
    def update_param(self):
        
        # self.update_signal.data_signal[bool].emit(True)
        arg_list['DT'] = float(self._param_dt.text())
        arg_list['NUM_NEURON'] = int(self._param_numneuron.text())
        arg_list['TAU'] = float(self._param_tau.text())
        arg_list['TMAX'] = float(self._param_tmax.text())
        arg_list['VMAX'] = float(self._param_vmax.text())
        arg_list['ETA'] = float(self._param_eta.text())
        arg_list['LAMBDA'] = float(self._param_lambda.text())
        arg_list['VTH'] = float(self._param_vth.text())
        arg_list['C'] = float(self._param_c.text())
        self.updateMode = self._dropdown_updateMode.currentText()
        # self.myDataLoop = threading.Thread(name='myDataLoop', target=dataSendLoop, daemon=True, args=([self.addData_callbackFunc]))
        # self.myDataLoop.start()
    # def init_Q(self):
    #     global Q, arg_list
    #     self.mode_Q = self._dropdown_Qshape.currentText()
    #     Q = gtnn.generateQ(self.mode_Q)
    #     pass

    def update_Qparam(self):
        global arg_list, Q
        mode = self._dropdown_Qshape.currentText()
        if np.char.equal(mode, "identity") or\
           np.char.equal(mode, "feedforward"):
            self._ff_label_layer_density.show()
            self._ff_label_num_recip.show()
            self._ff_layer_density.show()
            self._ff_num_recip.show()
            self._rand_label_layer_density.hide()
            self._rand_label_num_recip.hide()
            self._rand_layer_density.hide()
            self._rand_num_recip.hide()
            self._label_Q_file.hide()
            self._Q_file.hide()
            self._label_overlap.show()
            self._overlap.show()
            arg_list['RECIP_FILE'] = str(self._ff_num_recip.text())
            arg_list['LAYER_FILE'] = str(self._ff_layer_density.text())
            arg_list['OVERLAP'] = float(self._overlap.text())
            
            
        elif np.char.equal(mode, "random identity") or\
             np.char.equal(mode, "random feedforward"):

            self._ff_label_layer_density.hide()
            self._ff_label_num_recip.hide()
            self._ff_layer_density.hide()
            self._ff_num_recip.hide()
            self._rand_label_layer_density.show()
            self._rand_label_num_recip.show()
            self._rand_layer_density.show()
            self._rand_num_recip.show()
            self._label_Q_file.hide()
            self._Q_file.hide()
            self._label_overlap.show()
            self._overlap.show()
            arg_list['NUM_RECIP'] = int(self._rand_num_recip.text())
            arg_list['LAYER_DENSITY'] = float(self._rand_layer_density.text())
            arg_list['OVERLAP'] = float(self._overlap.text())

        elif np.char.equal(mode, "user data"):

            self._ff_label_layer_density.hide()
            self._ff_label_num_recip.hide()
            self._ff_layer_density.hide()
            self._ff_num_recip.hide()
            self._rand_label_layer_density.hide()
            self._rand_label_num_recip.hide()
            self._rand_layer_density.hide()
            self._rand_num_recip.hide()
            self._label_overlap.hide()
            self._overlap.hide()
            self._label_Q_file.show()
            self._Q_file.show()
            arg_list['QFILE'] = str(self._Q_file.text())

        Q = gtnn.generateQ(mode)
        # print(Q)
        norm = matplotlib.colors.Normalize()
        Q_temp = Q.tocsr()
        self._canvas_Q.axes.imshow(Q_temp.toarray(), norm=norm, cmap=plt.cm.gray)
        self._canvas_Q.draw()
        print("update Q format!!")
        return Q
    # MAYBE DONT NEED
    # def addData_callbackFunc(self, value):
    #     # print("Add data: " + str(value))
    #     self.myFig1.addData(value)
    #     # self.myFig2.addData(value)
    # @QtCore.pyqtSlot(np.float16)
    
    def gtnn_evolve(self):
        global arg_list, I, Q
        probe_1 = int(self.vplot_1.text())
        probe_2 = int(self.vplot_2.text())
        probe_3 = int(self.vplot_3.text())
        probe_4 = int(self.vplot_4.text())
        probe_5 = int(self.vplot_5.text())

        mode = self.updateMode
        Psip = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
        Psin = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)

        vp, vn = gtnn.generateV('rand')
        iter = 0

        

        while True:
            probe_1 = int(self.vplot_1.text())
            probe_2 = int(self.vplot_2.text())
            probe_3 = int(self.vplot_3.text())
            probe_4 = int(self.vplot_4.text())
            probe_5 = int(self.vplot_5.text())
            self.vplot1.addData(vp[probe_1] + Psip[probe_1])
            self.vplot2.addData(vp[probe_2] + Psip[probe_2])
            self.vplot3.addData(vp[probe_3] + Psip[probe_3])
            self.vplot4.addData(vp[probe_4] + Psip[probe_4])
            self.vplot5.addData(vp[probe_5] + Psip[probe_5])

            time.sleep(0.1/(self.speed + 1))

            if np.char.equal(mode, "routing"):
                ################################## Compressive sensing & routing
                # Gp = -I + Q @ (vp-vn) + Psip + np.diag(Q).reshape(vn.shape) * vn
                # Gn = I - Q @ (vp-vn) + Psin + np.diag(Q).reshape(vp.shape) * vp
                Gp = vp - I + Q @ (vp-vn) + Psip 
                Gn = vn + I - Q @ (vp-vn) + Psin 
                
                Psip = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
                Psin = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
                
                vp = vp + (arg_list['DT']/arg_list['TAU']) * ((vp*vp - arg_list['VMAX']**2) * Gp)\
                        / (-vp * Gp + arg_list['LAMBDA'] * arg_list['VMAX'])
                vn = vn + (arg_list['DT']/arg_list['TAU']) * ((vn*vn - arg_list['VMAX']**2) * Gn)\
                        / (-vn * Gn + arg_list['LAMBDA'] * arg_list['VMAX'])
                
                vp_flag = np.logical_or(np.abs(vp) > arg_list['VMAX'], np.abs(Gp) > arg_list['LAMBDA'])
                vn_flag = np.logical_or(np.abs(vn) > arg_list['VMAX'], np.abs(Gn) > arg_list['LAMBDA'])
                
                if np.any(vp_flag) or np.any(vn_flag):
                    print("WTF!!!!!!!!!! %d" %(iter))
                    print("Gp: %d", np.sum(np.abs(Gp) > arg_list['LAMBDA']))
                    print("Gn: %d", np.sum(np.abs(Gn) > arg_list['LAMBDA']))
                    print(Gn)
                    print(Gp)
                    break
                else:
                    pass
                    # _,num_converged = max_cut(Q, vp-vn)
                    # if num_converged == arg_list['NUM_NEURON']:
                    #     print("Converged!!! NOW CHECK Qv==b")
                    #     print(np.sum(Q @ (vp-vn) - b))
                    #     print(np.sum(np.linalg.inv(Q) @ b - (vp-vn)))


                Psip[vp > arg_list['VTH']] = arg_list['C']
                Psin[vn > arg_list['VTH']] = arg_list['C']
                vp[vp > arg_list['VTH']] = arg_list['VTH']
                vn[vn > arg_list['VTH']] = arg_list['VTH']

                if iter > 10000:
                    pass
                    # Q = adapt_Q(iter, Q, Psip, Psin, vp, vn, M)
                # Q = adapt_Q(iter, Q, Psip, Psin, vp, vn, M)
                

            elif np.char.equal(mode, 'combinatorial'):
                ################################### Combinatory
                # if iter <= 1000:
                #     Gp = - b + Q @ (vp-vn) + Psip + np.diag(Q).reshape(vn.shape) * vn
                #     Gn = b - Q @ (vp-vn) + Psin + np.diag(Q).reshape(vp.shape) * vp
                #     Psip = np.zeros((arg_list[NUM_NEURON], 1)).astype(np.float16)
                #     Psin = np.zeros((arg_list[NUM_NEURON], 1)).astype(np.float16)
                    
                #     vp = vp + (arg_list[DT]/arg_list[TAU]) * ((vp*vp - arg_list[VMAX]**2) * Gp)\
                #         /(-vp * Gp + arg_list[LAMBDA] * arg_list[VMAX])
                #     vn = vn + (arg_list[DT]/arg_list[TAU]) * ((vn*vn - arg_list[VMAX]**2) * Gn)\
                #         /(-vn * Gn + arg_list[LAMBDA] * arg_list[VMAX])
                # else:
                
                ##### NO RESET ######
                # Gp = Q @ (vp-vn) + Psip - np.cos(np.pi/2 * (vp-vn)) + Q @ np.cos(np.pi/2 * (vp-vn))
                # Gn = -Q @ (vp-vn) + Psin + np.cos(np.pi/2 * (vp-vn)) - Q @ np.cos(np.pi/2 * (vp-vn))
                cos_temp = np.cos(np.pi/2 * (vp-vn))
                # G_temp = Q @ ((vp-vn) + cos_temp)
                G_temp = Q @ (vp-vn)
                
                # Gp = G_temp + Psip - cos_temp 
                # Gn = -G_temp + Psin + cos_temp

                Gp = G_temp + Psip 
                Gn = -G_temp + Psin 

                ##### RESET #####
                # if iter >= 100000:
                #     if iter == 100000:
                #         v = vp-vn
                #         e = 1e-2
                #         vp[v <= -arg_list[VMAX] + e] = -1
                #         vn[v <= -arg_list[VMAX] + e] = 0
                #         vp[v >= arg_list[VMAX] - e] = 0
                #         vn[v >= arg_list[VMAX] - e] = -1
                #         vp[np.logical_and(arg_list[VMAX] - e > v, v > -arg_list[VMAX] + e)] = 0
                #         vn[np.logical_and(arg_list[VMAX] - e > v, v > -arg_list[VMAX] + e)] = 0
                #         # print(vp)
                #         # print(vn)
                #         print("reset!!!")
                #     cos_temp = np.cos(np.pi/2 * (vp-vn))
                #     G_temp = Q @ ((vp-vn) + cos_temp)
                    
                #     Gp = G_temp + Psip - cos_temp 
                #     Gn = -G_temp + Psin + cos_temp

                # else :
                #     Gp = vp + Q @ (vp-vn) + Psip
                #     Gn = vn -Q @ (vp-vn) + Psin
                
                Psip = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
                Psin = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)

                vp = vp - arg_list['TAU'] * (vp + np.sign(Gp) * arg_list['VMAX'])
                vn = vn - arg_list['TAU'] * (vn + np.sign(Gn) * arg_list['VMAX'])

                Psip[vp > arg_list['VTH']] = arg_list['C']
                Psin[vn > arg_list['VTH']] = arg_list['C']
                vp[vp > arg_list['VTH']] = arg_list['VTH']
                vn[vn > arg_list['VTH']] = arg_list['VTH']

                if iter %10000 == 0:
                    num_maxcut, num_converged = gtnn.max_cut(Q.toarray(), vp-vn)
                    print("max cut: %d, number converged: %d" %(num_maxcut, num_converged))
                # time.sleep(0.1)
            elif np.char.equal(mode, 'normal'):

                Gp = vp - I + Q @ (vp-vn) + Psip 
                Gn = vn + I - Q @ (vp-vn) + Psin 
                
                Psip = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
                Psin = np.zeros((arg_list['NUM_NEURON'], 1)).astype(np.float16)
                
                vp = vp + (arg_list['DT']/arg_list['TAU']) * ((vp*vp - arg_list['VMAX']**2) * Gp)\
                        / (-vp * Gp + arg_list['LAMBDA'] * arg_list['VMAX'])
                vn = vn + (arg_list['DT']/arg_list['TAU']) * ((vn*vn - arg_list['VMAX']**2) * Gn)\
                        / (-vn * Gn + arg_list['LAMBDA'] * arg_list['VMAX'])
                
                Psip[vp > arg_list['VTH']] = arg_list['C']
                Psin[vn > arg_list['VTH']] = arg_list['C']
                vp[vp > arg_list['VTH']] = arg_list['VTH']
                vn[vn > arg_list['VTH']] = arg_list['VTH']
            
            iter += 1
            
        
        



class CustomFigCanvas(FigureCanvas, TimedAnimation):
    def __init__(self):
        self.addedData = []
        # print('Matplotlib Version:', matplotlib.__version__)

        # The data
        self.xlim = 200
        self.n = np.linspace(0, self.xlim - 1, self.xlim)
        # a = []
        # b = []
        # a.append(2.0)
        # a.append(4.0)
        # a.append(2.0)
        # b.append(4.0)
        # b.append(3.0)
        # b.append(4.0)
        self.y = (self.n * 0.0) + 0.5

        # The window
        self.fig = Figure(figsize=(8, 8), dpi=100)
        self.ax1 = self.fig.add_subplot(111)

        # self.ax1 settings
        self.ax1.set_xlabel('time')
        self.ax1.set_ylabel('raw data')
        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='red', linewidth=2)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')

        # self.line2 = Line2D([], [], color='blue')
        # self.line2_tail = Line2D([], [], color='red', linewidth=2)
        # self.line2_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')

        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)

        # self.ax1.add_line(self.line2)
        # self.ax1.add_line(self.line2_tail)
        # self.ax1.add_line(self.line2_head)

        self.ax1.set_xlim(0, self.xlim - 1)
        self.ax1.set_ylim(-1, 2)

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=50, blit=True)

    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head]
        for l in lines:
            l.set_data([], [])

    def addData(self, value):
        self.addedData.append(value)

    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass

    def _draw_frame(self, framedata):
        margin = 2
        while(len(self.addedData) > 0):
            self.y = np.roll(self.y, -1)
            self.y[-1] = self.addedData[0]
            del(self.addedData[0])

        self.line1.set_data(self.n[0:self.n.size - margin], self.y[0:self.n.size - margin])
        self.line1_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]), np.append(self.y[-10:-1 - margin], self.y[-1 - margin]))
        self.line1_head.set_data(self.n[-1 - margin], self.y[-1 - margin])

        # self.line2.set_data(self.n[0:self.n.size - margin], self.y[0:self.n.size - margin] + 1)
        # self.line2_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]), np.append(self.y[-10:-1 - margin], self.y[-1 - margin]) + 1)
        # self.line2_head.set_data(self.n[-1 - margin], self.y[-1 - margin] + 1)

        # self._drawn_artists = [self.line1, self.line1_tail, self.line1_head, self.line2, self.line2_tail, self.line2_head]
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head]

class MatCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        super(MatCanvas, self).__init__(fig)

class Communicate(QtCore.QObject):
    data_signal = QtCore.pyqtSignal([float], [str], [bool], [int])

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Plastique'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec_())