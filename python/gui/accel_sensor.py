"""
accel_sensor.py 

Simple GUI for recording data from the ADXL345 accelerometers connected to an Arduino.

Author: Will Dickson, IO Rodeo Inc.
"""
import time
import math
import sys
import platform
import os
import os.path
import pylab
from PyQt4 import QtCore
from PyQt4 import QtGui
from accel_sensor_ui import Ui_AccelSensorMainWindow 
from accel_adxl345 import AccelADXL345

TIMER_INTERVAL_MS = 0.001
MIN_INWAITING_SIZE = 15

# Default parameters
DEFAULT_DURATION = 1.0
DEFAULT_SAMPLE_RATE = 500.0
DEFAULT_SAVE_FILE = 'sensor_data.txt'

# Validator parameters
DURATION_MIN = 0.01 
DURATION_MAX = 60 
DURATION_DECIMALS = 2
SAMPLE_RATE_DECIMALS = 0

class Sensor_MainWindow(QtGui.QMainWindow, Ui_AccelSensorMainWindow):

    def __init__(self,parent=None):
        super(Sensor_MainWindow,self).__init__(parent)
        self.setupUi(self)
        self.initialize()
        self.connectActions()
        self.setupTimer()

    @property
    def numSamples(self):
        return int(math.floor(self.duration*self.sampleRate))

    def connectActions(self):
        """
        Connect widget actions
        """
        self.serialPortLineEdit.editingFinished.connect(self.serialPortLineEdit_Callback)
        self.startStopPushButton.clicked.connect(self.startStop_Callback)
        self.connectCheckBox.pressed.connect(self.connectCheckBox_PressedCallback)
        self.connectCheckBox.clicked.connect(self.connectCheckBox_ClickedCallback)
        self.durationLineEdit.editingFinished.connect(self.durationChanged_Callback)
        self.sampleRateLineEdit.editingFinished.connect(self.sampleRateChanged_Callback)
        self.rangeComboBox.currentIndexChanged.connect(self.rangeChanged_Callback)
        self.savePushButton.clicked.connect(self.save_Callback)

    def setupTimer(self):
        """
        Setup timer object
        """
        self.timer = QtCore.QTimer()
        self.timer.setInterval(TIMER_INTERVAL_MS)
        self.timer.timeout.connect(self.timer_Callback)

    def initialize(self):
        """
        Initializes the system state
        """

        self.data = None 
        self.t = None 
        self.connected = False
        self.started = False
        self.timer = None
        self.dev = None
        self.maxSampleRate = None
        self.minSampleRate = None
        self.actualSampleDt = None 
        self.duration = DEFAULT_DURATION 
        self.sampleRate = DEFAULT_SAMPLE_RATE

        # Set default com port
        osType = platform.system()
        if osType == 'Linux':
            self.port = '/dev/ttyUSB0'
        else:
            self.port = 'com1'
        self.serialPortLineEdit.setText(self.port)

        # Setup duration and sample rate validators
        self.durationValidator = QtGui.QDoubleValidator(self)
        self.durationValidator.setRange(
                DURATION_MIN,
                DURATION_MAX,
                DURATION_DECIMALS
                )
        self.durationValidator.fixup = self.durationLineEditFixup
        self.durationLineEdit.setValidator(self.durationValidator)

        self.sampleRateValidator = QtGui.QDoubleValidator(self)
        self.sampleRateValidator.fixup = self.sampleRateFixup
        self.sampleRateLineEdit.setValidator(self.sampleRateValidator)

        # Set duration and sample rate to default
        self.durationLineEdit.setText('%1.2f'%(self.duration,))
        self.sampleRateLineEdit.setText('%1.0f'%(self.sampleRate,))

        # Setup range combobox
        self.allowedRangeValues = ('2', '4', '8', '16')
        for val in self.allowedRangeValues:
            self.rangeComboBox.addItem(val)
        self.rangeComboBox.setCurrentIndex(3)

        # Set start stop text based on state, disable/enable widgets and set status
        self.setStartStopText()
        self.enableDisableWidgets()
        self.statusLabel.setText('Status: not connected')

        # Setup axes
        self.mpl.canvas.axesDict['x'].get_xaxis().set_visible(False)
        self.mpl.canvas.axesDict['y'].get_xaxis().set_visible(False)
        self.mpl.canvas.axesDict['z'].set_xlabel('time (s)')
        self.plots = []
        self.axes = []
        for i, symb in enumerate(('x', 'y', 'z')):
            axis = self.mpl.canvas.axesDict[symb]
            axis.set_ylabel('a%s (m/s)'%(symb,))
            self.plots.append(axis.plot([],[],linewidth=1)[0])
            self.axes.append(axis)

        # Set save file and last directory 
        self.userHome = os.getenv('USERPROFILE')
        if self.userHome is None:
            self.userHome = os.getenv('HOME')
        self.lastSaveDir = self.userHome
        self.lastSaveFile = DEFAULT_SAVE_FILE

    def serialPortLineEdit_Callback(self):
        """
        Set serial port sting.
        """
        self.port = str(self.serialPortLineEdit.text())

    def rangeChanged_Callback(self):
        """
        Changes device range setting based on combobox value
        """
        newRange = self.getRange()
        self.dev.setRange(newRange)

    def durationChanged_Callback(self):
        """
        Changes recording duration based on lineedit value
        """
        durationStr = self.durationLineEdit.text()
        self.duration = float(durationStr)

    def durationLineEditFixup(self,value):
        durationStr = '%1.2f'%(self.duration,)
        self.durationLineEdit.setText(durationStr)

    def sampleRateChanged_Callback(self):
        """
        Changes the device sample rate setting based on the lineedit value.
        """
        # Get sample rate string and convert to float
        sampleRateStr = self.sampleRateLineEdit.text()
        self.sampleRate = float(sampleRateStr)

        # Set sample rate and get actual value used by device
        self.dev.setSampleRate(self.sampleRate)
        self.actualSampleDt = self.dev.getSampleDt()*1.0e-6

    def sampleRateFixup(self,valStr):
        sampleRateStr = '%1.0f'%(self.sampleRate,)
        self.sampleRateLineEdit.setText(sampleRateStr)

    def connectCheckBox_PressedCallback(self):
        """
        Starts connection/disconnection process ... called before
        connectCheckBoc_ClickedCallback. Basically, just sets state of checkbox
        to give the user an indication that something is happening and prints
        status message.
        """
        if self.connected == False:
            self.connectCheckBox.setCheckState(True)
            self.statusLabel.setText('Status: connecting ...')
        else:
            self.connectCheckBox.setCheckState(False)
            self.statusLabel.setText('Status: disconnecting ..')

    def connectCheckBox_ClickedCallback(self):
        """
        Finished connection process. If the device is unconnected it tries to 
        connect. If connected it disconnects.
        """
        if self.connected == False:
            try:
                self.dev = AccelADXL345(port=self.port)
                # Connect to device, set range and sample rate
                self.dev.setRange(self.getRange())
                self.dev.setSampleRate(self.sampleRate)

                # Get actual sample dt, max and min sample rates 
                self.actualSampleDt = self.dev.getSampleDt()*1.0e-6
                self.maxSampleRate = self.dev.getMaxSampleRate()
                self.minSampleRate = self.dev.getMinSampleRate()

                # Use max and min sample rate to set top and bottom of validator
                self.sampleRateValidator.setRange(
                        self.minSampleRate,
                        self.maxSampleRate,
                        SAMPLE_RATE_DECIMALS
                        )

                self.statusLabel.setText('Status: connected')
                self.connected = True
            except Exception, e:
                QtGui.QMessageBox.critical(self,'Error', '%s'%(e,))
                self.statusLabel.setText('Status: not connected')
                self.connectCheckBox.setCheckState(False)
        else:
            self.dev.close()
            self.dev = None
            self.connected = False
            self.statusLabel.setText('Status: not connected')
            self.connectCheckBox.setCheckState(False)

        self.enableDisableWidgets()

    def save_Callback(self):
        """
        Save acquired data
        """
        filepath = os.path.join(self.lastSaveDir,self.lastSaveFile)
        filename = QtGui.QFileDialog.getSaveFileName(None,'Select log file',filepath)
        filename = str(filename)
        if filename:
            data = pylab.concatenate((self.t,self.data),axis=1)
            pylab.savetxt(filename,data)
            self.lastSaveDir =  os.path.split(filename)[0]
            self.lastSaveFile = os.path.split(filename)[1]

    def startStop_Callback(self):
        """
        Callback for start/stop pushbutton clicked events.
        """
        if self.started == False:
            self.startDataStreaming()
        else:
            self.stopDataStreaming()
        self.setStartStopText()

    def timer_Callback(self):
        """
        Callback for timer events. Grabs available values from the device until sufficient
        samples have been acquired then plots the data.
        """
        # Read the available samples from the device
        while self.dev.inWaiting() > MIN_INWAITING_SIZE and len(self.data) < self.numSamples:
            try:
                newData = self.dev.readValues()
            except IOError, e:
                self.stopDataStreaming(plot=False)
                break
                
            self.data.extend(newData)
            percent = min([100,100*len(self.data)/float(self.numSamples)])
            percentStr = '%1.0f'%(percent,) + '%'
            self.statusLabel.setText('Status: acquiring samples %s'%(percentStr,))
            self.statusLabel.repaint()
        
        # Check if enough samples have been acquired
        if len(self.data) >= self.numSamples:
            self.statusLabel.repaint()
            self.stopDataStreaming()

    def startDataStreaming(self):
        """
        Start data streaming from the device.
        """
        self.started = True
        self.data = [] 
        self.t = None
        self.dev.emptyBuffer()
        self.dev.startStreaming()
        self.timer.start()

    def stopDataStreaming(self,plot=True):
        """
        Stops data streaming from device
        """
        self.timer.stop()
        # Stop streaming, empty buffer, etc
        self.dev.stopStreaming()
        self.dev.emptyBuffer()
        self.started = False
        self.statusLabel.setText('Status: connected')
        self.setStartStopText()
        self.enableDisableWidgets()

        if plot and len(self.data) > 0:
            # Reduce size of data if necessary data and create time array 
            N = len(self.data)
            if N > self.numSamples:
                N = self.numSamples
                self.data = self.data[0:N]
            self.data = self.dev.accelScale*pylab.array(self.data)
            self.t = self.actualSampleDt*pylab.arange(0,N)
            self.t = self.t.reshape((self.t.shape[0],1))

            # Plot data
            for i in range(0,3):
                # Set data and make visible 
                self.plots[i].set_visible(True)
                self.plots[i].set_data(self.t,self.data[:,i])

                # Set time range 
                minT = self.t.min()
                maxT = self.t.max()
                self.axes[i].set_xlim(minT,maxT)

                # Set data range
                minData = self.data[:,i].min()
                maxData = self.data[:,i].max()
                self.axes[i].set_ylim(minData,maxData)

            self.mpl.canvas.fig.canvas.draw()
        else:
            pass
            


    def setStartStopText(self):
        """
        Sets the text of the start/stop button based on recoreding has been
        started.
        """
        if self.started == True:
            self.startStopPushButton.setText('Stop')
        else:
            self.startStopPushButton.setText('Start')

    def enableDisableWidgets(self):
        """
        Enable/Disable widgets based on sysem state.
        """

        if self.connected == False:
            self.startStopPushButton.setEnabled(False)
            self.durationLineEdit.setEnabled(False)
            self.durationLabel.setEnabled(False)
            self.sampleRateLabel.setEnabled(False)
            self.sampleRateLineEdit.setEnabled(False)
            self.rangeLabel.setEnabled(False)
            self.rangeComboBox.setEnabled(False)
        else:
            self.startStopPushButton.setEnabled(True)
            self.durationLineEdit.setEnabled(True)
            self.durationLabel.setEnabled(True)
            self.sampleRateLabel.setEnabled(True)
            self.sampleRateLineEdit.setEnabled(True)
            self.rangeLabel.setEnabled(True)
            self.rangeComboBox.setEnabled(True)

        if self.data is None: 
            self.savePushButton.setEnabled(False)
        else:
            self.savePushButton.setEnabled(True)

    def getRange(self):
        """
        Get the current range as set by the combobox 
        """
        rangeStr = self.rangeComboBox.currentText()
        return int(rangeStr)


    def main(self):
        self.show()

# -----------------------------------------------------------------------
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    sensor = Sensor_MainWindow()
    sensor.main()
    app.exec_()

