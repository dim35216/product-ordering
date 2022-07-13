% Product Sequencing encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Implementation of constraint 2 (same_volume)

reward_volume(X, Y) :- switch(X, Y), campaign(X, C), campaign(Y, C), volume(X, V), volume(Y, V),
                       packaging(X, P1), P1 != "Normal".

#show reward_volume/2.
#maximize{ 1@2, X, Y : reward_volume(X, Y) }.
