"""
get_samples.py - demonstrates how to stream samples from the device
"""
import sys
import pylab
from accel_adxl345 import AccelADXL345

port = '/dev/ttyUSB0'
dev = AccelADXL345(port=port)
dev.setRange(16)
dev.setSampleRate(500)

print 'acquiring samples'
sys.stdout.flush()
t,data = dev.getSamples(5000,verbose=True)

# Compute mean and get magnitude of vector
if 0:
    mean = data.mean(axis=0)
    mean_mag = pylab.sqrt(mean[0]**2 + mean[1]**2 + mean[2]**2)
    scale_factor = 9.81/mean_mag
    print 'magnitude of mean:', mean_mag
    print 'scale factor:', scale_factor

pylab.subplot(311)
pylab.plot(t,data[:,0])
pylab.ylabel('ax')

pylab.subplot(312)
pylab.plot(t,data[:,1])
pylab.ylabel('ay')

pylab.subplot(313)
pylab.plot(t,data[:,2])
pylab.ylabel('az')
pylab.xlabel('t (s)')
pylab.show()



