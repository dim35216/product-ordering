; Product Ordering problem
; Author: Michael Dinzinger

(define (domain ProductOrdering) 
(:requirements :strips :typing :action-costs)

(:types product campaign - object)

(:functions
    (changeover-time ?x ?y - product)
    (total-cost)
)

(:predicates
  (changeover ?x ?y - product)
  (product-campaign ?p - product ?c - campaign)
  (initialized)
  (not-initialized)
  (finalized)
  (product-processed ?x - product)
  (product-queued ?x - product)
  (campaign-processed ?x - product)
  (campaign-queued ?c - campaign)
  (campaign-switch-possible ?c ?d - campaign)
)

(:action initialize
  :parameters (?x - product ?c - campaign)
  :precondition (and
                  (not-initialized)
                  (product-campaign ?x ?c)
                )
  :effect (and
            (product-queued ?x)
            (campaign-queued ?c)
            (initialized)
            (not (not-initialized))
          )
)

(:action product-switch
  :parameters (?x ?y - product ?c - campaign)
  :precondition (and
                  (changeover ?x ?y)
                  (product-queued ?x)
                  (product-campaign ?x ?c)
                  (product-campaign ?y ?c)
                  (campaign-queued ?c)
                  (initialized)
                )
  :effect (and
            (product-processed ?x)
            (not (product-queued ?x))
            (product-queued ?y)
            (increase (total-cost) (changeover-time ?x ?y))
          )
)

(:action campaign-switch
  :parameters (?x ?y - product ?c ?d - campaign)
  :precondition (and
                  (initialized)
                  (changeover ?x ?y)
                  (product-campaign ?x ?c)
                  (product-campaign ?y ?d)
                  (campaign-switch-possible ?c ?d)
                  (product-queued ?x)
                  (campaign-queued ?c)
                )
  :effect (and
            (product-processed ?x)
            (not (product-queued ?x))
            (product-queued ?y)
            (campaign-processed ?c)
            (not (campaign-queued ?c))
            (campaign-queued ?d)
            (increase (total-cost) (changeover-time ?x ?y))
          )
)

(:action finalize
  :parameters (?x - product ?c - campaign)
  :precondition (and
                  (initialized)
                  (product-campaign ?x ?c)
                  (product-queued ?x)
                  (campaign-queued ?c)
                )
  :effect (and
            (not (initialized))
            (finalized)
            (product-processed ?x)
            (not (product-queued ?x))
            (campaign-processed ?c)
            (not (campaign-queued ?c))
          )
)

(:action dummy
  :precondition (and (finalized))
  :effect (and (finalized))
)

)
