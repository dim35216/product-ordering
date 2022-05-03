% Auxiliary logic program for converting a Product Ordering problem instance into a TSP instance
% Encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Addition of an auxiliary node V
% Processing of the input constants s (start) and e (end)
% 
% If s is specified:
%   The node V is connected with an outgoing arc to s of cost 0
%   To all remaining nodes, the node V is connected with an outgoing arc of cost 10080
% Else:
%   The node V is connected to all other nodes with an outgoing arc of cost 0
% 
% If e is specified:
%   The node V is connected with an ingoing arc to e of cost 0
%   To all remaining nodes, the node V is connected with an ingoing arc of cost 10080
% Else:
%   The node V is connected to all other nodes with an ingoing arc of cost 0

node(v).
edge(v, X) :- node(X), X != v.
edge(X, v) :- node(X), X != v.
cost(v, X, 0) :- edge(v, X), not node(s).
cost(v, X, 0) :- edge(v, X), X = s.
cost(v, X, 10080) :- edge(v, X), node(s), X != s.
cost(X, v, 0) :- edge(X, v), not node(e).
cost(X, v, 0) :- edge(X, v), X = e.
cost(X, v, 10080) :- edge(X, v), node(e), X != e.