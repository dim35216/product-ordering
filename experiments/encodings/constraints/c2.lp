% Product Sequencing encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Implementation of constraint 2 (max_quantity)

max_quantity_campaign(C, Qmax) :- Qmax = #max{ Q : campaign(X, C), quantity(X, Q), packaging(X, "Normal") }, campaign(_, C).
penaulty_quantity(X, Y) :- switch(X, Y), campaign(X, C), campaign(Y, C), ackaging(X, "Normal"), quantity(X, Qmax),
                           max_quantity_campaign(C, Qmax).

#show penaulty_quantity/2.
#minimize{ 1@2, X, Y : penaulty_quantity(X, Y) }.
