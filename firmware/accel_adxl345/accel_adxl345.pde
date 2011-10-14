/* 
  accel_adxl345.pde 
 
  Firmware for streaming data from the ADXL345 accelerometer.  
 
  Author: Will Dickson, IO Rodeo Inc.
 
 */ 
#include <FastWire.h>
#include <FastADXL345.h>
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

// Initialize serial port, I2C communications, setup accelerometer, acceleromter 
//  buffer and timer
void setup() {

    Serial.begin(baudRate);

    Wire.begin();
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
            break;

        case CMD_START_STREAM:
            ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
                state.mode = MODE_STREAMING;
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
                Serial << raw.XAxis << "," << raw.YAxis << "," << raw.ZAxis << endl;
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

        default:
            break;
    }

}

// Sends accelerometer data to the host PC
void sendAccelData() {
    static int cnt = 0;
    static AccelerometerRaw raw;

    while (buffer.getSize() > 0) {
        raw = buffer.getVal();
        Serial << raw.XAxis << " " << raw.YAxis << " " << raw.ZAxis;
        cnt++;
        if (cnt < maxSendCnt) {
            Serial << ":";
        }
        else {
            Serial << endl;
            cnt = 0;
        }
    }
}

// Interrupt serive routine for timer1 overflow. Reads data from the accelerometer
// and puts it into the accelerometer buffer.
void timerCallback() {
    static AccelerometerRaw raw;
    if ((accel.IsConnected) && (state.mode == MODE_STREAMING)) { 
        sei();
        raw = accel.ReadRawAxis();
        buffer.putVal(raw);
        //Serial << raw.XAxis << endl;
        //Serial << raw.YAxis << endl;
        //Serial << raw.ZAxis << endl;
    }
}



