accel_adxl345
-------------

A matlab class for interfacing the ADXL345 accelerometer via an Ardiuno. Note,
assumes the Arduino is running the firmware found in the accel_adxl345/firmware
directory.


Installation
------------
Place the accel_adxl345/matlab/src directory onto the matlab PATH. 

Basic Usage
-----------
dev = AccelADXL345('com1'); % Create device object
dev.setSampleRate(100);     % Set sample rate to 100Hz
dev.getSamples(100);        % Read 100 samples from device

Examples
--------
Examples demonstrating the use of this class can be found in the
accel_adxl345/matlab/examples folder.
