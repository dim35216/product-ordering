% Product Sequencing encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Implementation of constraint 2 (max_quantity)

max_quantity_campaign(C, Qmax) :- Qmax = #max{ Q : campaign(X, C), quantity(X, Q) }, campaign(_, C).
rating_quantity(X, Y) :- switch(X, Y), campaign(X, C), campaign(Y, C), packaging(Y, "Normal"), quantity(Y, Qmax),
                         max_quantity_campaign(C, Qmax).

#show rating_quantity/2.
#maximize{ 1@2, X, Y : rating_quantity(X, Y) }.
