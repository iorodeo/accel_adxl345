/*
  constants.h

  Constants and enumermations for the accel_adxl firmware.

  Will Dickson, IO Rodeo Inc.

*/ 
#ifndef CONSTANTS_H 
#define CONSTANTS_H


// Constants
const unsigned long baudRate = 38400;
const unsigned int maxSendCnt = 20;
const unsigned int bufferSize = 100;

const unsigned long defaultTimerPeriod = 2000;
const unsigned long minTimerPeriod = 2000;
const unsigned long maxTimerPeriod = 100000;

const unsigned int numRange = 4;
const unsigned int allowedRange[] = {2,4,8,16};
const unsigned int defaultRange = 16;

const int maxSampleDiff = 200;

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
    CMD_GET_MIN_TIMER_PERIOD,
    CMD_GET_BAD_SAMPLE_COUNT
};

#endif
