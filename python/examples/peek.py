"""
peek.py - demonstrates how to grab single readings from the accelerometer
"""
import time
from accel_adxl345 import AccelADXL345

port = '/dev/ttyUSB0'
dev = AccelADXL345(port=port)
dev.setRange(2)

if 0:
    print dev.peekValue()

if 0:
    for i in range(0,100):
        print dev.peekValue()
if 1:
    t0 = time.time()
    while 1:
        vals = dev.peekValue()
        print '%1.2f, %1.2f, %1.2f'%(vals[0], vals[1], vals[2])


