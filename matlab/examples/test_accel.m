% test_accel.m
%
% A simple test of the AccelADXL345 accelerometer class. Reads values from
% the devices. Sets the sample dt and the sample frequency. Reads values 
% using peek. Reads values using getSamples.
%
% ---------------------------------------------------------------------------
function test_accel
    
    % Open the device
    fprintf('\nOpening device ... ');
    dev = AccelADXL345('com57');
    dev.open();
    fprintf('done\n\n');
    
    % Read some values from the device
    fprintf('sampleDt: %d\n', dev.sampleDt);
    fprintf('maxSampleDt: %d\n', dev.maxSampleDt);
    fprintf('minSampleDt: %d\n', dev.minSampleDt);
    fprintf('range: %d\n', dev.range);
    fprintf('\n');
    
    % Try changing the sample dt
    newDt = 8000;
    fprintf('setting sampleDt to %d\n', newDt); 
    dev.setSampleDt(newDt);
    fprintf('sampleDt: %d\n\n', dev.sampleDt);
    
    % Try chaning the sample rate
    freq = 500;
    fprintf('setting sample rate to: %f (Hz)\n', freq);
    dev.setSampleRate(freq);
    freq = dev.getSampleRate();
    fprintf('sample rate: %f (Hz)\n', freq);
    fprintf('sampleDt: %d\n\n', dev.sampleDt);
    
    % Try chaning the range setting
    newRange = 16;
    fprintf('setting range to %d\n', newRange);
    dev.setRange(newRange);
    fprintf('range: %d\n\n', dev.range);
    
    % Grab a simple sample using peek
    fprintf('getting single sample using peek\n');
    accel = dev.peek();
    fprintf('dev.peek = [%f, %f, %f]\n\n', accel(1), accel(2), accel(3));
    
    % Grab a number of samples - paced at sample rate
    n = 5000;
    fprintf('grabbing %d samples\n',n)
    [data, t] = dev.getSamples(n);
    
    % Close and delete the device
    dev.close();
    delete(dev);
    
    % Plot the results
    subplot(3,1,1)
    plot(t,data(:,1));
    ylabel('ax')
    
    subplot(3,1,2)
    plot(t,data(:,2));
    ylabel('ay');
    
    subplot(3,1,3)
    plot(t,data(:,3));
    ylabel('az')
    xlabel('t (sec)')

end
