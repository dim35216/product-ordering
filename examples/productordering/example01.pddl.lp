% Definitions
#const timesteps=26.
time(1..timesteps).
product(p10012; p10014; p20001; p50013).

% ---- action: initialize ----
action(initialize(X))	:- product(X).

processing(X, T)	:- time(T), occ(initialize(X), T), product(X).
initialized(T)	:- time(T), occ(initialize(X), T), product(X).
overall_changeover_time(V, T)	:- time(T), occ(initialize(X), T), product(X), V = 0.
-overall_changeover_time(V, T)	:- time(T), occ(initialize(X), T), product(X), overall_changeover_time(V, T - 1).

possible(initialize(X), T)	:- time(T), available(X), not worked_off(X, T - 1), not processing(X, T - 1), not initialized(T - 1), not complete(T - 1), product(X).

% ---- action: switch ----
action(switch(X, Y))	:- product(X), product(Y).

worked_off(X, T)	:- time(T), occ(switch(X, Y), T), product(X), product(Y).
-processing(X, T)	:- time(T), occ(switch(X, Y), T), product(X), product(Y).
processing(Y, T)	:- time(T), occ(switch(X, Y), T), product(X), product(Y).
overall_changeover_time(V, T)	:- time(T), occ(switch(X, Y), T), product(X), product(Y), overall_changeover_time(V1, T - 1), changeover_time(X, Y, V2), V = V1 + V2.
-overall_changeover_time(V, T)	:- time(T), occ(switch(X, Y), T), product(X), product(Y), overall_changeover_time(V, T - 1).

possible(switch(X, Y), T)	:- time(T), available(X), available(Y), not worked_off(X, T - 1), processing(X, T - 1), not worked_off(Y, T - 1), not processing(Y, T - 1), initialized(T - 1), not complete(T - 1), product(X), product(Y).

% ---- action: finalize ----
action(finalize(X))	:- product(X).

worked_off(X, T)	:- time(T), occ(finalize(X), T), product(X).
-processing(X, T)	:- time(T), occ(finalize(X), T), product(X).
complete(T)	:- time(T), occ(finalize(X), T), product(X).

possible(finalize(X), T)	:- time(T), available(X), not worked_off(X, T - 1), processing(X, T - 1), initialized(T - 1), not complete(T - 1), product(X).

% ---- action: dummy ----
action(dummy).

possible(dummy, T)	:- time(T), complete(T - 1).

% Action generation rule with Executability constraint
1 { occ(A, T) : possible(A, T), action(A) } 1 :- time(T).

% Inertia rules
%% Fluents (Predicates)
processing(X, T)	:- time(T), processing(X, T - 1), not -processing(X, T).
worked_off(X, T)	:- time(T), worked_off(X, T - 1).
initialized(T)	:- time(T), initialized(T - 1).
complete(T)	:- time(T), complete(T - 1).
%% Numeric Fluents (Functions)
overall_changeover_time(V, T)	:- time(T), overall_changeover_time(V, T - 1), not -overall_changeover_time(V, T).

% Goal representation
%% Hard goals
goal :- complete(timesteps), worked_off(p10012, timesteps), worked_off(p10014, timesteps), worked_off(p20001, timesteps), worked_off(p50013, timesteps).
:- not goal.
%% Soft goals
#minimize{ V : overall_changeover_time(V, timesteps) }.

% Display
#show occ/2.

% Initial state
%% Fluents
available(p10014).
available(p10012).
available(p20001).
available(p50013).
%% Numeric Fluents
changeover_time(p10012, p10012, 9223372036854775807).
changeover_time(p10012, p10014, 6).
changeover_time(p10012, p20001, 9).
changeover_time(p10012, p50013, 8).
changeover_time(p10014, p10012, 6).
changeover_time(p10014, p10014, 9223372036854775807).
changeover_time(p10014, p20001, 10).
changeover_time(p10014, p50013, 15).
changeover_time(p20001, p10012, 3).
changeover_time(p20001, p10014, 3).
changeover_time(p20001, p20001, 9223372036854775807).
changeover_time(p20001, p50013, 12).
changeover_time(p50013, p10012, 15).
changeover_time(p50013, p10014, 22).
changeover_time(p50013, p20001, 27).
changeover_time(p50013, p50013, 9223372036854775807).
