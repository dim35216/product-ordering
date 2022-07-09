% TSP encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Normal encoding with bad properties in scalability

{ cycle(X, Y) : edge(X, Y) } = 1 :- node(X).
{ cycle(X, Y) : edge(X, Y) } = 1 :- node(Y).

reached(X) :- X = #min{ Y : node(Y) }.
reached(Y) :- cycle(X, Y), reached(X).

:- node(Y), not reached(Y).

#show cycle/2.

#minimize{ C, X : cost(X, Y, C), cycle(X, Y) }.