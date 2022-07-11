% Product Sequencing encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Implementation of advanced optimization directive

outcost(X, C) :- changeover_time(X, _, C).

order(X, C1, C2) :- outcost(X, C1), outcost(X, C2), C1 < C2, C <= C1 : outcost(X, C), C < C2.

penaulty(X, C1, C2 - C1) :- order(X, C1, C2), switch(X, Y), changeover_time(X, Y, C2).
penaulty(X, C1, C2 - C1) :- order(X, C1, C2), penaulty(X, C2, _).

#minimize{ D@1, X, C : penaulty(X, C, D) }.
