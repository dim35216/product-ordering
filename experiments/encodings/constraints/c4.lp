% Product Sequencing encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Implementation of constraint 4

duration(X, D) :- product(X), X != v, quantity(X, Q), plannedPerformance(X, P), D = (Q * 60 / P).
#show duration/2.

processing(Y, S, E, 1) :- switch(v, Y), duration(Y, D), S = 150, E = (S + D).
processing(Y, S, E, C + 1) :- switch(X, Y), X != v, Y != v, processing(X, _, Ex, C),
                                      changeover_time(X, Y, T), S = (Ex + T + 1),
                                      duration(Y, D), E = (S + D), C < #count{ Xc : product(Xc) }.
#show processing/4.

processing_bc(X, Smod, Emod) :- bottleCrate(X, "True"), processing(X, S, E, _), Smod = ((S / 360) \ 4), Emod = ((E / 360) \ 4).
#show processing_bc/3.

processing_bc_daytime(X) :- bottleCrate(X, "True"),
                           { processing_bc(X, 1, 1); processing_bc(X, 1, 2); processing_bc(X, 2, 2) } = 1.
#show processing_bc_daytime/1.
#maximize{ 1@3, X : processing_bc_daytime(X) }.
% :- bottleCrate(X, "True"), not processing_bc_daytime(X).
