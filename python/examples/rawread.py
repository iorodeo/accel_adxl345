import time
from accel_adxl345 import AccelADXL345

port = '/dev/ttyUSB2'
dev = AccelADXL345(port=port)
dev.startStreaming()
data = []
while len(data) < 1000:
    newData = dev.readValues()
    data.append(newData)
    print len(data)

dev.stopStreaming()
dev.emptyBuffer()

for i in range(0,10):
    time.sleep(0.5)
    print dev.inWaiting()

print dev.getSampleDt()
        
