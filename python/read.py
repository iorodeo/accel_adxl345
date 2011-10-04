import time
import serial
import sys


class Accelerometer(serial.Serial):

    def __init__(self, port='/dev/ttyUSB0', baudrate=2000000, timeout=2.0):
        super(Accelerometer,self).__init__(port=port,baudrate=baudrate,timeout=timeout)
        time.sleep(2.0)

    def readData(self,numvals):
        numpts = 0
        while numpts < numvals:
            vals = self.readline()
            vals.split()

# -----------------------------------------------------------------------------------
import pylab
import scipy
import scipy.signal

accel = Accelerometer()

if 0:

    N=100;
    data = []

    for i in range(0,N):
        print i
        line = accel.readline()
        line = line.strip()
        line = line.split(',')
        try:
            line = [float(x) for x in line]
            data.extend(line)
        except:
            print 'fail', line
            pass

    data = scipy.array(data)
    pylab.plot(data)
    pylab.show()

if 1:
    num_pts = 1000 
    n = 0

    data = []
    medfilt_size= 5

    print 'Clearing buffer ...', 
    sys.stdout.flush()
    cnt = 0
    while accel.inWaiting() > 0:
        print cnt, 
        sys.stdout.flush()
        accel.readline()
        cnt+=1
    print 'done'
    sys.stdout.flush()
    
    while len(data) < num_pts:
        
        line = accel.readline()
        line = line.strip()
        line = line.split(';')
        print len(data) 
        for vals in line:
            vals = vals.split(',')
            try:
                vals = scipy.array([float(x) for x in vals])
                data.append(vals)
            except:
                print 'fail', vals
                pass
    
    data = scipy.array(data)
    scale = 0.0312
    ax = data[:,0]*scale
    ay = data[:,1]*scale
    az = data[:,2]*scale
    
    pylab.subplot(311)
    pylab.plot(ax)
    pylab.subplot(312)
    pylab.plot(ay)
    pylab.subplot(313)
    pylab.plot(az)
    pylab.show()
     


