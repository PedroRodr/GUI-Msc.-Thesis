
numero_sensores = 6;
numero_colunas = size(real_2d,2);
numero_amostras = height(real_2d);
A = rmoutliers(real_2d(1:numero_amostras,:),"mean"); %remove os outliers dos dados
for k=1:numero_colunas
    A(:,k) = A(:,k) - median(A(:,k));   %Remove a media de cada sensor para obter a variacao
end

% %Reorganiza as colunas
B = [];
i = 1;

for k =1:(numero_colunas)
    if rem(k, numero_colunas/numero_sensores) == 0
        B(:,i+(4*numero_sensores)) = A(:,k);
        i=i+1;
     elseif rem(k, numero_colunas/numero_sensores) == 4
         B(:,i+(3*numero_sensores)) = A(:,k);     
    elseif rem(k, numero_colunas/numero_sensores) == 3
        B(:,i+(2*numero_sensores)) = A(:,k);    
    elseif rem(k, numero_colunas/numero_sensores) == 2
        B(:,i+(numero_sensores)) = A(:,k);
    else
        B(:,i) = A(:,k);
    end
end
%B=A;
% n=1;
% for k=1:numero_colunas
%     if (B(:,k) == 0)
%         j(n) = k;
%         n= n + 1;
%     end
% end

%j=[70:75];
%B(:,j) = [];
%j=[100:165];
%B(j,:) = [];

%calibracao = B;

% x=linspace(0,4.8*(numero_colunas/numero_sensores),numero_colunas);
% x = round(x);
% y=linspace(0,numero_amostras,height(B(1:159,:)-calibracao))/10;
% y=round(y);
% figure
% imagesc(x,y,(B(1:159,:)-calibracao))
% pbaspect([48*(numero_colunas/numero_sensores)/numero_amostras 1 1])
% cb1 =colorbar();
% ylabel(cb1,"Variação da capacitância [fF]",Rotation=270)
% colormap("jet")
% title("Imagem pós processamento")
% xlabel ("X (mm)")
% ylabel ("Y (mm)")

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
y=linspace(0,numero_amostras,height(B))/10;
y=round(y);
figure
imagesc(x,y,B)
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
 pbaspect([numero_colunas/(numero_amostras) 1 1])
% cb1 =colorbar();
% ylabel(cb1,"Variação da capacitância [fF]",Rotation=270)
% colormap("jet")
% title("Imagem pós processamento")
% xlabel ("X")
% ylabel ("Y (mm)")


