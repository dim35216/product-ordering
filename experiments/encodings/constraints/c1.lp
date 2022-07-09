% Product Sequencing encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Implementation of constraint 1

impossible(X, Y) :- changeover(X, Y),
                    campaign(X, C1), campaign(Y, C2),
                    campaign_order(C1, O1), campaign_order(C2, O2),
                    O2 - O1 < 0.

campaign_switch(C1, C2, X, Y) :- switch(X, Y), campaign(X, C1), campaign(Y, C2). % , C1 != C2.
:- campaign_switch(C1, C2, _, _), campaign_switch(C2, C1, _, _), C1 != C2.
:- campaign_switch(C1, C2, X, _), campaign_switch(C1, C2, Y, _), C1 != C2, X != Y.
:- campaign_switch(C1, C2, _, X), campaign_switch(C1, C2, _, Y), C1 != C2, X != Y.
numCampaigns(N) :- N = #count{ C : product(X), campaign(X, C) }.
numCampaignSwitches(N) :- N = #count{ C1, C2 : campaign_switch(C1, C2, _, _), C1 != C2 }.
:- numCampaigns(N1), numCampaignSwitches(N2), N1 <= N2.
