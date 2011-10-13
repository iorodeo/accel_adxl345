/*
   AccelerometerBuf.cpp 

   Will Dickson IO Rodeo Inc.

*/

#include <util/atomic.h>
#include "AccelerometerBuf.h"

AccelerometerBuf::AccelerometerBuf() {
}

void AccelerometerBuf::init(unsigned int _bufSize) {
    bufSize = _bufSize;
    xBuf.init(2*bufSize);
    yBuf.init(2*bufSize);
    zBuf.init(2*bufSize);
}

void AccelerometerBuf::putVal(AccelerometerRaw raw) {
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        if (xBuf.getSize() < xBuf.getCapacity()) {
            xBuf.putInt(raw.XAxis);
            yBuf.putInt(raw.YAxis);
            zBuf.putInt(raw.ZAxis);
        }
    }
}

AccelerometerRaw AccelerometerBuf::getVal() {
    AccelerometerRaw raw;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
        raw.XAxis = xBuf.getInt();
        raw.YAxis = yBuf.getInt();
        raw.ZAxis = zBuf.getInt();
    }
    return raw;
}

int AccelerometerBuf::getSize() {
    return xBuf.getSize()/2;
}

void AccelerometerBuf::clear() {
    xBuf.clear();
    yBuf.clear();
    zBuf.clear();
}

void AccelerometerBuf::deAllocate() {
    xBuf.deAllocate();
    yBuf.deAllocate();
    zBuf.deAllocate();
}






