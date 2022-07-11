% Perfect TSP encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Advanced encoding with good properties in scalability
% The Encoding was copied from a video of the Potassco YouTube-Channel:
% https://youtu.be/m0wL33OO_DA

{ cycle(X, Y) : edge(X, Y) } = 1 :- node(X).
{ cycle(X, Y) : edge(X, Y) } = 1 :- node(Y).

reached(X) :- X = #min{ Y : node(Y) }.
reached(Y) :- cycle(X, Y), reached(X).

:- node(Y), not reached(Y).

#show cycle/2.

outcost(X, C) :- cost(X, _, C).

order(X, C1, C2) :- outcost(X, C1), outcost(X, C2), C1 < C2, C <= C1 : outcost(X, C), C < C2.

penaulty(X, C1, C2 - C1) :- order(X, C1, C2), cycle(X, Y), cost(X, Y, C2).
penaulty(X, C1, C2 - C1) :- order(X, C1, C2), penaulty(X, C2, _).

#minimize{ D, X, C : penaulty(X, C, D) }.