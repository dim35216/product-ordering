% Perfect TSP encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Advanced encoding with good properties in scalability
% The Encoding was copied from a video of the Potassco YouTube-Channel:
% https://youtu.be/m0wL33OO_DA

impossible(X, Y) :- changeover(X, Y),
                    campaign(X, C1), campaign(Y, C2),
                    campaign_order(C1, O1), campaign_order(C2, O2),
                    O2 - O1 < 0.

{ switch(X, Y) : changeover(X, Y), not impossible(X, Y) } = 1 :- product(X).
{ switch(X, Y) : changeover(X, Y), not impossible(X, Y) } = 1 :- product(Y).

reached(X) :- X = #min{ Y : product(Y) }.
reached(Y) :- switch(X, Y), reached(X).

:- product(Y), not reached(Y).

campaign_switch(C1, C2) :- switch(X, Y), campaign(X, C1), campaign(Y, C2).
:- campaign_switch(C1, C2), campaign_switch(C2, C1).

#show switch/2.

outcost(X, C) :- changeover_time(X, _, C).

order(X, C1, C2) :- outcost(X, C1), outcost(X, C2), C1 < C2, C <= C1 : outcost(X, C), C < C2.

penaulty(X, C1, C2 - C1) :- order(X, C1, C2), switch(X, Y), changeover_time(X, Y, C2).
penaulty(X, C1, C2 - C1) :- order(X, C1, C2), penaulty(X, C2, _).

#minimize{ D, X, C : penaulty(X, C, D) }.