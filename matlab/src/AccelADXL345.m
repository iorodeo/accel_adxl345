% AccelADXL345.m
%
% Interface to ADXL345 accelerometer connected to Arduino.
%
% Will Dickson, IO Rodeo Inc.
% -------------------------------------------------------------------------
classdef AccelADXL345 < handle
    
    properties (Constant)
        % Serial communication command ids
        cmdStopStreaming = 0;
        cmdStartStreaming = 1;
        cmdSetTimerPeriod = 2;
        cmdGetTimerPeriod = 3;
        cmdSetRange = 4;
        cmdGetRange = 5;
        cmdGetSample = 6;
        cmdGetMaxTimerPeriod = 7;
        cmdGetMinTimerPeriod = 8;
        
        % Set of allowed accelerations ranges
        allowedAccelRange = [2,4,8,16];
        
        % Scale factor for converting integers values to accelerations
        accelScale = 0.0384431560448;
    end
    
    properties
        % Serial communication parameters
        ser = [];
        port = [];
        baudrate = 38400;
        databits = 8;
        stopbits = 1;
        timeout = 1.0;
        resetDelay = 2.0;
        terminator = 'LF';
    end
    
    properties (SetAccess=private)
         % Data streaming parameters
        sampleDt = [];
        maxSampleDt = 10000;
        minSampleDt = 2000;
        range = [];
    end
    
    properties (Dependent)
        isOpen;
    end
    
    methods
        
        function self = AccelADXL345(port,baudrate)
            self.ser = serial( ...
                port, ...
                'baudrate', self.baudrate, ...
                'databits', self.databits, ...
                'stopbits', self.stopbits, ...
                'timeout',  self.timeout, ...
                'terminator', self.terminator ...
                );
        end
        
        function open(self)
            % Open serial port if not already open.
            if self.isOpen == false
                fopen(self.ser);
                pause(self.resetDelay);
            end
            self.emptyBuffer();
            self.sampleDt = self.getSampleDt();
            self.maxSampleDt = self.getMaxSampleDt();
            self.minSampleDt = self.getMinSampleDt();
            self.range = self.getRange();
        end
        
        function close(self)
            % close serial port is not already closed
            if self.isOpen == true
                fclose(self.ser);
                self.sampleDt = [];
                self.range = [];
            end
        end
        
        function delete(self)
            % Object delete function. Closes and deletes serial port
            % object.
            if self.isOpen
                self.close();
            end
            delete(self.ser);
        end
        
        function isOpen = get.isOpen(self)
            % Checks is serial port is open. Returns true (1) if it is and
            % false (0) if it is not.
            status = get(self.ser,'Status');
            if strcmpi(status,'open')
                isOpen = true;
            else
                isOpen = false;
            end
        end
        
        function dt = getMaxSampleDt(self)
            % Returns the maximum allowed sample dt
            cmd = sprintf('[%d]', self.cmdGetMaxTimerPeriod);
            self.sendCmd(cmd);
            dt = self.readNum();
        end
        
        function dt = getMinSampleDt(self)
            % Returns the minimum allowed sample dt
            cmd = sprintf('[%d]', self.cmdGetMinTimerPeriod);
            self.sendCmd(cmd);
            dt = self.readNum();
        end
        
        function dt = getSampleDt(self)
            % Get current sample dt, in microseconds, for acquiring data
            % from the device.
            cmd = sprintf('[%d]', self.cmdGetTimerPeriod);
            self.sendCmd(cmd);
            dt = self.readNum();
        end
        
        function setSampleDt(self, dt)
            % Sets the sample dt, given in microseconds, for acquiring data
            % from the device.
            if dt > self.maxSampleDt
                error('sample dt is too large');
            end
            if dt < self.minSampleDt
                error('sample dt is too small');
            end
            cmd = sprintf('[%d, %d]', self.cmdSetTimerPeriod, floor(dt));
            self.sendCmd(cmd);
            self.sampleDt = self.getSampleDt();
        end
        
        function range = getRange(self)
           % Gets the current acceleration range from the device
           cmd = sprintf('[%d]', self.cmdGetRange);
           self.sendCmd(cmd);
           range = self.readNum();
        end
        
        function setRange(self, range)
           % Sets the current acceleration range
           self.checkRange(range);
           cmd = sprintf('[%d, %d]', self.cmdSetRange, range);
           self.sendCmd(cmd);
           self.range = self.getRange();
        end
        
        function accel = peek(self)
            % Grabs a single sample from the device
            cmd = sprintf('[%d]', self.cmdGetSample);
            self.sendCmd(cmd);
            out = fscanf(self.ser);
            
            % Convert values to float array
            accel = str2array(out);
            accel = accel*self.accelScale;
            
        end
        
        function setSampleRate(self, freq)
            % Set the sample rate of the device to freq, where freq is
            % given in Hz. 
            dtSec = 1.0/freq;
            dtMicroSec = round(dtSec*1.0e6);
            self.setSampleDt(dtMicroSec);
        end
        
        function freq = getSampleRate(self)
            % Returns the current sample rate in Hz.
            dtSec = self.sampleDt*1.0e-6;
            freq = 1.0/dtSec;
        end
        
        function [data, t] = getSamples(self,n)
           % Acquire n samples from the device with the sample rate specified
           % by 1/sampleDt. 
           
           % Start Streaming
           self.emptyBuffer();
           self.startStreaming()
           
           % Collect data from device
           data = zeros(n,3);
           done = false;
           cnt = 1;
           while ~done
               outData = fread(self.ser,3, 'int16');
               outSync = fread(self.ser,1, 'uint8');
               % Check that last byte is zero - if not we are out of sync
               if ~(outSync == 0) 
                   error('Error reading data - stream out of sync');
               end
               data(cnt,:) = [outData(1),outData(2),outData(3)];
               cnt = cnt + 1;
               if cnt >= n
                   done = true;
               end
           end
           
           % Stop Streaming and empty buffer
           self.stopStreaming();
           self.emptyBuffer();
           
           % Convert integer data to acceleration and create time array
           data = self.accelScale*data;
           dtSec = self.sampleDt*1.0e-6;
           t = [1:n]*dtSec;
        end
        
        %end
        % -----------------------------------------------------------------
        %methods (Access=private)
        
        function emptyBuffer(self)
            % Empty serial port buffer
            if self.isOpen
                if self.ser.BytesAvailable > 0
                    fread(self.ser, self.ser.BytesAvailable);
                end
            end
        end
        
        function sendCmd(self,cmd)
            % Send command to serial serice
            if self.isOpen
                fprintf(self.ser,'%s\n',cmd);
            else
                error('serice must be open to send message');
            end
        end
        
        function val = readNum(self)
            % Reads a single number from the serial port.
            outStr = fscanf(self.ser);
            val = str2num(outStr);
        end
        
        function stopStreaming(self)
            % Stop serice streaming
            cmd = sprintf('[%d]', self.cmdStopStreaming);
            self.sendCmd(cmd);
        end
        
        function startStreaming(self)
            % Start serice streaming
            cmd = sprintf('[%d]', self.cmdStartStreaming);
            self.sendCmd(cmd);
        end
        
        function checkRange(self,val)
           % Check whether or not the value is within the set of allowed
           % acceleration ranges.
           if ~any(self.allowedAccelRange == val)
               error('acceleration range not allowed');
           end
           
        end
        
    end
    
end


% -------------------------------------------------------------------------
function array = str2array(line)
% Converts an input string of numbers separated by commas into to an array.

line = strtrim(line);
line = strsplit(line,' ');
array = zeros(size(line));

% Convert elements to doubles
test = true;
for i = 1:length(line)
    array(i) = str2double(line{i});
    if isempty(array(i))
        test = false;
    end
end
% Return empty array if read failed
if test == false
    array = [];
end
end
