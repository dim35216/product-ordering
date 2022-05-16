(define (problem ProductOrdering-test)
    (:domain ProductOrdering)

(:objects
    p23545
    p12020
    p12021
    p23547 - product
)

(:goal
    (and
        (complete)
        (worked-off p23545)
        (worked-off p12020)
        (worked-off p12021)
        (worked-off p23547)
    )
)

(:init
    (available p23545)
    (available p12020)
    (available p12021)
    (available p23547)
    (= (changeover-time p23545 p23545) 10080)
    (= (changeover-time p23545 p12020) 30)
    (= (changeover-time p23545 p12021) 30)
    (= (changeover-time p23545 p23547) 30)
    (= (changeover-time p12020 p23545) 180)
    (= (changeover-time p12020 p12020) 10080)
    (= (changeover-time p12020 p12021) 90)
    (= (changeover-time p12020 p23547) 480)
    (= (changeover-time p12021 p23545) 180)
    (= (changeover-time p12021 p12020) 90)
    (= (changeover-time p12021 p12021) 10080)
    (= (changeover-time p12021 p23547) 480)
    (= (changeover-time p23547 p23545) 180)
    (= (changeover-time p23547 p12020) 480)
    (= (changeover-time p23547 p12021) 480)
    (= (changeover-time p23547 p23547) 10080)
)

(:metric minimize (+ (overall-changeover-time)))

)
