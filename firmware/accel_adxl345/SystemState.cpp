/*
  SystemState.cpp
 
  Author: William Dickson, IO Rodeo Inc.
 
 */

#include "TimerOne.h"
#include "SystemState.h"

SystemState::SystemState() {
    mode = MODE_STOPPED;
    timerPeriod = defaultTimerPeriod;
}

void SystemState::init() {
    Timer1.initialize(timerPeriod);
}

void SystemState::setTimerInterrupt(void (*isr)()) {
    Timer1.attachInterrupt(isr);
}

void SystemState::setTimerPeriod(unsigned long period) {
    if ((period >= minTimerPeriod) && (period <= maxTimerPeriod)) {
        timerPeriod = period;
        Timer1.setPeriod(timerPeriod);
    }
}

unsigned long SystemState::getTimerPeriod() {
    return timerPeriod;
}


