% TW Prolog Demo for Time_Warp IDE
% Educational demonstration of logic programming concepts

% Facts about family relationships
parent(john, mary).
parent(john, mike).
parent(susan, mary).
parent(susan, mike).
parent(mary, alice).
parent(mary, bob).
parent(mike, charlie).

% Gender facts
male(john).
male(mike).
male(bob).
male(charlie).
female(susan).
female(mary).
female(alice).

% Rules defining relationships
father(F, C) :- parent(F, C), male(F).
mother(M, C) :- parent(M, C), female(M).
grandparent(GP, GC) :- parent(GP, P), parent(P, GC).
grandfather(GF, GC) :- grandparent(GF, GC), male(GF).
grandmother(GM, GC) :- grandparent(GM, GC), female(GM).
sibling(S1, S2) :- parent(P, S1), parent(P, S2), S1 \= S2.
brother(B, S) :- sibling(B, S), male(B).
sister(S, Sib) :- sibling(S, Sib), female(S).

% Facts about programming languages
language(pascal, structured).
language(basic, procedural).
language(prolog, logic).
language(python, object_oriented).
language(javascript, scripting).

% Rules about language paradigms
educational(L) :- language(L, structured).
educational(L) :- language(L, procedural).
powerful(L) :- language(L, logic).
modern(L) :- language(L, object_oriented).
web_development(L) :- language(L, scripting).

% Mathematical facts
fibonacci(0, 0).
fibonacci(1, 1).
fibonacci(N, F) :- N > 1, N1 is N - 1, N2 is N - 2,
                   fibonacci(N1, F1), fibonacci(N2, F2), F is F1 + F2.

% List operations demo
member(X, [X|_]).
member(X, [_|T]) :- member(X, T).

% Demo queries (uncomment to test):
% ?- father(john, mary).
% ?- grandparent(susan, alice).
% ?- sibling(mary, mike).
% ?- educational(pascal).
% ?- powerful(prolog).
% ?- fibonacci(5, F).
% ?- member(2, [1,2,3,4]).