% TSP encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Normal encoding with bad properties in scalability

rating_volume(X, Y) :- switch(X, Y), campaign(X, C), campaign(Y, C), volume(X, V), volume(Y, V),
                       packaging(X, P1), packaging(Y, P2), P1 != P2, P1 != 'Normal'.

#show rating_volume/2.
#maximize{ 1@2, X, Y : rating_volume(X, Y) }

max_size_campaign(C, S) :- Smax = #max{ S : campaign(Z, C), size(Z, S) }, campaign(_, C).
rating_size(X, Y) :- switch(X, Y), campaign(X, C), campaign(Y, C), packaging(Y, 'Normal'), size(Y, Smax),
                     max_size_campaign(C, Smax).

#show rating_size/2.
#maximize{ 1@2, X, Y : rating_size(X, Y) }

impossible(X, Y) :- changeover(X, Y),
                    campaign(X, C1), campaign(Y, C2),
                    campaign_order(C1, O1), campaign_order(C2, O2),
                    O2 - O1 < 0.

{ switch(X, Y) : changeover(X, Y), not impossible(X, Y) } = 1 :- product(X).
{ switch(X, Y) : changeover(X, Y), not impossible(X, Y) } = 1 :- product(Y).

reached(X) :- X = #min{ Y : product(Y) }.
reached(Y) :- switch(X, Y), reached(X).

:- product(Y), not reached(Y).

campaign_switch(C1, C2) :- switch(X, Y), campaign(X, C1), campaign(Y, C2), C1 != C2.
numCampaigns(N) :- N = #sum{ 1, C : product(X) , campaign(X, C) }.
numCampaignSwitches(N) :- N = #sum{ 1, C1, C2 : campaign_switch(C1, C2) }.
:- numCampaigns(N1), numCampaignSwitches(N2), N1 != N2 + 1.

#show switch/2.

#minimize{ C, X : changeover_time(X, Y, C), switch(X, Y) }.