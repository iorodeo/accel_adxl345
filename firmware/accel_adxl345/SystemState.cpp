/*
  SystemState.cpp
 
  Author: William Dickson, IO Rodeo Inc.
 
 */

#include "TimerOne.h"
#include "SystemState.h"

SystemState::SystemState() {
    mode = MODE_STOPPED;
    timerPeriod = defaultTimerPeriod;
    setRange(defaultRange);
    badSampleCount = 0;
}

void SystemState::init() {
    Timer1.initialize(timerPeriod);
}

void SystemState::setTimerInterrupt(void (*isr)()) {
    Timer1.attachInterrupt(isr);
}

void SystemState::setTimerPeriod(unsigned long value) {
    if ((value >= minTimerPeriod) && (value <= maxTimerPeriod)) {
        timerPeriod = value;
        Timer1.setPeriod(timerPeriod);
    }
}

unsigned long SystemState::getTimerPeriod() {
    return timerPeriod;
}

unsigned int SystemState::getRange() {
    return range;
}

void SystemState::setRange(unsigned int value) {
    bool test = false;
    // Check that value is in the set of allowed ranges
    for (int i=0; i<numRange; i++) {
        if (value == allowedRange[i]) {
            test = true;
        }
    }
    // Set range and maxValue
    if (test) {
        range = value;
    }
}


