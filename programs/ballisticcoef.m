clear
close all

RK4th = true;
count = 0;
RT2 = 100000.;
VT2 = -6000.;
BETA = 500.; % lb/ft^2 
RT2H = 100025.;
VT2H = -6150.;
BETAH = 800.;
ORDER = 3;
TS = .05;
TF = 30.;
Q33 = 0./TF;
T = 0.;
S = 0.;
H = .001;
SIGNOISE = sqrt(500.); % 0% 
PHI = zeros(ORDER,ORDER);
P = zeros(ORDER,ORDER);
Q = zeros(ORDER,ORDER);
IDN = eye(ORDER);
P(1,1) = SIGNOISE*SIGNOISE;
P(2,2) = 20000.;
P(3,3) = 300.^2;
HMAT = zeros(1,ORDER);
HMAT(1,1) = 1.;

while RT2 >= 0.
   
    RT2OLD = RT2;
    VT2OLD = VT2;
%     STEP = 1;
    rk_on = true;
    FLAG = 0;
    
    while rk_on % STEP <= 1
        
        if FLAG == 1
            RT2 = RT2+H*RT2D;
            VT2 = VT2+H*VT2D;
            T = T+H;
%             STEP = 2;
            rk_on = false;
        end
        
        RT2D = VT2;
        %    estimated air density     gravity  Vz^2                gravity
        %    
        VT2D = .0034 * exp(-RT2 / 22000.) * 32.174*VT2*VT2/(2.*BETA)-32.174;
        % betaD = 0
        FLAG = 1;
    end
    
    FLAG = 0;

    if RK4th
    RT2 = .5*(RT2OLD+RT2+H*RT2D);
    VT2 = .5*(VT2OLD+VT2+H*VT2D);
    end


%     fprintf('[%.8f %.8f]\n', RT2, VT2);
    S = S+H;
    
    if S >= TS-.00001
        S = 0.;
        
        % 
        % predict \ covariance 
        %% 
        RHOH = .0034*exp(-RT2H/22000.);
        F21 = -32.174*RHOH*VT2H*VT2H/(2.*22000.*BETAH);
        F22 = RHOH*32.174*VT2H/BETAH;
        F23 = -RHOH*32.174*VT2H*VT2H/(2.*BETAH*BETAH);
        PHI(1,1) = 1.;
        PHI(1,2) = TS;
        PHI(2,1) = F21*TS;
        PHI(2,2) = 1.+F22*TS;
        PHI(2,3) = F23*TS;
        PHI(3,3) = 1.;
        Q(2,2) = F23*F23*Q33*TS*TS*TS/3.;
        Q(2,3) = F23*Q33*TS*TS/2.;
        Q(3,2) = Q(2,3);
        Q(3,3) = Q33*TS;
        M = PHI*P*PHI'+Q;
        
        % 
        % correct 
        %% 
        HMHT = HMAT*M*HMAT';
        R = SIGNOISE * SIGNOISE;
        HMHTR = HMHT(1,1) + R;
        HMHTRINV = 1./HMHTR;
        MHT = M*HMAT';
        
        for I = 1:ORDER
            GAIN(I,1) = MHT(I,1)*HMHTRINV;
        end
        
        P = (IDN-GAIN*HMAT)*M;
        
        %
        % take a measure 
        %%
        XNOISE = randn * SIGNOISE;
        Z = RT2+XNOISE;
        
        
        % 
        % predict + correct \ state 
        %% 
        RT2DB = VT2H;
        VT2DB = .0034*32.174*VT2H*VT2H*exp(-RT2H/22000.)/(2.*BETAH)-32.174;
        RES = Z -(RT2H+RT2DB*TS);
        
        RT2H = RT2H+RT2DB*TS+GAIN(1,1)*RES;
        VT2H = VT2H+VT2DB*TS+GAIN(2,1)*RES;
        BETAH = BETAH+GAIN(3,1)*RES;
        
        % 
        % errors 
        %% 
        ERRY = RT2-RT2H;
        SP11 = sqrt(P(1,1));
        ERRV = VT2-VT2H;
        SP22 = sqrt(P(2,2));
        ERRBETA = BETA-BETAH;
        SP33 = sqrt(P(3,3));
        RT2K = RT2/1000.;
        count = count+1;
        ArrayT(count) = T;
        ArrayRT2(count) = RT2;
        ArrayRT2H(count) = RT2H;
        ArrayRT2K(count) = RT2K;
        ArrayVT2(count) = VT2;
        ArrayVT2H(count) = VT2H;
        ArrayBETA(count) = BETA;
        ArrayBETAH(count) = BETAH;
        ArrayERRBETA(count) = ERRBETA;
        ArraySP33(count) = SP33;
    end
end

lb2kg = 1;%0.453592; 
ft2m  = 1;%0.3048;


% z
figure
subplot(2, 2, 1)
hold on
plot(ArrayT, ArrayRT2 * ft2m, 'm', 'linewidth', 3);
plot(ArrayT, ArrayRT2H * ft2m, 'c', 'linewidth', 1.5);
grid
xlabel('Time (s)')
title('RT2 (m)')
legend('true', 'estimate')
% ax = ancestor(h, 'axes');
% ax.YAxis.Exponent = 0;
% ax.YAxis.TickLabelFormat = '%.0f';

% vz
subplot(2, 2, 3)
hold on 
plot(ArrayT, ArrayVT2 * ft2m, 'm', 'linewidth', 3)
plot(ArrayT, ArrayVT2H * ft2m, 'c', 'linewidth', 1.5)
grid
xlabel('Time (s)')
title('VT2 (m/s)')


% beta
subplot(2, 2, 2)
hold on 
plot(ArrayT, ArrayBETA * lb2kg / ft2m^2, 'm', 'linewidth', 2)
plot(ArrayT, ArrayBETAH * lb2kg / ft2m^2, 'c', 'linewidth', 2)
grid
xlabel('Altitude (KM)')
title('Ballistic Coefficient (kg/m^2)')
legend('true', 'estimate')
% axis([0 100 0 1000])


% figure
% plot(ArrayRT2K,ArraySP33,ArrayRT2K,-ArraySP33,ArrayRT2K,ArrayERRBETA, 'linewidth', 2)
% grid
% xlabel('Altitude (Kft)')
% title('Error in Ballistic Coefficient (Lb/Ft^2)')


% clc
output = [ArrayT',ArrayRT2K',ArrayRT2',ArrayRT2H',ArrayVT2',...
ArrayVT2H',ArrayBETA',ArrayBETAH'];
% save datfil.txt output /ascii
% disp 'simulation finished'






