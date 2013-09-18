/*
   AccelerometerBuf.h

   Will Dickson, IO Rodeo Inc.
*/ 
#if defined(ARDUINO) && ARDUINO >= 100
#include "Arduino.h"
#else
#include "WProgram.h"
#endif
#include <ByteBuffer.h>
#include <FastADXL345.h>
//#include <ADXL345.h>

class AccelerometerBuf {

    public:
        AccelerometerBuf();
        void init(unsigned int bufSize);
        void putVal(AccelerometerRaw raw);
        AccelerometerRaw getVal();
        int getSize();
        void clear();
        void deAllocate();
        unsigned int bufSize;
    private:
        ByteBuffer xBuf;
        ByteBuffer yBuf;
        ByteBuffer zBuf;
};
