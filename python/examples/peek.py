"""
peek.py - demonstrates how to grab single readings from the accelerometer
"""
from accel_adxl345 import AccelADXL345

port = '/dev/ttyUSB0'
dev = AccelADXL345(port=port)
dev.setRange(2)

if 0:
    print dev.peek()

if 1:
    for i in range(0,100):
        print dev.peek()

