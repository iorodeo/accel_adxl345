/*
  constants.h

  Constants and enumermations for the accel_adxl firmware.

  Will Dickson, IO Rodeo Inc.

*/ 
#ifndef CONSTANTS_H 
#define CONSTANTS_H


// Constants
const unsigned long baudRate = 115200;
const unsigned int maxSendCnt = 15;
const unsigned int bufferSize = 50;

const unsigned long defaultTimerPeriod = 2000;
const unsigned long minTimerPeriod = 2000;
const unsigned long maxTimerPeriod = 100000;

const unsigned int numRange = 4;
const unsigned int allowedRange[] = {2,4,8,16};
const unsigned int defaultRange = 16;

// Enumss
enum OperatingMode {
    MODE_STOPPED, 
    MODE_STREAMING
};

enum SerialCmd {
    CMD_STOP_STREAM, 
    CMD_START_STREAM,
    CMD_SET_TIMER_PERIOD,
    CMD_GET_TIMER_PERIOD, 
    CMD_SET_RANGE,
    CMD_GET_RANGE,
    CMD_GET_SAMPLE,
    CMD_GET_MAX_TIMER_PERIOD,
    CMD_GET_MIN_TIMER_PERIOD
};

#endif
