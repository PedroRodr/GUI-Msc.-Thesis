
numero_sensores = 1;
numero_colunas = size(Cap_board_data,2);
numero_amostras = height(Cap_board_data);
A = Cap_board_data
%Remove channels defeituosos
B=A;
i=0;
for k = 1:(numero_colunas)
    if A(1,k) == 0
        B(:,k-i) = [];
        i= i+1;
    end
end
numero_colunas = numero_colunas-i
%Remove leituras defeituosas
C=B;
i=0;
for k = 1:(numero_amostras-1)
    if B(k,1) == 0
        C(k-i,:) = [];
        i= i+1;
    end
end
numero_amostras = numero_amostras-i-1;
D = filloutliers(C(1:numero_amostras,:),"mean"); %remove os outliers dos dados
%D = rmoutliers(C(1:numero_amostras,:),"percentile",[2 99]); %remove os outliers dos dados
E=D;
for k=1:numero_colunas
    E(:,k) = D(:,k) - median(D(:,k));   %Remove a media de cada sensor para obter a variacao
end
F=E;
%F = rmoutliers(E(:,1:numero_colunas),"percentiles",[30 99]); %remove os outliers dos dados
%j=[70:75];
%B(:,j) = [];
%j=[100:165];
%B(j,:) = [];


% x=linspace(0,4.8*(numero_colunas/numero_sensores),numero_colunas);
% x = round(x);
% y=linspace(0,numero_amostras,height(B))/10;
% y=round(y);
% figure
% imagesc(x,y,B)
% pbaspect([48*(numero_colunas/numero_sensores)/numero_amostras 1 1])
% cb1 =colorbar();
% ylabel(cb1,"Variação da capacitância [fF]",Rotation=270)
% colormap("jet")
% title("Original")
% xlabel ("X (mm)")
% ylabel ("Y (mm)")
x=linspace(0,(numero_colunas/numero_sensores),numero_colunas);
x = round(x);
y=linspace(0,numero_amostras,height(F))/10;
y=round(y);
figure
imagesc(x,y,F)
pbaspect([1 1 1])
cb1 =colorbar();
ylabel(cb1,"Variação da capacitância [fF]",Rotation=270)
colormap("jet")
title("Original")
xlabel ("X (mm)")
ylabel ("Y (mm)")
% Superficie
% figure
% x=linspace(0,4.8,12);
% x = round(x);
% surf(x,y,B,EdgeColor='none')
% pbaspect([numero_colunas/(numero_amostras) 1 1])
% cb1 =colorbar();
% ylabel(cb1,"Variação da capacitância [fF]",Rotation=270)
% colormap("jet")
% title("Imagem pós processamento")
% xlabel ("X")
% ylabel ("Y (mm)")


