(define (problem ProductOrdering-test)
    (:domain ProductOrdering)

(:objects
    p23545
    p12020
    p12021
    p23547
    pstart
    pend - product
    "Blau"
    "Rot"
    "Sterilisation_zu_Wochenbeginn"
    "Wochenendreinigung"
    Start
    End - campaign
)

(:init
    (not-initialized)
    (changeover pstart p23545)
    (= (changeover-time pstart p23545) 0)
    (changeover p23545 pend)
    (= (changeover-time p23545 pend) 0)
    (changeover p23545 p12020)
    (= (changeover-time p23545 p12020) 30)
    (changeover p23545 p12021)
    (= (changeover-time p23545 p12021) 30)
    (changeover p23545 p23547)
    (= (changeover-time p23545 p23547) 30)
    (changeover pstart p12020)
    (= (changeover-time pstart p12020) 0)
    (changeover p12020 pend)
    (= (changeover-time p12020 pend) 0)
    (changeover p12020 p23545)
    (= (changeover-time p12020 p23545) 180)
    (changeover p12020 p12021)
    (= (changeover-time p12020 p12021) 90)
    (changeover p12020 p23547)
    (= (changeover-time p12020 p23547) 480)
    (changeover pstart p12021)
    (= (changeover-time pstart p12021) 0)
    (changeover p12021 pend)
    (= (changeover-time p12021 pend) 0)
    (changeover p12021 p23545)
    (= (changeover-time p12021 p23545) 180)
    (changeover p12021 p12020)
    (= (changeover-time p12021 p12020) 90)
    (changeover p12021 p23547)
    (= (changeover-time p12021 p23547) 480)
    (changeover pstart p23547)
    (= (changeover-time pstart p23547) 0)
    (changeover p23547 pend)
    (= (changeover-time p23547 pend) 0)
    (changeover p23547 p23545)
    (= (changeover-time p23547 p23545) 180)
    (changeover p23547 p12020)
    (= (changeover-time p23547 p12020) 480)
    (changeover p23547 p12021)
    (= (changeover-time p23547 p12021) 480)
    (product-campaign p23545 "Sterilisation_zu_Wochenbeginn")
    (product-campaign p12020 "Rot")
    (product-campaign p12021 "Blau")
    (product-campaign p23547 "Wochenendreinigung")
    (product-campaign pstart Start)
    (product-campaign pend End)
    (campaign-switch-possible Start "Blau")
    (campaign-switch-possible Start "Rot")
    (campaign-switch-possible Start "Sterilisation_zu_Wochenbeginn")
    (campaign-switch-possible Start "Wochenendreinigung")
    (campaign-switch-possible "Blau" End)
    (campaign-switch-possible "Rot" End)
    (campaign-switch-possible "Sterilisation_zu_Wochenbeginn" End)
    (campaign-switch-possible "Wochenendreinigung" End)
    (campaign-switch-possible "Blau" "Rot")
    (campaign-switch-possible "Blau" "Wochenendreinigung")
    (campaign-switch-possible "Rot" "Blau")
    (campaign-switch-possible "Rot" "Wochenendreinigung")
    (campaign-switch-possible "Sterilisation_zu_Wochenbeginn" "Blau")
    (campaign-switch-possible "Sterilisation_zu_Wochenbeginn" "Rot")
    (campaign-switch-possible "Sterilisation_zu_Wochenbeginn" "Wochenendreinigung")
)

(:goal
    (and
        (finalized)
        (product-processed pstart)
        (product-processed pend)
        (product-processed p23545)
        (product-processed p12020)
        (product-processed p12021)
        (product-processed p23547)
        (campaign-processed "Blau")
        (campaign-processed "Rot")
        (campaign-processed "Sterilisation_zu_Wochenbeginn")
        (campaign-processed "Wochenendreinigung")
    )
)

(:metric minimize (total-cost))

)
