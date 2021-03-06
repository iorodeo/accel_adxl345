"""
accel_adxl345.py

This modules defines the AccelADXL345 class for streaming data from the
ADXL345 accelerometers. 
"""
import time
import serial
import sys
import numpy
import struct

BUF_EMPTY_NUM = 5
BUF_EMPTY_DT = 0.05

class AccelADXL345(serial.Serial):

    def __init__(self, **kwarg):

        # Command ids
        self.cmd_id = {
                'stop_streaming'       : 0,
                'start_streaming'      : 1,
                'set_timer_period'     : 2, 
                'get_timer_period'     : 3,
                'set_range'            : 4,
                'get_range'            : 5,
                'get_sample'           : 6,
                'get_max_timer_period' : 7,
                'get_min_timer_period' : 8,
                'get_bad_sample_count' : 9,
                }

        # Allowed accelerations ranges and scale factors
        self.allowedAccelRange = (2, 4, 8, 16)
        self.accelScale = 0.0384431560448

        try:
            self.reset_sleep = kwarg.pop('reset_sleep')
        except KeyError:
            self.reset_sleep = True

        try:
            self.accelRange = kwarg.pop('range')
        except KeyError:
            self.accelRange = 16
        if not self.checkAccelRange(self.accelRange):
            raise ValueError, 'unknown acceleration range {0}'.format(self.accelRange)

        _kwarg = {
                'port'     : '/dev/ttyUSB0',
                'timeout'  : 0.1,
                'baudrate' : 38400,
                }

        _kwarg.update(kwarg)
        super(AccelADXL345,self).__init__(**_kwarg)
        if self.reset_sleep:
            time.sleep(2.0)
        self.emptyBuffer()

        # Get sample dt and current range setting
        self.sampleDt = self.getSampleDt()
        self.accelRange = self.getRange()

        # Get max and min allowed sample dt
        self.minSampleDt = self.getMinSampleDt()
        self.maxSampleDt = self.getMaxSampleDt()

    def sendCmd(self,cmd):
        """
        Send the command, cmd, to the device
        """
        self.write(cmd)

    def readValue(self):
        """
        Read a value from the device.
        """
        line = self.readline()
        line = line.strip()
        return line

    def readFloat(self):
        """
        Read a single float of list of floats separated by commas
        """
        value = self.readValue()
        if ' ' in value:
            value = value.split(' ')
            value = [float(x) for x in value]
        else:
            value = float(value)
        return value

    def readInt(self):
        """
        Read a single integer or list of integers separated by commas.
        """
        value = self.readValue()
        if ' ' in value:
            value = value.split(' ')
            value = [int(x) for x in value]
        else:
            value = int(value)
        return value

    def emptyBuffer(self):
        """
        Empty the serial input buffer.
        """
        for i in range(0,BUF_EMPTY_NUM):
            #print 'empty %d'%(i,), self.inWaiting()
            self.flushInput()
            time.sleep(BUF_EMPTY_DT)


    def checkAccelRange(self,value):
        """
        Check if the value is within the allowed range set.
        """
        return value in self.allowedAccelRange

    def startStreaming(self):
        """
        Start data streaming form the accelerometer
        """
        cmd = '[{0}]\n'.format(self.cmd_id['start_streaming'])
        self.sendCmd(cmd)

    def stopStreaming(self):
        """
        Stop data streaming from the accelerometer
        """
        cmd = '[{0}]\n'.format(self.cmd_id['stop_streaming'])
        self.sendCmd(cmd)

    def getSampleDt(self):
        """
        Returns the sample interval, dt, in microseconds
        """
        cmd = '[{0}]\n'.format(self.cmd_id['get_timer_period']) 
        self.sendCmd(cmd)
        dt = self.readFloat()
        return dt 

    def getBadSampleCount(self):
        """
        Returns the number of bad/corrupted samples.
        """
        cmd = '[{0}]\n'.format(self.cmd_id['get_bad_sample_count'])
        self.sendCmd(cmd)
        val = self.readInt()
        return val

    def setSampleDt(self,dt):
        """
        Sets the sample interval in microseconds.
        """
        _dt = int(dt)
        if _dt > self.maxSampleDt or _dt < self.minSampleDt:
            raise ValueError, 'sample dt out of range'
        cmd = '[{0},{1}]\n'.format(self.cmd_id['set_timer_period'],_dt)
        self.sendCmd(cmd)
        self.sampleDt = _dt

    def getSampleRate(self):
        """
        Returns the sample rate in Hz
        """
        return 1.0/self.sampleDt


    def setSampleRate(self,freq):
        """
        Sets the sample rate in Hz
        """
        dt = int(1.0e6/freq)
        self.setSampleDt(dt)

    def getMaxSampleDt(self):
        """
        Gets the maximun allowed sample dt in microseconds.
        """
        cmd = '[{0}]\n'.format(self.cmd_id['get_max_timer_period'])
        self.sendCmd(cmd)
        value =  self.readInt()
        return value

    def getMinSampleDt(self):
        """
        Gets the minimum allowed sample dt in microseconds.
        """
        cmd = '[{0}]\n'.format(self.cmd_id['get_min_timer_period'])
        self.sendCmd(cmd)
        value = self.readInt()
        return value

    def getMaxSampleRate(self):
        """
        Returns the maximum allowed sample rate in Hz
        """
        minSampleDtSec = self.minSampleDt*(1.0e-6)
        return 1.0/minSampleDtSec

    def getMinSampleRate(self):
        """
        Returns the minum allowed samples rate in Hz
        """
        maxSampleDtSec = self.maxSampleDt*(1.0e-6)
        return 1.0/maxSampleDtSec

    def getRange(self):
        """
        Returns the current accelerometer range setting.
        """
        cmd = '[{0}]\n'.format(self.cmd_id['get_range'])
        self.sendCmd(cmd)
        accelRange = self.readInt()
        return accelRange

    def setRange(self,value):
        """
        Sets the current accelerometer range.
        """
        _value = int(value)
        if _value in self.allowedAccelRange:
            cmd = '[{0}, {1}]\n'.format(self.cmd_id['set_range'],_value)
        self.sendCmd(cmd)
        _value = self.getRange()
        self.accelRange = _value

    def getAllowedAccelRange(self):
        """
        Returns all allowed range settings
        """
        return self.allowedAccelRange

    def peekValue(self):
        """
        Grabs a sinlge sample (ax,ay,az) from the accelerometer.
        """
        cmd = '[{0}]\n'.format(self.cmd_id['get_sample'])
        self.sendCmd(cmd)
        samples = self.readFloat()
        samples = [x*self.accelScale for x in samples]
        return samples
        
    def getSamples(self,N,verbose=False): 
        """
        Streams N samples from the accelerometer at the current sample rate 
        setting.
        """
        # Start streaming 
        self.emptyBuffer()
        self.startStreaming()

        # Read samples
        data = []
        while len(data) < N:
            if verbose:
                print len(data)
            newData = self.readValues()
            data.extend(newData)

        #  Stop streaming and empty buffer
        self.stopStreaming()
        self.emptyBuffer()

        # Convert to an array, truncate to number of samples requested 
        data = numpy.array(data) 
        data = self.accelScale*data[:N,:]
        
        # Use sample rate to get array of time points
        dtSec = self.sampleDt*1.0e-6
        t = dtSec*numpy.arange(data.shape[0])

        return t, data

    #def readValues(self,verbose=False):
    #    data = []
    #    if self.inWaiting() > 0:
    #        line = self.readline()
    #        line = line.strip()
    #        line = line.split(':')
    #        for vals in line:
    #            vals = vals.split(' ')
    #            try:
    #                vals = [float(x) for x in vals]
    #                if len(vals) == 3:
    #                    data.append(vals)
    #            except:
    #                if verbose:
    #                    print 'fail'
    #    return data

    def readValues(self):
        data = []
        while self.inWaiting() >= 7:
            byteVals = self.read(7)
            ax = struct.unpack('<h',byteVals[0:2])[0]
            ay = struct.unpack('<h',byteVals[2:4])[0]
            az = struct.unpack('<h',byteVals[4:6])[0]
            chk = ord(byteVals[6]) 
            if not chk == 0:
                raise IOError, 'streaming data is not in sync.'
            data.append([ax,ay,az])
        return data




