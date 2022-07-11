% Product Sequencing encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% In resemblance on the TSP encoding from the video of the Potassco YouTube-Channel:
% https://youtu.be/m0wL33OO_DA

% Transformation of PS instance in TSP instance
product(v).
changeover(v, X) :- product(X).
changeover_time(v, X, 0) :- product(X).
changeover(X, v) :- product(X).
changeover_time(X, v, 0) :- product(X).

% Generate
impossible(v, v).
{ switch(X, Y) : changeover(X, Y), not impossible(X, Y) } = 1 :- product(X).
{ switch(X, Y) : changeover(X, Y), not impossible(X, Y) } = 1 :- product(Y).

% Display
#show switch/2.

% Reachability test
reached(X) :- X = #min{ Y : product(Y) }.
reached(Y) :- switch(X, Y), reached(X).
:- product(Y), not reached(Y).
