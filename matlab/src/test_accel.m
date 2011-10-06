function test_accel
    
    fprintf('\nOpening device ... ');
    dev = AccelADXL345('com57');
    dev.open();
    fprintf('done\n\n');
    
    fprintf('sampleDt: %d\n', dev.sampleDt);
    fprintf('maxSampleDt: %d\n', dev.maxSampleDt);
    fprintf('minSampleDt: %d\n', dev.minSampleDt);
    fprintf('range: %d\n', dev.range);
    fprintf('\n');
    
    newDt = 8000;
    fprintf('setting sampleDt to %d\n', newDt); 
    dev.setSampleDt(newDt);
    fprintf('sampleDt: %d\n\n', dev.sampleDt);
    
    freq = 500;
    fprintf('setting sample rate to: %f (Hz)\n', freq);
    dev.setSampleRate(freq);
    freq = dev.getSampleRate();
    fprintf('sample rate: %f (Hz)\n', freq);
    fprintf('sampleDt: %d\n\n', dev.sampleDt);
    
   
    newRange = 16;
    fprintf('setting range to %d\n', newRange);
    dev.setRange(newRange);
    fprintf('range: %d\n\n', dev.range);
    
    fprintf('getting single sample using peek\n');
    accel = dev.peek();
    fprintf('dev.peek = [%f, %f, %f]\n\n', accel(1), accel(2), accel(3));
    
    n = 1000;
    fprintf('grabbing %d samples\n',n)
    [data, t] = dev.getSamples(n);
    
    dev.close();
    delete(dev);
    
    subplot(3,1,1)
    plot(t,data(:,1),'.');
    ylabel('ax')
    
    subplot(3,1,2)
    plot(t,data(:,2),'.');
    ylabel('ay');
    
    subplot(3,1,3)
    plot(t,data(:,3),'.');
    ylabel('az')
    xlabel('t (sec)')

end