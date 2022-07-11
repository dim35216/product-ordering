% Product Sequencing encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Implementation of constraint 2 (same_volume)

rating_volume(X, Y) :- switch(X, Y), campaign(X, C), campaign(Y, C), volume(X, V), volume(Y, V),
                       packaging(X, P1), P1 != "Normal".

#show rating_volume/2.
#maximize{ 1@2, X, Y : rating_volume(X, Y) }.
