% simple.m
%
% A simple example demonstrating how to use the AccelADXl345 accelerometer
% class.
% 
% --------------------------------------------------------------------------
function simple

    % Open the device
    dev = AccelADXL345('com57');
    dev.open();

    % Set the sample rate
    dev.setSampleRate(500);

    % Get the samples
    [data, t] = dev.getSamples(500);

    % Plot the results
    subplot(3,1,1)
    plot(t,data(:,1));
    ylabel('ax (m/s)')
    
    subplot(3,1,2)
    plot(t,data(:,2));
    ylabel('ay (m/s)');
    
    subplot(3,1,3)
    plot(t,data(:,3));
    ylabel('az (m/s)')
    xlabel('t (sec)')

end


