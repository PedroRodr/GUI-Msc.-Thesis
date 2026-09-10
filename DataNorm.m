function [ DataN ] = DataNorm(data, scale)
%   Tested in MATLAB R2014a
%
%DataNorm takes an MxN data set and normalises the data to the maximum
%value.
%Input
%   Data        A one or two dimensional matrix of intensity data
%   Scale      Choose the scale, either decibels 'db' or linear 'lin'
%   
%   Benjamin Knight-Gregson
%   Ben@Knight-Gregson.com
if strcmp(scale,'db')==1
    if max(max(data)) <= 0
        data=data-min(min(data)); %Shifts data so that minimum value equals zero.
    end
    if min(size(data))==1
        DataN=mag2db(data/max(data));
    else
        DataN=mag2db(data./max(max(data)));
    end
end
if strcmp(scale,'lin')==1
    if min(size(data))==1
        DataN=data/max(data);
    else
        DataN=data./max(max(data));
    end
end
end

