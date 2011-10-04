/* 
  SystemState.h
 
  Author: Will Dickson, IO Rodeo Inc.
 
 */ 
#ifndef SYSTEM_STATE_H
#define SYSTTEM_STATE_H
#include "constants.h"

class SystemState {

    public: 
        SystemState();
        OperatingMode  mode; 
        void init();
        void setTimerInterrupt(void (*isr)());
        void setTimerPeriod(unsigned long timerPeriod);
        unsigned long getTimerPeriod();

    private:
        unsigned long timerPeriod; 
};

#endif

