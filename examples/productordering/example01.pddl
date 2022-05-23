(define (problem ProductOrdering-example01)
(:domain ProductOrdering)

(:objects
    p10012
    p10014
    p20001
    p50013 - product
)


(:goal (and
    (finalized)
    (processed p10012)
    (processed p10014)
    (processed p20001)
    (processed p50013)
    )
)


(:init
    (to-be-processed p10012)
    (to-be-processed p10014)
    (to-be-processed p20001)
    (to-be-processed p50013)
    (changeover p10012 p10012)
    (changeover p10012 p10014)
    (changeover p10012 p20001)
    (changeover p10012 p50013)
    (changeover p10014 p10012)
    (changeover p10014 p10014)
    (changeover p10014 p20001)
    (changeover p10014 p50013)
    (changeover p20001 p10012)
    (changeover p20001 p10014)
    (changeover p20001 p20001)
    (changeover p20001 p50013)
    (changeover p50013 p10012)
    (changeover p50013 p10014)
    (changeover p50013 p20001)
    (changeover p50013 p50013)
    (= (changeover-time p10012 p10012) 9223372036854775807)
    (= (changeover-time p10012 p10014) 6)
    (= (changeover-time p10012 p20001) 9)
    (= (changeover-time p10012 p50013) 8)
    (= (changeover-time p10014 p10012) 6)
    (= (changeover-time p10014 p10014) 9223372036854775807)
    (= (changeover-time p10014 p20001) 10)
    (= (changeover-time p10014 p50013) 15)
    (= (changeover-time p20001 p10012) 3)
    (= (changeover-time p20001 p10014) 3)
    (= (changeover-time p20001 p20001) 9223372036854775807)
    (= (changeover-time p20001 p50013) 12)
    (= (changeover-time p50013 p10012) 15)
    (= (changeover-time p50013 p10014) 22)
    (= (changeover-time p50013 p20001) 27)
    (= (changeover-time p50013 p50013) 9223372036854775807)
)


(:metric minimize (+ (overall-changeover-time)))

)
