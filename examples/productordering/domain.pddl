; Product Ordering problem
; Author: Michael Dinzinger

(define (domain ProductOrdering) 
(:requirements :strips :typing :action-costs)

(:types product - object)

(:functions
    (changeover-time ?x ?y - product)
    (total-cost)
)

(:predicates
  (changeover ?x ?y - product)
  (to-be-processed ?x - product)
  (processed ?x - product)
  (queued ?x - product)
  (processing)
  (not-initialized)
  (finalized)
)

(:action initialize
  :parameters (?x - product)
  :precondition (and
                  (not-initialized)
                  (to-be-processed ?x)
                )
  :effect (and
            (queued ?x)
            (processing)
            (not (not-initialized))
          )
)

(:action switch
  :parameters (?x ?y - product)
  :precondition (and
                  (changeover ?x ?y)
                  (to-be-processed ?x)
                  (to-be-processed ?y)
                  (queued ?x)
                  (processing)
                )
  :effect (and
            (not (to-be-processed ?x))
            (processed ?x)
            (queued ?y)
            (increase (total-cost) (changeover-time ?x ?y))
          )
)

(:action finalize
  :parameters (?x - product)
  :precondition (and
                  (to-be-processed ?x)
                  (processing)
                )
  :effect (and
            (not (to-be-processed ?x))
            (processed ?x)
            (not (processing))
            (finalized)
          )
)

(:action dummy
  :precondition (and (finalized))
  :effect (and (finalized))
)

)
