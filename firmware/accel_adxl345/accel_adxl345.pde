/* 
  accel_adxl345.pde 
 
  Firmware for streaming data from the ADXL345 accelerometer.  
 
  Author: Will Dickson, IO Rodeo Inc.
 
 */ 
#include <FastWire.h>
#include <FastADXL345.h>
//#include <Wire.h>
//#include <ADXL345.h>
#include <Streaming.h>
#include <util/atomic.h>
#include <TimerOne.h>
#include <ByteBuffer.h>
#include <SerialReceiver.h>
#include "constants.h"
#include "AccelerometerBuf.h"
#include "SystemState.h"

// Function prototypes
void setAccelData();
void timerCallback();
void handleMessage();

// Global varialbles
ADXL345 accel;                       
AccelerometerBuf buffer;             
SystemState state; 
SerialReceiver receiver;
bool isFirst = true;

// Initialize serial port, I2C communications, setup accelerometer, acceleromter 
//  buffer and timer
void setup() {

    Serial.begin(baudRate);

    Wire.begin();
    // Disable internal pullups
    digitalWrite(A4,LOW);
    digitalWrite(A5,LOW);
    accel = ADXL345();

    buffer.init(bufferSize);

    accel.SetRange(state.getRange(), true);
    accel.EnableMeasurements();

    state.init();
    state.setTimerInterrupt(timerCallback);
}


// Main loop - primarily used for serial communications
void loop() {

    // Handle incoming serial information
    while (Serial.available() > 0) {
        receiver.process(Serial.read());
        if(receiver.messageReady()) {
            handleMessage();
            receiver.reset();
        }
    }
    
    // Send acceleration data to host PC
    if (state.mode  == MODE_STREAMING) {
        sendAccelData();
    }
}


// Handler for incoming serial messages
void handleMessage() {
    SerialCmd cmd;
    long timerPeriod;
    unsigned int range;
    AccelerometerRaw raw;

    cmd = (SerialCmd) receiver.readInt(0);

    switch (cmd) {

        case CMD_STOP_STREAM:
            ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
                state.mode = MODE_STOPPED;
            }
            isFirst = true;
            buffer.clear();
            break;

        case CMD_START_STREAM:
            ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
                state.mode = MODE_STREAMING;
                isFirst = true;
            }
            break;

        case CMD_SET_TIMER_PERIOD:
            ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
                timerPeriod = receiver.readLong(1);
                state.setTimerPeriod(timerPeriod);
            }
            break;

        case CMD_GET_TIMER_PERIOD:
            if (state.mode == MODE_STOPPED) { 
                Serial << state.getTimerPeriod() << endl;
            }
            break;

        case CMD_SET_RANGE:
            if (state.mode == MODE_STOPPED) {
                range = (unsigned int) receiver.readInt(1);
                state.setRange(range);
                accel.SetRange(state.getRange(),true);
            }
            break;

        case CMD_GET_RANGE:
            if (state.mode == MODE_STOPPED) {
                Serial << state.getRange() << endl;
            }
            break;

        case CMD_GET_SAMPLE:
            if (state.mode == MODE_STOPPED) {
                raw = accel.ReadRawAxis();
                Serial << raw.XAxis << " " << raw.YAxis << " " << raw.ZAxis << endl;
                //Serial << 11 << " " << 22 << " " << 33 << endl;
            }
            break;

        case CMD_GET_MAX_TIMER_PERIOD:
            if (state.mode == MODE_STOPPED) {
                Serial << maxTimerPeriod << endl; 
            }
            break;

        case CMD_GET_MIN_TIMER_PERIOD:  
            if (state.mode == MODE_STOPPED) {
                Serial << minTimerPeriod << endl;
            }
            break;

        case CMD_GET_BAD_SAMPLE_COUNT:
            if (state.mode == MODE_STOPPED) {
                Serial << state.badSampleCount << endl;
            }
            break;

        default:
            break;
    }

}

// Sends accelerometer data to the host PC
void sendAccelData() {
    unsigned int sendCnt=0;
    int maxValue;
    static AccelerometerRaw raw;
    static AccelerometerRaw rawlast;

    while ((buffer.getSize() > 0) && (sendCnt < maxSendCnt)) {
        raw = buffer.getVal();
        Serial << _BYTE(lowByte(raw.XAxis)) << _BYTE(highByte(raw.XAxis));
        Serial << _BYTE(lowByte(raw.YAxis)) << _BYTE(highByte(raw.YAxis));
        Serial << _BYTE(lowByte(raw.ZAxis)) << _BYTE(highByte(raw.ZAxis));
        Serial << _BYTE(0); // bit to check that data is in sync.
        sendCnt++;
        isFirst = false;
    }
}

// Interrupt serive routine for timer1 overflow. Reads data from the accelerometer
// and puts it into the accelerometer buffer.
void timerCallback() {
    bool test = true;
    AccelerometerRaw raw0;
    AccelerometerRaw raw1;
    AccelerometerRaw rawMedian;
    unsigned long t0;
    unsigned long t1;
    unsigned long t2;

    if ((accel.IsConnected) && (state.mode == MODE_STREAMING)) { 
        sei();
        // Take two measurements ... and compare them
        raw0 = accel.ReadRawAxis();
        raw1 = accel.ReadRawAxis();
        if (abs(raw0.XAxis - raw1.XAxis) > maxSampleDiff) {
            test=false;
        }
        if (abs(raw0.YAxis - raw1.YAxis) > maxSampleDiff) {
            test=false;
        }
        if (abs(raw0.ZAxis - raw1.ZAxis) > maxSampleDiff) {
            test=false;
        }
        if (test) {
            buffer.putVal(raw0);
        }
        else {
            state.badSampleCount++;
        }
        //Serial << raw0.XAxis << " " << raw1.XAxis << endl;
        //Serial << raw0.YAxis << " " << raw1.YAxis << endl;
        //Serial << raw0.ZAxis << " " << raw1.ZAxis << endl;
        //Serial << raw0.XAxis - raw1.XAxis << endl;
        //Serial << raw0.YAxis - raw1.YAxis << endl;
        //Serial << raw0.ZAxis - raw1.ZAxis << endl;
        //Serial << endl;
    }
}

int medianOfThree(int val0, int val1, int val2) {
    int vals[3];

}



