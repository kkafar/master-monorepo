class Event:
    NEW_BEST = 'newbest'
    BEST_IN_GEN = 'bestingen'
    DIVERSITY = 'diversity'
    POP_GEN_TIME = 'popgentime'
    ITER_INFO = 'iterinfo'

    ALL_EVENTS = [
        NEW_BEST,
        BEST_IN_GEN,
        DIVERSITY,
        POP_GEN_TIME,
        ITER_INFO,
    ]


class Col:
    EVENT = 'event'
    GENERATION = 'gen'
    TIME = 'time'
    FITNESS = 'fitness'

    ALL_COLLS = [
        EVENT,
        GENERATION,
        TIME,
        FITNESS,
    ]


COL_EVENT = 'event'
COL_GENERATION = 'gen'
COL_TIME = 'time'
COL_FITNESS = 'fitness'

OUTPUT_LABELS = [
    COL_EVENT,
    COL_GENERATION,
    COL_TIME,
    COL_FITNESS,
]

EVENT_NEW_BEST = 'newbest'
EVENT_BEST_IN_GEN = 'bestingen'
EVENT_DIVERSITY = 'diversity'
EVENT_POP_GEN_TIME = 'popgentime'
EVENT_ITER_INFO = 'iterinfo'

OUTPUT_EVENTS = [
    EVENT_BEST_IN_GEN,
    EVENT_NEW_BEST,
    EVENT_DIVERSITY,
    EVENT_POP_GEN_TIME,
    EVENT_ITER_INFO,
]

