dt = 0.01; %ms
timeline = 0:dt:100; %ms

V = -70;

weight = 1;

% leak
gl = 1;
El = -70;
% Ext
ge = 0;
Ee = -60;
% ihb
gi = 0;
Ei = -75;

ges = zeros(1,length(timeline));
gis = zeros(1,length(timeline));

ges(timeline > 10 & timeline < 11) = 1;

gis(timeline > 30 & timeline < 31) = 1;

ges(timeline > 50 & timeline < 51) = 1;
gis(timeline > 50 & timeline < 51) = 1;

ges(timeline > 70 & timeline < 71) = 1;
gis(timeline > 70.5 & timeline < 71.5) = 1;

ges(timeline > 90.5 & timeline < 91.5) = 1;
gis(timeline > 90 & timeline < 91) = 1;

prevge = 0;
prevgi = 0;
idx = 1;
clf;
for i = timeline
    % Apply gate values
    ge = ges(idx);
    gi = gis(idx);
    % Apply text
    if prevgi == 0 && gi > 0
        text(timeline(idx),El +1, 'IPSP')
    end
    if prevge == 0 && ge > 0
        text(timeline(idx),El-1, 'EPSP')
    end
    % Set history
    prevgi = gi;
    prevge = ge;
    % Add random gate value deviation (peak detection doesnt work with
    % rand)
%     ge = ge + (rand() -0.5) * 0.1;
%     gi = gi + (rand() -0.5) * 0.1;
    % Form
    V = V - dt*(gl*(V-El) + weight*ge*(V-Ee) + weight*gi*(V-Ei));
    % Save'n index
    rmV(idx) = V;
    idx = idx + 1;
end
hold on
plot(timeline, rmV)
xlabel('Time (ms)');
ylabel('Membrane potential (mV)');
% [val, idx] = max(rmV);
% text(timeline(idx), val, sprintf('Top: %.4f', val));
% Peaks
[pks,locs] = findpeaks(abs(rmV+75),'MinPeakDistance',6);
for idx = locs
    text(timeline(idx), rmV(idx), sprintf('Top: %.4f', rmV(idx)));
end