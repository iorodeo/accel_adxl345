import time
import serial
import sys
import numpy


class AccelADXL345(serial.Serial):

    def __init__(self, **kwarg):

        # Command ids
        self.cmd_id = {
                'stop_streaming'   : 0,
                'start_streaming'  : 1,
                'set_timer_period' : 2, 
                'get_timer_period' : 3,
                'set_range'        : 4,
                'get_range'        : 5,
                'get_sample'       : 6,
                }

        self.allowedAccelRange = (2, 4, 8, 16)

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
                'timeout'  : 0.3,
                'baudrate' : 2000000,
                }

        _kwarg.update(kwarg)
        super(AccelADXL345,self).__init__(**_kwarg)
        if self.reset_sleep:
            time.sleep(2.0)
        self.emptyBuffer()

        # Get sample rate and current range setting
        self.sampleRate = self.getSampleRate()
        self.accelRange = self.getRange()

    def sendCmd(self,cmd):
        self.write(cmd)

    def readValue(self):
        line = self.readline()
        return line.strip()

    def readFloat(self):
        value = self.readValue()
        if ',' in value:
            value = value.split(',')
            value = [float(x) for x in value]
        else:
            value = float(value)
        return value

    def readInt(self):
        value = self.readValue()
        if ',' in value:
            value = value.split(',')
            value = [int(x) for x in value]
        else:
            value = int(value)
        return value

    def emptyBuffer(self):
        while self.inWaiting() > 0:
            line = self.readline()

    def checkAccelRange(self,value):
        print value
        print self.allowedAccelRange
        return value in self.allowedAccelRange

    def startStreaming(self):
        cmd = '[{0}]\n'.format(self.cmd_id['start_streaming'])
        self.sendCmd(cmd)

    def stopStreaming(self):
        cmd = '[{0}]\n'.format(self.cmd_id['stop_streaming'])
        self.sendCmd(cmd)

    def getSampleRate(self):
        cmd = '[{0}]\n'.format(self.cmd_id['get_timer_period']) 
        self.sendCmd(cmd)
        sampleRate = self.readFloat()
        return sampleRate

    def getRange(self):
        cmd = '[{0}]\n'.format(self.cmd_id['get_range'])
        self.sendCmd(cmd)
        accelRange = self.readInt()
        return accelRange

    def setRange(self,value):
        if value in self.allowedAccelRange:
            cmd = '[{0}, {1}]\n'.format(self.cmd_id['set_range'],value)
        self.sendCmd(cmd)
        value = self.getRange()
        self.accelRange = value

    def peek(self):
        cmd = '[{0}]\n'.format(self.cmd_id['get_sample'])
        self.sendCmd(cmd)
        return self.readFloat()
        
    def getSamples(self,N,verbose=False): 
        """
        Read N samples from the sensor.
        """

        # Start streaming 
        self.emptyBuffer()
        self.startStreaming()

        # Read samples
        data = []
        while len(data) < N:
            if verbose:
                print len(data)
            line = accel.readline()
            line = line.strip()
            line = line.split(';')
            for vals in line:
                vals = vals.split(',')
                try:
                    vals = [float(x) for x in vals]
                    data.append(vals)
                except:
                    if verbose:
                        print 'fail'

        #  Stop streaming and empty buffer
        self.stopStreaming()
        self.emptyBuffer()

        # Convert to an array, truncate to number of samples requested 
        data = numpy.array(data) 
        data = data[:N,:]
        
        # Use sample rate to get array of time points
        t = (1.0/self.sampleRate)*numpy.arange(data.shape[0])

        return t, data

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    import pylab

    accel = AccelADXL345()
    print 'sampleRate:', accel.sampleRate
    print 'accelRange:', accel.accelRange
    accel.setRange(2)
    print 'accelRange:', accel.accelRange

    for i in range(0,10):
        print 'peek:', accel.peek()

    t,data = accel.getSamples(1000) 

    pylab.subplot(311)
    pylab.plot(t,data[:,0])
    pylab.subplot(312)
    pylab.plot(t,data[:,1])
    pylab.subplot(313)
    pylab.plot(t,data[:,2])
    pylab.show()
