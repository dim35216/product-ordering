; Product Ordering problem
; Author: Michael Dinzinger

(define (domain ProductOrdering) 
(:requirements :typing :adl :preferences :numeric-fluents)

(:types product - object)

(:functions
    (changeover-time ?x ?y - product)
    (overall-changeover-time)
)

(:predicates
  (available ?x - product)
  (changeover ?x ?y - product)
  (processing ?x - product)
  (worked-off ?x - product)
  (initialized)
  (complete)
)

(:action initialize
  :parameters (?x - product)
  :precondition (and
                  (available ?x)
                  (not (worked-off ?x))
                  (not (processing ?x))
                  (not (initialized))
                  (not (complete))
                )
  :effect (and
            (processing ?x)
            (initialized)
            (assign (overall-changeover-time) 0)
          )
)

(:action switch
  :parameters (?x ?y - product)
  :precondition (and
                  (available ?x)
                  (available ?y)
                  (changeover ?x ?y)
                  (not (worked-off ?x))
                  (processing ?x)
                  (not (worked-off ?y))
                  (not (processing ?y))
                  (initialized)
                  (not (complete))
                )
  :effect (and
            (worked-off ?x)
            (not (processing ?x))
            (processing ?y)
            (+ (overall-changeover-time) (changeover-time ?x ?y))
          )
)

(:action finalize
  :parameters (?x - product)
  :precondition (and
                  (available ?x)
                  (not (worked-off ?x))
                  (processing ?x)
                  (initialized)
                  (not (complete))
                )
  :effect (and
            (worked-off ?x)
            (not (processing ?x))
            (complete)
          )
)

(:action dummy
  :precondition (and (complete))
)

)
