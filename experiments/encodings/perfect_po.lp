% Perfect TSP encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Advanced encoding with good properties in scalability
% The Encoding was copied from a video of the Potassco YouTube-Channel:
% https://youtu.be/m0wL33OO_DA

product(v).
changeover(v, X) :- product(X).
changeover_time(v, X, 0) :- product(X).
changeover(X, v) :- product(X).
changeover_time(X, v, 0) :- product(X).

rating_volume(X, Y) :- switch(X, Y), campaign(X, C), campaign(Y, C), volume(X, V), volume(Y, V),
                       packaging(X, P1), packaging(Y, P2), P1 != P2, P1 != "Normal".

#show rating_volume/2.
#maximize{ 1@2, X, Y : rating_volume(X, Y) }.

max_quantity_campaign(C, Qmax) :- Qmax = #max{ Q : campaign(X, C), quantity(X, Q) }, campaign(_, C).
rating_quantity(X, Y) :- switch(X, Y), campaign(X, C), campaign(Y, C), packaging(Y, "Normal"), quantity(Y, Qmax),
                         max_quantity_campaign(C, Qmax).

#show rating_quantity/2.
#maximize{ 1@2, X, Y : rating_quantity(X, Y) }.

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


impossible(X, Y) :- changeover(X, Y),
                    campaign(X, C1), campaign(Y, C2),
                    campaign_order(C1, O1), campaign_order(C2, O2),
                    O2 - O1 < 0.

{ switch(X, Y) : changeover(X, Y), not impossible(X, Y) } = 1 :- product(X).
{ switch(X, Y) : changeover(X, Y), not impossible(X, Y) } = 1 :- product(Y).

reached(X) :- X = #min{ Y : product(Y) }.
reached(Y) :- switch(X, Y), reached(X).

:- product(Y), not reached(Y).

campaign_switch(C1, C2, X, Y) :- switch(X, Y), campaign(X, C1), campaign(Y, C2). % , C1 != C2.
:- campaign_switch(C1, C2, _, _), campaign_switch(C2, C1, _, _), C1 != C2.
:- campaign_switch(C1, C2, X, _), campaign_switch(C1, C2, Y, _), C1 != C2, X != Y.
:- campaign_switch(C1, C2, _, X), campaign_switch(C1, C2, _, Y), C1 != C2, X != Y.
numCampaigns(N) :- N = #count{ C : product(X), campaign(X, C) }.
numCampaignSwitches(N) :- N = #count{ C1, C2 : campaign_switch(C1, C2, _, _), C1 != C2 }.
:- numCampaigns(N1), numCampaignSwitches(N2), N1 <= N2.

#show switch/2.

outcost(X, C) :- changeover_time(X, _, C).

order(X, C1, C2) :- outcost(X, C1), outcost(X, C2), C1 < C2, C <= C1 : outcost(X, C), C < C2.

penaulty(X, C1, C2 - C1) :- order(X, C1, C2), switch(X, Y), changeover_time(X, Y, C2).
penaulty(X, C1, C2 - C1) :- order(X, C1, C2), penaulty(X, C2, _).

#minimize{ D@1, X, C : penaulty(X, C, D) }.