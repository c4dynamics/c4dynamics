count   	=	0;
VC      	=	4000.;
XNT     	=	96.6;
YIC     	=	0.;
VM      	=	3000.;

HEDEG   	=	0.;     % initial heading error degrees     
HEDEGFIL	=	20.;
XNP     	=	3.;     % kalman gain 

SIGRIN  	=	.001;
TS      	=	.1;
APN     	=	0.;
TF      	=	10.;
Y       	=	YIC;
YD      	=	-VM*HEDEG/57.3;
YDIC    	=	YD;

TS2     	=	TS*TS;
TS3     	=	TS2*TS;
TS4     	=	TS3*TS;
TS5     	=	TS4*TS;

PHIN    	=	XNT*XNT/TF;
RTM     	=	VC*TF;

SIGNOISE	=	SIGRIN;
SIGPOS  	=	RTM*SIGNOISE;
SIGN2   	=	SIGPOS^2;

P11     	=	SIGN2;
P12     	=	0.;
P13     	=	0.;
P22     	=	(VM*HEDEGFIL/57.3)^2;
P23     	=	0.;
P33     	=	XNT*XNT;

T       	=	0.;
H       	=	.01;
S       	=	0.;
YH      	=	0.;
YDH     	=	0.;
XNTH    	=	0.;
XNC     	=	0.;

while T <= (TF - 1e-5)
    YOLD=Y;                         % relative position 
    YDOLD=YD;                       % relative velocity        
    
    
    %
    % integration 
    %% 
    STEP=1;
    FLAG=0;
    while STEP <=1
        if FLAG==1
            Y=Y+H*YD;
            YD=YD+H*YDD;
            T=T+H;
            STEP=2;
        end
        
        %
        % proportional navigation 
        %% 
        TGO=TF-T+.00001;
        RTM=VC*TGO;
        XLAM=Y/(VC*TGO);
        XLAMD=(RTM*YD+Y*VC)/(RTM^2);
        
        YDD=XNT-XNC;                % relative acceleration    
        
        
        FLAG=1;
    end
    
    
    FLAG=0;
    Y=.5*(YOLD+Y+H*YD);             % 2nd order runge kutta (1)
    YD=.5*(YDOLD+YD+H*YDD);         % 2nd order runge kutta (2)
    S=S+H;
    
    if S >= (TS - 1e-5)
        
        S       	=	0.;
        TGO     	=	TF-T+.000001;
        RTM     	=	VC*TGO;
        SIGNOISE	=	SIGRIN;
        SIGPOS  	=	RTM*SIGNOISE;
        SIGN2   	=	SIGPOS^2;
        
        % 
        % covariance matrix prediction
        %% 
        M11=P11+TS*P12+.5*TS2*P13+TS*(P12+TS*P22+.5*TS2*P23);
        M11=M11+.5*TS2*(P13+TS*P23+.5*TS2*P33)+TS5*PHIN/20.;
        M12=P12+TS*P22+.5*TS2*P23+TS*(P13+TS*P23+.5*TS2*P33)+TS4*PHIN/8.;
        M13=P13+TS*P23+.5*TS2*P33+PHIN*TS3/6.;
        M22=P22+TS*P23+TS*(P23+TS*P33)+PHIN*TS3/3.;
        M23=P23+TS*P33+.5*TS2*PHIN;
        M33=P33+PHIN*TS;
        
        %
        % kalman gains
        %%
        K1=M11/(M11+SIGN2);
        K2=M12/(M11+SIGN2);
        K3=M13/(M11+SIGN2);
        
        %
        % covariance matrix correction
        %% 
        P11=(1.-K1)*M11;
        P12=(1.-K1)*M12;
        P13=(1.-K1)*M13;
        P22=-K2*M12+M22;
        P23=-K2*M13+M23;
        P33=-K3*M13+M33;
        
        %
        % measurement 
        %% 
        XLAMNOISE=SIGNOISE*randn;
        YSTAR=RTM*(XLAM+XLAMNOISE);
        
        %
        % innovation
        %%
        RES=YSTAR-YH-TS*YDH-.5*TS*TS*(XNTH-XNC);
        
        %
        % state prediction + correction 
        %%
        YH=K1*RES+YH+TS*YDH+.5*TS*TS*(XNTH-XNC); % position estimation: y' = yd * dt,  
        YDH=K2*RES+YDH+TS*(XNTH-XNC);            % velocity estimation  yd' = ydd * dt,  
        XNTH=K3*RES+XNTH;                        % acc estimation 
        
        
        XLAMDH=(YH+YDH*TGO)/(VC*TGO*TGO);        % line of sight estimation     
        XNC=XNP*VC*XLAMDH+APN*.5*XNP*XNTH;       % acceleration command    
        
        ERRNT=XNT-XNTH;
        
        SP33=sqrt(P33);
        SP33P=-SP33;
        
        
        
        % 
        % store
        %% 
        count=count+1;
        ArrayT(count)=T;
        ArrayXNTG(count)=XNT/32.2;
        ArrayXNTHG(count)=XNTH/32.2;
        ArrayERRNTG(count)=ERRNT/32.2;
        ArraySP33G(count)=SP33/32.2;
        ArraySP33PG(count)=SP33P/32.2;
        ArrayY(count)=Y;
        ArrayXNCG(count)=XNC/32.2;
    end
end

% acceleration 
figure
plot(ArrayT,ArrayXNTG,ArrayT,ArrayXNTHG),grid
xlabel('Time (S)')
ylabel('Acceleration (G)')
legend('', 'true')

% acceleration error
figure
plot(ArrayT,ArrayERRNTG,ArrayT,ArraySP33G,ArrayT,ArraySP33PG),grid
xlabel('Time (S)')
ylabel('Error in Acceleration (G)')
legend('err', 'std')
clc
output=[ArrayT',ArrayY',ArrayXNCG',ArrayXNTG',ArrayXNTHG',ArrayERRNTG',ArraySP33G',ArraySP33PG'];
save datfil.txt output /ascii
disp('simulation finished')
    

% position 
figure
plot(ArrayT,ArrayXNTG,ArrayT,ArrayXNTHG),grid
xlabel('Time (S)')
ylabel('velocity (m/s)')
legend('', 'true')


    
    
    
    