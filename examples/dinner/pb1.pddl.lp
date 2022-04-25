% Definitions
#const timesteps=4.
time(1..timesteps).

%% Constants
% empty
%% Objects
% empty

% ---- action: cook ----
action(cook).

dinner(T)	:- time(T), occ(cook, T).

possible(cook, T)	:- time(T), clean(T - 1).

% ---- action: wrap ----
action(wrap).

present(T)	:- time(T), occ(wrap, T).

possible(wrap, T)	:- time(T), quiet(T - 1).

% ---- action: carry ----
action(carry).

-garbage(T)	:- time(T), occ(carry, T).
-clean(T)	:- time(T), occ(carry, T).

possible(carry, T)	:- time(T), garbage(T - 1).

% ---- action: dolly ----
action(dolly).

-garbage(T)	:- time(T), occ(dolly, T).
-quiet(T)	:- time(T), occ(dolly, T).

possible(dolly, T)	:- time(T), garbage(T - 1).

% Action generation rule with Executability constraint
1 { occ(A, T) : possible(A, T), action(A) } 1 :- time(T).

% Inertia rules
%% Fluents (Predicates)
clean(T)	:- time(T), clean(T - 1), not -clean(T).
dinner(T)	:- time(T), dinner(T - 1).
quiet(T)	:- time(T), quiet(T - 1), not -quiet(T).
present(T)	:- time(T), present(T - 1).
garbage(T)	:- time(T), garbage(T - 1), not -garbage(T).
%% Numeric Fluents (Functions)
% empty

% Goal representation
%% Hard goals
goal :- dinner(timesteps), present(timesteps), not garbage(timesteps).
:- not goal.
%% Soft goals
% empty

% Display
#show occ/2.

% Initial state
%% Fluents
garbage(0).
clean(0).
quiet(0).
%% Numeric Fluents
% empty
