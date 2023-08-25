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
    POP_SIZE = 'popsize'
    DIVERSITY = 'diversity'
    EVAL_TIME = 'eval_time'
    SEL_TIME = 'sel_time'
    CROSS_TIME = 'cross_time'
    MUT_TIME = 'mut_time'
    REPL_TIME = 'repl_time'
    ITER_TIME = 'iter_time'

    ALL_COLLS = [
        EVENT,
        GENERATION,
        TIME,
        FITNESS,
        POP_SIZE,
        DIVERSITY,
        EVAL_TIME,
        SEL_TIME,
        CROSS_TIME,
        MUT_TIME,
        REPL_TIME,
        ITER_TIME
    ]


class Schema:
    SCHEMA_FOR_EVENT = {
        Event.NEW_BEST: [Col.GENERATION, Col.TIME, Col.FITNESS],
        Event.DIVERSITY: [Col.GENERATION, Col.TIME, Col.POP_SIZE, Col.DIVERSITY],
        Event.BEST_IN_GEN: [Col.GENERATION, Col.TIME, Col.FITNESS],
        Event.POP_GEN_TIME: [Col.TIME],
        Event.ITER_INFO: [Col.GENERATION, Col.EVAL_TIME, Col.SEL_TIME,
                          Col.CROSS_TIME, Col.MUT_TIME, Col.REPL_TIME, Col.ITER_TIME]
    }

    def for_event(event: str) -> list[str]:
        return Schema.SCHEMA_FOR_EVENT[event]

