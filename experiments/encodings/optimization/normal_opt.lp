% Product Sequencing encoding in Answer Set Programming
% Author: Michael Dinzinger
% 
% Implementation of normal optimization directive

#minimize{ C, X : changeover_time(X, Y, C), switch(X, Y) }.
